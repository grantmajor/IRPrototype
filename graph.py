import pandas as pd
import geopandas as gpd
import plotly.express as px

data = pd.read_csv("data/points_inside.csv")

# Convert to GeoDataFrame
gdf = gpd.GeoDataFrame(
    data,
    geometry=gpd.points_from_xy(data.longitude, data.latitude),
    crs="EPSG:4326"
)

fig = px.scatter_map(gdf, 
                     lat=gdf.geometry.y,
                     lon=gdf.geometry.x,
                     zoom=12,
                     color="velocity (cm/yr)",
                     color_continuous_scale=px.colors.cyclical.IceFire,
                     map_style="satellite")

fig.show()

