from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.bot_creation import bot, dp
from core.database.database_main import table_users, table_channels
from core.states import SendMsgToAllStatesGroup, AddChannelStatesGroup
from core.utilities import proxy_add_value, proxy_get_value
from core.logger_config import logger


@dp.message_handler(content_types=types.ContentType.ANY, state=SendMsgToAllStatesGroup.get_msg)
async def confirmation(message: types.Message, state: FSMContext):
    print('msg accepted')
    btn_yes = InlineKeyboardButton('Отослать', callback_data='send_confirm')
    btn_no = InlineKeyboardButton('Редактировать', callback_data='send_edit')
    confirm_sending = InlineKeyboardMarkup()
    confirm_sending.add(btn_yes, btn_no)
    await SendMsgToAllStatesGroup.confirmation.set()
    await proxy_add_value(state, 'msg_to_all', message.message_id)
    await bot.send_message(chat_id=message.chat.id, text='⚠️Так будет выглядеть сообщение:', parse_mode='markdown')
    print('before forward')
    await bot.forward_message(chat_id=message.chat.id, from_chat_id=message.chat.id,
                           message_id=message.message_id)
    print('after forward')
    await bot.send_message(chat_id=message.chat.id, text='⚠️Подтвердить отпрвку???', reply_markup=confirm_sending)
    await proxy_add_value(state, 'msg_keyboard_id', message.message_id + 3)


@dp.callback_query_handler(lambda call: call.data.startswith('send'), state=SendMsgToAllStatesGroup.confirmation)
async def confirm_end(callback: types.CallbackQuery, state: FSMContext):
    message_id = await proxy_get_value(state, 'msg_keyboard_id')
    if callback.data == 'send_confirm':
        msg = await proxy_get_value(state, 'msg_to_all')
        for user_id in table_users.get_all_user_id():
            try:
                await bot.forward_message(chat_id=user_id, from_chat_id=callback.message.chat.id, message_id=msg)

                await state.finish()
                await callback.answer()
                await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=message_id,
                                            text='✅*Сообщение было отправлено всем пользователям!*',
                                            reply_markup=None, parse_mode='markdown')
            except Exception as e:
                pass
    elif callback.data == 'send_edit':
        await bot.send_message(chat_id=callback.message.chat.id,
                               text='*⚠️Отправьте сообщение, которое хотите разаслать всем пользователям заново*',
                               parse_mode='markdown')
        await SendMsgToAllStatesGroup.get_msg.set()
        await callback.answer()
        await proxy_add_value(state, 'msg_keyboard_id', callback.message.message_id + 3)
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=message_id,
                                    text='✅*Выполнен переход к редактированию сообщения!*',
                                    reply_markup=None, parse_mode='markdown')


@dp.message_handler(content_types=['text'], state=AddChannelStatesGroup.get_id)
async def add_channel(message: types.Message, state: FSMContext):
    try:
        checking_permissions_existance = await bot.get_chat_member(message.text, message.chat.id)
        print('checked')
        channel_info = await bot.get_chat(message.text)
        channel_id = channel_info['id']
        channel_tag = channel_info['username']
        channel_name = channel_info['title']
        table_channels.add_channel(channel_id=channel_id, channel_tag=channel_tag, channel_name=channel_name)
        await bot.send_message(chat_id=message.chat.id,
                               text=f'*Канал был добавлен:\nID канала: {channel_id}\nТег канала: @{channel_tag}\nНазвание канала: {channel_name}*',
                               parse_mode='markdown')
        await state.finish()
    except Exception as e:
        await bot.send_message(chat_id=message.chat.id,
                               text=f'*Ошибка:\n{e}\n\nВы ввели некорректный адрес или не выдали права администратора Боту в канале. Попробуйте ещё раз.*',
                               parse_mode='markdown')
        logger.info(e)
