#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import krakenex
import pandas as pd
import time

def get_api_credentials(): #Prompt to enter required API keys
    api_key = input("Enter your Kraken API Key: ")
    api_secret = input("Enter your Kraken Private Key: ")
    return api_key, api_secret

def get_holdings(api): #determines current holdings
    response = api.query_private('Balance')
    if response.get('error'): #error handling
        raise Exception(response['error'])
    return response['result']

def get_market_data(api, pair): #retrieves market data
    response = api.query_public('OHLC', {'pair': pair, 'interval': 5}) #sets ihe interval to 5 minutes, time interval options are 1, 5, 15, 30, 60, 240, 1440, 10080, and 21600 minutes
    if response.get('error'): #error handling
        raise Exception(response['error'])
    return pd.DataFrame(response['result'][pair], columns=['time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'])

#Calculates moving averages
#based on time intervals, default is 12 and 26 time intervals (MACD Indicator)
#length of time interval determined above
def calculate_moving_averages(df, short_window=12, long_window=26):
    df['short_mavg'] = df['close'].astype(float).rolling(window=short_window).mean()
    df['long_mavg'] = df['close'].astype(float).rolling(window=long_window).mean()
    return df

def analyze_assets(api, holdings, pairs, min_order_sizes, usd_balance):
    sell_assets = []
    buy_candidates = {}
    affordable_assets = []

    amount_per_asset = (usd_balance / 4) * 0.95 #95% to account for some losses from transaction fees. Divides by 4 to diversify into up to 4 other currencies

    for pair in pairs:
        data = get_market_data(api, pair)
        df = calculate_moving_averages(data)
        current_price = float(df['close'].iloc[-1])

        # Adjusted sell criteria, 1.05 increases the threshhold by 5% to encourage the program to only make trades with slightly higher profit potential
        if (df['short_mavg'].iloc[-1] < df['long_mavg'].iloc[-1] * 1.05) and pair in holdings:
            sell_assets.append(pair)

        # Adjusted buy criteria, 1.05 for the same reasons as above
        min_order_size = float(min_order_sizes.get(pair, 1))
        if (df['short_mavg'].iloc[-1] > df['long_mavg'].iloc[-1] * 1.05) and amount_per_asset >= current_price * min_order_size:
            buy_candidates[pair] = current_price
            affordable_assets.append(pair)

    selected_assets = sorted(affordable_assets, key=lambda x: buy_candidates[x], reverse=True)[:4]
    return sell_assets, selected_assets
#everything from here down was written drunk, i dont even entirely know what i was thinking, prepare for cryptic comments, sorry
def execute_trades(api, sell_assets, buy_assets, holdings, min_order_sizes): #executes trade orders
    for asset in sell_assets:
        volume = float(holdings.get(asset.split(':')[1], 0))
        if volume > 0:
            print(f"Selling {volume} of {asset}")
            response = api.query_private('AddOrder', {
                'pair': asset, 
                'type': 'sell', 
                'ordertype': 'market', 
                'volume': str(volume)
            })
            print(response)

    time.sleep(30) #30 second delay to allow the balance to update

    updated_holdings = get_holdings(api)
    usd_balance = float(updated_holdings.get('ZUSD', 0))

    num_assets_to_buy = len(buy_assets) if buy_assets else 1
    amount_per_asset = (usd_balance / num_assets_to_buy) * 0.95

    for asset in buy_assets:
        market_price = float(get_market_data(api, asset)['close'].iloc[-1])
        volume = amount_per_asset / market_price
        formatted_volume = "{:.8f}".format(volume)

        if volume >= min_order_sizes.get(asset, 1):
            print(f"Buying {formatted_volume} of {asset}")
            response = api.query_private('AddOrder', {
                'pair': asset, 
                'type': 'buy', 
                'ordertype': 'market', 
                'volume': formatted_volume
            })
            print(response)
        else:
            print(f"Volume {formatted_volume} for {asset} is below minimum threshold.")

def main():
    api_key, api_secret = get_api_credentials()
    api = krakenex.API(key=api_key, secret=api_secret)
