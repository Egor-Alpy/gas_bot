# ======================================================================================================================
# BOT CREATION ----- BOT CREATION ----- BOT CREATION ----- BOT CREATION ----- BOT CREATION ----- BOT CREATION ----- BOT
# ======================================================================================================================
# IMPORT ----- IMPORT ----- IMPORT ----- IMPORT ----- IMPORT ----- IMPORT ----- IMPORT ----- IMPORT ----- IMPORT ----- I
from data.config import TOKEN
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage


# temporary storage
storage = MemoryStorage()

# Инициализация бота
bot = Bot(TOKEN)
dp = Dispatcher(bot=bot, storage=storage)


