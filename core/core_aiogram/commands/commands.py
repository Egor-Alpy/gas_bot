import types

from data.text import CMD_ADMIN, CMD_CLIENT, CMD_MENU, CMD_HELP, CMD_DEL_CHANNEL, CMD_ADD_CHANNEL, CMD_SEND_MSG
from core.core_aiogram.commands.client import *
from core.core_aiogram.commands.admin import *
from core.main_loop import *
from core.database.database_main import table_users


async def set_commands():
    await bot.set_my_commands(
        [
            types.BotCommand(f'/{CMD_MENU}', "menu"),
            types.BotCommand(f'/{CMD_HELP}', "help"),
        ]
    )


@dp.message_handler(commands=['start'])
async def start_function(message: types.Message):
    await start_func(message)


@dp.message_handler(commands=CMD_CLIENT + CMD_ADMIN)
async def commands_all(message: types.Message) -> None:
    LAN = table_users.get_user_language(message.chat.id)
    if message.text[1:] in CMD_ADMIN:
        if message.chat.id not in ADMINS:
            await bot.send_message(chat_id=message.chat.id, text=MSG[LAN]['NO_ROOTS'])
            return
    if not await check_user_subscriptions(message.chat.id):
        await bot.send_message(chat_id=message.chat.id, text=get_msg_channels_to_subscribe(LAN), parse_mode='html')
    else:
        await COMMAND_FUNCTIONS_DICT[str(message.text)[1:]](message, LAN)


async def help_func(message: types.Message, LAN):
    if message.chat.id not in ADMINS:
        await bot.send_message(chat_id=message.chat.id, text=MSG[LAN]['CLIENT']['HELP'], parse_mode='markdown')
    else:
        await bot.send_message(chat_id=message.chat.id, text=MSG[LAN]['ADMIN']['HELP'], parse_mode='markdown')


@dp.message_handler()
async def all_text_handler(message: types.Message):
    LAN = table_users.get_user_language(message.chat.id)
    if not await check_user_subscriptions(message.chat.id):
        await bot.send_message(chat_id=message.chat.id,
                               text=get_msg_channels_to_subscribe(LAN),
                               parse_mode='markdown')
    else:
        await message.reply(text=MSG[LAN]['OTHER'],
                            parse_mode='markdown') # comment all function with handler





COMMAND_FUNCTIONS_DICT = {
    CMD_MENU: settings_func,
    CMD_HELP: help_func,
    CMD_ADD_CHANNEL: add_channel,
    CMD_DEL_CHANNEL: del_channel,
    CMD_SEND_MSG: send_msg_to_all
}
