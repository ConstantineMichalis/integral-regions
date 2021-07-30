import flask; import plotly.express as px
import dash; import dash_core_components as dcc; import dash_html_components as html
from dash.dependencies import Input, Output

# Setup the app. The server & app names should match those in Procfile 
server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)


app.layout = html.H1("SAGAPAW RE MALAKA", className="header__text")


# Run the Dash app
app.run_server(debug=True, use_reloader=False)
