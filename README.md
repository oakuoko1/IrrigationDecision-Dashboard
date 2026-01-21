# Field-to-Alert: Irrigation Decision Dashboard

A real-time irrigation scheduling dashboard using soil water balance methodology similar to ARSPivot utilizing soil moisture deficit and CWSI (Crop Water Stress Index) to trigger irrigation events. Built as a portfolio project to develop dashboards and platforms for farmers, agronomists or users to assist data driven decisions.


## Features

- **Multi-depth Soil Moisture Monitoring**: Track volumetric water content at 6", 12", and 18" depths
- **Canopy Temperature Tracking**: Monitor crop thermal status for CWSI-based decisions
- **Interactive Visualizations**: Plotly charts with Water Holding Capacity threshold lines
- **Configurable Soil Properties**: Adjust for different texture classes (sand to clay)
- **Real-time Metrics**: Current readings with 24-hour change indicators

## Quick Start
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/irrigation-dashboard.git
cd irrigation-dashboard

# Create and activate virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash
# source venv/bin/activate    # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run Irrapp.py
```

## Project Status

 **Completed Stage 1**: Basic visualizations with non-real sensor data

**Next Steps:**
- Stage 2: Add real-time weather data (Open-Meteo API), water balance calc, CWSI calculations
- Stage 3: Interactive field map, Set up email alerts engine with multimodal AI based recommendations



## Technology Stack

Python, Streamlit, Pandas, Plotly, Folium

## Author

Ohene Akuoko | oakuoko@gmail.com
