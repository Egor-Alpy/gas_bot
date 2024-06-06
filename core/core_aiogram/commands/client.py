# IMPORT ----- IMPORT ----- IMPORT ----- IMPORT ----- IMPORT ----- IMPORT ----- IMPORT ----- IMPORT ----- IMPORT ----- I
from data.text import get_msg_channels_to_subscribe, MSG, BUTTONS
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.core_aiogram.bot_creation import bot, dp
from aiogram import types

from core.database.database_main import table_users, table_channels

from core.logger_config import logger
from core.core_aiogram.keyboards import get_interval_markup, get_language_markup
from data.config import ADMINS

from core.utilities import check_user_subscriptions


@dp.callback_query_handler(lambda call: call.data.startswith('turn_on_off'))
async def turn_on_off_callback_func(callback: types.CallbackQuery, state: FSMContext):
    # проверка на подписку каналов
    LAN = table_users.get_user_language(callback.message.chat.id)
    if not await check_user_subscriptions(callback.message.chat.id) and callback.message.chat.id not in ADMINS:
        channels = ''
        for tag in table_channels.get_channel_tags():
            channels += f'\n@{tag}'
        await bot.send_message(chat_id=callback.message.chat.id,
                               text=get_msg_channels_to_subscribe(LAN),
                               parse_mode='markdown')
        await callback.answer()
        return

    user_previous_interval = table_users.get_user_interval(callback.message.chat.id)
    kb_settings = InlineKeyboardMarkup()
    btn_choose_interval = InlineKeyboardButton(BUTTONS[LAN]['INTERVAL'], callback_data='set_interval')
    btn_choose_language = InlineKeyboardButton(BUTTONS[LAN]['LANGUAGE'], callback_data='set_language')
    current_interval = table_users.get_user_interval(callback.message.chat.id)
    print(current_interval == 'None')
    if current_interval == 'None':
        btn_turn_on_off = InlineKeyboardButton(BUTTONS[LAN]['TURN']['OFF'], callback_data='turn_on_off')
    else:
        btn_turn_on_off = InlineKeyboardButton(BUTTONS[LAN]['TURN']['ON'], callback_data='turn_on_off')
    kb_settings.add(btn_choose_interval).add(btn_choose_language, btn_turn_on_off)
    if user_previous_interval == 'None':
        table_users.set_new_interval(callback.message.chat.id, 30)
        await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                            reply_markup=kb_settings)
        await callback.answer(MSG[LAN]['SETTINGS']['START'])
    else:
        table_users.set_new_interval(callback.message.chat.id, None)
        await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                            reply_markup=kb_settings)
        await callback.answer(MSG[LAN]['SETTINGS']['STOP'])

    await callback.answer()


@dp.callback_query_handler(lambda call: call.data.startswith('set_interval'))
async def turn_on_off_func(callback: types.CallbackQuery):
    LAN = table_users.get_user_language(callback.message.chat.id)
    # проверка на подписку каналов
    if not await check_user_subscriptions(callback.message.chat.id) and callback.message.chat.id not in ADMINS:
        channels = ''
        for tag in table_channels.get_channel_tags():
            channels += f'\n@{tag}'
        await bot.send_message(chat_id=callback.message.chat.id,
                               text=get_msg_channels_to_subscribe(LAN),
                               parse_mode='markdown')
        await callback.answer()
        return

    await callback.answer()
    markup_interval = get_interval_markup(callback)
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                text=MSG[LAN]['SETTINGS']['INTERVAL'],
                                reply_markup=markup_interval, parse_mode='markdown')


@dp.callback_query_handler(lambda call: call.data.startswith('interval'))
async def set_new_user_interval_func(callback: types.CallbackQuery):
    # проверка на подписку каналов
    LAN = table_users.get_user_language(callback.message.chat.id)
    if not await check_user_subscriptions(callback.message.chat.id) and callback.message.chat.id not in ADMINS:
        channels = ''
        for tag in table_channels.get_channel_tags():
            channels += f'\n@{tag}'
        await bot.send_message(chat_id=callback.message.chat.id,
                               text=get_msg_channels_to_subscribe(LAN),
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


@dp.callback_query_handler(lambda call: call.data.startswith('set_language'))
async def choose_language_func(callback: types.CallbackQuery):
    LAN = table_users.get_user_language(callback.message.chat.id)
    if not await check_user_subscriptions(callback.message.chat.id) and callback.message.chat.id not in ADMINS:
        channels = ''
        for tag in table_channels.get_channel_tags():
            channels += f'\n@{tag}'
        await bot.send_message(chat_id=callback.message.chat.id,
                               text=get_msg_channels_to_subscribe(LAN),
                               parse_mode='markdown')
        await callback.answer()
        return
    LAN = table_users.get_user_language(callback.message.chat.id)
    markup_language = get_language_markup(callback)
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                text=MSG[LAN]['SETTINGS']['LANGUAGE'],
                                reply_markup=markup_language, parse_mode='markdown')


