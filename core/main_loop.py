import asyncio
import random
from datetime import timezone, timedelta, datetime

import requests

from core.utilities import get_financial_data
from core.database.database_main import table_users
from data.text import get_msg_gas_price
from data.config import TOKEN
import time

from threading import Thread

last_tickers_prices = {"BTCUSDT": '', "ETHUSDT": '', 'BNBUSDT': '', 'SOLUSDT': '', "TONUSDT": ''}
last_market_data = {"market_cap_usd": '', "volume_24h_usd": '', "dominance_btc_percentage": '',
                    "dominance_eth_percentage": ''}
last_gas_price = ''
time_end_end, time_start_start = 0, 0


# Бесконечный цикл рассылки сообщений о цене Газа в ETH
async def start_sending():
    global last_tickers_prices
    global last_market_data
    global last_gas_price
    while True:
        list_of_tasks = []
        list_of_lists_of_tasks = []

        # цикл ожидания рассылки
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

        time_start_start = time.time()

        financial_data = get_financial_data(last_market_data, last_gas_price, last_tickers_prices)
        rus_msg = get_msg_gas_price(LAN='RUS', financial_data=financial_data)
        eng_msg = get_msg_gas_price(LAN='ENG', financial_data=financial_data)

        users = table_users.get_user_id_by_time(time=seconds_since_start_of_day)
        for i in range(1000):
            users.append(str(random.randint(168320310, 968320310)))
        print(users)

        for user_id in users:

            '''if not await check_user_subscriptions(user_id):
                pass'''
            if True:  # else
                try:  # !!!!!!!!!!!! Delete
                    user_interval = table_users.get_user_interval(user_id)
                except Exception as e:  # Delete
                    user_interval = 30  # Delete
                if user_interval != 'None':
                    LAN = table_users.get_user_language(user_id)
                    # print('task has been crated')
                    if LAN == 'ENG':
                        list_of_tasks.append(create_user_thread(user_id, eng_msg))
                    elif LAN == 'RUS':
                        list_of_tasks.append(create_user_thread(user_id, rus_msg))
                    else:  # Delete
                        list_of_tasks.append(create_user_thread(user_id, rus_msg))  # Delete
                    if len(list_of_tasks) > 50:
                        list_of_lists_of_tasks.append(start_wait_threads(list_of_tasks))
                        list_of_tasks = []
        if len(list_of_tasks) > 0:
            list_of_lists_of_tasks.append(start_wait_threads(list_of_tasks))

        last_tickers_prices = financial_data['ticker_prices']
        last_market_data = financial_data['market_data']
        last_gas_price = financial_data['gas_price']

        time_end_end = time.time()
        print(time_end_end - time_start_start, 'total time collecting data')
        if list_of_tasks:
            time_start_start = time.time()
            print(time_start_start, ' -  STARTING SENDING MSG MSG -        --------------------------------------------------------------------        ----------------------------------------------')
            await asyncio.wait(list_of_lists_of_tasks)

            time_end_end = time.time()
            await asyncio.sleep(5)
            global msg_counter
            print('[                                                                                   ]')
            print('[                                                                                   ]')
            print('[                                                                                   ]')
            print(time_end_end - time_start_start, 'total time |', msg_counter, 'total messages sent')
            print('[                                                                                   ]')
            print('[                                                                                   ]')
            print('[                                                                                   ]')
            msg_counter = 0
        await asyncio.sleep(1)


all_time = 0
msg_counter = 0


def tg_send_message(chat_id: str, msg: str, token: str):
    global msg_counter
    msg_counter += 1
    start_time = time.time()
    try:
        url = f'https://api.telegram.org/bot{token}/sendMessage'
        data = {
            'chat_id': chat_id,
            'text': msg,
            'parse_mode': 'Markdown',
        }
        response = requests.post(url, json=data)
        end_time = time.time()
        global all_time
        all_time += end_time - start_time
        # print(end_time - start_time, '- sending time', chat_id)
        # print(time.time(), 'finishing sending of the message')
        if response.status_code == 200:
            return 0, None
        else:
            return -1, Exception(f"Status code is not 200! Json: {response.json()}")
    except Exception as e:
        return -1, Exception(f"Could not tg_send_message with error: {e}")


async def create_user_thread(user_id, msg):
    Thread(target=tg_send_message, args=(user_id, msg, TOKEN), daemon=True).start()


async def start_wait_thread(list_of_tasks):
    await asyncio.wait(list_of_tasks)
    print(time.time(), ' threads finished it"s work, all 50 messages were sent')

def start_start_wait_thread(list_of_tasks):
    asyncio.run(start_wait_thread(list_of_tasks))


async def start_wait_threads(list_of_tasks):  # list_of_lists_of_tasks
    print('THREAD WAS CREATED !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1')
    Thread(target=start_start_wait_thread, args=[list_of_tasks], daemon=True).start()
    '''for list_of_tasks in list_of_lists_of_tasks:
        print('thread has been started parrallel')
        print('list', list_of_tasks)
        Thread(target=start_start_wait_thread, args=[list_of_tasks], daemon=True).start()
        print('thread has been finished parrallel')'''