#import modules
import requests
import json

from datetime import datetime
import time

# constants marking report out
NUMBER_CRYPTOCURRENCIES = 100
CURRENCY = 'USD'
TIME = 1440 #minutes of cycle (24h)

class Bot:
    def __init__(self):
        self.url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        self.params = {
            'start': 1,
            'limit': NUMBER_CRYPTOCURRENCIES,
            'convert': CURRENCY
        }
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': 'acaa2fac-67e2-40cc-8612-33c27b3d7c3d'
        }
    #obtain data on cryptocurrencies from CoinMarketCap
    def fetchCurrenciesData(self):
        r = requests.get(url = self.url, headers = self.headers, params = self.params).json()
        return r['data']

###define functions to get specific information:

#cryptocurrency with the highest volume in last 24h
def getHighestVolume(currencies):

    volume24 = []
    for currency in currencies:
        volume = currency['quote']['USD']['volume_24h']
        name = currency['name']
        volume24.append({'name': name,
                          'volume' : volume})

    #method to sort cryptocurrencies
    def sortMethod(currency):
        return currency['volume']

    volume24.sort(reverse = True, key = sortMethod)

    name = volume24[0]['name']
    volume = volume24[0]['volume']
    print(f'The cryptocurrency reached the highest volume in last 24h is {name} with ${volume}\n')

    return volume24[0]

#the best and the worst ten cryptocurrencies for percent increment in last 24h
def getBestWorstCurrencies(currencies):

    percentChange24 = []
    for currency in currencies:
        percentChange = currency['quote']['USD']['percent_change_24h']
        name = currency['name']
        percentChange24.append({'name' : name,
                                  'percent_change_24h' : percentChange})

    # method to sort cryptocurrencies
    def sortMethod(currency):
        return currency['percent_change_24h']

    percentChange24.sort(reverse = True, key = sortMethod)

    bestCurrencies = [currency['name'] for currency in percentChange24[:10]]
    worstCurrencies = [currency['name'] for currency in percentChange24[-10:]]

    print(f'The best cryptocurrencies in last 24h: {*bestCurrencies,} \nand the worst: {*worstCurrencies,}\n')

    return bestCurrencies, worstCurrencies

#money needed to buy a unit of each first twenty cryptocurrencies
def amountFirstTwentyCrypto(currencies):
    currenciesName = []
    amountNeeded = 0
    for currency in currencies[:20]:
        price = currency['quote']['USD']['price']
        amountNeeded += price

        name = currency['name']
        currenciesName.append(name)

    print(f'Money needed to buy a unit of each first twenty cryptocurrencies: ${amountNeeded}\n')

    return amountNeeded, currenciesName

#money needed to buy a unit of crytpocurrencies with volume's higher than $76000000
def amountCryptoForSpecificVolume(currencies, volume = 76000000):

    amount = 0
    for currency in currencies:
        if currency['quote']['USD']['volume_24h'] > volume:
            price = currency['quote']['USD']['price']
            amount += price

    print(f'Money needed to buy a unit of crytpocurrencies with volume\'s higher than $76000000: ${amount}\n')

    return amount

#percentage of profit or loss if I had bought a unit of all first twenty cryptocurrencies yesterday
def percentageProfitOrLoss(amountFistTwenty, currenciesName):
    amount = 0
    for currency in currencies:
        if currency['name'] in currenciesName:
            percentChange = currency['quote']['USD']['percent_change_24h']
            priceNow = currency['quote']['USD']['price']
            priceYesterday = abs(((priceNow*100)/(percentChange+100)))
            amount += priceYesterday

    profitOrLoss = ((amountFistTwenty-amount)/(amountFistTwenty+amount))
    print(f'Percentage of profit or loss if I had bought a unit of all first twenty cryptocurrencies yesterday: {profitOrLoss:.2f}%\n')

    return f'{profitOrLoss:.2f}%'




running = True
while(running):

    start = input('Would you like to start a continuous 24h report on cryptocurrencies? (y/n)\n')

    if start.upper() == 'Y':

        reporting = True
        while(reporting):

            now = datetime.now()
            timeNow = now.strftime("%c")
            print(f'Process started {timeNow}\n')
            print('Results:\n')
            #obtain data
            bot = Bot()
            currencies = bot.fetchCurrenciesData()

            #obtain specific information
            volume = getHighestVolume(currencies)
            best, worst = getBestWorstCurrencies(currencies)
            amountFirstTwenty, currenciesName = amountFirstTwentyCrypto(currencies)
            amountSpecificVolume = amountCryptoForSpecificVolume(currencies)
            percentChange = percentageProfitOrLoss(amountFirstTwenty, currenciesName)

            report = {
                'timestamp': timeNow,
                'Cryptocurrency with highest volume in last 24h' : volume,
                'Best and worst cryptocurrencies' : [best, worst],
                'Money to buy a unit of first twenty cryptocurrencies' : amountFirstTwenty,
                'Money to buy a unit of cryptocurrencies with a volume of more than 76000000$' : amountSpecificVolume,
                'Percentage of profit or loss' : percentChange
            }

            #write a json file
            todayDate = datetime.strftime(now, '%d-%m-%Y')
            filename = f'report_{todayDate}.json'

            with open(filename, 'w') as outfile:
                json.dump(report, outfile, indent = 4)

            print('Report successfully saved!')
            print(f'Waiting for {TIME/60} hours before next report...')

            #get a report each 24h
            minutes = TIME
            seconds = 60 * minutes
            time.sleep(seconds)

    elif start.upper() == 'N':
        print('Goodbye, have a nice day!')
        running = False

    else:
        print('This value is not allowed!\n')