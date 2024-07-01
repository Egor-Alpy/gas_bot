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

from multiprocessing import Process
from core.main_loop import start_sending
import asyncio


# ON_STARTUP ----- ON_STARTUP ----- ON_STARTUP ----- ON_STARTUP ----- ON_STARTUP ----- ON_STARTUP ----- ON_STARTUP -----
# Infinity loop section
def start_message_sender():
    asyncio.run(start_sending())


def start_infinity_loop_process():
    process_sending_messages = Process(target=start_message_sender).start()
    logger.info('PROCESS: INFINITY LOOP process has been started!')


async def on_startup(_):
    await set_commands()
    logger.debug(f'{PROJECT_NAME} MAIN has been created!')


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
            time.sleep(100)


if __name__ == '__main__':
    process_main = Process(target=main).start()
    start_infinity_loop_process()
