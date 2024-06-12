import asyncio
from datetime import timezone, timedelta, datetime

import requests

from core.utilities import get_financial_data
from core.database.database_main import table_users
from data.text import get_msg_gas_price
from data.config import TOKEN
import time


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
        financial_data = get_financial_data(last_market_data, last_gas_price, last_tickers_prices)
        rus_msg = get_msg_gas_price(LAN='RUS', financial_data=financial_data)
        eng_msg = get_msg_gas_price(LAN='ENG', financial_data=financial_data)

        for user_id in table_users.get_user_id_by_time(time=seconds_since_start_of_day):
            '''if not await check_user_subscriptions(user_id):
                pass'''
            if True: # else
                user_interval = table_users.get_user_interval(user_id)
                if user_interval != 'None':
                    print('task has been created')
                    LAN = table_users.get_user_language(user_id)
                    if LAN == 'ENG':
                        list_of_tasks.append(asyncio.create_task(send_message_to_user(user_id, eng_msg)))
                    elif LAN == 'RUS':
                        for i in range(10):
                            list_of_tasks.append(asyncio.create_task(send_message_to_user(5205226194, rus_msg)))
                            list_of_tasks.append(asyncio.create_task(send_message_to_user(868320310, rus_msg)))
                        list_of_tasks.append(asyncio.create_task(send_message_to_user(user_id, rus_msg)))
        print('* * *')
        last_tickers_prices = financial_data['ticker_prices']
        last_market_data = financial_data['market_data']
        last_gas_price = financial_data['gas_price']
        while True:
            utc_plus_3 = timezone(timedelta(hours=3))
            now = datetime.now(utc_plus_3)
            start_of_day = datetime(now.year, now.month, now.day, tzinfo=utc_plus_3)
            time_difference = now - start_of_day
            seconds_since_start_of_day = int(time_difference.total_seconds())
            if seconds_since_start_of_day % 30 == 0:
                print('left the waiting cycle!')
                break
            time.sleep(0.9)
        if list_of_tasks:
            await asyncio.wait(list_of_tasks)
        global all_time
        global msg_counter
        print(all_time, 'total time |', msg_counter, 'total messages sent')
        all_time = 0
        msg_counter = 0
        await asyncio.sleep(1)


async def get_current_time():
    utc_plus_3 = timezone(timedelta(hours=3))
    now = datetime.now(utc_plus_3)
    start_of_day = datetime(now.year, now.month, now.day, tzinfo=utc_plus_3)
    time_difference = now - start_of_day
    seconds_since_start_of_day = int(time_difference.total_seconds())
    return seconds_since_start_of_day

all_time = 0
msg_counter = 0


async def send_message_to_user(user_id: int, msg_gas_price: str) -> None:
    start_time = time.time()
    tg_send_message(chat_id=str(user_id), msg=msg_gas_price, token=TOKEN)
    end_time = time.time()
    global all_time
    all_time += end_time - start_time
    print(end_time - start_time, '- sending time')
    global msg_counter
    msg_counter += 1


def tg_send_message(chat_id: str, msg: str, token: str):
    try:
        url = f'https://api.telegram.org/bot{token}/sendMessage'
        data = {
            'chat_id': chat_id,
            'text': msg,
            'parse_mode': 'Markdown',
        }
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return 0, None
        else:
            return -1, Exception(f"Status code is not 200! Json: {response.json()}")
    except Exception as e:
        return -1, Exception(f"Could not tg_send_message with error: {e}")
