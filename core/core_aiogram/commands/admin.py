import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.core_aiogram.bot_creation import bot, dp
from core.database.database_main import table_users, table_channels
from core.core_aiogram.states import SendMsgToAllStatesGroup, AddChannelStatesGroup
from core.utilities import proxy_add_value, proxy_get_value
from core.logger_config import logger
from data.text import MSG, msg_soft_not_added, msg_soft_added, BUTTONS
from core.core_aiogram.keyboards import get_channels_inlinekeyboard_4delete


async def add_channel(message: types.Message, LAN):
    await AddChannelStatesGroup.get_id.set()
    await bot.send_message(chat_id=message.chat.id, text=MSG[LAN]['ADMIN']['CHANNEL']['ADD'], parse_mode='markdown')


async def del_channel(message: types.Message, state: FSMContext, LAN):
    await proxy_add_value(state, 'LAN', LAN)
    await bot.send_message(chat_id=message.chat.id, text=MSG[LAN]['ADMIN']['CHANNEL']['DEL'], parse_mode='markdown',
                           reply_markup=get_channels_inlinekeyboard_4delete())


async def send_msg_to_all(message: types.Message, state: FSMContext, LAN):
    await SendMsgToAllStatesGroup.get_msg.set()
    await proxy_add_value(state, 'LAN', LAN)
    await bot.send_message(chat_id=message.chat.id,
                           text=MSG[LAN]['ADMIN']['SEND_MSG']['INPUT'],
                           parse_mode='markdown')


@dp.message_handler(content_types=types.ContentType.ANY, state=SendMsgToAllStatesGroup.get_msg)
async def confirmation(message: types.Message, state: FSMContext):
    LAN = await proxy_get_value(state, 'LAN')
    btn_yes = InlineKeyboardButton(BUTTONS[LAN]['PROMO']['SEND'], callback_data='send_confirm')
    btn_no = InlineKeyboardButton(BUTTONS[LAN]['PROMO']['EDIT'], callback_data='send_edit')
    confirm_sending = InlineKeyboardMarkup()
    confirm_sending.add(btn_yes, btn_no)
    await SendMsgToAllStatesGroup.confirmation.set()
    await bot.send_message(chat_id=message.chat.id, text=MSG[LAN]['ADMIN']['SEND_MSG']['CHECK'], parse_mode='markdown'
                           , reply_markup=confirm_sending)
    await message.send_copy(chat_id=message.chat.id)
    await proxy_add_value(state, 'msg_keyboard_id', message.message_id + 1)
    await proxy_add_value(state, 'message', message)


@dp.callback_query_handler(lambda call: call.data.startswith('send'), state=SendMsgToAllStatesGroup.confirmation)
async def confirm_end(callback: types.CallbackQuery, state: FSMContext):
    LAN = await proxy_get_value(state, 'LAN')
    message = await proxy_get_value(state, 'message')
    message_id = await proxy_get_value(state, 'msg_keyboard_id')
    list_of_tasks = []
    if callback.data == 'send_confirm':
        for user_id in table_users.get_all_user_id():
            list_of_tasks.append(asyncio.create_task(send_message_to_user_promo(message, user_id)))
        await asyncio.wait(list_of_tasks)
        await state.finish()
        await callback.answer()
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=message_id,
                                    text=MSG[LAN]['ADMIN']['SEND_MSG']['SENT'],
                                    reply_markup=None, parse_mode='markdown')
    elif callback.data == 'send_edit':
        await bot.send_message(chat_id=callback.message.chat.id,
                               text=MSG[LAN]['ADMIN']['SEND_MSG']['INPUT'],
                               parse_mode='markdown')
        await SendMsgToAllStatesGroup.get_msg.set()
        await callback.answer()
        await proxy_add_value(state, 'msg_keyboard_id', callback.message.message_id + 1)
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=message_id,
                                    text=MSG[LAN]['ADMIN']['SEND_MSG']['SENT'],
                                    reply_markup=None, parse_mode='markdown')


async def send_message_to_user_promo(message, chat_id):
    try:
        await message.send_copy(chat_id)
    except Exception as e:
        pass  # can't send messageg to user {user_id}


@dp.message_handler(content_types=['text'], state=AddChannelStatesGroup.get_id)
async def add_channel_load(message: types.Message, state: FSMContext):
    try:
        checking_permissions_existance = await bot.get_chat_member(message.text, message.chat.id)
        print('checked')
        channel_info = await bot.get_chat(message.text)
        channel_id = channel_info['id']
        channel_tag = channel_info['username']
        channel_name = channel_info['title']
        table_channels.add_channel_to_db(channel_id=channel_id, channel_tag=channel_tag, channel_name=channel_name)
        await bot.send_message(chat_id=message.chat.id, text=msg_soft_added(channel_id, channel_tag, channel_name),
                               parse_mode='markdown')
        await state.finish()
    except Exception as e:
        await bot.send_message(chat_id=message.chat.id, text=msg_soft_not_added(e), parse_mode='markdown')
        logger.info(e)
