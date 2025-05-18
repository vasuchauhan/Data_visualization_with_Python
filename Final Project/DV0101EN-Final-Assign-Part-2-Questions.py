#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import dash
import more_itertools
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

# Load the data using pandas
data = pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv')

# Initialize the Dash app
app = dash.Dash(__name__)

# Set the title of the dashboard
#app.title = "Automobile Statistics Dashboard"

#---------------------------------------------------------------------------------
# Create the dropdown menu options
dropdown_options = [
    {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
    {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
]
# List of years 
year_list = [i for i in range(1980, 2024, 1)]

# Create the layout of the app
app.layout = html.Div([
    # Add title to the dashboard
    html.H1("Automobile Sales Statistics Dashboard", style={'textAlign':'center', 'color':'#503D36', 'font-size':24}),
    
    # Add dropdown menus with better organization
    html.Div([
        html.Div([
            html.Label("Select Statistics:"),
            dcc.Dropdown(
                id='dropdown-statistics',
                options=dropdown_options,
                value=None,  # Changed from 'Select Statistics' to None
                placeholder='Select a report type'
            )
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
        
        html.Div([
            html.Label("Select Year:"),
            dcc.Dropdown(
                id='select-year',
                options=[{'label': i, 'value': i} for i in year_list],
                value=None,  # Changed from 'select-year' to None
                disabled=True
            )
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'})
    ]),
    
    # TASK 2.3: Add a division for output display
    html.Div(id='output-container', className='chart-grid', style={'display': 'flex', 'flex-wrap': 'wrap'})
])
#TASK 2.4: Creating Callbacks
# Define the callback function to update the input container based on the selected statistics
@app.callback(
    Output(component_id='select-year', component_property='disabled'),
    Input(component_id='dropdown-statistics', component_property='value')
)
def update_input_container(selected_statistics):
    if selected_statistics == 'Yearly Statistics': 
        return False
    else: 
        return True

# Callback for plotting
@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='select-year', component_property='value'), 
     Input(component_id='dropdown-statistics', component_property='value')]
)
def update_output_container(input_year, selected_statistics):
    if selected_statistics == 'Recession Period Statistics':
        # Filter the data for recession periods
        recession_data = data[data['Recession'] == 1]
        
        # Plot 1: Automobile sales fluctuate over Recession Period (year wise)
        yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(
            figure=px.line(yearly_rec, 
                x='Year',
                y='Automobile_Sales',
                title="Average Automobile Sales fluctuation over Recession Period")
        )

        # Plot 2: Calculate the average number of vehicles sold by vehicle type
        average_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()                 
        R_chart2 = dcc.Graph(
            figure=px.bar(average_sales,
                x='Vehicle_Type',
                y='Automobile_Sales',
                title='Average number of vehicles sold by type')
        )
        
        # Plot 3: Pie chart for total expenditure share by vehicle type during recessions
        exp_rec = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        R_chart3 = dcc.Graph(
            figure=px.pie(exp_rec, 
                values='Advertising_Expenditure', 
                names='Vehicle_Type', 
                title='Total expenditure by vehicle type during recession')
        )

        # Plot 4: Bar chart for the effect of unemployment rate on vehicle type and sales
        unempl_type_sales = recession_data.groupby(['unemployment_rate', 'Vehicle_Type'])['Automobile_Sales'].sum().reset_index()
        R_chart4 = dcc.Graph(
            figure=px.bar(unempl_type_sales,
                x='unemployment_rate',
                y='Automobile_Sales',
                color='Vehicle_Type',  # Added color to distinguish vehicle types
                labels={'unemployment_rate': 'Unemployment Rate', 'Automobile_Sales': 'Average Automobile Sales'},
                title='Effect of Unemployment Rate on Vehicle Type and Sales')
        )

        return [
            html.Div(className='chart-item', children=[
                html.Div(children=R_chart1, style={'width': '50%'}),
                html.Div(children=R_chart2, style={'width': '50%'})
            ], style={'display': 'flex', 'width': '100%'}),
            html.Div(className='chart-item', children=[
                html.Div(children=R_chart3, style={'width': '50%'}),
                html.Div(children=R_chart4, style={'width': '50%'})
            ], style={'display': 'flex', 'width': '100%'})
        ]

    # Yearly Statistic Report Plots
    elif input_year and selected_statistics == 'Yearly Statistics':
        yearly_data = data[data['Year'] == input_year]
                              
        # Plot 1: Yearly Automobile sales using line chart for the whole period
        yas = data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        Y_chart1 = dcc.Graph(
            figure=px.line(yas, 
                x='Year',
                y='Automobile_Sales',
                title='Yearly automobile sales')
        )
            
        # Plot 2: Total Monthly Automobile sales using line chart
        tmas = yearly_data.groupby('Month')['Automobile_Sales'].mean().reset_index()  # Changed to filter by selected year
        Y_chart2 = dcc.Graph(
            figure=px.line(tmas, 
                x='Month',
                y='Automobile_Sales',
                title=f'Monthly automobile sales for {input_year}')
        )

        # Plot 3: Bar chart for average number of vehicles sold during the given year
        avr_vdata = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()  # Changed to group by Vehicle_Type
        Y_chart3 = dcc.Graph(
            figure=px.bar(avr_vdata, 
                x='Vehicle_Type',
                y='Automobile_Sales',
                title=f'Average Vehicles Sold by Vehicle Type in {input_year}')
        )

        # Plot 4: Total Advertisement Expenditure for each vehicle using pie chart
        exp_data = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        Y_chart4 = dcc.Graph(
            figure=px.pie(exp_data,
                values='Advertising_Expenditure',
                names='Vehicle_Type',
                title=f'Total advertisement expenditure for each vehicle type in {input_year}')
        )

        return [
            html.Div(className='chart-item', children=[
                html.Div(children=Y_chart1, style={'width': '50%'}),
                html.Div(children=Y_chart2, style={'width': '50%'})
            ], style={'display': 'flex', 'width': '100%'}),
            html.Div(className='chart-item', children=[
                html.Div(children=Y_chart3, style={'width': '50%'}),
                html.Div(children=Y_chart4, style={'width': '50%'})
            ], style={'display': 'flex', 'width': '100%'})
        ]
        
    else:
        return html.Div([
            html.H4("Please select a report type and, if needed, a year to display statistics.")
        ])

# Run the Dash app
if __name__ == '__main__':
    app.run(debug=True)

