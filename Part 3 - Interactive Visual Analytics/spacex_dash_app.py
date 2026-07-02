# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
launch_sites_df = spacex_df.groupby(['Launch Site'], as_index=False).first()
spacex_df['label class'] = spacex_df['class'].map({0: 'Failed', 1: 'Success'})

options = [{ 'label': 'All Sites', 'value': 'All'}] + [{'label' : site, 'value': site}for site in launch_sites_df['Launch Site']]

# Create a dash application
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

# Create an app layout
app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={
            'textAlign': 'center',
            'color': '#503D36',
            'font-size': 40
        }
    ),
    # TASK 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    dcc.Dropdown(id='site-dropdown', options=options, value='All', placeholder='Select a launch site'),
    # html.Div,
    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),
    # html.Div,
    html.P("Payload range (Kg):"),
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        # min=min_payload, 
        # max=max_payload,
        # value=[min_payload, max_payload]
    ),
    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

@app.callback(
    Output('payload-slider', 'min'),
    Output('payload-slider', 'max'),
    Output('payload-slider', 'value'),
    Input('site-dropdown', 'value')
)
def update_slider(selected_site):
    if selected_site == 'All':
        df = spacex_df
    else:
        df = spacex_df[spacex_df['Launch Site'] == selected_site] 
    min_val = df['Payload Mass (kg)'].min()
    max_val = df['Payload Mass (kg)'].max()
    return min_val, max_val, [min_val, max_val]

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value'),
)

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
def get_pie_chart(selected_site):
    if selected_site == 'All':
        fig = px.pie(data_frame=spacex_df, names='Launch Site', values='class', title='Success Rate of All Sites')
    else:
        fig = px.pie(
            data_frame=spacex_df[spacex_df['Launch Site'] == selected_site], 
            names='label class', 
            title=f'Success Rate for site {selected_site}',
            labels={'0':'Failed', '1': 'Success'}
        )
    return fig

@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    Input('site-dropdown', 'value'),
    Input('payload-slider', 'value')
)
def get_scatter_chart(selected_site, payload):
    if selected_site == 'All':
        df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload[0]) & (spacex_df['Payload Mass (kg)'] <=payload[1])]
        fig = px.scatter(data_frame=df, x='Payload Mass (kg)', y='class', color='Booster Version Category', title='Correlation between Payload Mass and Success for all sites')
        fig.update_yaxes(
            tickvals=[0, 1],
            ticktext=['Failed', 'Success']
        )
    else:
        df = spacex_df[(spacex_df['Launch Site'] == selected_site) & (spacex_df['Payload Mass (kg)'] >= payload[0]) & (spacex_df['Payload Mass (kg)'] <=payload[1])]
        fig = px.scatter(data_frame=df, x='Payload Mass (kg)', y='class', color='Booster Version Category', title=f'Correlation between Payload Mass and Success for {selected_site}')
        fig.update_yaxes(
            tickvals=[0, 1],
            ticktext=['Failed', 'Success']
        )
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
