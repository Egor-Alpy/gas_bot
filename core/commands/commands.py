from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import state
from web3 import Web3

from core.bot_creation import bot
from aiogram import types
from data.text import CMD_START, CMD_ADMIN, CMD_CLIENT, CMD_SETTINGS
from core.commands.client import *
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from core.database.database_main import table_users
from core.logger_config import logger
from time import sleep
import asyncio
from core.states import TurnOnOffStatesGroup
from core.utilities import proxy_add_value, proxy_get_value


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


'''async def start_sending():
    while True:
        con_web3 = Web3(provider=Web3.HTTPProvider(endpoint_uri='https://rpc.ankr.com/eth'))
        gas = round(con_web3.eth.gas_price / 10 ** 9, 2)
        for user_id in table_users.get_all_user_id():
            try:
                await bot.send_message(chat_id=user_id, text=f'*gas price: {gas} ETH gwei*', parse_mode='markdown')
            except:
                pass # delete user who blocked the bot from db
            finally:
                print(f'sleep asyncio personal-user-time: {table_users.get_user_interval(user_id)}, [id: {user_id}]')
                await asyncio.sleep(table_users.get_user_interval(user_id))'''


counter = 1


async def start_sending():
    global counter
    while True:
        con_web3 = Web3(provider=Web3.HTTPProvider(endpoint_uri='https://rpc.ankr.com/eth'))
        gas = round(con_web3.eth.gas_price / 10 ** 9, 2)
        for user_id in table_users.get_all_user_id():
            user_interval = table_users.get_user_interval(user_id)
            if counter % user_interval == 0:
                print(f'{counter} % {user_interval} = {counter % user_interval}')
                print(f'{user_interval} - user_interval')
                try:
                    await bot.send_message(chat_id=user_id, text=f'*gas price: {gas} ETH gwei*', parse_mode='markdown')
                except Exception as e:
                    pass  # delete user who blocked the bot from db
        if counter == 1:
            counter += 29
        else:
            counter += 30
        await asyncio.sleep(30)
        print(counter, '- counter')
        print()


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


@dp.callback_query_handler(lambda call: call.data.startswith('turn_on_off'))
async def turn_on_off_callback_func(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    print(current_state)
    if str(current_state) == 'TurnOnOffStatesGroup:on':
        print('ok')
        user_previous_interval = await proxy_get_value(state, 'previous_interval')
        table_users.set_new_interval(callback.message.chat.id, user_previous_interval)
        await state.finish()
        await bot.send_message(chat_id=callback.message.chat.id, text=f'*Работа бота была возобновлена, текущий интервал отправки сообщений: {user_previous_interval}*', parse_mode='markdown')
        await callback.answer()
    else:
        await TurnOnOffStatesGroup.on.set()
        await proxy_add_value(state, 'previous_interval', table_users.get_user_interval(callback.message.chat.id))
        table_users.set_new_interval(callback.message.chat.id, None)
        await bot.send_message(chat_id=callback.message.chat.id, text=f'*Работа бота была приостановлена, чтобы возобновить рассылку ещё раз нажмите на "Выключатель" или установите интревал заново*', parse_mode='markdown')
        await callback.answer()


@dp.message_handler(state=TurnOnOffStatesGroup.on)
async def bot_off_condition(message: types.Message):
    await message.answer('*Чтобы продолжить работу бота выберите новый интервал или нажмите на "Выключатель", вызвав команду /settings.*', parse_mode='markdown')


@dp.callback_query_handler(lambda call: call.data.startswith('set_interval'))
async def turn_on_off_func(callback: types.CallbackQuery):
    await callback.answer()
    b30sec = InlineKeyboardButton('30 сек', callback_data='interval_30_sec')
    b1min = InlineKeyboardButton('1 мин', callback_data='interval_60_sec')
    b5min = InlineKeyboardButton('5 мин', callback_data='interval_300_sec')
    b15min = InlineKeyboardButton('15 мин', callback_data='interval_900_sec')
    b1h = InlineKeyboardButton('1 ч', callback_data='interval_3600_sec')
    b4h = InlineKeyboardButton('4 ч', callback_data='interval_14400_sec')
    b12h = InlineKeyboardButton('12 ч', callback_data='interval_33200_sec')
    b24h = InlineKeyboardButton('24 ч', callback_data='interval_66400_sec')
    b_back = InlineKeyboardButton('<< Назад', callback_data='back_to_settings')
    markup_interval = InlineKeyboardMarkup()
    markup_interval.add(b30sec, b1min).add(b5min, b15min).add(b1h, b4h).add(b12h, b24h).add(b_back)

    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='*Выберите интервал, с которым Вы будете получать информацию о цене газа в сети:*', reply_markup=markup_interval, parse_mode='markdown')


@dp.callback_query_handler(lambda call: call.data.startswith('interval'))
async def set_new_user_interval_func(callback: types.CallbackQuery):
    new_interval = int(callback.data.split('_')[1])
    table_users.set_new_interval(callback.message.chat.id, new_interval)
    await bot.send_message(callback.message.chat.id, f'*Новый установленный интервал: {table_users.get_user_interval(callback.message.chat.id)} секунд!*', parse_mode='markdown')
    await callback.answer()


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


