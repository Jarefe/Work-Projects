import requests, re, numpy as np
from bs4 import BeautifulSoup

def fetch_ebay_data(search: str, num_pages: int = 5):
    """Fetch eBay data for a given search term and number of pages"""
    prices = []
    # TODO: try to get titles of ebay listings in addition to prices
    titles = []

    # Loop through the pages of search results
    for page in range(1, num_pages + 1):
        # Build the eBay search URL with the correct parameters
        url = f'https://www.ebay.com/sch/i.html?_nkw={search.replace(' ', '+')}&_sacat=0&_from=R40&rt=nc&LH_Sold=1&LH_Complete=1&_pgn={page}'

        # Send GET request to eBay
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code != 200:
            print(f'Error fetching data from eBay: {response.status_code}')
            continue

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Handle zero results
        page_text = soup.get_text().lower()
        if '0 results found for' in page_text:
            print(f'0 sold results found for "{search}".')

        # Find all price elements on the page
        price_elements = soup.find_all('span', class_='s-item__price')

        # If no price elements found, then page is empty or there is an issue
        if not price_elements:
            print(f'No results found on page {page}. Stopping further requests.')
            break  # Scraping stopped if no results found

        # Extract the price from each element
        for price_element in price_elements:
            # Clean the price string to remove currency symbols and commas
            price_text = price_element.get_text()

            # Handle price ranges like '120 to 180'
            if 'to' in price_text:
                try:
                    low_price, high_price = price_text.split(' to ')
                    low_price = float(re.sub(r'[^\d.]', '', low_price))  # Clean and convert the low price
                    high_price = float(re.sub(r'[^\d.]', '', high_price))  # Clean and convert the high price
                    price = (low_price + high_price) / 2  # Use the average of the range
                except ValueError:
                    print(f'Error parsing price range: {price_text}')
                    continue  # Skip this price if there's a parsing error
            else:
                try:
                    # Clean and convert the price (single value)
                    price = float(re.sub(r'[^\d.]', '', price_text))

                    # If the price is too low or zero, skip it
                    if price < 20.0:
                        continue
                except ValueError:
                    print(f'Error parsing price: {price_text}')
                    continue  # Skip this price if it can't be parsed

            prices.append(price)

    # Handle the case where no valid prices were found
    if not prices:
        print('No valid prices found.')
        return []

    return prices


def remove_outliers(prices: list):
    """Remove outliers from a list of prices"""
    # Convert to numpy array
    prices = np.array(prices)
    if len(prices) < 4:
        return prices # Not enough to filter
    print(f'Unfiltered prices: {prices}')

    # Calculate Q1 & Q3 (25th and 75th percentile)
    q1 = np.percentile(prices, 25)
    q3 = np.percentile(prices, 75)

    # Inter quartile range
    iqr = q3 - q1

    # Define acceptable range
    # Can change iqr multiplier or lower bound as necessary
    # Setting lowest bound to 20 to avoid outliers that are too low to be relevant to device price
    lower_bound = round(max(q1 - 1.5 * iqr, 20), 2)
    upper_bound = round(q3 + 1.5 * iqr,2)

    print(f'lower bound: {lower_bound}\nupper bound: {upper_bound}')

    # Exclude outliers
    filtered_prices = prices[(prices >= lower_bound) & (prices <= upper_bound)]
    removed_prices = prices[~(prices >= lower_bound) | ~(prices <= upper_bound)].tolist()
    print(f'Removed prices: {removed_prices}')
    return filtered_prices


def calculate_price_statistics(prices: list):
    """Calculate average price, highest price, and lowest price from a list of prices"""
    if len(prices) == 0:
        print('No data for search term')
        return None

    # Remove outliers
    filtered_prices = remove_outliers(prices)

    print(f'Filtered prices: {filtered_prices}')

    return np.mean(filtered_prices), max(filtered_prices), min(filtered_prices)

def scrape_ebay_data(search="", pages = 2):
    search = search.strip()
    if not search:
        raise ValueError("Empty search term.")

    # Construct the eBay search URL reflecting the page count (showing page 1 as link)
    url = f'https://www.ebay.com/sch/i.html?_nkw={search.replace(" ", "+")}&_sacat=0&_from=R40&rt=nc&LH_Sold=1&LH_Complete=1&_pgn=1'

    # You might want to optionally return a list of URLs for pages 1 to pages, but here we keep page=1 as main link

    # Fetch prices from multiple pages as needed (your fetch_ebay_data function needs to handle pages)
    fetched_prices = fetch_ebay_data(search, pages)  # Make sure your fetch function supports page count
    fetched_prices = fetched_prices[2:]  # Remove irrelevant data, as before

    avg_price, highest_price, lowest_price = calculate_price_statistics(fetched_prices)

    return {
        "url": url,
        "average price": avg_price,
        "highest price": highest_price,
        "lowest price": lowest_price,
        "prices": fetched_prices
    }