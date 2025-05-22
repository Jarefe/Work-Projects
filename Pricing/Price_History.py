# Import required libraries and modules
import os
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv

# Load environment variables (e.g., file paths or other configurations)
load_dotenv()

def calculate_date_difference(date1, date2) -> int:
    """
    Calculate the number of days between two dates.

    Supports formats:
    - mm/dd/yyyy
    - yyyy/mm/dd

    :param date1: Start date as string or datetime object.
    :param date2: End date as string or datetime object.
    :return: Absolute number of days between the two dates, or 0 on error.
    """
    if pd.isna(date1) or pd.isna(date2):
        return 0

    formats = ['%m/%d/%Y', '%Y/%m/%d']

    def parse_date(date_str):
        if isinstance(date_str, datetime):
            return date_str
        for fmt in formats:
            try:
                return datetime.strptime(str(date_str), fmt)
            except ValueError:
                continue
        return None  # If all formats fail

    date1_obj = parse_date(date1)
    date2_obj = parse_date(date2)

    if date1_obj and date2_obj:
        return abs((date2_obj - date1_obj).days)
    else:
        return 0



def get_ebay_url(item_id: str) -> str:
    """
    Generate a search URL for eBay to find sold and completed listings for an item.

    :param item_id: Unique identifier for the item, typically its name or model.
    :return: Valid eBay search URL for sold and completed listings.
    """
    brand = input("Enter the brand of the item to search for on eBay: ")
    item_id = brand + " " + item_id  # Concatenate brand and item name for specific search
    return (
        f'https://www.ebay.com/sch/i.html?_nkw={item_id.replace(" ", "+")}&_sacat=0&_from=R40&rt=nc&LH_Sold=1&LH_Complete=1&_pgn=1'
    )


def print_summary(values):
    """
    Print key financial details and metrics for items in the dataset.

    :param values: Dictionary where keys are labels (e.g., 'Max Profit Item')
                   and values are rows from the DataFrame.
    """
    for key, value in values.items():
        print(key)
        print("-" * 40)
        print(f"Item ID         : {value['Item']}")
        print(f"Condition       : {value['Condition']}")
        print(f"Purchase Date   : {value['Purchase Date']}")
        print(f"Purchase Cost   : ${value['Purchase Cost']:.2f}")
        print(f"Sale Date       : {value['Sale Date']}")
        print(f"Sale Price      : ${value['Sale Price']:.2f}")
        print(f"Profit          : ${value['Profit']:.2f}")
        print(f"Revenue Share   : {value['Revenue Share']}")
        print(f"Status          : {value['Status']}")
        print(f"# Days to Sell  : {value['# Days to sell']}")
        print("-" * 40)


def profit_distribution(df):
    """
    Generate a histogram to visualize the distribution of profit.

    :param df: DataFrame containing a 'Profit' column with numeric data.
    :return: Plotly histogram figure object.
    """
    fig = px.histogram(
        df,
        x='Profit',
        nbins=50,
        title='Profit Distribution',
        marginal='box',
        color_discrete_sequence=['blue']
    )

    fig.update_layout(
        xaxis_title='Profit ($)',
        yaxis_title='Number of Items',
        bargap=0.1  # Reduce gap between bars for better visualization
    )

    return fig


def sale_price_vs_profit(df):
    """
    Create a scatterplot showing the relationship between sale price and profit.

    :param df: DataFrame with items' sale prices, profits, and conditions.
    :return: Plotly scatterplot figure object.
    """
    fig = px.scatter(
        df,
        x='Sale Price',
        y='Profit',
        color='Condition',
        title='Sale Price vs. Profit',
        labels={'Sale Price': 'Sale Price ($)', 'Profit': 'Profit ($)'},
        hover_data=['Item', 'Condition', 'Purchase Date', 'Purchase Cost', 'Sale Date', 'Sale Price']
    )

    # Adjust marker properties for better aesthetics
    fig.update_traces(marker=dict(size=8, opacity=0.7), selector=dict(mode='markers'))
    return fig


