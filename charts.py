# src/visualization/charts.py
"""
Plotly chart generation for the irrigation dashboard.

Creates interactive time series visualizations for:
- Soil moisture at multiple depths
- Canopy and air temperature
- Threshold reference lines
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, Optional

import sys
sys.path.append('..')
from config import DISPLAY, SOIL, get_soil_properties


def create_soil_moisture_chart(
    df: pd.DataFrame,
    soil_texture: str = "Silt Loam",
    show_thresholds: bool = True
) -> go.Figure:
    """
    Create an interactive soil moisture time series chart.
    
    Shows moisture at 3 depths with field capacity and wilting point
    reference lines for context.
    
    Args:
        df: DataFrame with timestamp, sm_6in, sm_12in, sm_18in columns
        soil_texture: Soil texture class for threshold lines
        show_thresholds: Whether to display FC/PWP reference lines
        
    Returns:
        Plotly Figure object
    """
    # Get soil properties for threshold lines
    soil_props = get_soil_properties(soil_texture)
    fc = soil_props["fc"]
    pwp = soil_props["pwp"]
    
    # Create figure
    fig = go.Figure()
    
    # Add soil moisture traces for each depth
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['sm_6in'],
        name='6" Depth',
        line=dict(color=DISPLAY.colors['depth_6in'], width=2),
        hovertemplate='%{y:.3f} cm³/cm³<extra>6" Depth</extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['sm_12in'],
        name='12" Depth',
        line=dict(color=DISPLAY.colors['depth_12in'], width=2),
        hovertemplate='%{y:.3f} cm³/cm³<extra>12" Depth</extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['sm_18in'],
        name='18" Depth',
        line=dict(color=DISPLAY.colors['depth_18in'], width=2),
        hovertemplate='%{y:.3f} cm³/cm³<extra>18" Depth</extra>'
    ))
    
    # Add threshold reference lines
    if show_thresholds:
        # Field Capacity line
        fig.add_hline(
            y=fc, 
            line_dash="dash", 
            line_color="#3498db",
            annotation_text="Field Capacity",
            annotation_position="right"
        )
        
        # Wilting Point line
        fig.add_hline(
            y=pwp, 
            line_dash="dash", 
            line_color="#e74c3c",
            annotation_text="Wilting Point",
            annotation_position="right"
        )
        
        # MAD threshold (refill point)
        mad_threshold = pwp + 0.5 * (fc - pwp)  # 50% depletion
        fig.add_hline(
            y=mad_threshold,
            line_dash="dot",
            line_color="#f39c12",
            annotation_text="Refill Point (50% MAD)",
            annotation_position="right"
        )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text="Soil Moisture by Depth",
            font=dict(size=20)
        ),
        xaxis_title="Date/Time",
        yaxis_title="Volumetric Water Content (cm³/cm³)",
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=400,
        margin=dict(l=60, r=120, t=80, b=60),
        plot_bgcolor='white',
        yaxis=dict(
            gridcolor='#f0f0f0',
            range=[0, 0.50]  # Typical VWC range
        ),
        xaxis=dict(gridcolor='#f0f0f0')
    )
    
    return fig


def create_temperature_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create a dual temperature chart showing canopy and air temperature.
    
    The difference between canopy and air temperature indicates stress:
    - Canopy cooler than air = healthy transpiration
    - Canopy warmer than air = water stress
    
    Args:
        df: DataFrame with timestamp, canopy_temp_c, air_temp_c columns
        
    Returns:
        Plotly Figure object
    """
    fig = go.Figure()
    
    # Air temperature trace
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['air_temp_c'],
        name='Air Temperature',
        line=dict(color='#3498db', width=2),
        hovertemplate='%{y:.1f}°C<extra>Air</extra>'
    ))
    
    # Canopy temperature trace
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['canopy_temp_c'],
        name='Canopy Temperature',
        line=dict(color='#e74c3c', width=2),
        hovertemplate='%{y:.1f}°C<extra>Canopy</extra>'
    ))
    
    # Add shaded region between them to highlight differential
    fig.add_trace(go.Scatter(
        x=df['timestamp'].tolist() + df['timestamp'].tolist()[::-1],
        y=df['canopy_temp_c'].tolist() + df['air_temp_c'].tolist()[::-1],
        fill='toself',
        fillcolor='rgba(231, 76, 60, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Tc - Ta Differential',
        showlegend=True,
        hoverinfo='skip'
    ))
    
    fig.update_layout(
        title=dict(
            text="Canopy & Air Temperature",
            font=dict(size=20)
        ),
        xaxis_title="Date/Time",
        yaxis_title="Temperature (°C)",
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=350,
        margin=dict(l=60, r=60, t=80, b=60),
        plot_bgcolor='white',
        yaxis=dict(gridcolor='#f0f0f0'),
        xaxis=dict(gridcolor='#f0f0f0')
    )
    
    return fig


def create_depth_comparison_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create a stacked area chart comparing moisture across depths.
    
    Useful for visualizing the soil moisture profile and
    identifying which depth is driving stress.
    """
    fig = go.Figure()
    
    # Get last 72 hours for cleaner visualization
    df_recent = df.tail(72)
    
    fig.add_trace(go.Scatter(
        x=df_recent['timestamp'],
        y=df_recent['sm_18in'],
        name='18" (Deep)',
        fill='tozeroy',
        line=dict(color=DISPLAY.colors['depth_18in']),
        stackgroup='one'
    ))
    
    fig.add_trace(go.Scatter(
        x=df_recent['timestamp'],
        y=df_recent['sm_12in'] - df_recent['sm_18in'],
        name='12" (Middle)',
        fill='tonexty',
        line=dict(color=DISPLAY.colors['depth_12in']),
        stackgroup='one'
    ))
    
    fig.add_trace(go.Scatter(
        x=df_recent['timestamp'],
        y=df_recent['sm_6in'] - df_recent['sm_12in'],
        name='6" (Surface)',
        fill='tonexty',
        line=dict(color=DISPLAY.colors['depth_6in']),
        stackgroup='one'
    ))
    
    fig.update_layout(
        title="Soil Moisture Profile (Last 72 Hours)",
        xaxis_title="Date/Time",
        yaxis_title="Cumulative VWC",
        height=300,
        margin=dict(l=60, r=60, t=60, b=60),
        plot_bgcolor='white',
    )
    
    return fig