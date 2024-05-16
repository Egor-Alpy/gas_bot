from web3 import Web3

from core.bot_creation import bot
from aiogram import types
from data.text import CMD_START, CMD_ADMIN, CMD_CLIENT, CMD_SETTINGS
from core.commands.client import *
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from core.database.database_main import table_users
from core.logger_config import logger

import asyncio
import aioschedule





async def set_commands():
    await bot.set_my_commands(
        [
            types.BotCommand(f'/{CMD_SETTINGS}', "настройки"),
            types.BotCommand(f'/help', "поддержка"),
        ]
    )


@dp.message_handler(commands=CMD_START)
async def commands_all(message: types.Message) -> None:
    await start_func(message)


# handler: all commands
@dp.message_handler(commands=CMD_CLIENT + CMD_ADMIN)
async def commands_all(message: types.Message) -> None:
    await COMMAND_FUNCTIONS_DICT[str(message.text)[1:]](message)


async def start_func(message: types.Message):
    logger.debug(f'Command: /start | Message: {message} | User: {message.from_user.id}')

    if str(message.from_user.id) not in table_users.get_all_user_id():
        table_users.add_user(user_id=message.from_user.id, username=message.from_user.username, name=message.from_user.first_name, surname=message.from_user.last_name)
        logger.info(
            f'User has been added to the DB [id: {message.from_user.id}, username: {message.from_user.username}]')
        logger.debug(f'New user has been registered! | User: {message.from_user.id}')
    await settings_func(message)


@dp.message_handler(commands=['settings'])
async def settings_func(message: types.Message):
    if str(message.from_user.id) not in table_users.get_all_user_id():
        table_users.add_user(user_id=message.from_user.id, username=message.from_user.username, name=message.from_user.first_name, surname=message.from_user.last_name)
        logger.info(
            f'User has been added to the DB [id: {message.from_user.id}, username: {message.from_user.username}]')

    kb_settings = InlineKeyboardMarkup()
    btn_choose_interval = InlineKeyboardButton('Установить интервал', callback_data='set_interval')
    btn_turn_on_off = InlineKeyboardButton("Выключатель", callback_data='turn_on_off')
    kb_settings.add(btn_choose_interval, btn_turn_on_off)
    await message.answer('*Настройте параметры бота*', reply_markup=kb_settings, parse_mode='markdown')


async def gas_msg():
    con_web3 = Web3(provider=Web3.HTTPProvider(endpoint_uri='https://rpc.ankr.com/eth'))
    gas = round(con_web3.eth.gas_price / 10**9, 2)
    all_user_id_list = table_users.get_all_user_id()
    print(all_user_id_list)
    for user_id in all_user_id_list:
        print(user_id)
        await bot.send_message(chat_id=user_id, text=f"Gas price is {gas} ETH gwei")


async def turn_on_off_func(user_id: int, interval: int):
    aioschedule.every(3).seconds.do(gas_msg)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


@dp.callback_query_handler(lambda call: call.data.startswith('turn_on_off'))
async def turn_on_off_callback_func(callback: types.CallbackQuery):
    await callback.answer()
    await turn_on_off_func(callback: types.CallbackQuery)


@dp.callback_query_handler(lambda call: call.data.startswith('set_interval'))
async def turn_on_off_func(callback: types.CallbackQuery):
    await callback.answer()
    b30sec = InlineKeyboardButton('30 sec', callback_data='interval30sec')
    b1min = InlineKeyboardButton('1 min', callback_data='interval1min')
    b5min = InlineKeyboardButton('5 min', callback_data='interval5min')
    b15min = InlineKeyboardButton('15 min', callback_data='interval15min')
    b1h = InlineKeyboardButton('1 h', callback_data='interval1h')
    b4h = InlineKeyboardButton('4 h', callback_data='interval4h')
    b12h = InlineKeyboardButton('12 h', callback_data='interval12h')
    b24h = InlineKeyboardButton('24 h', callback_data='interval24h')
    b_back = InlineKeyboardButton('<< Назад', callback_data='back_to_settings')
    markup_interval = InlineKeyboardMarkup()
    markup_interval.add(b30sec, b1min, b5min).add(b15min, b1h, b4h).add(b12h, b24h).add(b_back)

    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='*Выберите интервал, с которым Вы будете получать информацию о цене газа в сети:*', reply_markup=markup_interval, parse_mode='markdown')


@dp.callback_query_handler(lambda call: call.data.startswith('back_to_settings'))
async def back_to_settings_func(callback: types.CallbackQuery):
    kb_settings = InlineKeyboardMarkup()
    btn_choose_interval = InlineKeyboardButton('Установить интервал', callback_data='set_interval')
    btn_turn_on_off = InlineKeyboardButton("Выключатель", callback_data='turn_on_off')
    kb_settings.add(btn_choose_interval, btn_turn_on_off)
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='*Настройте параметры бота*', reply_markup=kb_settings, parse_mode='markdown')


COMMAND_FUNCTIONS_DICT = {
    CMD_START: start_func,
    CMD_SETTINGS: settings_func
}


