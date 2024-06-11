from web3 import Web3
from core.client_web3.coingecko import Coingecko
from core.logger_config import logger


class ClientWeb3:
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
    def get_financial_data(last_market_data, last_gas_price, last_tickers_prices):
        market_data = Coingecko.get_coin_gecko_data(last_market_data)
        gas = ClientWeb3.get_gas_price(last_gas_price)
        prices = Coingecko.get_tickers_prices(last_tickers_prices)
        financial_data = {'market_data': market_data, 'gas_price': gas, 'ticker_prices': prices}
        print(financial_data)
        return financial_data
