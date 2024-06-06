# ======================================================================================================================
# MAIN ----- MAIN ----- MAIN ----- MAIN ----- MAIN ----- MAIN ----- MAIN ----- MAIN ----- MAIN ----- MAIN ---- MAIN ----
# ======================================================================================================================
# IMPORT ----- IMPORT ----- IMPORT ----- IMPORT ----- IMPORT ----- IMPORT ----- IMPORT ----- IMPORT ----- IMPORT -----
from aiogram import executor
import time

from data.config import PROJECT_NAME

from core.core_aiogram.commands.commands import set_commands
from core.logger_config import logger
from core.core_aiogram.bot_creation import dp
from core.main_loop import start_sending
import asyncio

from multiprocessing import Process


# ON_STARTUP ----- ON_STARTUP ----- ON_STARTUP ----- ON_STARTUP ----- ON_STARTUP ----- ON_STARTUP ----- ON_STARTUP -----
async def on_startup(_):
    await set_commands()
    logger.debug(f'{PROJECT_NAME} has been started!')


def start_message_sender():
    asyncio.run(start_sending())


def main():
    while True:
        try:
            executor.start_polling(
                dispatcher=dp,
                skip_updates=True,
                on_startup=on_startup
            )
            logger.debug(f'{PROJECT_NAME} has been finished!')
        except Exception as e:
            logger.error(f'Exception in the main execution block: {e}')
            time.sleep(5)


if __name__ == '__main__':
    p1 = Process(target=start_message_sender, daemon=True)
    p1.start()
    logger.info('Thread: Sending process has been started!')
    main()
    logger.info('Thread: Main process has been started!')









