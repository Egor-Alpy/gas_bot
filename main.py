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
async def on_startup(_):
    await set_commands()
    logger.debug(f'{PROJECT_NAME} MAIN has been created!')


def main_loop():
    while True:
        try:
            executor.start_polling(
                dispatcher=dp,
                skip_updates=True,
                on_startup=on_startup
            )
            logger.debug(f'{PROJECT_NAME} has been finished!')
        except KeyboardInterrupt:
            logger.debug(f'{PROJECT_NAME} main loop has been finished!')
            exit()
        except Exception as e:
            logger.error(f'Exception in the main_loop execution block: {e}')
            time.sleep(100)


def infinity_sending_loop():
    while True:
        try:
            logger.debug(f'Infinity loop has been started')
            asyncio.run(start_sending())
        except KeyboardInterrupt:
            logger.debug(f'Infinity loop has been finished!')
            exit()
        except Exception as e:
            logger.error(f'Exception in the infinity loop execution block: {e}')
            time.sleep(100)


def main():
    try:
        # 02
        process = Process(target=infinity_sending_loop)
        process.start()
        # 01
        main_loop()
    except KeyboardInterrupt:
        logger.debug(f'{PROJECT_NAME} main_loop has been finished!')
        exit()
    except Exception as e:
        logger.error(f'Exception in the main_loop execution block: {e}')


if __name__ == '__main__':
    main()
