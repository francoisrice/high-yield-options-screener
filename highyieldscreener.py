# TODO: Create main function to pass in parameters
# TODO: Add progress bar to for loops

import os
import urllib.request
from openbb import obb
from priceprediction import PricePredictor

obb.account.login(pat=os.environ['OPENBB_KEY'])

def calculateShortPutYield(symbol, funds, predictionPrice):
    # Get the stocks option chain
    symbolData = obb.derivatives.options.chains(symbol=symbol, provider='cboe').to_df()
    
    # Only keep active short PUTS in the next 10 days with a good chance of profit that can be afforded
    symbolData = symbolData.query(f'option_type == "put" & dte <= 10 & dte > 0 & strike <= {funds/100} & strike <= {predictionPrice}').sort_values(by='strike', ascending=False)
    
    # Calculate the yield of each contract
    contracts = []
    for rowNumber in range(len(symbolData)):
        if symbolData.iloc[rowNumber]["bid"]/(symbolData.iloc[rowNumber]["strike"]) > 0.0:
            contracts.append([symbolData.iloc[rowNumber]["contract_symbol"], symbolData.iloc[rowNumber]["dte"], symbolData.iloc[rowNumber]["strike"], symbolData.iloc[rowNumber]["bid"]/(symbolData.iloc[rowNumber]["strike"]), symbolData.iloc[rowNumber]["bid_size"] ])
    
    return contracts

pp = PricePredictor()

# Refresh list of stocks
urllib.request.urlretrieve('ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt', 'files/nasdaqlisted.txt')
urllib.request.urlretrieve('ftp://ftp.nasdaqtrader.com/SymbolDirectory/otherlisted.txt', 'files/otherlisted.txt')

funds = 4000
probability = 0.3
daysToExp = 10

# Pull data into memory
contracts = []
with open('files/nasdaqlisted.txt') as nasdaqListed:
    nasdaq = nasdaqListed.read().splitlines()

    # Add progress bar
    for symbolLine in nasdaq:
    
        symbolLineData = symbolLine.split('|')
        if symbolLineData[3] == 'N': # Filter out Test Stocks
            try:
                # predictionPrice = priceprediction(symbolLine[0])
                predictionPrice = pp.calculate_safe_short_put_price(symbolLineData[0], probability, daysToExp)
            except Exception as e:
                print(e)
                raise Exception(f"Error with {symbolLineData[0]}")
            contracts += calculateShortPutYield(symbolLineData[0], funds, predictionPrice)
        print("Processed: "+symbolLineData[0])

with open('files/otherlisted.txt') as otherListed:
    other = otherListed.read().splitlines()
    for symbolLine in other:
        symbolLineData = symbolLine.split('|')
        if symbolLineData[6] == 'N': # Filter out Test Issues
            try:
                predictionPrice = pp.calculate_safe_short_put_price(symbolLineData[0], probability, daysToExp)
            except Exception as e: 
                print(e)
                raise Exception(f"Error with {symbolLineData[0]}")
            contracts += calculateShortPutYield(symbolLineData[0], funds, predictionPrice)
        print("Processed: "+symbolLineData[0])

# Sort contracts by descending yield
contracts.sort(key=lambda x:x[3],reverse=True)
# contracts = sorted(contracts, key=lambda x: x[3], reverse=True)