#see readme
    min_order_sizes = {
        '1INCHUSD': 20,
        'AAVEUSD': 0.07,
        'ACAUSD': 100,
        'ACHUSD': 330,
        'ADAUSD': 20,
        'ADXUSD': 40,
        'AGLDUSD': 9,
        'AIRUSD': 860,
        'AKTUSD': 6,
        'ALCXUSD': 0.4,
        'ALGOUSD': 50,
        'ALICEUSD': 7,
        'ALPHAUSD': 70,
        'ANKRUSD': 250,
        'ANTUSD': 1,
        'APEUSD': 4,
        'API3USD': 5,
        'APTUSD': 1,
        'ARBUSD': 5,
        'ARPAUSD': 110,
        'ASTRUSD': 100,
        'ATLASUSD': 3350,
        'ATOMUSD': 0.7,
        'AUDIOUSD': 30,
        'AUDUSD': 10,
        'AVAXUSD': 0.5,
        'AXSUSD': 1,
        'BADGERUSD': 2,
        'BALUSD': 2.5,
        'BANDUSD': 4,
        'BATUSD': 30,
        'BCHUSD': 0.025,
        'BICOUSD': 20,
        'BITUSD': 12,
        'BLURUSD': 30,
        'BLZUSD': 35,
        'BNCUSD': 25,
        'BNTUSD': 12,
        'BOBAUSD': 40,
        'BONDUSD': 2,
        'BRICKUSD': 50,
        'BSXUSD': 70000,
        'BTTUSD': 13000000,
        'C98USD': 30,
        'CELRUSD': 420,
        'CFGUSD': 15,
        'CHRUSD': 50,
        'CHZUSD': 80,
        'COMPUSD': 0.1,
        'COTIUSD': 120,
        'CQTUSD': 45,
        'CRVUSD': 10,
        'CSMUSD': 800,
        'CTSIUSD': 40,
        'CVCUSD': 60,
        'CVXUSD': 1.5,
        'DAIUSD': 5,
        'DASHUSD': 0.2,
        'DENTUSD': 7000,
        'DOTUSD': 1.2,
        'DYDXUSD': 2.5,
        'EGLDUSD': 0.2,
        'ENJUSD': 20,
        'ENSUSD': 0.6,
        'EOSUSD': 10,
        'ETHPYUSD': 0.01,
        'ETHWUSD': 4,
        'EULUSD': 2,
        'EURTUSD': 5,
        'EWTUSD': 3,
        'FARMUSD': 0.2,
        'FETUSD': 20,
        'FIDAUSD': 30,
        'FILUSD': 1.5,
        'FISUSD': 20,
        'FLOWUSD': 10,
        'FLRUSD': 450,
        'FORTHUSD': 2,
        'FTMUSD': 25,
        'FXSUSD': 1,
        'GALAUSD': 330,
        'GALUSD': 4,
        'GARIUSD': 140,
        'GHSTUSD': 7,
        'GLMRUSD': 25,
        'GMTUSD': 30,
        'GMXUSD': 0.13,
        'GNOUSD': 0.05,
        'GRTUSD': 60,
        'GSTUSD': 550,
        'GTCUSD': 5,
        'HDXUSD': 1100,
        'HFTUSD': 15,
        'ICPUSD': 1.5,
        'ICXUSD': 30,
        'IDEXUSD': 100,
        'IMXUSD': 10,
        'INJUSD': 0.7,
        'INTRUSD': 410,
        'JASMYUSD': 1500,
        'JUNOUSD': 30,
        'KARUSD': 70,
        'KAVAUSD': 8,
        'KEEPUSD': 60,
        'KEYUSD': 960,
        'KILTUSD': 10,
        'KINTUSD': 15,
        'KINUSD': 400000,
        'KNCUSD': 7,
        'KP3RUSD': 0.1,
        'KSMUSD': 0.3,
        'LCXUSD': 130,
        'LDOUSD': 3,
        'LINKUSD': 0.7,
        'LMWRUSD': 50,
        'LPTUSD': 0.8,
        'LRCUSD': 30,
        'LSKUSD': 7,
        'LUNA2USD': 12,
        'LUNAUSD': 80000,
        'MANAUSD': 17,
        'MASKUSD': 2,
        'MATICUSD': 9,
        'MCUSD': 15,
        'MINAUSD': 13,
        'MIRUSD': 350,
        'MKRUSD': 0.0035,
        'MNGOUSD': 350,
        'MOONUSD': 20,
        'MOVRUSD': 1.2,
        'MSOLUSD': 0.2,
        'MULTIUSD': 3,
        'MVUSD': 140,
        'MXCUSD': 640,
        'NANOUSD': 8,
        'NEARUSD': 4,
        'NMRUSD': 0.4,
        'NODLUSD': 1700,
        'NYMUSD': 45,
        'OCEANUSD': 16,
        'OGNUSD': 40,
        'OMGUSD': 10,
        'OPUSD': 4,
        'ORCAUSD': 6,
        'OXTUSD': 70,
        'OXYUSD': 350,
        'PARAUSD': 100,
        'PAXGUSD': 0.003,
        'PEPEUSD': 6000000,
        'PERPUSD': 9,
        'PHAUSD': 50,
        'PLAUSD': 30,
        'POLISUSD': 40,
        'POLSUSD': 18,
        'PONDUSD': 600,
        'POWRUSD': 30,
        'PSTAKEUSD': 190,
        'PYTHUSD': 10,
        'PYUSDUSD': 5,
        'QNTUSD': 0.05,
        'QTUMUSD': 2.5,
        'RADUSD': 4,
        'RAREUSD': 80,
        'RARIUSD': 5,
        'RAYUSD': 30,
        'RBCUSD': 440,
        'RENUSD': 110,
        'REPV2USD': 10,
        'REQUSD': 80,
        'RLCUSD': 5,
        'RNDRUSD': 3,
        'ROOKUSD': 10,
        'RPLUSD': 0.25,
        'RUNEUSD': 2.5,
        'SAMOUSD': 1500,
        'SANDUSD': 16,
        'SBRUSD': 6000,
        'SCRTUSD': 20,
        'SCUSD': 1600,
        'SDNUSD': 30,
        'SEIUSD': 50,
        'SGBUSD': 1250,
        'SHIBUSD': 700000,
        'SNXUSD': 2.5,
        'SOLUSD': 0.2,
        'SPELLUSD': 10200,
        'SRMUSD': 130,
        'STEPUSD': 325,
        'STGUSD': 10,
        'STORJUSD': 10,
        'STXUSD': 10,
        'SUIUSD': 10,
        'SUPERUSD': 60,
        'SUSHIUSD': 8,
        'SYNUSD': 15,
        'TBTCUSD': 0.00025,
        'TEERUSD': 30,
        'TIAUSD': 3,
        'TLMUSD': 480,
        'TOKEUSD': 15,
        'TRUUSD': 140,
        'TRXUSD': 60,
        'TUSD': 270,
        'TUSDUSD': 5,
        'TVKUSD': 250,
        'UMAUSD': 4,
        'UNFIUSD': 0.7,
        'UNIUSD': 1,
        'USDCUSD': 5,
        'USDTZUSD': 10,
        'USTUSD': 175,
        'WAVESUSD': 3,
        'WAXLUSD': 15,
        'WBTCUSD': 0.00025,
        'WOOUSD': 25,
        'XBTPYUSD': 0.0001,
        'XCNUSD': 6500,
        'XDGUSD': 80,
        'XETCZUSD': 0.3,
        'XETHZUSD': 0.01,
        'XLTCZUSD': 0.08,
        'XMLNZUSD': 0.3,
        'XREPZUSD': 1.5,
        'XRTUSD': 3,
        'XTZUSD': 7,
        'XXBTZUSD': 0.0001,
        'XXLMZUSD': 40,
        'XXMRZUSD': 0.035,
        'XXRPZUSD': 10,
        'XZECZUSD': 0.2,
        'YFIUSD': 0.001,
        'YGGUSD': 20,
        'ZEURZUSD': 0.5,
        'ZGBPZUSD': 5,
        'ZRXUSD': 20
    
        # Example minimum order size
        # Add other pairs and their minimums here
    }

    pairs = [
                '1INCHUSD',
                'AAVEUSD',
                'ACAUSD',
                'ACHUSD',
                'ADAUSD',
                'ADXUSD',
                'AGLDUSD',
                'AIRUSD',
                'AKTUSD',
                'ALCXUSD',
                'ALGOUSD',
                'ALICEUSD',
                'ALPHAUSD',
                'ANKRUSD',
                'ANTUSD',
                'APEUSD',
                'API3USD',
                'APTUSD',
                'ARBUSD',
                'ARPAUSD',
                'ASTRUSD',
                'ATLASUSD',
                'ATOMUSD',
                'AUDIOUSD',
                'AUDUSD',
                'AVAXUSD',
                'AXSUSD',
                'BADGERUSD',
                'BALUSD',
                'BANDUSD',
                'BATUSD',
                'BCHUSD',
                'BICOUSD',
                'BITUSD',
                'BLURUSD',
                'BLZUSD',
                'BNCUSD',
                'BNTUSD',
                'BOBAUSD',
                'BONDUSD',
                'BRICKUSD',
                'BSXUSD',
                'BTTUSD',
                'C98USD',
                'CELRUSD',
                'CFGUSD',
                'CHRUSD',
                'CHZUSD',
                'COMPUSD',
                'COTIUSD',
                'CQTUSD',
                'CRVUSD',
                'CSMUSD',
                'CTSIUSD',
                'CVCUSD',
                'CVXUSD',
                'DAIUSD',
                'DASHUSD',
                'DENTUSD',
                'DOTUSD',
                'DYDXUSD',
                'EGLDUSD',
                'ENJUSD',
                'ENSUSD',
                'EOSUSD',
                'ETHPYUSD',
                'ETHWUSD',
                'EULUSD',
                'EURTUSD',
                'EWTUSD',
                'FARMUSD',
                'FETUSD',
                'FIDAUSD',
                'FILUSD',
                'FISUSD',
                'FLOWUSD',
                'FLRUSD',
                'FORTHUSD',
                'FTMUSD',
                'FXSUSD',
                'GALAUSD',
                'GALUSD',
                'GARIUSD',
                'GHSTUSD',
                'GLMRUSD',
                'GMTUSD',
                'GMXUSD',
                'GNOUSD',
                'GRTUSD',
                'GSTUSD',
                'GTCUSD',
                'HDXUSD',
                'HFTUSD',
                'ICPUSD',
                'ICXUSD',
                'IDEXUSD',
                'IMXUSD',
                'INJUSD',
                'INTRUSD',
                'JASMYUSD',
                'JUNOUSD',
                'KARUSD',
                'KAVAUSD',
                'KEEPUSD',
                'KEYUSD',
                'KILTUSD',
                'KINTUSD',
                'KINUSD',
                'KNCUSD',
                'KP3RUSD',
                'KSMUSD',
                'LCXUSD',
                'LDOUSD',
                'LINKUSD',
                'LMWRUSD',
                'LPTUSD',
                'LRCUSD',
                'LSKUSD',
                'LUNA2USD',
                'LUNAUSD',
                'MANAUSD',
                'MASKUSD',
                'MATICUSD',
                'MCUSD',
                'MINAUSD',
                'MIRUSD',
                'MKRUSD',
                'MNGOUSD',
                'MOONUSD',
                'MOVRUSD',
                'MSOLUSD',
                'MULTIUSD',
                'MVUSD',
                'MXCUSD',
                'NANOUSD',
                'NEARUSD',
                'NMRUSD',
                'NODLUSD',
                'NYMUSD',
                'OCEANUSD',
                'OGNUSD',
                'OMGUSD',
                'OPUSD',
                'ORCAUSD',
                'OXTUSD',
                'OXYUSD',
                'PARAUSD',
                'PAXGUSD',
                'PEPEUSD',
                'PERPUSD',
                'PHAUSD',
                'PLAUSD',
                'POLISUSD',
                'POLSUSD',
                'PONDUSD',
                'POWRUSD',
                'PSTAKEUSD',
                'PYTHUSD',
                'PYUSDUSD',
                'QNTUSD',
                'QTUMUSD',
                'RADUSD',
                'RAREUSD',
                'RARIUSD',
                'RAYUSD',
                'RBCUSD',
                'RENUSD',
                'REPV2USD',
                'REQUSD',
                'RLCUSD',
                'RNDRUSD',
                'ROOKUSD',
                'RPLUSD',
                'RUNEUSD',
                'SAMOUSD',
                'SANDUSD',
                'SBRUSD',
                'SCRTUSD',
                'SCUSD',
                'SDNUSD',
                'SEIUSD',
                'SGBUSD',
                'SHIBUSD',
                'SNXUSD',
                'SOLUSD',
                'SPELLUSD',
                'SRMUSD',
                'STEPUSD',
                'STGUSD',
                'STORJUSD',
                'STXUSD',
                'SUIUSD',
                'SUPERUSD',
                'SUSHIUSD',
                'SYNUSD',
                'TBTCUSD',
                'TEERUSD',
                'TIAUSD',
                'TLMUSD',
                'TOKEUSD',
                'TRUUSD',
                'TRXUSD',
                'TUSD',
                'TUSDUSD',
                'TVKUSD',
                'UMAUSD',
                'UNFIUSD',
                'UNIUSD',
                'USDCUSD',
                'USDTZUSD',
                'USTUSD',
                'WAVESUSD',
                'WAXLUSD',
                'WBTCUSD',
                'WOOUSD',
                'XBTPYUSD',
                'XCNUSD',
                'XDGUSD',
                'XETCZUSD',
                'XETHZUSD',
                'XLTCZUSD',
                'XMLNZUSD',
                'XREPZUSD',
                'XRTUSD',
                'XTZUSD',
                'XXBTZUSD',
                'XXLMZUSD',
                'XXMRZUSD',
                'XXRPZUSD',
                'XZECZUSD',
                'YFIUSD',
                'YGGUSD',
                'ZEURZUSD',
                'ZGBPZUSD',
                'ZRXUSD'     
            ]

    try:
        while True:
            holdings = get_holdings(api)
            usd_balance = float(holdings.get('ZUSD', 0))
            sell_assets, buy_assets = analyze_assets(api, holdings, pairs, min_order_sizes, usd_balance)
            
            trades_executed = False

            if sell_assets or buy_assets:
                execute_trades(api, sell_assets, buy_assets, holdings, min_order_sizes)
                trades_executed = True

            if not trades_executed:
                print("No trades made")
            
            time.sleep(300)
    except Exception as e:
        print(f"An error occurred in main: {e}")

if __name__ == "__main__":
    main()

