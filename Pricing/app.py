from dash import Dash, html, dcc, Output, Input

from Pricing.Price_History import (
    process_pricing_history,  # Function to filter and preprocess data
    profit_distribution,  # Function to create a profit distribution graph
    sale_price_vs_profit,  # Function to create a graph for sale price vs profit
    sales_by_condition,  # Function to create a graph for sales by condition
    days_to_sell_distribution,  # Function to plot days-to-sell distribution
    avg_profit_by_purchase_range,  # Function to create graph for avg profit by purchase range
    monthly_profit_over_time  # Function to create a profit-over-time graph
)

# TODO: integrate pricing, excel module, and ebay scraping in one all encompassing dashboard app

# Initialize Dash app
app = Dash()

# Load preprocessed data from Price_History module
df = process_pricing_history()

# Dictionary mapping graph names to their respective functions
graph_functions = {
    "Profit Distribution": profit_distribution,
    "Sale Price vs. Profit": sale_price_vs_profit,
    "Sales by Condition": sales_by_condition,
    "Days to Sell Distribution": days_to_sell_distribution,
    "Avg Profit by Purchase Range": avg_profit_by_purchase_range,
    "Monthly Profit Over Time": monthly_profit_over_time
}

# Define the app layout (visible structure for the web page)
app.layout = html.Div([
    # Main heading displaying the item's financial summary
    html.H1(f"Financial Summary of Item {df['Item'].iloc[1]}", style={'textAlign': 'center'}),

    # Radio button for toggling between dropdown or displaying all graphs
    html.Div([
        html.Label("Select View"),  # Label for selector
        dcc.RadioItems(
            id="view-type",  # Radio button selection (dropdown or all)
            options=[
                {"label": "Dropdown", "value": "dropdown"},
                {"label": "All", "value": "all"},
            ],
            value="dropdown",  # Default selection is "dropdown"
            labelStyle={"display": "inline-block", 'margin-right': '10px'},
        )
    ], style={'margin-bottom': '10px'}),  # Add margin for spacing

    # Dropdown for selecting a specific graph (only shown in 'dropdown' mode)
    html.Div([
        dcc.Dropdown(
            id='graph-selector',  # Dropdown for graph selection
            options=[{'label': name, 'value': name} for name in graph_functions.keys()],
            value='Profit Distribution'  # Default dropdown value (first graph)
        )
    ], id='dropdown-container', style={'width': '50%', 'margin': '0 auto'}),

    # Container to display graphs (based on the selected mode)
    html.Div(id='graph-container'),
])


@app.callback(
    Output('dropdown-container', 'style'),  # Controls whether the dropdown is visible
    Output('graph-container', 'children'),  # Defines the content of the graph container
    Input('view-type', 'value'),  # Input from radio button: Dropdown or All
    Input('graph-selector', 'value')  # Input from dropdown: Selected graph (if dropdown mode is active)
)
def update_view(view_type, selected_graph):
    """
    Callback to update the dashboard content based on the selected view type.
    - In 'dropdown' mode, only the selected graph from the dropdown is displayed.
    - In 'all' mode, all graphs are displayed simultaneously, and the dropdown menu is hidden.

    :param view_type: A string indicating the selected view ('dropdown' or 'all').
    :param selected_graph: A string indicating the selected graph from the dropdown (used in dropdown mode).
    :return: A tuple containing:
        1. CSS style to control the visibility of the dropdown menu (display: block/none).
        2. Children for the graph-container div (single graph or all graphs).
    """

    if view_type == 'dropdown':
        # If dropdown mode is selected, show dropdown and render the selected graph
        dropdown_style = {'width': '50%', 'margin': '0 auto', 'display': 'block'}  # Dropdown visible
        selected_func = graph_functions[selected_graph]  # Get the selected graph's function
        fig = selected_func(df)  # Generate the graph using the selected function
        graph = dcc.Graph(figure=fig)  # Display the selected graph
        return dropdown_style, graph

    elif view_type == 'all':
        # If all graphs mode is selected, hide the dropdown and render all graphs
        dropdown_style = {'display': 'none'}  # Hide dropdown menu
        all_graphs = [
            html.Div([
                html.H3(name, style={'textAlign': 'center'}),  # Title for each graph
                dcc.Graph(figure=func(df))  # Render the graph
            ], style={'marginBottom': '40px'})  # Add spacing between graphs
            for name, func in graph_functions.items()  # Loop through all graphs to render
        ]
        return dropdown_style, all_graphs

    # Fallback in case of invalid mode selection (should never happen)
    return None, None


# Main entry point to run the Dash app
if __name__ == '__main__':
    app.run(debug=True)