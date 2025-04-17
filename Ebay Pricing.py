import requests
from bs4 import BeautifulSoup
import numpy as np
import re
import webbrowser

def fetch_ebay_data(search: str, num_pages: int = 2):
    prices = []

    # Loop through the pages of search results
    for page in range(1, num_pages + 1):
        # Build the eBay search URL with the correct parameters
        url = f"https://www.ebay.com/sch/i.html?_nkw={search.replace(' ', '+')}&_sacat=0&_from=R40&rt=nc&LH_Sold=1&LH_Complete=1&_pgn={page}"
        
        # Send GET request to eBay
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code != 200:
            print(f"Error fetching data from eBay: {response.status_code}")
            continue
        
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all price elements on the page
        price_elements = soup.find_all('span', class_='s-item__price')

        # If no price elements found, then page is empty or there is an issue
        if not price_elements:
            print(f"No results found on page {page}. Stopping further requests.")
            break  # Scraping stopped if no results found
        
        # Extract the price from each element
        for price_element in price_elements:
            # Clean the price string to remove currency symbols and commas
            price_text = price_element.get_text()
            
            # Handle price ranges like "120 to 180"
            if 'to' in price_text:
                try:
                    low_price, high_price = price_text.split(' to ')
                    low_price = float(re.sub(r'[^\d.]', '', low_price))  # Clean and convert the low price
                    high_price = float(re.sub(r'[^\d.]', '', high_price))  # Clean and convert the high price
                    price = (low_price + high_price) / 2  # Use the average of the range
                except ValueError:
                    print(f"Error parsing price range: {price_text}")
                    continue  # Skip this price if there's a parsing error
            else:
                try:
                    # Clean and convert the price (single value)
                    price = float(re.sub(r'[^\d.]', '', price_text))
                    
                    # If the price is too low or zero, skip it
                    if price < 1.0:
                        continue
                except ValueError:
                    print(f"Error parsing price: {price_text}")
                    continue  # Skip this price if it can't be parsed

            prices.append(price)

    # Handle the case where no valid prices were found
    if not prices:
        print("No valid prices found.")
        return []

    return prices

def remove_outliers(prices: list):
    # Convert to numpy array
    prices = np.array(prices)

    # Calculate Q1 & Q3 (25th and 75th percentile)
    q1 = np.percentile(prices, 25)
    q3 = np.percentile(prices, 75)

    # Inter quartile range
    iqr = q3 - q1

    # Define acceptable range
    lower_bound = max(q1 - 1.5 * iqr, 10)
    upper_bound = q3 + 1.5 * iqr

    print(f"lower bound: {lower_bound} \n upper bound: {upper_bound}")
    
    # Exclude outliers
    filtered_prices = prices[(prices >= lower_bound) & (prices <= upper_bound)]
    return filtered_prices

def find_average_price(prices: list):
    if len(prices) == 0:
        print("No data for search term")
        return None
    
    # Remove outliers
    filtered_prices = remove_outliers(prices)

    average_price = np.mean(filtered_prices)

    return average_price, max(filtered_prices), min(filtered_prices)

# Get user input for search term and cutoff price
search = input("Enter search term: ").strip()

try:
    cutoff = float(input("Enter cutoff price ($): ").strip())
except:
    print("No input provided, default cutoff is 80")
    cutoff = 80.0

# Open webpage for user to refer to
link = f"https://www.ebay.com/sch/i.html?_nkw={search.replace(' ', '+')}&_sacat=0&_from=R40&rt=nc&LH_Sold=1&LH_Complete=1&_pgn=1"
webbrowser.open(link) # comment out if no need to open page

# Fetch eBay data and calculate the average price
fetched_prices = fetch_ebay_data(search)
fetched_prices = fetched_prices[2:]

# Check if we have valid prices and compute the average price
if fetched_prices:
    avg_price, highest_price, lowest_price = find_average_price(fetched_prices)
    if avg_price is not None:
        print(f"Prices: {fetched_prices}\n")
        print(f"Average Price after removing outliers: {avg_price:.2f}")
        print(f"Highest price after removing outliers: {highest_price}")
        print(f"Lowest price after removing outliers: {lowest_price}")

        if avg_price < cutoff:
            print("Device is below cut line")
