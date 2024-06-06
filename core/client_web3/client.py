import requests
from pycoingecko import CoinGeckoAPI
from web3 import Web3

from core.logger_config import logger

global last_tickers_prices
global last_market_data
global last_gas_price
last_tickers_prices = {"BTCUSDT": '', "ETHUSDT": '', 'BNBUSDT': '', 'SOLUSDT': '', "TONUSDT": ''}
last_market_data = {"market_cap_usd": '', "volume_24h_usd": '', "dominance_btc_percentage": '',
                    "dominance_eth_percentage": ''}
last_gas_price = ''


class Client:
    @staticmethod
    def get_tickers_prices(last_tickers_prices):
        tickers_prices = {"BTCUSDT": '', "ETHUSDT": '', 'BNBUSDT': '', 'SOLUSDT': '', "TONUSDT": ''}
        for symbol in tickers_prices:
            url = f"https://api.bybit.com/v2/public/tickers?symbol={symbol}"
            try:
                response = requests.get(url)
                data = response.json()

                if 'result' in data and len(data['result']) > 0:
                    tickers_prices[f"{symbol}"] = round(float(data['result'][0]['last_price']), 1)
                    if symbol == 'TONUSDT':
                        tickers_prices[f"{symbol}"] = round(float(data['result'][0]['last_price']), 2)
                else:
                    return None
            except Exception as e:
                tickers_prices[f"{symbol}"] = last_tickers_prices[f"{symbol}"]
                logger.info(f"{e} - Error in getting cryptocurrency [{symbol}] prices!")
        return tickers_prices

    @staticmethod
    def get_coin_gecko_data(last_market_data):
        try:
            cg = CoinGeckoAPI()
            data = cg.get_global()

            market_cap = data['total_market_cap']['usd']
            volume_24h = data['total_volume']['usd']
            dominance_btc = data['market_cap_percentage']['btc']
            dominance_eth = data['market_cap_percentage']['eth']
        except Exception as e:
            logger.info(f"{e} - Error in getting market info!")
            market_cap = last_market_data['total_market_cap']['usd']
            volume_24h = last_market_data['total_volume']['usd']
            dominance_btc = last_market_data['market_cap_percentage']['btc']
            dominance_eth = last_market_data['market_cap_percentage']['eth']

        return {
            'market_cap_usd': '%.3f' % (market_cap / 10 ** 12),
            'volume_24h_usd': '%.3f' % (volume_24h / 10 ** 9),
            'dominance_btc_percentage': '%.2f' % dominance_btc,
            'dominance_eth_percentage': '%.2f' % dominance_eth
        }

    @staticmethod
    def get_gas_price(last_gas_price):
        try:
            con_web3 = Web3(provider=Web3.HTTPProvider(endpoint_uri='https://rpc.ankr.com/eth'))
            gas = round(con_web3.eth.gas_price / 10 ** 9, 2)
        except Exception as e:
            gas = last_gas_price
            logger.info(f"{e} - Error in getting GAS price!")
        return gas

    @staticmethod
    def get_financial_data():
        market_data = Client.get_coin_gecko_data(last_market_data)
        gas = Client.get_gas_price(last_gas_price)
        prices = Client.get_tickers_prices(last_tickers_prices)
        financial_data = {'market_data': market_data, 'gas_price': gas, 'ticker_prices': prices}
        print(financial_data)
        return financial_data
