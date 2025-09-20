# app/dashboard.py
import os
import pandas as pd
from sqlalchemy import create_engine
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# ---- DB connection (matches docker-compose) ----
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "ukdata")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")
ENGINE = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# ---- App ----
app = dash.Dash(__name__)
app.title = "UK Open Data Analytics"

def year_clause(year: str) -> str:
    if year == "All":
        return ""
    y = int(year)
    # inclusive start, exclusive end (index friendly)
    return f"accident_date >= DATE '{y}-01-01' AND accident_date < DATE '{y+1}-01-01'"


def kpis_sql(year, max_sev):
    where = []
    yc = year_clause(year)
    if yc:
        where.append(yc)
    if max_sev:
        where.append(f"severity <= {int(max_sev)}")
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    return f"""
        SELECT
          COUNT(*)::BIGINT AS n,
          COALESCE(AVG(number_of_casualties),0) AS avg_cas,
          COALESCE(AVG(number_of_vehicles),0)  AS avg_veh
        FROM accidents
        {where_sql};
    """

def trend_sql(year, max_sev):
    where = []
    yc = year_clause(year)
    if yc:
        where.append(yc)
    if max_sev:
        where.append(f"severity <= {int(max_sev)}")
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    return f"""
        SELECT DATE_TRUNC('month', accident_date) AS month, COUNT(*)::BIGINT AS cnt
        FROM accidents
        {where_sql}
        GROUP BY 1
        ORDER BY 1;
    """


def roads_sql(year, max_sev):
    where = []
    yc = year_clause(year)
    if yc:
        where.append(yc)
    if max_sev:
        where.append(f"severity <= {int(max_sev)}")
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    return f"""
        SELECT road_type, COUNT(*)::BIGINT AS cnt
        FROM accidents
        {where_sql}
        GROUP BY road_type
        ORDER BY cnt DESC NULLS LAST
        LIMIT 10;
    """

def points_sql(year, max_sev, limit=5000):
    where = ["latitude IS NOT NULL", "longitude IS NOT NULL"]
    yc = year_clause(year)
    if yc:
        where.append(yc)
    if max_sev:
        where.append(f"severity <= {int(max_sev)}")
    where_sql = "WHERE " + " AND ".join(where)
    return f"""
        SELECT latitude, longitude, severity
        FROM accidents
        {where_sql}
        LIMIT {int(limit)};
    """


app.layout = html.Div(
    [
        html.H1("🇬🇧 UK Open Data Analytics", style={"marginBottom": "8px"}),

        html.Div(
            [
                html.Div(
                    [
                        html.Label("Year"),
                        dcc.Dropdown(
                            id="year",
                            options=["All", 2019, 2020, 2021, 2022, 2023],
                            value="All",
                            clearable=False,
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Label("Max severity (1=fatal, 3=slight)"),
                        dcc.Dropdown(
                            id="max_sev",
                            options=[1, 2, 3],
                            value=3,
                            clearable=False,
                        ),
                    ]
                ),
            ],
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "12px", "maxWidth": "520px"},
        ),

        html.Div(id="kpi-cards",
                 style={"display": "grid", "gridTemplateColumns": "repeat(3, 1fr)",
                        "gap": "12px", "marginTop": "14px"}),

        dcc.Graph(id="trend", style={"height": "320px", "marginTop": "10px"}),
        dcc.Graph(id="roads", style={"height": "320px"}),
        dcc.Graph(id="map", style={"height": "600px"}),
    ],
    style={"padding": "16px"},
)

# ---- Callbacks ----
@app.callback(
    Output("kpi-cards", "children"),
    Input("year", "value"),
    Input("max_sev", "value"),
)
def render_kpis(year, max_sev):
    df = pd.read_sql(kpis_sql(year, max_sev), ENGINE)
    n = int(df.loc[0, "n"])
    avg_cas = float(df.loc[0, "avg_cas"])
    avg_veh = float(df.loc[0, "avg_veh"])

    def card(title, value):
        return html.Div(
            [
                html.Div(title, style={"color": "#808080", "fontSize": "14px"}),
                html.Div(value, style={"fontSize": "28px", "fontWeight": "700"}),
            ],
            style={"border": "1px solid #333", "borderRadius": "12px", "padding": "16px"},
        )

    return [card("Accidents", f"{n:,}"),
            card("Avg casualties", f"{avg_cas:.2f}"),
            card("Avg vehicles", f"{avg_veh:.2f}")]

@app.callback(
    Output("trend", "figure"),
    Input("year", "value"),
    Input("max_sev", "value"),
)
def render_trend(year, max_sev):
    df = pd.read_sql(trend_sql(year, max_sev), ENGINE)
    fig = px.line(df, x="month", y="cnt", markers=True, title="Monthly accidents")
    fig.update_layout(xaxis_title="Month", yaxis_title="Count")
    return fig

@app.callback(
    Output("roads", "figure"),
    Input("year", "value"),
    Input("max_sev", "value"),
)
def render_roads(year, max_sev):
    df = pd.read_sql(roads_sql(year, max_sev), ENGINE)
    fig = px.bar(df, x="road_type", y="cnt", title="Top road types")
    fig.update_layout(xaxis_title="Road type", yaxis_title="Count")
    return fig

@app.callback(
    Output("map", "figure"),
    Input("year", "value"),
    Input("max_sev", "value"),
)
def render_map(year, max_sev):
    df = pd.read_sql(points_sql(year, max_sev, limit=5000), ENGINE)
    if df.empty:
        return px.scatter_mapbox(lat=[], lon=[], zoom=4).update_layout(mapbox_style="open-street-map", title="Map")
    fig = px.scatter_mapbox(df, lat="latitude", lon="longitude", color="severity",
                            title="Accidents (sampled)", zoom=4, height=600)
    fig.update_layout(mapbox_style="open-street-map")
    return fig

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)
