import requests
import datetime
import matplotlib.pyplot as plt
import json
import csv

# get date as datetime object
def dateObject(rawDate):
    date = datetime.date(int(rawDate[0:4]), int(rawDate[5:7]), int(rawDate[8:10]))
    return date

# get day before as datetime object
def getDayBefore(date):
    Previous_Date = date- datetime.timedelta(days=1)
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
#print(dataExchange)


# choose ticker to look at
ticker = "AAPL"

# get earning dates
url = 'https://www.alphavantage.co/query?function=EARNINGS&symbol=' + ticker + '&apikey=H0RH5KTMI3NJOCWX'
r = requests.get(url)
data = r.json()
earningDates = []
for i in range(len(data['quarterlyEarnings'])):
    earningDates.append(data['quarterlyEarnings'][i]['reportedDate'])
    #print(data['quarterlyEarnings'][i]['reportedDate'])
# print(earningDates[len(earningDates) - 1])
# print(earningDates)

#analysis
url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=' + ticker + '&outputsize=full&apikey=H0RH5KTMI3NJOCWX'
r = requests.get(url)
data = r.json()
days = list(data['Time Series (Daily)'].keys())
# print(days)
losses = []
gains = []
counter = 0

fig1 = plt.figure(figsize=plt.figaspect(0.8))

# days to look forward after earnings
length = 30
# max number of years to look back
years = 5

