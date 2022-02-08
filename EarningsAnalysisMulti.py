import requests
import datetime
import matplotlib.pyplot as plt
import json
import csv
import json
import io





# get date as datetime object
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

def isWeekend(date):
    weekno = date.weekday()
    if weekno >= 5:  # 5 Sat, 6 Sun
        return True
    else:
        return False


length = 30

years = 5
stocks = [['URI', 1 ]]
# , ['AFL', 1], ['AMZN', 1], ['ALGM', 0]]
for p in range(len(stocks)):
    exchange = 'SPX'
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
    # print(dataExchange)


    ticker = stocks[p][0]

    # get earning date
    url = 'https://www.alphavantage.co/query?function=EARNINGS&symbol=' + ticker + '&apikey=H0RH5KTMI3NJOCWX'
    r = requests.get(url)
    data = r.json()
    earningDates = []
    for i in range(len(data['quarterlyEarnings'])):
        earningDates.append(data['quarterlyEarnings'][i]['reportedDate'])
    with open(ticker + 'earnings.json', 'w') as f:
        json.dump(data, f)
        #print(data['quarterlyEarnings'][i]['reportedDate'])
    # print(earningDates[len(earningDates) - 1])
    # print(earningDates)

    #analysis
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=' + ticker + '&outputsize=full&apikey=H0RH5KTMI3NJOCWX'
    r = requests.get(url)
    data = r.json()
    print(data)
    days = list(data['Time Series (Daily)'].keys())
    with open(ticker + '.json', 'w') as f:
        json.dump(data, f)
    # print(days)
    losses = []
    gains = []
    counter = 0

    fig1 = plt.figure(figsize=plt.figaspect(0.8))


    for i in range(1, 4 * years):
        # print("earnings Date")
        # print(earningDates[i])
        previousDay = getDayBefore(dateObject(earningDates[i]))
        while( previousDay.strftime('%Y-%m-%d') not in days):
            previousDay = previousDay - datetime.timedelta(days=1)
        previousClose = data['Time Series (Daily)'][previousDay.strftime('%Y-%m-%d')]['4. close']
        if(earningDates[i] not in days):
            continue
        # print("previousClose")
        # print(previousClose)
        earningsOpen = data['Time Series (Daily)'][earningDates[i]]['1. open']
        # print("earningsOpen")
        # print(earningsOpen)
        earningsHigh = data['Time Series (Daily)'][earningDates[i]]['2. high']
        # print("earningsHigh")
        # print(earningsHigh)
        earningsClose = data['Time Series (Daily)'][earningDates[i]]['4. close']
        # print("earningsClose")
        # print(earningsClose)
        earningsExchangeClose = dataExchange[earningDates[i]]['4. close']

        currentDay = dateObject(earningDates[i]) + datetime.timedelta(days=1)
        while(currentDay.strftime('%Y-%m-%d') not in days):
            currentDay = currentDay + datetime.timedelta(days=1)
        nextDayOpen = data['Time Series (Daily)'][currentDay.strftime('%Y-%m-%d')]['1. open']
        # print("nextDayOpen")
        # print(nextDayOpen)
        nextDayHigh = data['Time Series (Daily)'][currentDay.strftime('%Y-%m-%d')]['2. high']
        # print("nextDayHigh")
        # print(nextDayHigh)
        nextDayClose = data['Time Series (Daily)'][currentDay.strftime('%Y-%m-%d')]['4. close']
        # print("nextDayClose")
        # print(nextDayClose)
        nextDayExchangeClose = dataExchange[currentDay.strftime('%Y-%m-%d')]['4. close']


        ratio = 100 * (float(nextDayClose) - float(earningsClose)) / float(earningsClose)
        if(stocks[p][1] == 0):
            ratio = 100 * (float(earningsClose) - float(previousClose)) / float(previousClose)
        # print("precent raise earnings close to next day close")
        # print(ratio)

        


        #next five days
        
        high = 0
        low = 1000000
        highDayWk = -1
        lowDayWk = -1
        opens = []
        highs = []
        lows = []
        closes = []
        endOfPeriodPrice = 0

        if(stocks[p][1] == 0):
            currentDay = currentDay - datetime.timedelta(days=1)
        for j in range(0, length):
            currentDay = currentDay + datetime.timedelta(days=1)
            while(currentDay.strftime('%Y-%m-%d') not in days):
                    currentDay = currentDay + datetime.timedelta(days=1)
            dayOpening = float(data['Time Series (Daily)'][currentDay.strftime('%Y-%m-%d')]['1. open'])
            dayHigh = float(data['Time Series (Daily)'][currentDay.strftime('%Y-%m-%d')]['2. high'])
            dayLow = float(data['Time Series (Daily)'][currentDay.strftime('%Y-%m-%d')]['3. low'])
            dayClose = float(data['Time Series (Daily)'][currentDay.strftime('%Y-%m-%d')]['4. close'])
            if(j == length - 1 ):
                endOfPeriodPrice = dayClose
                endOfPeriodExchangePrice = float(dataExchange[currentDay.strftime('%Y-%m-%d')]['4. close'])
            opens.append(dayOpening)
            highs.append(dayHigh)
            lows.append(dayLow)
            closes.append(dayClose)
            if dayHigh > high:
                high = dayHigh
                highDayWk = j
            if dayLow < low:
                low = dayLow
                lowDayWk = j
        if(ratio > 0):
            counter += 1
            dataArray = []
            x = []
            for j in range(len(opens)):
                dataArray.append(opens[j])
                x.append(0 + j * 3)
                dataArray.append(highs[j])
                x.append(1 + j * 3)
                dataArray.append(closes[j])
                x.append(2 + j * 3)
            ax = fig1.add_subplot(5,4,counter)
            ax.set_title(currentDay.strftime('%Y-%m-%d'))
            ax.plot(x, dataArray)
        # else:
            # counter += 1
            # dataArray = []
            # x = []
            # for j in range(len(opens)):
            #     dataArray.append(opens[j])
            #     print(f"opens[{j}]")
            #     print(opens[j])
            #     x.append(0 + j * 3)
            #     dataArray.append(lows[j])
            #     x.append(1 + j * 3)
            #     dataArray.append(closes[j])
            #     x.append(2 + j * 3)
            # ax = fig1.add_subplot(5,4,counter)
            # ax.set_title(currentDay.strftime('%Y-%m-%d'))
            # ax.plot(x, dataArray)
        periodPercentRaise = 0
        periodPercentLoss = 0
        if(stocks[p][1] == 1):
            periodPercentRaise = 100 * (high - float(nextDayClose)) / float(nextDayClose)
            periodPercentLoss = 100 * (low - float(nextDayClose)) / float(nextDayClose)
        elif (stocks[p][1] == 0):
            periodPercentRaise = 100 * (high - float(earningsClose)) / float(earningsClose)
            periodPercentLoss = 100 * (low - float(earningsClose)) / float(earningsClose)
        # print("periodPercentRaise")
        # print(periodPercentRaise)
        # print("periodPercentLoss")
        # print(periodPercentLoss)
        # print("Week high: ")
        # print(high)
        # print("high day")
        # print(highDayWk)
        # print("Week low: ")
        # print(low)
        # print("low day")
        # print(lowDayWk)
        
        endOfPeriodRatio = 0
        exchangeRatio = 0
        if(stocks[p][1] == 1):
            endOfPeriodRatio = 100 * ( endOfPeriodPrice - float(nextDayClose)) / float(nextDayClose)
            exchangeRatio = 100 * ( endOfPeriodExchangePrice - float(nextDayExchangeClose)) / float(nextDayExchangeClose)
        elif (stocks[p][1] == 0):
            endOfPeriodRatio = 100 * ( endOfPeriodPrice - float(earningsClose)) / float(earningsClose)
            exchangeRatio = 100 * ( endOfPeriodExchangePrice - float(earningsExchangeClose)) / float(earningsExchangeClose)
        if(ratio < 0):
            losses.append([ratio, periodPercentRaise, periodPercentLoss, highDayWk, lowDayWk, endOfPeriodRatio, exchangeRatio, endOfPeriodRatio - exchangeRatio])
        else:
            gains.append([ratio, periodPercentRaise, periodPercentLoss, highDayWk, lowDayWk, endOfPeriodRatio, exchangeRatio, endOfPeriodRatio - exchangeRatio])
    print(stocks[p][0])
    print('ratio, periodMaxPercentLoss / Raise, lowDayWk / highDayWk, endOfPeriodRatio, exchangeRatio, endOfperiodRatio - exchangeRatio')
    
    with open("Analysis.csv", 'a',  newline='') as file:
        writer = csv.writer(file, delimiter = ',', quotechar = '|', quoting = csv.QUOTE_MINIMAL)
        writer.writerow([stocks[p][0]])
        writer.writerow(['ratio', 'periodMaxPercentRaise', 'periodMaxPercentLoss', 'highDayWk', 'lowDayWk', 'endOfPeriodRatio', 'exchangeRatio', 'endOfperiodRatio - exchangeRatio'])
        print("losses")
        writer.writerow(["losses"])
        for k in range(len(losses)):
            print(losses[k])
            row = []
            for x in range(len(losses[k])):
                row.append(losses[k][x])
            writer.writerow(row)
            ','.join(str(x) for x in losses[k])
        print("gains")
        writer.writerow(["gains"])
        for k in range(len(gains)):
            print(gains[k])
            row = []
            for x in range(len(gains[k])):
                row.append(gains[k][x])
            writer.writerow(row)

        dayTot = 0
        for i in range(len(gains)):
            dayTot += gains[i][3]
        gainAveDay = dayTot * 1.0 / len(gains)
        dayTot = 0
        for i in range(len(losses)):
            dayTot += losses[i][4]
        lossAveDay = dayTot * 1.0 / len(losses)
        print("gainAveDay")
        print(str(gainAveDay))
        print("lossAveDay")
        print(str(lossAveDay))

        writer.writerow(["gainAveDay"])
        writer.writerow([str(gainAveDay)])
        writer.writerow(["lossAveDay"])
        writer.writerow([str(lossAveDay)])

        #ave profit from buying stock that gained and profit from buying stock that didn't gain
        totalGain = 0
        for i in range(len(gains)):
            totalGain += gains[i][7]
        aveGainGainers = totalGain * 1.0 / len(gains)
        totalGain = 0
        for i in range(len(losses)):
            totalGain += losses[i][7]
        aveGainlosers = totalGain * 1.0 / len(losses)
        print("aveGainGainers")
        print(str(aveGainGainers))
        print('aveGainlosers')
        print(str(aveGainlosers))
        writer.writerow(["aveGainGainers"])
        writer.writerow([str(aveGainGainers)])
        writer.writerow(['aveGainlosers'])
        writer.writerow([str(aveGainlosers)])






    # plt.show()
    #print(data)

    #print(data['annualEarnings'])