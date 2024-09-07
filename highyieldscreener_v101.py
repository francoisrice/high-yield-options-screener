# TO-ADD: Attach assignment probability of each strike to the contract entry in contracts list
# ---> Highest "true yield" is yield * (1 - probability)

import sys
import os
from datetime import date
import time

import urllib.request
from tqdm import tqdm

from openbb import obb
from priceprediction import PricePredictor

obb.account.login(pat=os.environ['OPENBB_KEY'])

pp = PricePredictor()

def calculateShortPutYield(symbol, funds, predictionPrice):
    # Get the stocks option chain
    symbolData = obb.derivatives.options.chains(symbol=symbol, provider='cboe').to_df()
    
    # Only keep active short PUTS in the next 10 days with a good chance of profit that can be afforded
    symbolData = symbolData.query(f'option_type == "put" & dte <= 10 & dte > 0 & strike <= {funds/100} & strike <= {predictionPrice}').sort_values(by='strike', ascending=False)
    
    # Calculate the yield of each contract
    contracts = []
    for rowNumber in range(len(symbolData)):
        if symbolData.iloc[rowNumber]["bid"]/(symbolData.iloc[rowNumber]["strike"]) > 0.001:
            if os.environ["LIKELY_YIELD"]:
                probability = pp.
                contracts.append([symbolData.iloc[rowNumber]["contract_symbol"], "DTE: "+str(symbolData.iloc[rowNumber]["dte"]), "Strike Price: "+str(symbolData.iloc[rowNumber]["strike"]), "Yield: "+str(symbolData.iloc[rowNumber]["bid"]/(symbolData.iloc[rowNumber]["strike"])), "Probability: "+str(1-probability), "Likely Yield: "+str(symbolData.iloc[rowNumber]["bid"]/(symbolData.iloc[rowNumber]["strike"])*(1-probability)), "Size Available: "+str(symbolData.iloc[rowNumber]["bid_size"]) ])
            else:
            # symbolStrikeProbability = pp.calculate_price_probability(symbol, symbolData.iloc[rowNumber]["strike"], daysToExp)
            # # ?? - obb.derivatives.options.probability(symbol=symbol, strike=symbolData.iloc[rowNumber]["strike"], dte=symbolData.iloc[rowNumber]["dte"], option_type='put')
                contracts.append([symbolData.iloc[rowNumber]["contract_symbol"], "DTE: "+str(symbolData.iloc[rowNumber]["dte"]), "Strike Price: "+str(symbolData.iloc[rowNumber]["strike"]), "Yield: "+str(symbolData.iloc[rowNumber]["bid"]/(symbolData.iloc[rowNumber]["strike"])), "Size Available: "+str(symbolData.iloc[rowNumber]["bid_size"]) ])
            # contracts.append([symbolData.iloc[rowNumber]["contract_symbol"], "DTE: "+str(symbolData.iloc[rowNumber]["dte"]), "Strike Price: "+str(symbolData.iloc[rowNumber]["strike"]), "Yield: "+str(symbolData.iloc[rowNumber]["bid"]/(symbolData.iloc[rowNumber]["strike"])), "Likely Yield: "+str(symbolData.iloc[rowNumber]["bid"]/(symbolData.iloc[rowNumber]["strike"])*(1-symbolStrikeProbability)) , "Size Available: "+str(symbolData.iloc[rowNumber]["bid_size"]) ])
    
    return contracts

def create_sorted_yield_list(funds, probability, daysToExp):
    # Refresh list of stocks
    urllib.request.urlretrieve('ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt', 'files/nasdaqlisted.txt')
    urllib.request.urlretrieve('ftp://ftp.nasdaqtrader.com/SymbolDirectory/otherlisted.txt', 'files/otherlisted.txt')

    # Pull data into memory
    contracts = []
    with open('files/nasdaqlisted.txt') as nasdaqListed:
        nasdaq = nasdaqListed.read().splitlines()

        # Short List testing
        # nasdaq = ['GOOG','MARA','NIO','NVDA','AAPL','TSLA','AMZN','MSFT','AMD','BABA','FB','NFLX','PYPL','SQ','SOFI','SNAP','UBER']
        # nasdaq = ['MARA','NIO','BYND','SOFI','CLSK']
        #####

        for symbolLine in tqdm(nasdaq):
        
            symbolLineData = symbolLine.split('|')
            if symbolLineData[3] == 'N': # Filter out Test Stocks
                try:
                    # predictionPrice = priceprediction(symbolLine[0])
                    predictionPrice = pp.calculate_safe_short_put_price(symbolLineData[0], probability, daysToExp)
                    contracts += calculateShortPutYield(symbolLineData[0], funds, predictionPrice)
                except Exception as e:
                    print(e, "Error with: "+symbolLineData[0])
                    continue
            print("Processed: "+symbolLineData[0])

    with open('files/otherlisted.txt') as otherListed:
        other = otherListed.read().splitlines()
        for symbolLine in tqdm(other):
            symbolLineData = symbolLine.split('|')
            if symbolLineData[6] == 'N': # Filter out Test Issues
                try:
                    predictionPrice = pp.calculate_safe_short_put_price(symbolLineData[0], probability, daysToExp)
                    contracts += calculateShortPutYield(symbolLineData[0], funds, predictionPrice)
                except Exception as e: 
                    print(e, "Error with: "+symbolLineData[0])
                    continue
            print("Processed: "+symbolLineData[0])

    # Sort contracts by descending yield
    if os.environ["LIKELY_YIELD"]:
        contracts.sort(key=lambda x:x[5],reverse=True)
    else:
        contracts.sort(key=lambda x:x[3],reverse=True)

    with open(f'files/contracts_{date.today()}_{str(funds)}_{str(probability)}_{str(daysToExp)}.txt', 'w') as f:
        for contract in contracts:
            f.write(f"{contract}\n")

    return contracts

if __name__ == '__main__':
    args = sys.argv
    print(args)
    start = time.time()

    funds = args[1]
    probability = args[2]
    daysToExp = args[3]

    create_sorted_yield_list(int(funds), float(probability), int(daysToExp))
    end = time.time()
    print(f"Total processing time: {end-start} seconds")