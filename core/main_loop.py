import asyncio
from datetime import timezone, timedelta, datetime

from core.client_web3.client_web3 import ClientWeb3
from core.core_aiogram.bot_creation import bot
from core.core_aiogram.commands.client import check_user_subscriptions
from core.database.database_main import table_users
from data.text import get_msg_gas_price



last_tickers_prices = {"BTCUSDT": '', "ETHUSDT": '', 'BNBUSDT': '', 'SOLUSDT': '', "TONUSDT": ''}
last_market_data = {"market_cap_usd": '', "volume_24h_usd": '', "dominance_btc_percentage": '',
                    "dominance_eth_percentage": ''}
last_gas_price = ''


# Бесконечный цикл рассылки сообщений о цене Газа в ETH
async def start_sending():
    global last_tickers_prices
    global last_market_data
    global last_gas_price
    while True:
        list_of_tasks = []

        seconds_since_start_of_day = await get_current_time()
        financial_data = ClientWeb3.get_financial_data(last_market_data, last_gas_price, last_tickers_prices)
        rus_msg = get_msg_gas_price(LAN='RUS', financial_data=financial_data)
        eng_msg = get_msg_gas_price(LAN='ENG', financial_data=financial_data)

        for user_id in table_users.get_user_id_by_time(time=seconds_since_start_of_day):
            '''if not await check_user_subscriptions(user_id):
                pass'''
            if True: # else
                user_interval = table_users.get_user_interval(user_id)
                if user_interval != 'None':
                    LAN = table_users.get_user_language(user_id)
                    if LAN == 'ENG':
                        list_of_tasks.append(asyncio.create_task(send_message_to_user(user_id, eng_msg)))
                    elif LAN == 'RUS':
                        list_of_tasks.append(asyncio.create_task(send_message_to_user(user_id, rus_msg)))
        last_tickers_prices = financial_data['ticker_prices']
        last_market_data = financial_data['market_data']
        last_gas_price = financial_data['gas_price']
        await waiting_for_sending_messages()
        if list_of_tasks:
            await asyncio.wait(list_of_tasks, timeout=2)
        print(list_of_tasks)
        print('task completeeeed !!!!!!!!!!!!!!!!!!!!!!!!! !!!!!!!!!!!!!! !!!!!!!!!!!')
        await asyncio.sleep(1)


async def get_current_time():
    utc_plus_3 = timezone(timedelta(hours=3))
    now = datetime.now(utc_plus_3)
    start_of_day = datetime(now.year, now.month, now.day, tzinfo=utc_plus_3)
    time_difference = now - start_of_day
    seconds_since_start_of_day = int(time_difference.total_seconds())
    return seconds_since_start_of_day


async def send_message_to_user(user_id: int, msg_gas_price: str) -> None:

    print('before sending')
    await bot.send_message(chat_id=user_id, text=msg_gas_price, parse_mode='markdown')
    '''await bot.send_message(chat_id=user_id, text=msg_gas_price, parse_mode='markdown')'''
    print('sent')
    '''try:
        asyncio.timeout(3)
        await bot.send_message(chat_id=user_id, text=msg_gas_price, parse_mode='markdown')
    except Exception as e:
        print(e, 'EXCEPTION ERRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRROR')
        pass  # delete user who blocked the bot from db'''


async def waiting_for_sending_messages():
    while True:
        utc_plus_3 = timezone(timedelta(hours=3))
        now = datetime.now(utc_plus_3)
        start_of_day = datetime(now.year, now.month, now.day, tzinfo=utc_plus_3)
        time_difference = now - start_of_day
        seconds_since_start_of_day = int(time_difference.total_seconds())
        # print(seconds_since_start_of_day, ' * * * * * * ', seconds_since_start_of_day % 30)
        if seconds_since_start_of_day % 30 == 0:
            break
        await asyncio.sleep(0.9)

