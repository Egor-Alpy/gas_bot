
from data.text import CMD_START, CMD_ADMIN, CMD_CLIENT, CMD_MENU, CMD_HELP, CMD_DEL_CHANNEL, CMD_ADD_CHANNEL, \
    CMD_SEND_MSG
from core.commands.client import *
from core.commands.admin import *
from core.database.database_main import table_users
from core.logger_config import logger


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
            await bot.send_message(chat_id=message.chat.id, text=MSG['RUS']['NO_ROOTS'])
            return
    if message.text == '/start':
        if str(message.from_user.id) not in table_users.get_all_user_id():
            table_users.add_user(user_id=message.from_user.id, username=message.from_user.username,
                                 name=message.from_user.first_name, surname=message.from_user.last_name)
            logger.info(
                f'User has been added to the DB [id: {message.from_user.id}, username: {message.from_user.username}]')
    if not await check_user_subscriptions(message.chat.id):
        await bot.send_message(chat_id=message.chat.id, text=get_msg_channels_to_subscribe(), parse_mode='markdown')
    else:
        await COMMAND_FUNCTIONS_DICT[str(message.text)[1:]](message)


async def help_func(message: types.Message):
    if message.chat.id not in ADMINS:
        await bot.send_message(chat_id=message.chat.id, text=MSG['RUS']['CLIENT']['HELP'], parse_mode='markdown')
    else:
        await bot.send_message(chat_id=message.chat.id, text=MSG['RUS']['ADMIN']['HELP'], parse_mode='markdown')


@dp.message_handler()
async def all_text_handler(message: types.Message):
    if not await check_user_subscriptions(message.chat.id):
        await bot.send_message(chat_id=message.chat.id,
                               text=get_msg_channels_to_subscribe(),
                               parse_mode='markdown')
    else:
        await message.reply(text=MSG['RUS']['OTHER'],
                            parse_mode='markdown')


COMMAND_FUNCTIONS_DICT = {
    CMD_START: start_func,
    CMD_MENU: settings_func,
    CMD_HELP: help_func,
    CMD_ADD_CHANNEL: add_channel,
    CMD_DEL_CHANNEL: del_channel,
    CMD_SEND_MSG: send_msg_to_all
}