def sales_by_condition(df):
    """
    Create a boxplot displaying sales prices grouped by item condition.

    :param df: DataFrame containing sale prices and item conditions.
    :return: Plotly boxplot figure object.
    """
    fig = px.box(
        df,
        x='Condition',
        y='Sale Price',
        title='Sales by Condition',
        labels={'Sale Price': 'Sale Price ($)'},
        color_discrete_sequence=px.colors.sequential.Plasma
    )

    return fig


def days_to_sell_distribution(df):
    """
    Visualize the distribution of the number of days items took to sell.

    :param df: DataFrame with purchase and sale dates.
    :return: Plotly histogram figure object.
    """
    # Add a column for days to sell, calculated using the helper function
    df['# Days to sell'] = df.apply(
        lambda row: calculate_date_difference(row['Purchase Date'], row['Sale Date']),
        axis=1
    )

    fig = px.histogram(
        df,
        x='# Days to sell',
        nbins=50,
        title='Days to Sell Distribution',
        marginal='box',
        color_discrete_sequence=['blue']
    )

    fig.update_layout(
        xaxis_title='Days to Sell',
        yaxis_title='Number of Items',
        bargap=0.1
    )

    return fig


def avg_profit_by_purchase_range(df):
    """
    Generate a bar chart showing average profit for purchase cost ranges.

    :param df: DataFrame containing 'Purchase Cost' and 'Profit' columns.
    :return: Plotly bar chart figure object.
    """
    df = df.copy()  # Avoid modifying the original DataFrame
    bin_edges = np.histogram_bin_edges(df['Purchase Cost'].dropna(), bins=20)
    df['Cost Range'] = pd.cut(df['Purchase Cost'], bins=bin_edges, include_lowest=True)

    # Convert the interval (Cost Range) to string for JSON serialization
    df['Cost Range'] = df['Cost Range'].astype(str)

    avg_profit = df.groupby('Cost Range')['Profit'].mean().reset_index()

    fig = px.bar(
        avg_profit,
        x='Cost Range',
        y='Profit',
        title='Average Profit by Purchase Range',
        labels={'Profit': 'Average Profit ($)'},
        color_discrete_sequence=px.colors.sequential.Plasma
    )

    fig.update_layout(xaxis_tickangle=-45)  # Rotate x-axis labels for readability

    return fig


def monthly_profit_over_time(df):
    """
    Plot the total profit aggregated by month.

    :param df: DataFrame with 'Sale Date' and 'Profit' columns.
    :return: Plotly line chart figure object.
    """
    # Ensure the 'Sale Date' column is in datetime format
    df['Sale Date'] = pd.to_datetime(df['Sale Date'], errors='coerce')
    df = df.dropna(subset=['Sale Date'])  # Remove rows with invalid 'Sale Date'

    # Group by month and calculate total profit
    profit = df.groupby(df['Sale Date'].dt.to_period('M'))['Profit'].sum().reset_index()
    profit['Sale Date'] = profit['Sale Date'].dt.to_timestamp()

    fig = px.line(
        profit,
        x='Sale Date',
        y='Profit',
        title='Profit Over Time',
        labels={'Profit': 'Total Profit ($)'},
        markers=True
    )

    return fig


