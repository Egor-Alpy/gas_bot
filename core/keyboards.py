from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.bot_creation import dp, bot
from core.database.database_main import table_users, table_channels


def get_interval_markup(callback):
    markup_interval = InlineKeyboardMarkup()
    current_interval = table_users.get_user_interval(callback.message.chat.id)
    btn_list = []
    btn_name_list = {'30 сек': 'interval_30', '1 мин': 'interval_60', '5 мин': 'interval_300', '15 мин': 'interval_900',
                     '1 ч': 'interval_3600', '4 ч': 'interval_14400', '12 ч': 'interval_43200',
                     '24 ч': 'interval_86400'}
    for btn_name, callback_name in btn_name_list.items():
        if str(current_interval) == callback_name.split('_')[1]:
            btn_name = '»»»    ' + btn_name + '    «««'
        btn = InlineKeyboardButton(btn_name, callback_data=callback_name)
        btn_list.append(btn)
        if len(btn_list) == 2:
            markup_interval.add(btn_list[0], btn_list[1])
            btn_list = []
    b_back = InlineKeyboardButton('« Назад', callback_data='back_to_settings')
    markup_interval.add(b_back)
    return markup_interval


def get_channels_inlinekeyboard_4delete():
    rows = table_channels.get_all_channels_info()
    channels_markup = InlineKeyboardMarkup()
    for i in range(len(rows)):
        channels_markup.add(InlineKeyboardButton(f"{rows[i][2]} | @{rows[i][1]} | {rows[i][0]}", callback_data='DELETE_CHANNEL_' + rows[i][0]))
    return channels_markup


@dp.callback_query_handler(lambda call: call.data.startswith('DELETE_CHANNEL_'))
async def del_channel(callback: types.CallbackQuery):
    channel_id = callback.data.split('_')[-1]
    table_channels.del_channel(channel_id)
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=get_channels_inlinekeyboard_4delete())
