import os
from datetime import datetime
from statistics import mean
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Load environment variables (e.g., for reading environment-specific file paths or configurations)
load_dotenv()

def calculate_date_difference(date1, date2) -> int:
    """
    Calculate the number of days between two dates in mm/dd/yyyy format.
    
    :param date1: Start date, either as a string in mm/dd/yyyy format or NaN.
    :param date2: End date, either as a string in mm/dd/yyyy format or NaN.
    :return: Number of days between the two dates. Returns 0 if either date is invalid or missing.
    """
    if pd.isna(date1) or pd.isna(date2):
        # Handle cases where either or both dates are missing (NaN)
        return 0

    try:
        # Ensure dates are strings and parse them into datetime objects
        date1_str = str(date1)
        date2_str = str(date2)
        date1_obj = datetime.strptime(date1_str, '%m/%d/%Y')
        date2_obj = datetime.strptime(date2_str, '%m/%d/%Y')
        return abs((date2_obj - date1_obj).days)
    except ValueError:
        # Catch cases where the date format is invalid
        return 0

def get_ebay_url(item_id: str) -> str:
    """
    Generate a search URL for eBay to find sold and completed listings for an item.

    :param item_id: The unique identifier for the item, typically its name or model.
    :return: A valid URL string for searching the item on eBay.
    """
    brand = input("Enter the brand of the item to search for on eBay: ")
    item_id = brand + " " + item_id
    return (
        f'https://www.ebay.com/sch/i.html?_nkw={item_id.replace(" ", "+")}&_sacat=0&_from=R40&rt=nc&LH_Sold=1&LH_Complete=1&_pgn=1'
    )

