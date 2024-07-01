from datetime import timezone, timedelta, datetime
from multiprocessing import Process

import requests

from core.core_aiogram.bot_creation import bot
from core.utilities import get_financial_data
from core.database.database_main import table_users, table_channels
from data.text import get_msg_gas_price, MSG
from data.config import TOKEN, ADMINS
from core.logger_config import logger
import time

from threading import Thread

last_tickers_prices = {
    "BTCUSDT": '',
    "ETHUSDT": '',
    'BNBUSDT': '',
    'SOLUSDT': '',
    "TONUSDT": ''
}
last_market_data = {
    "market_cap_usd": '',
    "volume_24h_usd": '',
    "dominance_btc_percentage": '',
    "dominance_eth_percentage": ''
}
last_gas_price = ''
time_end_end, time_start_start = 0, 0

try:
    # infinity gas price loop
    async def start_sending():
        global last_tickers_prices
        global last_market_data
        global last_gas_price
        while True:
            users_to_receive_msg = {}

            # waiting loop
            while True:
                utc_plus_3 = timezone(timedelta(hours=3))
                now = datetime.now(utc_plus_3)
                start_of_day = datetime(now.year, now.month, now.day, tzinfo=utc_plus_3)
                time_difference = now - start_of_day
                seconds_since_start_of_day = int(time_difference.total_seconds())
                if seconds_since_start_of_day % 30 == 0:
                    logger.info('Left the waiting loop!')
                    break
                time.sleep(0.9)

            try:
                financial_data = get_financial_data(last_market_data, last_gas_price, last_tickers_prices)
                rus_msg = get_msg_gas_price(LAN='RUS', financial_data=financial_data)
                eng_msg = get_msg_gas_price(LAN='ENG', financial_data=financial_data)
                users = table_users.get_user_id_by_time(time=seconds_since_start_of_day)
                for user_id in users:
                    if await check_user_subscriptionss(user_id):
                        user_turned_condition = table_users.get_turned_condition(user_id)
                        if user_turned_condition == 'turned_ON':
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


    def create_user_thread(user_id: int, msg: str) -> None:
        Thread(target=tg_send_message, args=(user_id, msg)).start()


    def tg_send_message(chat_id: str, msg: str):
        try:
            url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
            data = {
                'chat_id': chat_id,
                'text': msg,
                'parse_mode': 'html',
                'disable_web_page_preview': True
            }
            response = requests.post(url, json=data)
            if response.status_code == 200:
                return 0, None
            else:
                return -1, Exception(f"Status code is not 200! Json: {response.json()}")
        except Exception as e:
            return -1, Exception(f"Could not tg_send_message with error: {e}")


    async def check_user_subscriptionss(user_id):
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
except Exception as e:
    logger.error(f'Exception in the infinity loop block: {e}')
    time.sleep(100)
    process_sending_messages = Process(target=start_sending).start()
    logger.info('PROCESS: INFINITY LOOP process has been started AGAIN!')
