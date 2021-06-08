#This program scrapes a table from dogsofthedow's website. Creates a dataframe
#and uses the data from one column in the dataframe to make calls to APIs
#on finnhub.com, which returns stock information that can be used to create an
#additional dataframe. The dataframes are then merged horizontally to display
#stock data for certain compaines

# import libraries
import requests
import pandas as pd
from bs4 import BeautifulSoup
import json

# url to get table data from
url = "https://www.dogsofthedow.com/largest-companies-by-market-cap.htm"

page = requests.get(url, verify=False) # request html

soup = BeautifulSoup(page.content, 'html.parser') # use BeautifulSoup to parse html content

# find and scrape data from the right table
table = soup.find('table', class_="tablepress tablepress-id-20 tablepress-responsive")

# Create the lists to store scraped data
L1 = []
L2 = []

# Create a for loop and if statment to find and append data to the list
for row in table.findAll('tr'):
  cells = row.findAll('td')
  if len(cells) == 7:
    L1.append(cells[0].find(text=True).rstrip("\n"))
    L2.append(cells[1].find(text=True).rstrip("\n"))

# Create a Dataframe that uses the data in the list 
Df = pd.DataFrame()
Df['Ticker']         = L1
Df['Company Name']   = L2

# Format dataframe to display all rows and columns
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# Create first dataframe by formating previous dataframe to display the first 30 rows
Df1 = Df.head(30)

# Convert Column name 'Ticker' into a list
comp_names = Df['Ticker'].to_list()

# Free API key from https://finnhub.io
key = 'key'

# List of information to extract
OpenPrice = []
HighPrice = []
LowPrice = []
CurrentPrice = []
PreviousClosePrice = []
MarketCap = []
Country = []
Currency = []
Industry = []


# For loop to request and store data from API
for company in comp_names:
  url = f"https://finnhub.io/api/v1/quote?symbol={company}&token={key}" 
  URL = f"https://finnhub.io/api/v1/stock/profile2?symbol={company}&token={key}"

  #Request information from API and store data into r and q variables
  r = requests.get(url)
  q = requests.get(URL)
  # If statements to check if API calls were successful, then append specific wanted data
  if r.status_code == 200:
    data = r.json()
    OpenPrice.append(data['o'])
    HighPrice.append(data['h'])
    LowPrice.append(data['l'])
    CurrentPrice.append(data['c'])
    PreviousClosePrice.append(data['pc'])
  if q.status_code == 200:
    data = q.json()
    MarketCap.append(data['marketCapitalization'])
    Country.append(data['country'])
    Currency.append(data['currency'])
    Industry.append(data['finnhubIndustry'])

# Create a dictionary to store collected data
Company_Daily_Stock_Data = {
                              'Country': Country,
                              'Currency': Currency,
                              'Industry': Industry,
                              'Stock Opening Price': OpenPrice,
                              'High Stock Price': HighPrice,
                              'Low Stock Price': LowPrice,
                              'Current Stock Price': CurrentPrice,
                              'Previous Stock Closing Price' : PreviousClosePrice,
                              'Market Capitalization': MarketCap
                           }

# Create second dataframe from Company Daily Stock Data dictionary
Df2 = pd.DataFrame(Company_Daily_Stock_Data)

Df3 = pd.concat([Df1,Df2], axis = 1) # Merge the two previous dataframes into one

# Display merged dataframe
print("DataFrame:")
print(Df3)

Df3.to_csv('Stock Price Statistics.csv') # Parse data to csv file

# Display description statitics
Stock_Price_Stats = Df3.describe().apply(lambda x: x.apply('{0:.2f}'.format))
print("Description Statistics:")
print(Stock_Price_Stats)

