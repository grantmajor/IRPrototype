import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
import streamlit as st

title = "IR Dashboard v0.1a"

st.title(title)
st.set_page_config(layout="wide",
                   page_title=title,
                   )
st.divider()

threshold = 0.0

col1, col2 = st.columns(spec=[0.7, 0.3], width="stretch")

# Import data from project directory
data = pd.read_csv("data/points_inside.csv")


# Convert dataframe to GeoDataFrame
gdf = gpd.GeoDataFrame(
    data,
    geometry=gpd.points_from_xy(data.longitude, data.latitude),
    crs="EPSG:4326"
)


with col2:
    # User sets threshold for colored points
    threshold = st.slider("Velocity Threshold",
                            min_value=0.0, 
                            max_value=5.0, 
                            value=0.0, 
                            step=0.01)
        
# Create absolute value of velocity data
gdf["abs_vel"] = gdf["velocity (cm/yr)"].abs()

# Get data above threshold
high_vel = gdf[gdf["abs_vel"] > threshold]

# Get data below threshold
low_vel = gdf[gdf["abs_vel"] <= threshold]

# Initialize figure
fig = go.Figure()

# Base trace, light gray points for data under velocity threshold
fig.add_trace(go.Scattermap(
    lat=low_vel.geometry.y,
    lon=low_vel.geometry.x,
    mode="markers",
    marker=dict(
        size=7,
        color="lightgray",
        opacity=0.4
    ),
    showlegend=False,
    hoverinfo="skip"
))


# Colored trace, using colorbar for data above threshold
fig.add_trace(go.Scattermap(
    lat=high_vel.geometry.y,
    lon=high_vel.geometry.x,
    mode="markers",
    marker=dict(
        size=9,
        color=high_vel["velocity (cm/yr)"],
        colorscale="IceFire",
        cmin=gdf["velocity (cm/yr)"].min(),
        cmax=gdf["velocity (cm/yr)"].max(),
        colorbar=dict(
            title="Velocity (cm/yr)"
        ),
        showscale=True
    ),
    name="Above Threshold"
))

# Use satellite for base map, center map at data
fig.update_layout(
    map=dict(
        style="satellite",
        zoom=10,
        center=dict(
            lat=gdf.geometry.y.mean(),
            lon=gdf.geometry.x.mean()
        )
    ),
    margin=dict(r=0,t=0,l=0,b=0),
    height=600
)

# Show plot in streamlit
st.plotly_chart(fig, use_container_width=True)