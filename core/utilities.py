from core.core_aiogram.bot_creation import bot
from core.database.database_main import table_users, table_channels
from core.logger_config import logger
from data.config import ADMINS
from data.text import MSG


async def proxy_add_value(state, key, value):
    async with state.proxy() as data:
        data[key] = value


async def proxy_get_value(state, key):
    async with state.proxy() as data:
        return data[key]


async def proxy_get_all(state):
    async with state.proxy() as data:
        return data.as_dict()


async def check_user_subscriptions(user_id: int) -> bool:
    previous_subscription_status = table_users.get_subscription_status(user_id)
    channel_tags = table_channels.get_channel_tags()
    LAN = table_users.get_user_language(user_id)
    if not channel_tags:
        table_users.set_subscription_status('True', user_id)
        return True
    for channel_tag in channel_tags:
        '''try:'''
        user_channel_status = await bot.get_chat_member(chat_id='@' + channel_tag, user_id=user_id)
        if (user_channel_status['status'] not in ['creator', 'administrator', 'member'] and int(user_id) not
                in ADMINS):
            if previous_subscription_status == 'True':
                await bot.send_message(chat_id=user_id, text=MSG[LAN]['SUB']['CLOSED'], parse_mode='markdown')
            table_users.set_subscription_status('False', user_id)
            return False
        '''except Exception as e:
            if str(e) == 'User not found':
                logger.info(f'Bot does not have rights in [{channel_tag}] channel')
            else:
                logger.info(f'Error in check user sub: {e}')'''
    if previous_subscription_status == 'False':
        # await bot.send_message(chat_id=user_id, text=MSG[LAN]['SUB']['OPENED'], parse_mode='markdown')    MARKER MARKER MARKER MARK
        pass
    table_users.set_subscription_status('True', user_id)
    return True


async def handle_system_message(error):
    logger.info(f"SYSTEM_MESSAGE: {error}")
    for user_id in ADMINS:
        await bot.send_message(chat_id=user_id, text=f"SYSTEM_MESSAGE: {error}")
