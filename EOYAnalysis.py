from re import I
import requests
import datetime
import matplotlib.pyplot as plt
import json
import csv

def dateObject(rawDate):
    date = datetime.date(int(rawDate[0:4]), int(rawDate[5:7]), int(rawDate[8:10]))
    return date

# get day before as datetime object
def getDayBefore(date):
    Previous_Date = date - datetime.timedelta(days=1)
    weekno = Previous_Date.weekday()
    if weekno >= 5:  # 5 Sat, 6 Sun
        Previous_Date = date - datetime.timedelta(days=2)
    return Previous_Date

#Check if day is a weekend
def isWeekend(date):
    weekno = date.weekday()
    if weekno >= 5:  # 5 Sat, 6 Sun
        return True
    else:
        return False


# have pre loaded data from exchange
#exchange = 'SPX'
exchange = 'SPX2'
dataExchange = {}
with open("C:\\Users\\plant\\Documents\\StockCode\\" + exchange + ".csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        i = 0
        for row in csv_reader:
            if(len(row) != 6):
                break
            if i != 0:
                dataExchange[row[0]] = {'1. open': row[1], '2. high' : row[2], '3. low': row[3], '4. close': row[4]}
            i += 1

# choose ticker to look at
ticker = "AAPL"

url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=' + ticker + '&outputsize=full&apikey=H0RH5KTMI3NJOCWX'
r = requests.get(url)
data = r.json()
days = list(data['Time Series (Daily)'].keys())

year = 5
year = 2020

for i in range(5):
    # start of year
    firstDay = dateObject(year + "0101")
    while(firstDay.strftime('%Y-%m-%d') not in days):
        firstDay = firstDay + datetime.timedelta(days=1)
    startPrice = data['Time Series (Daily)'][firstDay.strftime('%Y-%m-%d')]['1. open']
    iStartPrice = dataExchange[firstDay.strftime('%m-%d-%Y')]['1. close']

    
    date = dateObject(year + "0131")
    ratios = []
    prices = []
    iRatios = []
    iPrices = []

# insead of adding month to date just create array of dateobject so you garuntee you get last trading daty

    for i in range(1,25):
        date = ""
        if i < 10:
            date += "0"
        date += i
        date += "31"
        date = date + datetime.timedelta(months=1)
        ourDate = date
        while(ourDate.strftime('%Y-%m-%d') not in days):
            ourDate = ourDate - datetime.timedelta(days=1)
        monthsLaterPrice = data['Time Series (Daily)'][ourDate.strftime('%Y-%m-%d')]['4. close']
        prices.append(monthsLaterPrice)
        ratios.append((startPrice - monthsLaterPrice) / startPrice)

        iMonthsLaterPrice = dataExchange[ourDate.strftime('%m-%d-%Y')]['4. close']
        iPrices.append(monthsLaterPrice)
        iRatios.append((iStartPrice - iMonthsLaterPrice) / iStartPrice)

    #index ratios

        
    next12Ratios = []
    iNext12Ratios = []
    last2 = (prices[11] - prices[9]) / prices[9]
    iLast2 = (iPrices[11] - iPrices[9]) / iPrices[9]

    if(ratios[9] < 0):
        # want the ratio of two month left to year end -> how much it went down between them
        # ocmpared to index
        for i in range(12,25):
            next12Ratios.append((prices[i] - prices[11]) / prices[11])
            iNext12Ratios.append((iPrices[i] - iPrices[11]) / iPrices[11])



        # look at next few months -> after 




