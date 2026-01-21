# src/app.py
"""
Field-to-Alert: Irrigation Decision Dashboard

Stage 1: Basic visualization of synthetic sensor data.

Run with: streamlit run src/app.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# Import our modules
from config import FIELD, SOIL, DISPLAY, get_soil_properties
from FakeData import generate_sensor_data, get_current_conditions
from charts import (
    create_soil_moisture_chart,
    create_temperature_chart,
    create_depth_comparison_chart
)


# =============================================================================
# Page Configuration
# =============================================================================

st.set_page_config(
    page_title="Field-to-Alert | Irrigation Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for cleaner appearance
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1a5276;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        border-left: 4px solid #27ae60;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# Sidebar Configuration
# =============================================================================

with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/irrigation.png", width=80)
    st.title("⚙️ Settings")
    
    st.markdown("---")
    
    # Field Information
    st.subheader("📍 Field Location")
    field_name = st.text_input("Field Name", value=FIELD.name)
    col1, col2 = st.columns(2)
    with col1:
        latitude = st.number_input("Latitude", value=FIELD.latitude, format="%.4f")
    with col2:
        longitude = st.number_input("Longitude", value=FIELD.longitude, format="%.4f")
    
    st.markdown("---")
    
    # Soil Configuration
    st.subheader("🪨 Soil Properties")
    soil_texture = st.selectbox(
        "Soil Texture Class",
        options=list(SOIL.TEXTURE_PROPERTIES.keys()),
        index=list(SOIL.TEXTURE_PROPERTIES.keys()).index("Silt Loam")
    )
    
    # Display selected soil properties
    soil_props = get_soil_properties(soil_texture)
    st.caption(f"Field Capacity: {soil_props['fc']:.2f} cm³/cm³")
    st.caption(f"Wilting Point: {soil_props['pwp']:.2f} cm³/cm³")
    st.caption(f"Available Water: {soil_props['taw']:.2f} cm³/cm³")
    
    st.markdown("---")
    
    # Display Settings
    st.subheader("📊 Display Options")
    days_history = st.slider("Days of History", 3, 30, DISPLAY.days_history)
    show_thresholds = st.checkbox("Show Threshold Lines", value=True)
    
    st.markdown("---")
    
    # Refresh button
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# =============================================================================
# Data Generation (Cached)
# =============================================================================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_sensor_data(days: int, texture: str) -> pd.DataFrame:
    """Generate and cache synthetic sensor data."""
    return generate_sensor_data(days=days, soil_texture=texture)


# Load data
df = load_sensor_data(days_history, soil_texture)
current = get_current_conditions(df)


# =============================================================================
# Main Dashboard
# =============================================================================

# Header
st.markdown(f'<p class="main-header">🌱 Field-to-Alert Dashboard</p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-header">{field_name} | {FIELD.crop} | {FIELD.growth_stage}</p>', unsafe_allow_html=True)

# Current Conditions - Key Metrics Row
st.subheader("📡 Current Sensor Readings")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="6\" Soil Moisture",
        value=f"{current['sm_6in']:.3f}",
        delta=f"{(current['sm_6in'] - df['sm_6in'].iloc[-24]):.3f} (24h)",
        help="Volumetric water content at 6 inch depth"
    )

with col2:
    st.metric(
        label="12\" Soil Moisture",
        value=f"{current['sm_12in']:.3f}",
        delta=f"{(current['sm_12in'] - df['sm_12in'].iloc[-24]):.3f} (24h)",
        help="Volumetric water content at 12 inch depth"
    )

with col3:
    st.metric(
        label="18\" Soil Moisture",
        value=f"{current['sm_18in']:.3f}",
        delta=f"{(current['sm_18in'] - df['sm_18in'].iloc[-24]):.3f} (24h)",
        help="Volumetric water content at 18 inch depth"
    )

with col4:
    st.metric(
        label="Canopy Temp",
        value=f"{current['canopy_temp_c']:.1f}°C",
        delta=f"{(current['canopy_temp_c'] - current['air_temp_c']):.1f}°C vs Air",
        delta_color="inverse",  # Negative is good (cooler canopy)
        help="Canopy temperature from infrared sensor"
    )

with col5:
    st.metric(
        label="Air Temp",
        value=f"{current['air_temp_c']:.1f}°C",
        help="Ambient air temperature"
    )

st.caption(f"Last updated: {current['timestamp'].strftime('%Y-%m-%d %H:%M')}")

st.markdown("---")

# Charts Section
st.subheader("📈 Soil Moisture Trends")

# Main soil moisture chart
moisture_chart = create_soil_moisture_chart(df, soil_texture, show_thresholds)
st.plotly_chart(moisture_chart, use_container_width=True)

# Temperature and depth comparison side by side
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🌡️ Temperature Trends")
    temp_chart = create_temperature_chart(df)
    st.plotly_chart(temp_chart, use_container_width=True)

with col_right:
    st.subheader("📊 Moisture Profile")
    depth_chart = create_depth_comparison_chart(df)
    st.plotly_chart(depth_chart, use_container_width=True)

st.markdown("---")

# Data Table (Collapsible)
with st.expander("📋 View Raw Data"):
    st.dataframe(
        df.tail(48).sort_values('timestamp', ascending=False),
        use_container_width=True,
        hide_index=True
    )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #888; font-size: 0.9rem;'>
        <p>Stage 1: Basic Visualization | Built for Grower Engagement Demo</p>
        <p>Data shown is synthetic for demonstration purposes</p>
    </div>
    """,
    unsafe_allow_html=True
)