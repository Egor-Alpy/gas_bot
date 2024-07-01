from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.core_aiogram.bot_creation import dp, bot
from core.database.database_main import table_users, table_channels
from data.text import BUTTONS


def get_interval_markup(callback) -> InlineKeyboardMarkup:
    LAN = table_users.get_user_language(callback.message.chat.id)
    markup_interval = InlineKeyboardMarkup()
    current_interval = table_users.get_user_interval(callback.message.chat.id)
    btn_list = []
    if LAN == 'RUS':
        btn_name_list = {'30 сек': 'interval_30', '1 мин': 'interval_60', '3 мин': 'interval_180',
                         '5 мин': 'interval_300',
                         '15 мин': 'interval_900', '30 мин': 'interval_1800', '1 ч': 'interval_3600',
                         '4 ч': 'interval_14400',
                         '12 ч': 'interval_43200', '24 ч': 'interval_86400'}
    elif LAN == 'ENG':
        btn_name_list = {'30 sec': 'interval_30', '1 min': 'interval_60', '3 min': 'interval_180',
                         '5 min': 'interval_300',
                         '15 min': 'interval_900', '30 min': 'interval_1800', '1 h': 'interval_3600',
                         '4 h': 'interval_14400',
                         '12 h': 'interval_43200', '24 h': 'interval_86400'}
    for btn_name, callback_name in btn_name_list.items():
        if str(current_interval) == callback_name.split('_')[1]:
            btn_name = '»»»    ' + btn_name + '    «««'
        btn = InlineKeyboardButton(btn_name, callback_data=callback_name)
        btn_list.append(btn)
        if len(btn_list) == 2:
            markup_interval.add(btn_list[0], btn_list[1])
            btn_list = []
    b_back = InlineKeyboardButton(BUTTONS[LAN]['BACK'], callback_data='back_to_settings')
    markup_interval.add(b_back)
    return markup_interval


def get_language_markup(callback) -> InlineKeyboardMarkup:
    markup_language = InlineKeyboardMarkup()
    current_language = table_users.get_user_language(callback.message.chat.id)
    btn_name_list = {'Русский': 'language_RUS', 'English': 'language_ENG'}
    for btn_name, callback_name in btn_name_list.items():
        if str(current_language) == callback_name.split('_')[-1]:
            btn_name = '»»»    ' + btn_name + '    «««'
        btn = InlineKeyboardButton(btn_name, callback_data=callback_name)
        markup_language.add(btn)
    LAN = current_language
    b_back = InlineKeyboardButton(BUTTONS[LAN]['BACK'], callback_data='back_to_settings')
    markup_language.add(b_back)
    return markup_language


def get_channels_inlinekeyboard_4delete() -> InlineKeyboardMarkup:
    rows = table_channels.get_all_channels_info()
    channels_markup = InlineKeyboardMarkup()
    for i in range(len(rows)):
        channels_markup.add(InlineKeyboardButton(f"{rows[i][2]} | @{rows[i][1]} | {rows[i][0]}", callback_data='DELETE_CHANNEL_' + rows[i][0]))
    return channels_markup


@dp.callback_query_handler(lambda call: call.data.startswith('DELETE_CHANNEL_'))
async def del_channel(callback: types.CallbackQuery) -> None:
    channel_id = callback.data.split('_')[-1]
    table_channels.del_channel(channel_id)
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=get_channels_inlinekeyboard_4delete())
