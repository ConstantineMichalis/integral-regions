import pandas as pd
import plotly.express as px
import flask
import dash; import dash_core_components as dcc; import dash_html_components as html
from dash.dependencies import Input, Output

# Setup the app. The server & app names should match those in Procfile 
app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])

# Associating server
server = app.server

dsn_tns = cx_Oracle.makedsn(r'maxorclprd30.maintain.integral.co.uk', '1521', service_name='PRD30MAX') 
conn = cx_Oracle.connect(user=r'constantine_michalis', password=r'68Pe_kdV7yzC5eX', dsn=dsn_tns) 


cur = conn.cursor()

cur.execute("""select distinct l.location, pluspcustomer, c.name,  s.latitudey, s.longitudex, a.ancestor, a2.ancestor as branch, c.type, l.status, s.postalcode
            from JLL_MX76_PRD30_1.locations l 
            join JLL_MX76_PRD30_1.serviceaddress s on l.saddresscode = s.addresscode
            join JLL_MX76_PRD30_1.locancestor a on a.location = l.location
            join JLL_MX76_PRD30_1.locancestor a2 on a2.location = l.location
            join JLL_MX76_PRD30_1.pluspcustomer c on c.customer = l.pluspcustomer
            where ((a.ancestor not like ('L%')) and (a.ancestor not like ('%00000%')) and (a2.ancestor not like ('L%')) and (a2.ancestor like ('%00000%')) and (a2.ancestor != '000000'))
            and (l.pluspcustomer in (select customer from JLL_MX76_PRD30_1.pluspagreement where enddate>sysdate) and c.status = 'ACTIVE')
            """)


rows = cur.fetchall()

dts = pd.DataFrame(rows)

col_names = list([row[0] for row in cur.description])
dts.columns = col_names

conn.close()

#dts = pd.read_csv('./Locationregions.csv', sep= ',',encoding='cp1252')
lab = pd.read_csv('./laborregions.csv', sep= ',',encoding='cp1252')

dts = dts[dts['PLUSPCUSTOMER'] != 'C1000238']
dts.dtypes
dts.ANCESTOR = dts.ANCESTOR.astype('object') 
dts.BRANCH = dts.BRANCH.astype('object') 
dts.TYPE = dts.TYPE.astype('object') 
lab.LOCATION = lab.LOCATION.astype('object') 
token = open("./mapbox.token").read()



mycols = ['#e4717a', '#5d8aa8', '#a4c639', '#ffa812', '#a67b5b', '#915c83']

dark = dts[dts['STATUS'] == 'OPERATING']
fig1 = px.scatter_mapbox(dark, lat="LATITUDEY", 
                        lon="LONGITUDEX",
                        color="ANCESTOR", hover_data=(['LOCATION', 'PLUSPCUSTOMER'])
                        #, animation_frame = "ANCESTOR"
                        )

fig1.update_layout(mapbox_center_lat=53.55, mapbox_center_lon=-2.433,
                  mapbox = {'accesstoken': token,  'style': "carto-darkmatter", 'zoom': 4.7})


app.title = 'Integral Regions'
app.layout = html.Div([
    html.Div([html.Label('Add Customer (Write "All" for full overview)'),
              dcc.Input(id = 'cust1', value = 'All', type = 'text')], className = 'three columns'),
    html.Div([dcc.Graph(id='fig1', figure=fig1,style={'height': '90vh'})], className="nine columns")])

@app.callback (Output('fig1', 'figure'), [Input('cust1', 'value')])
def updatefig(g):
    if g=="All": return fig1
    elif g=="all": return fig1
    else: return px.scatter_mapbox(dark.query("PLUSPCUSTOMER == '"+g+"'"), lat="LATITUDEY", lon="LONGITUDEX", color="ANCESTOR", hover_data=(['LOCATION', 'PLUSPCUSTOMER'])).update_layout(mapbox_center_lat=53.55, mapbox_center_lon=-2.433, mapbox = {'accesstoken': token,  'style': "carto-darkmatter", 'zoom': 4.7})


# Run the Dash app
if __name__ == "__main__":
    # Starting flask server
    app.run_server(debug=True)
