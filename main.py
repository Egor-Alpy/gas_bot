# ======================================================================================================================
# MAIN ----- MAIN ----- MAIN ----- MAIN ----- MAIN ----- MAIN ----- MAIN ----- MAIN ----- MAIN ----- MAIN ---- MAIN ----
# ======================================================================================================================
# IMPORT ----- IMPORT ----- IMPORT ----- IMPORT ----- IMPORT ----- IMPORT ----- IMPORT ----- IMPORT ----- IMPORT -----
import asyncio

from aiogram import executor
import time

import core.commands.commands
from data.config import PROJECT_NAME

from core.commands.commands import set_commands
from core.logger_config import logger
from core.bot_creation import dp
from core.commands.commands import start_sending
import asyncio

from threading import Thread


# ON_STARTUP ----- ON_STARTUP ----- ON_STARTUP ----- ON_STARTUP ----- ON_STARTUP ----- ON_STARTUP ----- ON_STARTUP -----
async def on_startup(_):
    pass
    await set_commands()
    logger.debug(f'{PROJECT_NAME} has been started!')
    a = asyncio.create_task(start_sending())





def main():
    executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=on_startup)
    '''while True:
        try:
            executor.start_polling(
                dispatcher=dp,
                skip_updates=True,
                on_startup=on_startup
            )
            # logger.debug(f'{PROJECT_NAME} has been finished!')
        except Exception as e:
            # logger.error(f'Exception in the main execution block: {e}')
            time.sleep(5)'''


if __name__ == '__main__':
    main()



