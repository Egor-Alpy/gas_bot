# IMPORT ----- IMPORT ----- IMPORT ----- IMPORT ----- IMPORT ----- IMPORT ----- IMPORT ----- IMPORT ----- IMPORT ----- I
import asyncio
import datetime

from data.text import get_msg_channels_to_subscribe, get_msg_gas_price, MSG
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.bot_creation import bot, dp
from aiogram import types

from core.database.database_main import table_users, table_channels

from core.logger_config import logger
from core.keyboards import get_interval_markup
from data.config import ADMINS

from datetime import datetime, timedelta, timezone


# Бесконечный цикл рассылки сообщений о цене Газа в ETH
async def start_sending():
    while True:
        msg_gas_price = get_msg_gas_price()
        list_of_tasks = []
        for user_id in table_users.get_all_user_id():
            if not await check_user_subscriptions(user_id):
                pass
            else:
                user_interval = table_users.get_user_interval(user_id)
                if user_interval != 'None':

                    utc_plus_3 = timezone(timedelta(hours=3))
                    now = datetime.now(utc_plus_3)
                    start_of_day = datetime(now.year, now.month, now.day, tzinfo=utc_plus_3)
                    time_difference = now - start_of_day
                    seconds_since_start_of_day = int(time_difference.total_seconds())

                    if seconds_since_start_of_day % user_interval < 30:
                        list_of_tasks.append(asyncio.create_task(send_message_to_user(user_id, msg_gas_price)))
        await waiting_for_sending_messages()
        await asyncio.wait(list_of_tasks)
        await asyncio.sleep(1)


async def send_message_to_user(user_id: int, msg_gas_price: str) -> None:
    try:
        await bot.send_message(chat_id=user_id, text=msg_gas_price, parse_mode='markdown')
        print('msg delivered')
    except Exception as e:
        pass  # delete user who blocked the bot from db


async def waiting_for_sending_messages():
    while True:
        utc_plus_3 = timezone(timedelta(hours=3))
        now = datetime.now(utc_plus_3)
        start_of_day = datetime(now.year, now.month, now.day, tzinfo=utc_plus_3)
        time_difference = now - start_of_day
        seconds_since_start_of_day = int(time_difference.total_seconds())
        print(seconds_since_start_of_day, ' * * * * * * ', seconds_since_start_of_day % 30)
        '''utc_3 = pytz.timezone('Etc/GMT-3')
        now = datetime.now().astimezone(utc_3)
        seconds_in_minute = int(now.strftime('%H:%M:%S')[-2:])
        if seconds_in_minute == 0 or seconds_in_minute == 30:'''
        if seconds_since_start_of_day % 30 == 0:
            break
        await asyncio.sleep(0.9)


async def check_user_subscriptions(user_id: int) -> bool:
    previous_subscription_status = table_users.get_subscription_status(user_id)
    channel_tags = table_channels.get_channel_tags()
    if not channel_tags:
        table_users.set_subscription_status('True', user_id)
        return True

    for channel_tag in channel_tags:

        try:
            user_channel_status = await bot.get_chat_member(chat_id='@' + channel_tag, user_id=user_id)
            if user_channel_status['status'] not in ['creator', 'administrator', 'member'] and int(user_id) not in ADMINS:
                if previous_subscription_status == 'True':
                    await bot.send_message(chat_id=user_id, text=MSG['RUS']['SUB']['CLOSED'], parse_mode='markdown')
                table_users.set_subscription_status('False', user_id)
                return False
        except Exception as e:
            if str(e) == 'User not found':
                logger.info(f'Bot does not have rights in [{channel_tag}] channel')
        if previous_subscription_status == 'False':
            await bot.send_message(chat_id=user_id, text=MSG['RUS']['SUB']['OPENED'], parse_mode='markdown')
        table_users.set_subscription_status('True', user_id)
        return True


@dp.callback_query_handler(lambda call: call.data.startswith('turn_on_off'))
async def turn_on_off_callback_func(callback: types.CallbackQuery, state: FSMContext):
    # проверка на подписку каналов
    if not await check_user_subscriptions(callback.message.chat.id) and callback.message.chat.id not in ADMINS:
        channels = ''
        for tag in table_channels.get_channel_tags():
            channels += f'\n@{tag}'
        await bot.send_message(chat_id=callback.message.chat.id,
                               text=get_msg_channels_to_subscribe(),
                               parse_mode='markdown')
        await callback.answer()
        return

    user_previous_interval = table_users.get_user_interval(callback.message.chat.id)
    kb_settings = InlineKeyboardMarkup()
    btn_choose_interval = InlineKeyboardButton('Интервалы', callback_data='set_interval')
    current_interval = table_users.get_user_interval(callback.message.chat.id)
    if current_interval == 'None':
        btn_turn_on_off = InlineKeyboardButton("Выключить", callback_data='turn_on_off')
    else:
        btn_turn_on_off = InlineKeyboardButton("Включить", callback_data='turn_on_off')
    kb_settings.add(btn_choose_interval, btn_turn_on_off)
    if user_previous_interval == 'None':
        table_users.set_new_interval(callback.message.chat.id, 30)
        await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                            reply_markup=kb_settings)
        await callback.answer(MSG['RUS']['SETTINGS']['START'])
    else:
        table_users.set_new_interval(callback.message.chat.id, None)
        await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                            reply_markup=kb_settings)
        await callback.answer(MSG['RUS']['SETTINGS']['STOP'])

    await callback.answer()


