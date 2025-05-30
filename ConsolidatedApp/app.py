from flask import Flask, render_template, request, jsonify, send_file
from dash import Dash, dcc, html
import dash
import tempfile
from Pricing.Ebay_Scraping import scrape_ebay_data
from Pricing.Price_History import (
    process_pricing_history, profit_distribution, sale_price_vs_profit,
    sales_by_condition, days_to_sell_distribution,
    avg_profit_by_purchase_range, monthly_profit_over_time,
    profit_margin_distribution, avg_days_to_sell_by_condition, monthly_sales_volume
)
from ExcelFormatAPI.FormatReportProduction import format_excel_file
from ExcelFormatAPI.Auto_Attribute import process_extreme_attributes

# Initialize Flask app
app = Flask(__name__)

# Global temp file storage
TEMP_FILES = {}

# Shared DataFrame holder
df_holder = {'df': process_pricing_history()}  # Initially load placeholder

# -------------------- DASH APP --------------------
dash_app = Dash(
    __name__,
    server=app,
    url_base_pathname='/dash/'
)

# Mapping of graph display names to functions
graph_functions = {
    "Profit Distribution": profit_distribution,
    "Sale Price vs. Profit": sale_price_vs_profit,
    "Sales by Condition": sales_by_condition,
    "Days to Sell Distribution": days_to_sell_distribution,
    "Avg Profit by Purchase Range": avg_profit_by_purchase_range,
    "Monthly Profit Over Time": monthly_profit_over_time,
    "Profit Margin Distribution": profit_margin_distribution,
    "Avg Days to Sell by Condition": avg_days_to_sell_by_condition,
    "Monthly Sales Volume": monthly_sales_volume
}

# Dash layout
dash_app.layout = html.Div([
    html.H1(id="dashboard-title", children="Financial Summary", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Select View"),
        dcc.RadioItems(
            id="view-type",
            options=[
                {"label": "Dropdown", "value": "dropdown"},
                {"label": "All", "value": "all"}
            ],
            value="dropdown",
            labelStyle={"display": "inline-block", 'margin-right': '10px'}
        )
    ], style={'margin-bottom': '10px'}),

    html.Div([
        dcc.Dropdown(
            id='graph-selector',
            options=[{'label': name, 'value': name} for name in graph_functions.keys()],
            value='Profit Distribution',
            multi=False
        )
    ], id='dropdown-container', style={'width': '50%', 'margin': '0 auto'}),

    html.Div(id='graph-container', children=html.P("No data loaded. Please upload a pricing history file."))
])

# Callback to update view
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
    df = df_holder.get('df')
    if df is None or df.empty:
        return {'display': 'none'}, html.P("No data available. Upload a file to see graphs.")

    if view_type == 'all':
        all_graphs = [
            html.Div([
                html.H3(name, style={'textAlign': 'center'}),
                dcc.Graph(figure=func(df))
            ], style={'marginBottom': '40px'})
            for name, func in graph_functions.items()
        ]
        return {'display': 'none'}, all_graphs

    # Dropdown view: one graph only
    if selected_graph and selected_graph in graph_functions:
        fig = graph_functions[selected_graph](df)
        return {'width': '50%', 'margin': '0 auto', 'display': 'block'}, dcc.Graph(figure=fig)

    return {'width': '50%', 'margin': '0 auto', 'display': 'block'}, html.P("Please select a valid graph.")

# Callback to update title
@dash_app.callback(
    dash.Output('dashboard-title', 'children'),
    dash.Input('view-type', 'value')
)
def update_title(view_type):
    df = df_holder.get('df')
    if df is not None and 'Item' in df.columns and len(df) > 0:
        return f"Financial Summary of {df['Item'].iloc[0]}"
    return "Financial Summary"

# -------------------- FLASK ROUTES --------------------
@app.route('/format-excel', methods=['POST'])
def format_excel():
    file_storage = request.files['file']
    try:
        workbook = format_excel_file(file_storage)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        workbook.save(temp_file.name)

        filename = temp_file.name.split('/')[-1]
        TEMP_FILES[filename] = temp_file.name

        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name="formatted_excel.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/format-extreme', methods=['POST'])
def attribute():
    file_storage = request.files['file']
    try:
        workbook = process_extreme_attributes(file_storage)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        workbook.save(temp_file.name)

        filename = temp_file.name.split('/')[-1]
        TEMP_FILES[filename] = temp_file.name

        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name="formatted_excel.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    if filename in TEMP_FILES:
        return send_file(TEMP_FILES[filename], as_attachment=True)
    return "File not found or expired.", 404

@app.route('/upload-pricing-history', methods=['POST'])
def upload_pricing_history():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        file.save(temp_file.name)
        df_holder['df'] = process_pricing_history(temp_file.name)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/scrape-ebay', methods=['POST'])
def scrape_ebay():
    data = request.get_json()  # <-- parse JSON payload

    if not data or 'query' not in data:
        return jsonify({'error': 'No search query provided'}), 400

    query = data.get('query', '').strip()
    pages = int(data.get('pages', 1))

    try:
        result = scrape_ebay_data(query, pages)
        return jsonify({'results': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    return render_template('index.html')

# -------------------- MAIN --------------------
if __name__ == '__main__':
    app.run(debug=True)