for i in range(1, min(4 * years, len(earningDates))):
    print("earnings Date")
    print(earningDates[i])
    # get last day before the earnings - sometime not the previous day because
    # of weekends or possibly holidays 
    previousDay = getDayBefore(dateObject(earningDates[i]))
    while( previousDay.strftime('%Y-%m-%d') not in days):
        previousDay = previousDay - datetime.timedelta(days=1)
    #close of previous day
    previousClose = data['Time Series (Daily)'][previousDay.strftime('%Y-%m-%d')]['4. close']
    # in case somehow there is no data fro the earnings date just ignore this earnings and move on
    if(earningDates[i] not in days):
        continue


    #get relevant information for specific day from dataset
    print("\npreviousClose")
    print(previousClose)
    earningsOpen = data['Time Series (Daily)'][earningDates[i]]['1. open']
    print("\nearningsOpen")
    print(earningsOpen)
    earningsHigh = data['Time Series (Daily)'][earningDates[i]]['2. high']
    print("\nearningsHigh")
    print(earningsHigh)
    earningsClose = data['Time Series (Daily)'][earningDates[i]]['4. close']
    print("\nearningsClose")
    print(earningsClose)

    # get next day
    currentDay = dateObject(earningDates[i]) + datetime.timedelta(days=1)
    while(currentDay.strftime('%Y-%m-%d') not in days):
        currentDay = currentDay + datetime.timedelta(days=1)

    # get relevant information for next day
    nextDayOpen = data['Time Series (Daily)'][currentDay.strftime('%Y-%m-%d')]['1. open']
    print("\nnextDayOpen")
    print(nextDayOpen)
    nextDayHigh = data['Time Series (Daily)'][currentDay.strftime('%Y-%m-%d')]['2. high']
    print("\nnextDayHigh")
    print(nextDayHigh)
    nextDayClose = data['Time Series (Daily)'][currentDay.strftime('%Y-%m-%d')]['4. close']
    print("\nnextDayClose")
    print(nextDayClose)
    nextDayExchangeClose = dataExchange[currentDay.strftime('%m-%d-%Y')]['4. close']

    # calculate percent change from previous close to next day close
    # do this because you don;t know if earings came out before or after close
    ratio = 100 * (float(nextDayClose) - float(previousClose)) / float(previousClose)
    print("\nprecent raise prev day close to next day close")
    print(ratio)

    


    # looking at next "length" number of days

    high = 0
    low = 100000000
    highDayWk = -1
    lowDayWk = -1
    opens = []
    highs = []
    lows = []
    closes = []
    endOfPeriodPrice = 0


    for i in range(0, length):
        # get next day - start at the day after the day after earnings
        # current day is the day after earnings right now 
        currentDay = currentDay + datetime.timedelta(days=1)
        while(currentDay.strftime('%Y-%m-%d') not in days):
            currentDay = currentDay + datetime.timedelta(days=1)

        # get data from dataset
        dayOpening = float(data['Time Series (Daily)'][currentDay.strftime('%Y-%m-%d')]['1. open'])
        dayHigh = float(data['Time Series (Daily)'][currentDay.strftime('%Y-%m-%d')]['2. high'])
        dayLow = float(data['Time Series (Daily)'][currentDay.strftime('%Y-%m-%d')]['3. low'])
        dayClose = float(data['Time Series (Daily)'][currentDay.strftime('%Y-%m-%d')]['4. close'])

        if(i == length - 1):
            endOfPeriodPrice = dayClose
            endOfPeriodExchangePrice = float(dataExchange[currentDay.strftime('%m-%d-%Y')]['4. close'])
        opens.append(dayOpening)
        highs.append(dayHigh)
        lows.append(dayLow)
        closes.append(dayClose)
        if dayHigh > high:
            high = dayHigh
            highDayWk = i
            y = []
        if dayLow < low:
            low = dayLow
            lowDayWk = i


    # graph the length days after
    if(ratio > 0):
        counter += 1
        dataArray = []
        x = []
        for i in range(len(closes)):
            # dataArray.append(opens[i])
            # x.append(0 + i * 3)
            # dataArray.append(highs[i])
            # x.append(1 + i * 3)
            dataArray.append(closes[i])
            #x.append(2 + i * 3)
            x.append(i)
        ax = fig1.add_subplot(5,4,counter)
        ax.set_title(currentDay.strftime('%Y-%m-%d'))
        ax.plot(x, dataArray)
    else:
        counter += 1
        dataArray = []
        x = []
        for i in range(len(opens)):
            # dataArray.append(opens[i])
            # print(f"opens[{i}]")
            # print(opens[i])
            # x.append(0 + i * 3)
            # dataArray.append(lows[i])
            # x.append(1 + i * 3)
            dataArray.append(closes[i])
            x.append(i)
        ax = fig1.add_subplot(5,4,counter)
        ax.set_title(currentDay.strftime('%Y-%m-%d'))
        ax.plot(x, dataArray)


    # analyze the period
    periodPercentRaise = 100 * (high - float(nextDayClose)) / float(nextDayClose)
    periodPercentLoss = 100 * (low - float(nextDayClose)) / float(nextDayClose)
    print("periodPercentRaise")
    print(periodPercentRaise)
    print("periodPercentLoss")
    print(periodPercentLoss)
    print("Week high: ")
    print(high)
    print("high day")
    print(highDayWk)
    print("Week low: ")
    print(low)
    print("low day")
    print(lowDayWk)

    print('ratio, periodMaxPercentLoss / Raise, lowDayWk(ratio < 0)/ highDayWk(gainers ratio > 0), endOfPeriodRatio, exchangeRatio, endOfperiodRatio - exchangeRatio')
    endOfPeriodRatio = 100 * ( endOfPeriodPrice - float(nextDayClose)) / float(nextDayClose)
    exchangeRatio = 100 * ( endOfPeriodExchangePrice - float(nextDayExchangeClose)) / float(nextDayExchangeClose)
    if(ratio < 0):
        losses.append([ratio, periodPercentLoss, lowDayWk, endOfPeriodRatio, exchangeRatio, endOfPeriodRatio - exchangeRatio])
    else:
        gains.append([ratio, periodPercentRaise, highDayWk, endOfPeriodRatio, exchangeRatio, endOfPeriodRatio - exchangeRatio])
    
print("losses")
for i in range(len(losses)):
    print(losses[i])
    
print("gains")
for i in range(len(gains)):
    print(gains[i])


# analyze overall gainers and losers
dayTot = 0
for i in range(len(gains)):
    dayTot += gains[i][2]
gainAveDay = dayTot * 1.0 / len(gains)
dayTot = 0
for i in range(len(losses)):
    dayTot += losses[i][2]
lossAveDay = dayTot * 1.0 / len(losses)
print("gainAveDay")
print(gainAveDay)
print("lossAveDay")
print(lossAveDay)

#ave profit from buying stock that gained and profit from buying stock that didn't gain
totalGain = 0
for i in range(len(gains)):
    totalGain += gains[i][5]
aveGainGainers = totalGain * 1.0 / len(gains)
totalGain = 0
for i in range(len(losses)):
    totalGain += losses[i][5]
aveGainlosers = totalGain * 1.0 / len(losses)
print("aveGainGainers")
print(aveGainGainers)
print('aveGainlosers')
print(aveGainlosers)



plt.show()
#print(data)

#print(data['annualEarnings'])