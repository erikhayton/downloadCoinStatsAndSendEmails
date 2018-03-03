# This script downloads the statistics of the top "numCoins" coins from coinmarketcap every "waitPeriod"
# and sends an email to "youremail".  
# In the email data is divided in newly found "numPerformers" best performers and "numPerformers" worse performers.
# Performance is measured as "percent_change_24h".

import coinmarketcap
import json
import pandas as pd
import datetime
import time
import smtplib
from email.mime.text import MIMEText
import sys

def sendEmail(Subject, text):
    msg = MIMEText(text)
    msg['From'] = "info"
    msg['To'] = "youremail"
    msg['Subject'] = Subject

    server = smtplib.SMTP('yoursmptserver')
    server.starttls()
    server.login("youremail", "yourpassword")
    err = server.sendmail("youremail", "youremail", msg.as_string())
    server.quit()

def cycleDownload():
    # Grabs all of the coin data available
    numCoins = 150
    numPerformers = 15
    waitPeriod = 60*60*3
    warmup = 0
    summaryFile = open("summary.txt", "w")
    dicBestPerformers ={}
    dicWorsePerformers = {}
    loopind=0

    # price_usd, price_btc, percent_change_24h, percent_change_1h
    while(1):
        # retrive data
        loopind = loopind + 1
        market = coinmarketcap.Market()
        coins = market.ticker(limit=numCoins)
        # this creates a dataframe with the top numCoins
        coinDataFrame = pd.DataFrame([pd.Series(coins[i]) for i in range(numCoins)]).set_index('id')
        coinDataFrame = coinDataFrame.apply(pd.to_numeric, errors='ignore')
        coinDataFrame = coinDataFrame.sort_values(by=['percent_change_24h'])
        currentTime = datetime.datetime.now().strftime("%Y,%m,%d,%H,%M")

        #----------------------------------------------------------------------------#
        #print top 10 worse performers:
        #----------------------------------------------------------------------------#
        stringSort ='worse,'+ currentTime
        newWorsePerformers = []
        for i in range(numPerformers):
            coinName = coinDataFrame.iloc[i].name
            coinUsdPrice=coinDataFrame.iloc[i]['price_usd']
            coinPercentageChange=coinDataFrame.iloc[i]['percent_change_24h']
            coinHourPercentageChange = coinDataFrame.iloc[i]['percent_change_1h']
            stringSort = stringSort + ',' + \
                         coinName + ',' + \
                         str(coinPercentageChange)+ ',' +\
                         str(coinUsdPrice)
            if (coinName not in dicWorsePerformers and loopind>warmup):
                print("New worse performer found", coinName,coinPercentageChange, coinPercentageChange)
                newWorsePerformers.append([coinName,coinPercentageChange, coinHourPercentageChange, coinUsdPrice])

            dicWorsePerformers[coinName] = coinUsdPrice

        # print ot console worse performers
        print(stringSort)
        summaryFile.write(stringSort+'\n')
        summaryFile.flush()

        #----------------------------------------------------------------------------#
        #print top 10 best performers
        #----------------------------------------------------------------------------#
        stringSort='best,'+ currentTime
        newBestPerformers=[]
        for i in range(numCoins-1,numCoins-numPerformers-1, -1):
            coinName = coinDataFrame.iloc[i].name
            coinUsdPrice=coinDataFrame.iloc[i]['price_usd']
            coinPercentageChange=coinDataFrame.iloc[i]['percent_change_24h']
            coinHourPercentageChange = coinDataFrame.iloc[i]['percent_change_1h']
            stringSort = stringSort + ',' + \
                         coinName + ',' + \
                         str(coinPercentageChange)+ ',' +\
                         str(coinUsdPrice)
            if (coinName not in dicBestPerformers and loopind>warmup):
                print("New best performer found ", coinName, coinPercentageChange, coinPercentageChange)
                newBestPerformers.append([coinName,coinPercentageChange, coinHourPercentageChange, coinUsdPrice])

            dicBestPerformers[coinName] = coinUsdPrice

        # print ot console best performers
        print(stringSort)
        summaryFile.write(stringSort+'\n')
        summaryFile.flush()

        #----------------------------------------------------------------------------#
        # send an email with the stats
        #----------------------------------------------------------------------------#
        #send email with the best performes
        text=''
        if(newBestPerformers):
            text ='The new best performers are (name, 24%, 1%, price Usd)'+ '\n'
            newBestPerformers.sort(key = lambda l: (l[2], l[1]))
            for coin in newBestPerformers:
                text = text+ \
                       ' ' + str(coin[0]) +  \
                       ' ' + str(coin[1]) + \
                       ' ' + str(coin[2]) + \
                       ' ' + str(coin[3]) + '\n'
        #send email with the worse performes
        if (newWorsePerformers):
            text = text + '\n' + 'The new worse performers are (name, 24%, 1%, price Usd)'+ '\n'
            newWorsePerformers.sort(key=lambda l: (l[2], l[1]))
            for coin in newWorsePerformers:
                text = text+ \
                       ' ' + str(coin[0]) +  \
                       ' ' + str(coin[1]) + \
                       ' ' + str(coin[2]) + \
                       ' ' + str(coin[3]) + '\n'

        if(text):
            sendEmail("Market check", text)

        # timestamps and stores the csv file
        currentTimeFile = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
        coinDataFrame.to_csv(str(currentTimeFile) + '.csv')
        coinDataFrame.to_pickle(str(currentTimeFile) + '.pkl')

        # waits an hour until collecting data again
        time.sleep(waitPeriod)

    summaryFile.close()
        
        
if __name__ == '__main__':
	cycleDownload()