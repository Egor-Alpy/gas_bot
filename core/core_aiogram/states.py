from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

import core
from core.core_aiogram.bot_creation import dp
from data.text import CMD_ADMIN, CMD_CLIENT
from core.database.database_main import table_users


class AddChannelStatesGroup(StatesGroup):
    get_id = State()


class SendMsgToAllStatesGroup(StatesGroup):
    get_msg = State()
    confirmation = State()


@dp.message_handler(commands=CMD_ADMIN + CMD_CLIENT, state=AddChannelStatesGroup.all_states + SendMsgToAllStatesGroup.all_states)
async def cancel_commands_admin(message: types.Message, state: FSMContext):
    text = str(message.text)[1:]
    await state.finish()
    LAN = table_users.get_user_language(message.chat.id)
    if text in CMD_CLIENT + CMD_ADMIN:
        await core.core_aiogram.commands.commands.COMMAND_FUNCTIONS_DICT[text](message, LAN)

