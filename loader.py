# ⚖️ GPL-3.0 license
# 🏳️‍⚧️ Project on Mirai :<https://github.com/hoangpungnyuga/>
import logging
import asyncio
from aiogram.bot import Bot
from aiogram.types import ParseMode
from aiogram.dispatcher import Dispatcher
from configparser import ConfigParser
from aiogram.contrib.fsm_storage.memory import MemoryStorage

config = ConfigParser()
storage = MemoryStorage()
config.read("data/config.ini")
loop = asyncio.get_event_loop()

bot = Bot(token=config["aiogram"]["bot_token"], parse_mode=ParseMode.HTML)
dp = Dispatcher(bot=bot, loop=loop, storage=storage)
chat_log = config["aiogram"]["chat_log"]
chat_backup = config["aiogram"]["chat_backup"]
ownew = config["aiogram"]["ownew"]

support = "@Sunzurai or @wekosay" # Меняйте на свой по усмотрению

logging.basicConfig(filename="logs.log", level=logging.ERROR)
