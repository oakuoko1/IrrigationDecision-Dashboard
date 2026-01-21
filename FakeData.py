# src/data/synthetic.py
"""
Synthetic sensor data generation for dashboard demonstration.

Generates realistic soil moisture and canopy temperature patterns that:
- Show gradual drying from evapotranspiration
- Respond to rain events with moisture increases
- Display depth-dependent lag in moisture changes
- Include diurnal temperature patterns
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional

import sys
sys.path.append('..')
from config import FIELD, SOIL, SENSOR, get_soil_properties


def generate_sensor_data(
    days: int = 14,
    soil_texture: str = "Silt Loam",
    include_rain_events: bool = True,
    seed: Optional[int] = 42
) -> pd.DataFrame:
    """
    Generate synthetic soil moisture and canopy temperature data.
    
    The algorithm simulates:
    1. Base moisture starting at ~70% of field capacity
    2. Daily ET-driven depletion (faster in shallow depths)
    3. Rain events that increase moisture (deeper depths respond slower)
    4. Diurnal canopy temperature patterns
    
    Args:
        days: Number of days of historical data to generate
        soil_texture: Soil texture class for FC/PWP values
        include_rain_events: Whether to simulate rain events
        seed: Random seed for reproducibility
        
    Returns:
        DataFrame with columns: timestamp, sm_6in, sm_12in, sm_18in, 
                               canopy_temp_c, air_temp_c
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Get soil properties for this texture
    soil_props = get_soil_properties(soil_texture)
    fc = soil_props["fc"]       # Field capacity
    pwp = soil_props["pwp"]     # Wilting point
    taw = soil_props["taw"]     # Total available water
    
    # Generate hourly timestamps
    end_time = datetime.now().replace(minute=0, second=0, microsecond=0)
    start_time = end_time - timedelta(days=days)
    timestamps = pd.date_range(start=start_time, end=end_time, freq='h')
    n_hours = len(timestamps)
    
    # Initialize moisture at each depth (start at ~70% of available water)
    initial_moisture = pwp + 0.70 * taw
    
    sm_6in = np.full(n_hours, initial_moisture)
    sm_12in = np.full(n_hours, initial_moisture)
    sm_18in = np.full(n_hours, initial_moisture)
    
    # ET depletion rates (inches/hour) - faster near surface
    # Typical peak ET is ~0.3 in/day, distributed by depth
    base_et_rate = 0.012  # in/hour at peak
    
    # Depth-specific depletion factors (shallow dries faster)
    depletion_factors = {6: 1.0, 12: 0.6, 18: 0.3}
    
    # Generate rain events (if enabled)
    rain_events = []
    if include_rain_events:
        # Add 2-4 rain events over the period
        n_events = np.random.randint(2, 5)
        event_hours = np.random.choice(range(24, n_hours - 24), n_events, replace=False)
        
        for hour in event_hours:
            # Rain amount between 0.2 and 1.0 inches
            amount = np.random.uniform(0.2, 1.0)
            rain_events.append((hour, amount))
    
    # Simulate moisture dynamics hour by hour
    for i in range(1, n_hours):
        hour_of_day = timestamps[i].hour
        
        # Diurnal ET pattern (peaks at 2pm, minimal at night)
        if 6 <= hour_of_day <= 20:
            diurnal_factor = np.sin(np.pi * (hour_of_day - 6) / 14)
        else:
            diurnal_factor = 0.0
        
        hourly_et = base_et_rate * diurnal_factor
        
        # Apply ET depletion at each depth
        # Convert ET (inches) to volumetric change (approximate)
        et_volumetric = hourly_et / 6  # Simplified conversion
        
        sm_6in[i] = sm_6in[i-1] - et_volumetric * depletion_factors[6]
        sm_12in[i] = sm_12in[i-1] - et_volumetric * depletion_factors[12]
        sm_18in[i] = sm_18in[i-1] - et_volumetric * depletion_factors[18]
        
        # Check for rain events
        for event_hour, amount in rain_events:
            if i == event_hour:
                # Rain infiltration - immediate at surface, delayed at depth
                sm_6in[i] += amount * 0.08   # Quick response
                sm_12in[i] += amount * 0.04  # Delayed
                sm_18in[i] += amount * 0.02  # More delayed
            elif event_hour < i < event_hour + 12:
                # Continued infiltration to deeper depths
                hours_since = i - event_hour
                sm_12in[i] += amount * 0.003 * (12 - hours_since) / 12
                sm_18in[i] += amount * 0.002 * (12 - hours_since) / 12
        
        # Clamp values to physically realistic range
        sm_6in[i] = np.clip(sm_6in[i], pwp * 0.8, fc * 1.05)
        sm_12in[i] = np.clip(sm_12in[i], pwp * 0.8, fc * 1.05)
        sm_18in[i] = np.clip(sm_18in[i], pwp * 0.8, fc * 1.05)
    
    # Add measurement noise
    sm_6in += np.random.normal(0, SENSOR.moisture_noise_std, n_hours)
    sm_12in += np.random.normal(0, SENSOR.moisture_noise_std, n_hours)
    sm_18in += np.random.normal(0, SENSOR.moisture_noise_std, n_hours)
    
    # Generate air temperature with diurnal pattern
    # Base temp around 30°C with ±8°C daily swing
    base_temp = 30.0
    daily_amplitude = 8.0
    
    air_temp = np.array([
        base_temp + daily_amplitude * np.sin(np.pi * (ts.hour - 6) / 12)
        if 6 <= ts.hour <= 18 
        else base_temp - daily_amplitude * 0.5
        for ts in timestamps
    ])
    air_temp += np.random.normal(0, SENSOR.temp_noise_std, n_hours)
    
    # Canopy temperature: typically 1-4°C above air when stressed
    # Healthy, transpiring plants can be cooler than air
    # We'll make it correlate with soil moisture (drier = hotter canopy)
    avg_moisture = (sm_6in + sm_12in) / 2
    moisture_stress = 1 - (avg_moisture - pwp) / taw  # 0 = wet, 1 = dry
    moisture_stress = np.clip(moisture_stress, 0, 1)
    
    # Canopy temp offset: -2°C when wet (transpiring) to +5°C when stressed
    canopy_offset = -2 + 7 * moisture_stress
    canopy_temp = air_temp + canopy_offset
    canopy_temp += np.random.normal(0, SENSOR.temp_noise_std * 0.5, n_hours)
    
    # Build DataFrame
    df = pd.DataFrame({
        'timestamp': timestamps,
        'sm_6in': np.round(sm_6in, 4),
        'sm_12in': np.round(sm_12in, 4),
        'sm_18in': np.round(sm_18in, 4),
        'canopy_temp_c': np.round(canopy_temp, 1),
        'air_temp_c': np.round(air_temp, 1),
    })
    
    return df


def get_current_conditions(df: pd.DataFrame) -> dict:
    """
    Extract current (most recent) sensor readings.
    
    Returns dict with latest values for display in metrics.
    """
    latest = df.iloc[-1]
    
    return {
        'timestamp': latest['timestamp'],
        'sm_6in': latest['sm_6in'],
        'sm_12in': latest['sm_12in'],
        'sm_18in': latest['sm_18in'],
        'canopy_temp_c': latest['canopy_temp_c'],
        'air_temp_c': latest['air_temp_c'],
    }