def print_summary(values):
    """
    Print a summary of financial statistics for specific items in the dataset.
    
    :param values: A dictionary where the keys are labels (e.g., 'Max Profit Item') 
                   and the values are rows from the DataFrame containing item details.
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

def profit_distribution_graph(df: pd.DataFrame, title: str = "Profit Distribution"):
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Profit'], kde=True, bins=50, color='blue')
    plt.title(title)
    plt.xlabel('Profit ($)')
    plt.ylabel('Number of Items')
    plt.tight_layout()
    plt.show()

def sale_price_vs_profit(df):
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='Sale Price', y='Profit', data=df, hue='Condition', palette='viridis')
    plt.title('Sale Price vs. Profit')
    plt.xlabel('Sale Price ($)')
    plt.ylabel('Profit ($)')
    plt.show()

def sales_by_condition(df):
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Condition', data=df, y='Sale Price', hue='Condition', palette='coolwarm')
    plt.title('Sales by Condition')
    plt.xlabel('Condition')
    plt.ylabel('Number of Sales')
    plt.tight_layout()
    plt.show()

def process_dataframe(df: pd.DataFrame) -> None:
    """
    Perform various processing steps on the input DataFrame, including:
      - Filtering out unwanted data
      - Computing metrics like profit, average costs, and sale durations
      - Printing a financial summary of the cleaned data

    :param df: Input Pandas DataFrame containing raw pricing data.
    """
    # Extract the first item's identifier for context
    item = df.at[0, 'Item']
    print(f"Processing data for item: {item}\n")

    # Print initial data
    print("Initial data (including scrap items):")
    print(df, "\n")

    # Filter out scrap items from the dataset and make a new copy for safe calculations
    filtered_df = df[df['So Condition'] != 'SCRP'].copy()
    print("Data after filtering scrap items:")
    print(filtered_df, "\n")

    # Calculate how many days it took to sell each item
    filtered_df['# Days to sell'] = filtered_df.apply(
        lambda row: calculate_date_difference(row['Purchase Date'], row['Sale Date']),
        axis=1
    )

    print("Data with calculated '# Days to sell':")
    print(filtered_df, "\n")

    # Calculate basic statistics
    num_sold = len(filtered_df[filtered_df['Sale Price'].notna() & (filtered_df['Sale Price'] != 0)])
    num_inventory = filtered_df['Purchase Date'].count()
    inventory_left = num_inventory - num_sold

    print(f"🛠 Statistics:")
    print(f"  Total items: {num_inventory}")
    print(f"  Items sold: {num_sold}")
    print(f"  Items remaining in inventory: {inventory_left}\n")

    # Financial statistics
    avg_purchase_cost = mean(filtered_df['Purchase Cost'])
    avg_purchase_cost_no0 = mean(
        filtered_df['Purchase Cost'][(filtered_df['Purchase Cost'].notna()) & (filtered_df['Purchase Cost'] != 0)]
    )
    max_sale_price = max(filtered_df['Sale Price'].dropna())
    min_sale_price = min(
        filtered_df['Sale Price'][(filtered_df['Sale Price'].notna()) & (filtered_df['Sale Price'] != 0)]
    )
    avg_sale_price = mean(filtered_df['Sale Price'].dropna())
    avg_sale_price_no0 = mean(
        filtered_df['Sale Price'][(filtered_df['Sale Price'].notna()) & (filtered_df['Sale Price'] != 0)]
    )
    max_profit = max(filtered_df['Profit'])
    min_profit = min(filtered_df['Profit'])
    avg_profit = mean(filtered_df['Profit'])
    avg_profit_no0 = mean(
        filtered_df['Profit'][(filtered_df['Profit'].notna()) & (filtered_df['Profit'] != 0)]
    )
    total_profit = sum(filtered_df['Profit'])

    print("📈 Financial Summary:")
    print(f"  Total profit: ${total_profit:,.2f}")
    print(f"  Sale price range (excluding $0): [${min_sale_price:,.2f}, ${max_sale_price:,.2f}]")
    print(f"  Profit range: [${min_profit:,.2f}, ${max_profit:,.2f}]\n")

    print("Averages (including zeros):")
    print(f"  Average profit per item: ${avg_profit:,.2f}")
    print(f"  Average purchase cost per item: ${avg_purchase_cost:,.2f}")
    print(f"  Average sale price per item: ${avg_sale_price:,.2f}\n")

    print("Averages (excluding zeros):")
    print(f"  Average profit per item (excl. $0): ${avg_profit_no0:,.2f}")
    print(f"  Average purchase cost per item (excl. $0): ${avg_purchase_cost_no0:,.2f}")
    print(f"  Average sale price per item (excl. $0): ${avg_sale_price_no0:,.2f}\n")

    # Find items of interest: max profit, max sale, min profit, and min sale
    item_dict = {
        "Max Profit Item": filtered_df.loc[filtered_df['Profit'].idxmax()],
        "Min Profit Item": filtered_df.loc[filtered_df['Profit'].idxmin()],
        "Max Sale Item": filtered_df.loc[filtered_df['Sale Price'][(filtered_df['Sale Price'].notna()) &
                                                                   (filtered_df['Sale Price'] != 0)].idxmax()],
        "Min Sale Item": filtered_df.loc[filtered_df['Sale Price'][(filtered_df['Sale Price'].notna()) &
                                                                   (filtered_df['Sale Price'] != 0)].idxmin()]
    }

    print("🔍 Highlighted Items:")
    print_summary(item_dict)

    # Generate an eBay URL for the item with the highest profit
    url = get_ebay_url(str(item_dict["Max Profit Item"]['Item']))
    print(f"Ebay URL to sold listings for the highest profit item: {url}\n")

def generate_financial_summary(filepath: str = os.getenv('TEST_FILE') + '.xlsx'):
    """
    Main entry point for reading an Excel file, processing data, and printing a summary.

    :param filepath: Full file path to the Excel document containing pricing data.
    """
    # Read data from Excel file into a DataFrame
    df = pd.read_excel(filepath, skiprows=[0], usecols='B, C, E, G, H, K, L, N, O, R')
    process_dataframe(df)

# Entry point for script execution
generate_financial_summary()