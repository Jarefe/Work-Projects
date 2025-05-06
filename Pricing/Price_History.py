import os

import pandas as pd
import numpy as np
from dotenv import load_dotenv
from sklearn import linear_model
from Pricing.Ebay_Scraping import calculate_price_statistics

load_dotenv()

def pull_price_history(filepath: str = os.getenv('PRICE_HISTORY_FILEPATH') + 'Price History.xlsx'):
      # Create dataframe from price data
      # Potentially change to pull data from database instead of excel file
      # Using columns 'Revenue Share', 'Purchase Cost', 'Sale Price', and 'Profit'
      df = pd.read_excel(filepath, skiprows=[0], usecols='B,G,H,O,R')
      item = df.at[3, 'Item']

      df = df[df['Sale Price'] > 0] # remove rows with zero sale price (entails scrap units)

      print('DATAFRAME')
      print(df)
      print('==================================')
      sale_prices = df['Sale Price']
      print('SALE PRICES')
      print(sale_prices)
      print('==================================')

      X = df[['Revenue Share','Purchase Cost', 'Sale Price']]
      y = df['Profit']

      print('X axis')
      print(X)
      print('==================================')
      print('Y axis')
      print(y)

      avg_sale, max_sale, min_sale = calculate_price_statistics(sale_prices)
      print('Removing outliers in data...')


      print(f'Average Sale Price: {avg_sale}')
      print(f'Highest Sale Price: {max_sale}')
      print(f'Lowest Sale Price: {min_sale}')

pull_price_history()