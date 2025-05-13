from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import pandas as pd

from Price_History import generate_financial_summary

app = Dash()

df = generate_financial_summary()

app.layout = [
    html.Div(children='Price History'),
    dash_table.DataTable(data=df.to_dict('records'), page_size=50)
]

if __name__ == '__main__':
    app.run(debug=True)