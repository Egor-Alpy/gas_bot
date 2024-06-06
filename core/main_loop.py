import asyncio
from datetime import timezone, timedelta, datetime

from core.client_web3.client import Client
from core.core_aiogram.bot_creation import bot
from core.core_aiogram.commands.client import check_user_subscriptions
from core.database.database_main import table_users
from data.text import get_msg_gas_price


# Бесконечный цикл рассылки сообщений о цене Газа в ETH
async def start_sending():
    while True:
        list_of_tasks = []

        seconds_since_start_of_day = await get_current_time()
        financial_data = Client.get_financial_data()

        for user_id in table_users.get_user_id_by_time(time=seconds_since_start_of_day):
            msg_gas_price = get_msg_gas_price(LAN=table_users.get_user_language(user_id), financial_data=financial_data)   # газ должен рассчитываться выше, а не отдельно для кадого пользователя
            if not await check_user_subscriptions(user_id):
                pass
            else:
                user_interval = table_users.get_user_interval(user_id)
                if user_interval != 'None':
                    list_of_tasks.append(asyncio.create_task(send_message_to_user(user_id, msg_gas_price)))
        last_tickers_prices = financial_data['ticker_prices']
        last_market_data = financial_data['market_data']
        last_gas_price = financial_data['gas_price']
        await waiting_for_sending_messages()
        if list_of_tasks:
            await asyncio.wait(list_of_tasks)
        await asyncio.sleep(1)


async def get_current_time():
    utc_plus_3 = timezone(timedelta(hours=3))
    now = datetime.now(utc_plus_3)
    start_of_day = datetime(now.year, now.month, now.day, tzinfo=utc_plus_3)
    time_difference = now - start_of_day
    seconds_since_start_of_day = int(time_difference.total_seconds())
    return seconds_since_start_of_day


async def send_message_to_user(user_id: int, msg_gas_price: str) -> None:
    try:
        await bot.send_message(chat_id=user_id, text=msg_gas_price, parse_mode='markdown')
    except Exception as e:
        pass  # delete user who blocked the bot from db


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

