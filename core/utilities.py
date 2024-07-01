from core.coingecko import Coingecko
from core.core_aiogram.bot_creation import bot
from core.database.database_main import table_users, table_channels
from core.logger_config import logger
from core.core_web3 import ClientWeb3
from data.config import ADMINS
from data.text import MSG


async def proxy_add_value(state, key, value):
    async with state.proxy() as data:
        data[key] = value


async def proxy_get_value(state, key):
    async with state.proxy() as data:
        return data[key]


async def proxy_get_all(state):
    async with state.proxy() as data:
        return data.as_dict()


async def check_user_subscriptions(user_id: int) -> bool:
    try:
        previous_subscription_status = table_users.get_subscription_status(user_id)
        channel_tags = table_channels.get_channel_tags()
        LAN = table_users.get_user_language(user_id)
        if not channel_tags:
            table_users.set_subscription_status('True', user_id)
            return True
        for channel_tag in channel_tags:
            try:
                user_channel_status = await bot.get_chat_member(chat_id='@' + channel_tag, user_id=user_id)
                if (user_channel_status['status'] not in ['creator', 'administrator', 'member'] and int(user_id) not
                        in ADMINS):
                    if previous_subscription_status == 'True':
                        await bot.send_message(chat_id=user_id, text=MSG[LAN]['SUB']['CLOSED'], parse_mode='markdown')
                    table_users.set_subscription_status('False', user_id)
                    return False
            except Exception as e:
                if str(e) == 'User not found':
                    logger.info(f'Bot does not have rights in [{channel_tag}] channel')
                else:
                    logger.info(f'Error in check user sub [{user_id}]: {e}')
                    return False
        if previous_subscription_status == 'False':
            await bot.send_message(chat_id=user_id, text=MSG[LAN]['SUB']['OPENED'], parse_mode='markdown')
            table_users.set_subscription_status('True', user_id)
        return True
    except Exception as e:
        logger.info(f'Error in the large-block of check user sub: {e}')


async def handle_system_message(error):
    logger.info(f"SYSTEM_MESSAGE: {error}")
    for user_id in ADMINS:
        await bot.send_message(chat_id=user_id, text=f"SYSTEM_MESSAGE: {error}")


def get_financial_data(last_market_data, last_gas_price, last_tickers_prices):
    market_data = Coingecko.get_coin_gecko_data(last_market_data)
    gas = ClientWeb3.get_gas_price(last_gas_price)
    prices = Coingecko.get_tickers_prices(last_tickers_prices)
    financial_data = {'market_data': market_data, 'gas_price': gas, 'ticker_prices': prices}
    return financial_data
