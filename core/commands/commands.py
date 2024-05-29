from aiogram.dispatcher import FSMContext

from web3 import Web3

from core.bot_creation import bot
from aiogram import types
from data.text import CMD_START, CMD_ADMIN, CMD_CLIENT, CMD_MENU, CMD_HELP, CMD_DEL_CHANNEL, CMD_ADD_CHANNEL, \
    CMD_SEND_MSG, get_msg_channels_to_subscribe
from core.commands.client import *
from core.commands.admin import *
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from core.database.database_main import table_users
from core.logger_config import logger
from core.commands import client, admin
from time import sleep
import asyncio
from core.keyboards import get_channels_inlinekeyboard_4delete

from core.utilities import proxy_add_value, proxy_get_value


async def set_commands():
    await bot.set_my_commands(
        [
            types.BotCommand(f'/{CMD_MENU}', "настройки"),
            types.BotCommand(f'/{CMD_HELP}', "поддержка"),
        ]
    )


# handler: all commands
@dp.message_handler(commands=CMD_CLIENT + CMD_ADMIN)
async def commands_all(message: types.Message) -> None:
    if message.text[1:] in CMD_ADMIN:
        if message.chat.id in ADMINS:
            pass  # Пользователь находится в списке администраторов
        else:
            await bot.send_message(chat_id=message.chat.id, text='У вас нет прав на использование этой команды')
            return
    if message.text == '/start':
        if str(message.from_user.id) not in table_users.get_all_user_id():
            table_users.add_user(user_id=message.from_user.id, username=message.from_user.username,
                                 name=message.from_user.first_name, surname=message.from_user.last_name)
            logger.info(
                f'User has been added to the DB [id: {message.from_user.id}, username: {message.from_user.username}]')
    if not await check_user_subscriptions(message.chat.id):
        channels = ''
        for tag in table_channels.get_channel_tags():
            channels += f'\n@{tag}'
        await bot.send_message(chat_id=message.chat.id, text=get_msg_channels_to_subscribe(), parse_mode='markdown')
    else:
        await COMMAND_FUNCTIONS_DICT[str(message.text)[1:]](message)


async def help_func(message: types.Message):
    if message.chat.id not in ADMINS:
        await bot.send_message(chat_id=message.chat.id, text='*При возникновении неполадок с Ботом обращайтесь в '
                                                             'техническую поддержку: @wndrflp*', parse_mode='markdown')
    else:
        await bot.send_message(chat_id=message.chat.id, text=f'*Команды:\n\n/{CMD_ADD_CHANNEL} - добавить канал\n/{CMD_DEL_CHANNEL} - удалить канал\n/{CMD_SEND_MSG} - разослать сообщение всем пользователям*', parse_mode='markdown')


async def start_func(message: types.Message):
    logger.debug(f'Command: /start | Message: {message} | User: {message.from_user.id}')

    if str(message.from_user.id) not in table_users.get_all_user_id():
        table_users.add_user(user_id=message.from_user.id, username=message.from_user.username,
                             name=message.from_user.first_name, surname=message.from_user.last_name)
        logger.info(
            f'User has been added to the DB [id: {message.from_user.id}, username: {message.from_user.username}]')
        logger.debug(f'New user has been registered! | User: {message.from_user.id}')
    await settings_func(message)


async def send_msg_to_all(message: types.Message):
    await SendMsgToAllStatesGroup.get_msg.set()
    await bot.send_message(chat_id=message.chat.id,
                           text='*⚠️Введите сообщение, которое хотите отправить всем пользователям бота:*',
                           parse_mode='markdown')


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
    await message.answer('*Настройте параметры бота*', reply_markup=kb_settings, parse_mode='markdown')


async def add_channel(message: types.Message):
    await AddChannelStatesGroup.get_id.set()
    await bot.send_message(chat_id=message.chat.id, text='*Пришлите id или @тег канала, который хотите добавить.*\n(предварительно выдайте Боту права администратора в этом канале)', parse_mode='markdown')


async def del_channel(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text='*Выберите канал из списка, который хотите удалить*', parse_mode='markdown', reply_markup=get_channels_inlinekeyboard_4delete())


@dp.message_handler()
async def all_text_handler(message: types.Message):
    if not await check_user_subscriptions(message.chat.id):
        await bot.send_message(chat_id=message.chat.id,
                               text=get_msg_channels_to_subscribe(),
                               parse_mode='markdown')
    else:
        await message.reply(text='Такой команды не существует, чтобы настроить бота вызовите /menu.',
                            parse_mode='markdown')


COMMAND_FUNCTIONS_DICT = {
    CMD_START: start_func,
    CMD_MENU: settings_func,
    CMD_HELP: help_func,
    CMD_ADD_CHANNEL: add_channel,
    CMD_DEL_CHANNEL: del_channel,
    CMD_SEND_MSG: send_msg_to_all
}
