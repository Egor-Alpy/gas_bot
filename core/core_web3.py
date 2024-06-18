from web3 import Web3
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