@dp.callback_query_handler(lambda call: call.data.startswith('language'))
async def set_language_func(callback: types.CallbackQuery):
    previous_language = table_users.get_user_language(callback.message.chat.id)
    new_language = callback.data.split('_')[-1]
    table_users.set_new_language(callback.message.chat.id, new_language)
    if previous_language != new_language:
        table_users.set_new_language(callback.message.chat.id, new_language)
        language_markup = get_language_markup(callback)
        LAN = table_users.get_user_language(callback.message.chat.id)
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                    text=MSG[LAN]['SETTINGS']['LANGUAGE'], reply_markup=language_markup,
                                    parse_mode='markdown')
    await callback.answer()


@dp.callback_query_handler(lambda call: call.data.startswith('back_to_settings'))
async def back_to_settings_func(callback: types.CallbackQuery):
    # проверка на подписку каналов
    LAN = table_users.get_user_language(callback.message.chat.id)
    if not await check_user_subscriptions(callback.message.chat.id) and callback.message.chat.id not in ADMINS:
        channels = ''
        for tag in table_channels.get_channel_tags():
            channels += f'\n@{tag}'
        await bot.send_message(chat_id=callback.message.chat.id,
                               text=get_msg_channels_to_subscribe(LAN),
                               parse_mode='markdown')
        await callback.answer()
        return
    LAN = table_users.get_user_language(callback.message.chat.id)
    kb_settings = InlineKeyboardMarkup()
    btn_choose_interval = InlineKeyboardButton(BUTTONS[LAN]['INTERVAL'], callback_data='set_interval')
    btn_choose_language = InlineKeyboardButton(BUTTONS[LAN]['LANGUAGE'], callback_data='set_language')
    current_interval = table_users.get_user_interval(callback.message.chat.id)
    if current_interval == 'None':
        btn_turn_on_off = InlineKeyboardButton(BUTTONS[LAN]['TURN']['ON'], callback_data='turn_on_off')
    else:
        btn_turn_on_off = InlineKeyboardButton(BUTTONS[LAN]['TURN']['OFF'], callback_data='turn_on_off')
    kb_settings.add(btn_choose_interval).add(btn_choose_language, btn_turn_on_off)
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                text=MSG[LAN]['SETTINGS']['MENU'], reply_markup=kb_settings, parse_mode='markdown')


async def start_func(message: types.Message):
    logger.debug(f'Command: /start | Message: {message} | User: {message.from_user.id}')

    if str(message.from_user.id) not in table_users.get_all_user_id():
        table_users.add_user(user_id=message.from_user.id, username=message.from_user.username,
                             name=message.from_user.first_name, surname=message.from_user.last_name)
        logger.info(
            f'User has been added to the DB [id: {message.from_user.id}, username: {message.from_user.username}]')
        logger.debug(f'New user has been registered! | User: {message.from_user.id}')
    await settings_func(message, LAN='RUS')


async def settings_func(message: types.Message, LAN):
    if str(message.from_user.id) not in table_users.get_all_user_id():
        table_users.add_user(user_id=message.from_user.id, username=message.from_user.username,
                             name=message.from_user.first_name, surname=message.from_user.last_name)
        logger.info(
            f'User has been added to the DB [id: {message.from_user.id}, username: {message.from_user.username}]')

    kb_settings = InlineKeyboardMarkup()
    btn_choose_interval = InlineKeyboardButton(BUTTONS[LAN]['INTERVAL'], callback_data='set_interval')
    btn_choose_language = InlineKeyboardButton(BUTTONS[LAN]['LANGUAGE'], callback_data='set_language')
    current_interval = table_users.get_user_interval(message.chat.id)
    if current_interval == 'None':
        btn_turn_on_off = InlineKeyboardButton(BUTTONS[LAN]['TURN']['ON'], callback_data='turn_on_off')
    else:
        btn_turn_on_off = InlineKeyboardButton(BUTTONS[LAN]['TURN']['OFF'], callback_data='turn_on_off')
    kb_settings.add(btn_choose_interval).add(btn_choose_language, btn_turn_on_off)
    await message.answer(MSG[LAN]['SETTINGS']['MENU'], reply_markup=kb_settings, parse_mode='markdown')