@dp.callback_query_handler(lambda call: call.data.startswith('set_interval'))
async def turn_on_off_func(callback: types.CallbackQuery):
    # проверка на подписку каналов
    if not await check_user_subscriptions(callback.message.chat.id) and callback.message.chat.id not in ADMINS:
        channels = ''
        for tag in table_channels.get_channel_tags():
            channels += f'\n@{tag}'
        await bot.send_message(chat_id=callback.message.chat.id,
                               text=get_msg_channels_to_subscribe(),
                               parse_mode='markdown')
        await callback.answer()
        return

    await callback.answer()
    markup_interval = get_interval_markup(callback)
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                text=MSG['RUS']['SETTINGS']['INTERVAL'],
                                reply_markup=markup_interval, parse_mode='markdown')


@dp.callback_query_handler(lambda call: call.data.startswith('interval'))
async def set_new_user_interval_func(callback: types.CallbackQuery):
    # проверка на подписку каналов
    if not await check_user_subscriptions(callback.message.chat.id) and callback.message.chat.id not in ADMINS:
        channels = ''
        for tag in table_channels.get_channel_tags():
            channels += f'\n@{tag}'
        await bot.send_message(chat_id=callback.message.chat.id,
                               text=get_msg_channels_to_subscribe(),
                               parse_mode='markdown')
        await callback.answer()
        return

    new_interval = int(callback.data.split('_')[1])
    previous_interval = table_users.get_user_interval(callback.message.chat.id)
    if previous_interval != new_interval:
        table_users.set_new_interval(callback.message.chat.id, new_interval)
        markup_interval = get_interval_markup(callback)
        await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                            reply_markup=markup_interval)
    await callback.answer()


@dp.callback_query_handler(lambda call: call.data.startswith('back_to_settings'))
async def back_to_settings_func(callback: types.CallbackQuery):
    # проверка на подписку каналов
    if not await check_user_subscriptions(callback.message.chat.id) and callback.message.chat.id not in ADMINS:
        channels = ''
        for tag in table_channels.get_channel_tags():
            channels += f'\n@{tag}'
        await bot.send_message(chat_id=callback.message.chat.id,
                               text=get_msg_channels_to_subscribe(),
                               parse_mode='markdown')
        await callback.answer()
        return

    kb_settings = InlineKeyboardMarkup()
    btn_choose_interval = InlineKeyboardButton('Интервалы', callback_data='set_interval')
    current_interval = table_users.get_user_interval(callback.message.chat.id)
    if current_interval == 'None':
        btn_turn_on_off = InlineKeyboardButton("Включить", callback_data='turn_on_off')
    else:
        btn_turn_on_off = InlineKeyboardButton("Выключить", callback_data='turn_on_off')
    kb_settings.add(btn_choose_interval, btn_turn_on_off)
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                text=MSG['RUS']['SETTINGS']['MENU'], reply_markup=kb_settings, parse_mode='markdown')


async def start_func(message: types.Message):
    logger.debug(f'Command: /start | Message: {message} | User: {message.from_user.id}')

    if str(message.from_user.id) not in table_users.get_all_user_id():
        table_users.add_user(user_id=message.from_user.id, username=message.from_user.username,
                             name=message.from_user.first_name, surname=message.from_user.last_name)
        logger.info(
            f'User has been added to the DB [id: {message.from_user.id}, username: {message.from_user.username}]')
        logger.debug(f'New user has been registered! | User: {message.from_user.id}')
    await settings_func(message)


async def settings_func(message: types.Message):
    if str(message.from_user.id) not in table_users.get_all_user_id():
        table_users.add_user(user_id=message.from_user.id, username=message.from_user.username,
                             name=message.from_user.first_name, surname=message.from_user.last_name)
        logger.info(
            f'User has been added to the DB [id: {message.from_user.id}, username: {message.from_user.username}]')

    kb_settings = InlineKeyboardMarkup()
    btn_choose_interval = InlineKeyboardButton('Интервалы', callback_data='set_interval')
    current_interval = table_users.get_user_interval(message.from_user.id)
    if current_interval == 'None':
        btn_turn_on_off = InlineKeyboardButton("Включить", callback_data='turn_on_off')
    else:
        btn_turn_on_off = InlineKeyboardButton("Выключить", callback_data='turn_on_off')
    kb_settings.add(btn_choose_interval, btn_turn_on_off)
    await message.answer(MSG['RUS']['SETTINGS']['MENU'], reply_markup=kb_settings, parse_mode='markdown')
