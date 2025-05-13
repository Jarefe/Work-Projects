import os
from datetime import datetime

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from dotenv import load_dotenv

# Load environment variables, which might include file paths or configurations
load_dotenv()

def calculate_date_difference(date1, date2) -> int:
    """
    Calculate the number of days between two dates in mm/dd/yyyy format.

    :param date1: Start date, either as a string in mm/dd/yyyy format or NaN.
    :param date2: End date, either as a string in mm/dd/yyyy format or NaN.
    :return: Number of days between the two dates. Returns 0 if either date is invalid or missing.
    """
    if pd.isna(date1) or pd.isna(date2):
        # Handle missing or invalid dates gracefully
        return 0

    try:
        # Ensure input is parsed into datetime objects for calculation
        date1_obj = datetime.strptime(str(date1), '%m/%d/%Y')
        date2_obj = datetime.strptime(str(date2), '%m/%d/%Y')
        return abs((date2_obj - date1_obj).days)
    except ValueError:
        # Handle cases of invalid date formats
        return 0

def get_ebay_url(item_id: str) -> str:
    """
    Generate a search URL for eBay to find sold and completed listings for an item.

    :param item_id: The unique identifier for the item, typically its name or model.
    :return: A valid URL string for searching the item on eBay.
    """
    brand = input("Enter the brand of the item to search for on eBay: ")
    item_id = brand + " " + item_id  # Combine brand and item name for a more specific search
    return (
        f'https://www.ebay.com/sch/i.html?_nkw={item_id.replace(" ", "+")}&_sacat=0&_from=R40&rt=nc&LH_Sold=1&LH_Complete=1&_pgn=1'
    )

def print_summary(values):
    """
    Print a summary of financial attributes for specific items in the dataset.

    :param values: A dictionary where the keys are labels (e.g., 'Max Profit Item'),
                   and values are rows from the DataFrame containing item details.
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

def profit_distribution(df: pd.DataFrame, title: str = "Profit Distribution"):
    """
    Visualize the distribution of profit using a histogram.

    :param df: The input DataFrame containing the 'Profit' column.
    :param title: The title for the plot.
    """
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Profit'], kde=True, bins=50, color='blue')
    plt.title(title)
    plt.xlabel('Profit ($)')
    plt.ylabel('Number of Items')
    plt.tight_layout()
    plt.show()

def sale_price_vs_profit(df):
    """
    Generate a scatterplot showing the relationship between sale price and profit.

    :param df: The input DataFrame containing sale price, profit, and condition of items.
    """
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='Sale Price', y='Profit', data=df, hue='Condition', palette='coolwarm')
    plt.title('Sale Price vs. Profit')
    plt.xlabel('Sale Price ($)')
    plt.ylabel('Profit ($)')
    plt.tight_layout()
    plt.show()

def sales_by_condition(df):
    """
    Create a boxplot showing the distribution of sales prices by item condition.

    :param df: The input DataFrame containing sale price and item condition.
    """
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Condition', data=df, y='Sale Price', hue='Condition', palette='coolwarm')
    plt.title('Sales by Condition')
    plt.xlabel('Condition')
    plt.ylabel('Sale Price ($)')
    plt.tight_layout()
    plt.show()

def days_to_sell_distribution(df):
    """
    Plot the distribution of the number of days it took to sell items.

    :param df: The input DataFrame containing purchase and sale dates.
    """
    # Add a column to the DataFrame for days to sell
    df['# Days to sell'] = df.apply(
        lambda row: calculate_date_difference(row['Purchase Date'], row['Sale Date']),
        axis=1
    )
    plt.figure(figsize=(10, 6))
    sns.histplot(df['# Days to sell'], kde=True, bins=50, color='green')
    plt.title('Days to Sell Distribution')
    plt.xlabel('# Days to Sell')
    plt.ylabel('Number of Items')
    plt.tight_layout()
    plt.show()

def avg_profit_by_purchase_range(df):
    """
    Plot average profit for different purchase cost ranges.

    :param df: The input DataFrame containing purchase cost and profit details.
    """
    bin_edges = np.histogram_bin_edges(df['Purchase Cost'], bins=20)
    df['Cost Range'] = pd.cut(df['Purchase Cost'], bins=bin_edges, include_lowest=True)

    avg_profit = df.groupby('Cost Range')['Profit'].mean().reset_index()

    plt.figure(figsize=(10, 6))
    sns.barplot(x='Cost Range', y='Profit', data=avg_profit)
    plt.title('Average Profit by Purchase Range')
    plt.xlabel('Purchase Cost Range')
    plt.ylabel('Average Profit ($)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def monthly_profit_over_time(df):
    """
    Plot total profit over time aggregated by month.

    :param df: The input DataFrame containing sale dates and profit.
    """
    # Ensure 'Sale Date' is in datetime format
    df['Sale Date'] = pd.to_datetime(df['Sale Date'], errors='coerce')
    df = df.dropna(subset=['Sale Date'])  # Drop rows with invalid/missing Sale Dates

    # Group by month and sum profits
    profit = df.groupby(df['Sale Date'].dt.to_period('M'))['Profit'].sum().reset_index()
    profit['Sale Date'] = profit['Sale Date'].dt.to_timestamp()

    plt.figure(figsize=(10, 6))
    sns.lineplot(x='Sale Date', y='Profit', data=profit, marker='o')
    plt.title('Total Profit Over Time')
    plt.xlabel('Month')
    plt.ylabel('Total Profit ($)')
    plt.tight_layout()
    plt.show()

def process_dataframe(df: pd.DataFrame) -> None:
    """
    Perform various processing steps on the input DataFrame, including:
      - Cleaning and filtering data
      - Computing metrics like profit, average costs, and sale durations
      - Printing a financial summary of the cleaned data

    :param df: Input Pandas DataFrame containing raw pricing data.
    """
    # Extract the first item's identifier for context
    item = df.at[0, 'Item']
    print(f"Processing data for item: {item}\n")

    # Step 1: Print initial (raw) data
    print("Initial data (including scrap items):")
    print(df, "\n")

    # Step 2: Filter out scrap items for cleaner data
    filtered_df = df[df['So Condition'] != 'SCRP'].copy()
    print("Data after filtering scrap items:")
    print(filtered_df, "\n")

    # Step 3: Calculate '# Days to Sell' for each item
    filtered_df['# Days to sell'] = filtered_df.apply(
        lambda row: calculate_date_difference(row['Purchase Date'], row['Sale Date']),
        axis=1
    )
    print("Data with '# Days to sell' calculated:")
    print(filtered_df, "\n")

    # Additional metrics and visualizations are generated through specific functions

def generate_financial_summary(filepath: str = os.getenv('TEST_FILE') + '.xlsx'):
    """
    Main entry point for reading an Excel file, processing data, and printing or visualizing outputs.

    :param filepath: The file path to the Excel file containing raw pricing data.
    """
    # Load and process the Excel file
    df = pd.read_excel(filepath, skiprows=[0], usecols='B, C, E, G, H, K, L, N, O, R')
    process_dataframe(df)  # Perform main data processing steps
    profit_distribution(df)  # Generate relevant visualizations
    sale_price_vs_profit(df)
    sales_by_condition(df)
    days_to_sell_distribution(df)
    avg_profit_by_purchase_range(df)
    monthly_profit_over_time(df)

# Entry point for executing the script
generate_financial_summary()