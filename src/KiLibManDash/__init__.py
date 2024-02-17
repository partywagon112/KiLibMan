from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px

app = Dash(__name__)

app.layout = html.Div([
    html.H1(children='KiLibMan - Kicad Library Manager', style={'textAlign':'center'}),
    dcc.Dropdown(df.country.unique(), 'Canada', id='dropdown-selection'),
    dcc.Graph(id='graph-content')
])

if __name__ == '__main__':
    app.run(debug=True)