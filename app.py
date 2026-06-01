from dash import Dash, html, dcc, Input, Output, callback
import dash_ag_grid as dag
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go


data = pd.read_csv("data/points_inside.csv")
gdf = gpd.GeoDataFrame(
    data,
    geometry=gpd.points_from_xy(data.longitude, data.latitude),
    crs="EPSG:4326"
)


@callback(
    Output('graph-with-slider', 'figure'),
    Input('threshold-slider', 'value'))
def update_figure(thresh):
    fig = go.Figure()

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

    vel = gdf["velocity (cm/yr)"]

    out_thresh = gdf[
        (vel < thresh[0]) |
        (vel > thresh[1])]
    
    in_thresh = gdf[
    (vel >= thresh[0]) &
    (vel <= thresh[1])]

    
    # Base trace, light gray points for data under velocity threshold
    fig.add_trace(go.Scattermap(
        lat=out_thresh.geometry.y,
        lon=out_thresh.geometry.x,
        mode="markers",
        marker=dict(
            size=7,
            color="lightgray",
            opacity=0.4,
        ),
        showlegend=False,
        hoverinfo="skip"
    ))


    # trace for persistent colorbar
    fig.add_trace(
    go.Scattermap(
        lat=[gdf.geometry.y.mean()],
        lon=[gdf.geometry.x.mean()],
        mode="markers",
        marker=dict(
            size=0,  # invisible
            color=[gdf["velocity (cm/yr)"].min()],
            colorscale="IceFire",
            cmin=gdf["velocity (cm/yr)"].min(),
            cmax=gdf["velocity (cm/yr)"].max(),
            colorbar=dict(
                title="Velocity (cm/yr)"
            ),
            showscale=True
        ),
        hoverinfo="skip",
        showlegend=False
    )
)

    # Colored trace, using colorbar for data above threshold
    fig.add_trace(go.Scattermap(
        lat=in_thresh.geometry.y,
        lon=in_thresh.geometry.x,
        mode="markers",
        marker=dict(
            size=9,
            color=in_thresh["velocity (cm/yr)"],
            colorscale="IceFire",
            cmin=vel.min(),
            cmax=vel.max(),
        ),
        name="In Threshold"
    ))

    return fig




app = Dash()
app.layout = html.Div([
    html.H1(children="IR Prototype v0.2"),
    dcc.RangeSlider(-3, 
               3, 
               step=0.01, 
               value=[-3, 3], 
               id="threshold-slider"),
    dcc.Graph(id='graph-with-slider',
              figure=update_figure([-3, 3]))
])



if __name__ == '__main__':
    app.run(debug=True)