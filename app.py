from dash import Dash, html, dcc, Input, Output, callback
import dash_ag_grid as dag
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go

# read data and convert to geodataframe
data = pd.read_csv("data/points_inside.csv")
gdf = gpd.GeoDataFrame(
    data,
    geometry=gpd.points_from_xy(data.longitude, data.latitude),
    crs="EPSG:4326"
)


# set initial slider range to min/max of velocity column
MIN_THRESHOLD = gdf["velocity (cm/yr)"].min()
MAX_THRESHOLD = gdf["velocity (cm/yr)"].max()


# when slider changes, updates highlighted points and colorbar
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
        title=dict(
            text="Isabella Road Land Subsidence Velocity",
            x=0.5,
        ),
        margin=dict(r=0,t=0,l=0,b=0),
        autosize=True
    )

    vel = gdf["velocity (cm/yr)"]

    out_thresh = gdf[
        (vel < MIN_THRESHOLD) |
        (vel > MAX_THRESHOLD)]
    
    in_thresh = gdf[
    (vel >= MIN_THRESHOLD) &
    (vel <= MAX_THRESHOLD)]

    
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
            color=[MIN_THRESHOLD, MAX_THRESHOLD],
            colorscale="IceFire",
            cmin=MIN_THRESHOLD,
            cmax=MAX_THRESHOLD,
            colorbar=dict(
                x=0.98,
                y=0.98,
                xanchor="right",
                yanchor="top",
                title=dict(text="Velocity (cm/yr)",
                           font=dict(color="white")),
                len=0.5,
                thickness=15,
                orientation="h",
                tickfont=dict(size=10,
                              color="white"),
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


# when slider changes, updates text showing current range
@callback(
    Output("range-value", "children"),
    Input("threshold-slider", "value")
)
def display_range(val):
    return f"Range: [{val[0]:.2f}, {val[1]:.2f}] cm/yr"


@callback(
    Output("summ-stats", "children"),
    Input("threshold-slider", "value")
)
def update_stats(val):
    vel = gdf["velocity (cm/yr)"]
    in_thresh = gdf[
        (vel >= val[0]) &
        (vel <= val[1])
    ]

    total = len(gdf)
    count = len(in_thresh)
    percent = 100 * count / total if total > 0 else 0 

    return html.Div([
        html.H4("Statistics for Points in Threshold"),
        html.P(f"Points in Threshold: {count}"),
        html.P(f"Percent of Total: {percent:.1f}%"),
        html.P(f"Mean velocity: {in_thresh['velocity (cm/yr)'].mean():.2f} cm/yr"),
        html.P(f"Median velocity: {in_thresh['velocity (cm/yr)'].median():.2f} cm/yr"),
    ])

app = Dash()

# set app layout
app.layout = html.Div([


    html.H1("IR Prototype v0.2",
            style={"textAlign": "center"}),

    # div with slider and graph side by side
    html.Div([

        # div for threshold slider and text
        html.Div([
            
            html.H3("Velocity Threshold (cm/yr)"),

            dcc.RangeSlider(round(MIN_THRESHOLD, 2), round(MAX_THRESHOLD, 2),
                step=0.01,
                value=[MIN_THRESHOLD, MAX_THRESHOLD],
                id="threshold-slider"),
            
        html.Br(),

        html.Div(id="range-value"),

        html.Div(id="summ-stats")

        ],

        style= {"width": "20%",
                "padding": "20px"}), 


    # div for graph on right side
    html.Div([
        dcc.Graph(
            id='graph-with-slider',
            style={"height" : "85vh"},
            figure=update_figure([MIN_THRESHOLD, MAX_THRESHOLD])
            )
    ],
    style={"width": "80%"})

],
style={"display" : "flex"}

    )


])



if __name__ == '__main__':
    app.run(debug=True)