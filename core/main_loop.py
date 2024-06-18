import asyncio
import random
from datetime import timezone, timedelta, datetime

import requests

from core.utilities import check_user_subscriptions
from core.utilities import get_financial_data
from core.database.database_main import table_users
from data.text import get_msg_gas_price
from data.config import TOKEN
from core.logger_config import logger
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
        users_to_receive_msg = {}

        # цикл ожидания рассылки
        while True:
            utc_plus_3 = timezone(timedelta(hours=3))
            now = datetime.now(utc_plus_3)
            start_of_day = datetime(now.year, now.month, now.day, tzinfo=utc_plus_3)
            time_difference = now - start_of_day
            seconds_since_start_of_day = int(time_difference.total_seconds())
            if seconds_since_start_of_day % 30 == 28:
                print('left the waiting cycle!')
                break
            time.sleep(0.9)

        try:
            financial_data = get_financial_data(last_market_data, last_gas_price, last_tickers_prices)
            rus_msg = get_msg_gas_price(LAN='RUS', financial_data=financial_data)
            eng_msg = get_msg_gas_price(LAN='ENG', financial_data=financial_data)
            users = table_users.get_user_id_by_time(time=seconds_since_start_of_day)
            # for i in range(1000):                                                                      # Delete
            #     users.append(str(random.randint(168320310, 968320310)))                                # Delete
            for user_id in users:
                if await check_user_subscriptions(user_id):
                    user_interval = table_users.get_user_interval(user_id)
                    if user_interval != 'None':
                        LAN = table_users.get_user_language(user_id)
                        if LAN == 'ENG':
                            users_to_receive_msg[user_id] = eng_msg
                        elif LAN == 'RUS':
                            users_to_receive_msg[user_id] = rus_msg

            last_tickers_prices = financial_data['ticker_prices']
            last_market_data = financial_data['market_data']
            last_gas_price = financial_data['gas_price']

        except Exception as e:
            logger.info(f'ERROR: error in sending loop: {e}')

        for user_id, msg in users_to_receive_msg.items():
            create_user_thread(user_id, msg)


def create_user_thread(user_id, msg):
    Thread(target=tg_send_message, args=(user_id, msg)).start()


def tg_send_message(chat_id: str, msg: str):
    try:
        url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
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