def process_pricing_history_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process the raw dataset to clean, filter, and calculate metrics.

    :param df: Raw Pandas DataFrame with pricing and sale details.
    :return: Processed DataFrame.
    """
    # Step 1: Filter out 'SCRP' (scrap) items from the dataset
    filtered_df = df[df['So Condition'] != 'SCRP'].copy()

    # Step 2: Calculate '# Days to Sell' for each item
    filtered_df['# Days to sell'] = filtered_df.apply(
        lambda row: calculate_date_difference(row['Purchase Date'], row['Sale Date']),
        axis=1
    )

    return filtered_df


def output_graphs(df: pd.DataFrame):
    """
    Generate and display various visualizations from the dataset.

    :param df: Processed DataFrame containing relevant columns for analysis.
    """
    # Call each graph function sequentially and display the outputs
    profit_distribution(df).show()
    sale_price_vs_profit(df).show()
    sales_by_condition(df).show()
    days_to_sell_distribution(df).show()
    avg_profit_by_purchase_range(df).show()
    monthly_profit_over_time(df).show()

import pandas as pd

def read_all_sheets(filepath: str = None) -> pd.DataFrame:
    """
    Reads specified sheets from an Excel workbook and returns a dictionary of processed DataFrames,
    each processed based on its sheet name.

    :param filepath: Path to the Excel workbook (.xlsx or .xls).
    :return: single dataframe with all sheet information
    """
    try:

        all_sheets = pd.read_excel(filepath,sheet_name=None) # Reads all sheets
        all_sheets.pop("Dash Inventory") # Remove dash inventory
        df = pd.concat(all_sheets.values(), ignore_index=True)

        return df

    except Exception as e:
        raise RuntimeError(f"Failed to read Excel file: {e}")


def find_data_overlaps(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """
    Function to find data that exists in both sheets (will allow to pull pricing data and specs, then output as 1 dataframe with all relevant data for ML
    Intended for merging pricing

    :param df1: first dataframe to compare
    :param df2: second dataframe to compare
    :return: combined dataframe
    """
    # Merge on both keys (safer if one might be missing)
    combined_df = pd.merge(df1, df2, on="SN", how="inner")

    # Drop duplicates after merge if needed
    combined_df = combined_df.drop_duplicates(subset="SN")

    return combined_df

def process_pricing_history(filepath: str = None):
    """
    Main function to load, process, and visualize data from a pricing history excel file.

    :param filepath: File path to the Excel file containing raw data.
    :return: Processed DataFrame with relevant metrics.
    """
    # Load the Excel file and process the data
    # noinspection PyTypeChecker
    if filepath is not None:
        try:
            df = pd.read_excel(filepath, skiprows=[0], usecols='B, C, E, G, H, I, K, L, N, O, R')
            filtered_df = process_pricing_history_dataframe(df)
            return filtered_df
        except Exception as e:
            return e
    return None

def process_all_time_inventory(filepath: str = None):
    """
    Main function to handle data from an all time inventory w/ testing records excel file

    :param filepath: File path to the Excel file containing raw data.
    :return: Processed DataFrame with relevant metrics.
    """
    if filepath is not None:
        try:
            combined_df = read_all_sheets(filepath)
            return combined_df
        except Exception as e:
            return e
    return None

def filter_rr_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    filtered_df = df[df['Condition'] != 'SCRP'].copy()
    filtered_df['# Days to sell'] = filtered_df.apply(
        lambda row: calculate_date_difference(row['Added Date'], row['Sales Date']),
        axis=1
    )
    return filtered_df

def process_recovered_revenue(filepath: str = None):
    """
    Main function to handle data from a recovered revenue excel file

    :param filepath: File path to the Excel file containing raw data.
    :return: Processed DataFrame with relevant metrics.
    """
    if filepath is not None:
        try:
            df = pd.read_excel(filepath, usecols='F, H, N, O, P, R, S, T, U, V, Y, Z')
            df.rename(columns={'Serial Number': 'SN'}, inplace=True)
            filtered_df = filter_rr_dataframe(df)
            return filtered_df
        except Exception as e:
            return e
    return None

if __name__ == "__main__":
    # print(process_all_time_inventory(os.getenv("TESTING_ALL_TIME")))
    final_df = (find_data_overlaps(process_recovered_revenue(os.getenv("TESTING_RECOVERED_REVENUE")),process_all_time_inventory(os.getenv("TESTING_ALL_TIME"))))
    final_df.to_excel('final_output.xlsx', index=False)
