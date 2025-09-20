# Minimal Dash placeholder
import dash
from dash import html

app = dash.Dash(__name__)
app.layout = html.Div([html.H1("UK Open Data Analytics"), html.P("Dashboard placeholder.")])
# NEW (works)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)

