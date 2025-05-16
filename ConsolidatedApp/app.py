from flask import Flask, render_template, request, jsonify, send_file
from dash import Dash, dcc, html
import dash
import tempfile
from Pricing.Price_History import (
    filter_data, profit_distribution, sale_price_vs_profit, sales_by_condition,
    days_to_sell_distribution, avg_profit_by_purchase_range, monthly_profit_over_time
)
from ExcelFormatAPI.FormatReportProduction import format_excel_file

# Initialize Flask app
app = Flask(__name__)

# Store dictionary of temporarily generated file links
# Keys are filenames, and values are their corresponding file paths
TEMP_FILES = {}

# ------------------------------ DASH APP SECTION ------------------------------

# Initialize Dash app inside Flask
dash_app = Dash(
    __name__,
    server=app,
    url_base_pathname='/dash/'  # Location where the Dash app is served
)

# Load and preprocess pricing data
# NOTE: Replace "filter_data" with a dynamic user-uploaded Excel file and process it for Dash charts
df = filter_data()

# Dictionary that maps graph names to corresponding generation functions
graph_functions = {
    "Profit Distribution": profit_distribution,
    "Sale Price vs. Profit": sale_price_vs_profit,
    "Sales by Condition": sales_by_condition,
    "Days to Sell Distribution": days_to_sell_distribution,
    "Avg Profit by Purchase Range": avg_profit_by_purchase_range,
    "Monthly Profit Over Time": monthly_profit_over_time
}

# Define the layout of the Dash app
dash_app.layout = html.Div([
    html.H1(f"Financial Summary of Item {df['Item'].iloc[1]}", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Select View"),
        dcc.RadioItems(
            id="view-type",
            options=[
                {"label": "Dropdown", "value": "dropdown"},
                {"label": "All", "value": "all"}
            ],
            value="dropdown",  # Default selection is "Dropdown"
            labelStyle={"display": "inline-block", 'margin-right': '10px'}
        )
    ], style={'margin-bottom': '10px'}),

    html.Div([
        dcc.Dropdown(
            id='graph-selector',
            options=[{'label': name, 'value': name} for name in graph_functions.keys()],
            value='Profit Distribution'
        )
    ], id='dropdown-container', style={'width': '50%', 'margin': '0 auto'}),

    html.Div(id='graph-container'),
])


@dash_app.callback(
    [
        dash.Output('dropdown-container', 'style'),
        dash.Output('graph-container', 'children')
    ],
    [
        dash.Input('view-type', 'value'),
        dash.Input('graph-selector', 'value')
    ]
)
def update_view(view_type, selected_graph):
    """
    Update the layout of the Dash app based on the user's selection.

    :param view_type: The type of layout ('dropdown' or 'all').
    :param selected_graph: The name of the graph selected from the dropdown.
    :return: Layout updates: dropdown visibility and graph data.
    """
    if view_type == 'dropdown':
        dropdown_style = {'width': '50%', 'margin': '0 auto', 'display': 'block'}
        selected_func = graph_functions[selected_graph]
        fig = selected_func(df)  # Generate the graph using the selected function
        graph = dcc.Graph(figure=fig)
        return dropdown_style, graph

    elif view_type == 'all':
        dropdown_style = {'display': 'none'}
        all_graphs = [
            html.Div([
                html.H3(name, style={'textAlign': 'center'}),
                dcc.Graph(figure=func(df))
            ], style={'marginBottom': '40px'})
            for name, func in graph_functions.items()
        ]
        return dropdown_style, all_graphs

    return None, None


# ------------------------------ FLASK ROUTES ------------------------------


@app.route('/pricing')
def pricing():
    """
    Serve the pricing dashboard page.

    :return: Pricing dashboard page (HTML template).
    """
    return render_template('pricing.html')


@app.route('/format-excel', methods=['POST'])
def format_excel():
    """
    Process an uploaded raw Excel file, apply formatting, and provide it as a downloadable file.

    :return: Downloadable formatted Excel file or error JSON.
    """
    file_storage = request.files['file']
    try:
        # Process the uploaded file and return a formatted Excel workbook
        workbook = format_excel_file(file_storage)

        # Save the workbook to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        workbook.save(temp_file.name)

        # Save the file path in the TEMP_FILES dictionary
        filename = temp_file.name.split('/')[-1]
        TEMP_FILES[filename] = temp_file.name

        # Return the file as a downloadable attachment
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name="formatted_excel.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        # Return a JSON error message in case of failure
        return jsonify({'error': str(e)}), 500


@app.route('/download/<filename>')
def download_file(filename):
    """
    Serve a file for download if it exists in TEMP_FILES.

    :param filename: The name of the file to be downloaded (stored in TEMP_FILES).
    :return: Downloadable file or an error page if the file does not exist.
    """
    if filename in TEMP_FILES:
        file_path = TEMP_FILES[filename]
        return send_file(file_path, as_attachment=True, download_name="formatted_excel.xlsx")
    return "File not found or expired.", 404


@app.route('/scrape-ebay', methods=['POST'])
def scrape_ebay():
    """
    Scrape eBay listings based on the provided search parameters.
    (Currently expects JSON input; may need updates based on data format.)

    :return: Scraped data in JSON format.
    """
    # TODO: Test functionality
    # FIXME: Search still expects JSON, adapt if switching away.
    data = request.json  # Assume JSON input with search parameters
    result = scrape_ebay(data)  # Placeholder for scrape_ebay function
    return jsonify({'scraped_data': result})


@app.route('/')
def home():
    """
    Serve the homepage of the app, which provides links to pricing, Excel formatting, and eBay tracking.

    :return: Rendered homepage template (HTML).
    """
    return render_template('index.html')


# ------------------------------ MAIN ------------------------------

if __name__ == '__main__':
    """
    Run the Flask application in debug mode.
    """
    app.run(debug=True)