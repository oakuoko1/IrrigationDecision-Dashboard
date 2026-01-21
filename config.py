# src/config.py
"""
Configuration module for the Irrigation Dashboard.
Centralizes all constants, thresholds, and default settings.
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class FieldConfig:
    """Field location and identification."""
    name: str = "Demo Research Field"
    latitude: float = 34.15      # Texas Panhandle (similar to your ARS work)
    longitude: float = -102.05
    acreage: float = 125.0
    crop: str = "Corn"
    growth_stage: str = "V12 (Rapid Vegetative)"


@dataclass
class SoilConfig:
    """
    Soil hydraulic properties by texture class.
    
    FC = Field Capacity (volumetric water content, cm³/cm³)
    PWP = Permanent Wilting Point (cm³/cm³)
    TAW = Total Available Water = FC - PWP
    
    Values from USDA NRCS Soil Survey typical ranges.
    """
    
    TEXTURE_PROPERTIES: Dict[str, Dict[str, float]] = field(default_factory=lambda: {
        "Sand":            {"fc": 0.12, "pwp": 0.04},
        "Loamy Sand":      {"fc": 0.14, "pwp": 0.06},
        "Sandy Loam":      {"fc": 0.23, "pwp": 0.10},
        "Loam":            {"fc": 0.27, "pwp": 0.12},
        "Silt Loam":       {"fc": 0.33, "pwp": 0.13},
        "Sandy Clay Loam": {"fc": 0.26, "pwp": 0.15},
        "Clay Loam":       {"fc": 0.32, "pwp": 0.20},
        "Silty Clay Loam": {"fc": 0.37, "pwp": 0.22},
        "Clay":            {"fc": 0.43, "pwp": 0.29},
    })
    
    default_texture: str = "Silt Loam"


@dataclass
class WaterBalanceConfig:
    """
    Parameters for ARSPivot-style water balance model.
    
    SWD(t) = SWD(t-1) + ETc - Rain - Irrigation
    
    Irrigation triggered when SWD > MAD × TAW × RootDepth
    """
    
    mad_threshold: float = 0.50      # Management Allowable Depletion (50% of TAW)
    root_depth_in: float = 36.0      # Effective root zone depth
    crop_coefficient: float = 1.15   # Kc for corn at mid-season


@dataclass
class SensorConfig:
    """Sensor depths and data generation parameters."""
    
    depths_inches: List[int] = field(default_factory=lambda: [6, 12, 18])
    
    # Synthetic data parameters (realistic ranges)
    moisture_noise_std: float = 0.015     # Volumetric noise (±1.5%)
    temp_noise_std: float = 0.8           # Temperature noise (±0.8°C)
    canopy_temp_offset: float = 2.0       # Canopy typically warmer than air


@dataclass
class DisplayConfig:
    """UI and visualization settings."""
    
    days_history: int = 14
    
    colors: Dict[str, str] = field(default_factory=lambda: {
        "critical": "#e74c3c",     # Red - irrigate NOW
        "warning": "#f39c12",      # Orange - irrigate soon
        "optimal": "#27ae60",      # Green - good
        "saturated": "#3498db",    # Blue - too wet
        "depth_6in": "#e74c3c",    # Red for shallow
        "depth_12in": "#f39c12",   # Orange for mid
        "depth_18in": "#27ae60",   # Green for deep
    })


# Singleton instances for easy import
FIELD = FieldConfig()
SOIL = SoilConfig()
WATER_BALANCE = WaterBalanceConfig()
SENSOR = SensorConfig()
DISPLAY = DisplayConfig()


def get_soil_properties(texture: str) -> Dict[str, float]:
    """
    Get soil hydraulic properties for a texture class.
    
    Returns dict with: fc, pwp, taw (total available water)
    """
    props = SOIL.TEXTURE_PROPERTIES.get(texture, SOIL.TEXTURE_PROPERTIES["Silt Loam"])
    
    return {
        "fc": props["fc"],
        "pwp": props["pwp"],
        "taw": props["fc"] - props["pwp"],  # Total Available Water
    }