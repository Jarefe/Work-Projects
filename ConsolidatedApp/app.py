from flask import Flask, render_template, request, jsonify, send_file
from dash import Dash, dcc, html
import dash, tempfile
from Pricing.Price_History import (
    filter_data, profit_distribution, sale_price_vs_profit, sales_by_condition,
    days_to_sell_distribution, avg_profit_by_purchase_range, monthly_profit_over_time
)
from ExcelFormatAPI.FormatReportProduction import format_excel_file

# Initialize Flask app
app = Flask(__name__)

# Store generated file links
TEMP_FILES = {}

# Initialize Dash app inside Flask
dash_app = Dash(__name__, server=app, url_base_pathname='/dash/')

# Load preprocessed data from Price_History module
# TODO: edit price history scripts to take in an excel workbook and process it; have user upload file and generate graphs from there
df = filter_data()

# Dictionary mapping graph names to their respective functions
graph_functions = {
    "Profit Distribution": profit_distribution,
    "Sale Price vs. Profit": sale_price_vs_profit,
    "Sales by Condition": sales_by_condition,
    "Days to Sell Distribution": days_to_sell_distribution,
    "Avg Profit by Purchase Range": avg_profit_by_purchase_range,
    "Monthly Profit Over Time": monthly_profit_over_time
}

# Define Dash app layout
dash_app.layout = html.Div([
    html.H1(f"Financial Summary of Item {df['Item'].iloc[1]}", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Select View"),
        dcc.RadioItems(
            id="view-type",
            options=[{"label": "Dropdown", "value": "dropdown"}, {"label": "All", "value": "all"}],
            value="dropdown",
            labelStyle={"display": "inline-block", 'margin-right': '10px'},
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


# Callback to update the dashboard based on selected view type
@dash_app.callback(
    [dash.Output('dropdown-container', 'style'), dash.Output('graph-container', 'children')],
    [dash.Input('view-type', 'value'), dash.Input('graph-selector', 'value')]
)
def update_view(view_type, selected_graph):
    if view_type == 'dropdown':
        dropdown_style = {'width': '50%', 'margin': '0 auto', 'display': 'block'}
        selected_func = graph_functions[selected_graph]
        fig = selected_func(df)
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


# Route to handle pricing functionality
@app.route('/pricing')
def pricing():
    return render_template('pricing.html')  # Serve pricing page

    # Route to handle Excel formatting
@app.route('/format-excel', methods=['POST'])
def format_excel():
    file_storage = request.files['file']
    try:
        # Process the uploaded file to return a formatted workbook
        workbook = format_excel_file(file_storage)

        # Save the workbook to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        workbook.save(temp_file.name)

        # Save the file path in the TEMP_FILES dictionary
        filename = temp_file.name.split('/')[-1]
        TEMP_FILES[filename] = temp_file.name

        # Return the file as direct download attachment
        return send_file(temp_file.name,
                         as_attachment=True,
                         download_name="formatted_excel.xlsx",
                         mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to serve downloadable files
@app.route('/download/<filename>')
def download_file(filename):
    # Ensure the file exists and is in the TEMP_FILES dictionary
    if filename in TEMP_FILES:
        file_path = TEMP_FILES[filename]
        return send_file(file_path, as_attachment=True, download_name="#### Testing Report.xlsx")
    return "File not found or expired.", 404


# Route to handle eBay scraping
@app.route('/scrape-ebay', methods=['POST'])
def scrape_ebay():
    # TODO: test functionality
    data = request.json  # Assume JSON input with parameters for eBay scraping
    result = scrape_ebay(data)
    return jsonify({'scraped_data': result})


# Main route
@app.route('/')
def home():
    return render_template('index.html')  # Serve homepage (with options to interact with pricing, excel, ebay)


if __name__ == '__main__':
    app.run(debug=True)
