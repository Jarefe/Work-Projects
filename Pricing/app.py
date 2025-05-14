from dash import Dash, html, dcc, Output, Input

from Price_History import (
    filter_data,
    profit_distribution,
    sale_price_vs_profit,
    sales_by_condition,
    days_to_sell_distribution,
    avg_profit_by_purchase_range,
    monthly_profit_over_time
)

app = Dash()

# Load filtered data
df = filter_data()

# Define the available graph options and their corresponding functions
graph_functions = {
    "Profit Distribution": profit_distribution,
    "Sale Price vs. Profit": sale_price_vs_profit,
    "Sales by Condition": sales_by_condition,
    "Days to Sell Distribution": days_to_sell_distribution,
    "Avg Profit by Purchase Range": avg_profit_by_purchase_range,
    "Monthly Profit Over Time": monthly_profit_over_time
}

# App layout - includes a radio button selector, dropdown, and graph container
app.layout = html.Div([
    html.H1(f"Financial Summary of Item {df['Item'].iloc[1]}", style={'textAlign': 'center'}),

    # Radio button to toggle between dropdown and displaying all graphs
    html.Div([
        html.Label("Select View"),
        dcc.RadioItems(
            id="view-type",
            options=[
                {"label": "Dropdown", "value": "dropdown"},
                {"label": "All", "value": "all"},
            ],
            value="dropdown",
            labelStyle={"display": "inline-block", 'margin-right': '10px'},
        )
    ], style={'margin-bottom': '10px'}),

    # Dropdown for selecting a graph (used in 'dropdown' view)
    html.Div([
        dcc.Dropdown(
            id='graph-selector',
            options=[{'label': name, 'value': name} for name in graph_functions.keys()],
            value='Profit Distribution'  # Default selection
        )
    ], id='dropdown-container', style={'width': '50%', 'margin': '0 auto'}),

    # Container to display one or all graphs
    html.Div(id='graph-container'),
])


@app.callback(
    Output('dropdown-container', 'style'),
    Output('graph-container', 'children'),
    Input('view-type', 'value'),
    Input('graph-selector', 'value')
)
def update_view(view_type, selected_graph):
    """
    Update the dashboard based on the selected view type (dropdown or all).
    In dropdown mode, display a single graph selected from the dropdown.
    In all mode, display all available graphs.

    :param view_type: 'dropdown' to display a single graph or 'all' to display all graphs.
    :param selected_graph: The graph selected from the dropdown (ignored in 'all' mode).
    :return: A tuple containing:
        1. Style for the dropdown-container (to show/hide it based on view_type).
        2. A list of children to display in the graph-container.
    """
    if view_type == 'dropdown':
        # Show dropdown and display a single selected graph
        dropdown_style = {'width': '50%', 'margin': '0 auto', 'display': 'block'}  # Show dropdown
        selected_func = graph_functions[selected_graph]
        fig = selected_func(df)  # Generate the graph
        graph = dcc.Graph(figure=fig)
        return dropdown_style, graph

    elif view_type == 'all':
        # Hide dropdown and display all graphs
        dropdown_style = {'display': 'none'}  # Hide dropdown
        all_graphs = [
            html.Div([
                html.H3(name, style={'textAlign': 'center'}),  # Add title for each graph
                dcc.Graph(figure=func(df))
            ], style={'marginBottom': '40px'})  # Add spacing between graphs
            for name, func in graph_functions.items()
        ]
        return dropdown_style, all_graphs
    return None, None


if __name__ == '__main__':
    app.run(debug=True)