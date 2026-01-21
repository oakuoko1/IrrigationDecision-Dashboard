import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_folium import st_folium
import folium

# 1. Page Config
st.set_page_config(page_title="Irrigation Dashboard", layout="wide")

st.title("🌱 Irrigation Dashboard 2026")

# 2. Mock Data (Replace with your actual sensor data later)
data = pd.DataFrame({
    'Lat': [6.666], 'Lon': [-1.616], 'Moisture': [45]
})

# 3. Sidebar
st.sidebar.header("Controls")
zone = st.sidebar.selectbox("Select Zone", ["Zone A", "Zone B"])

# 4. Layout: Map & Chart
col1, col2 = st.columns(2)

with col1:
    st.subheader("Field Map")
    m = folium.Map(location=[6.666, -1.616], zoom_start=12)
    folium.Marker([6.666, -1.616], popup="Sensor 1").add_to(m)
    st_folium(m, width=500)

with col2:
    st.subheader("Moisture Levels")
    fig = px.bar(data, x='Moisture', orientation='h')
    st.plotly_chart(fig, use_container_width=True)