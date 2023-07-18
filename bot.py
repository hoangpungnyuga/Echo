# ⚖️ GPL-3.0 license
# 🏳️‍⚧️ Project on Mirai :<https://github.com/hoangpungnyuga/>
import argparse
import pytz
import time
from handlers import bot, dp
from aiogram.utils import executor
from datetime import datetime
from colorama import init, Fore, Back, Style 
from data.functions.models import Admins
from loader import *

class Notification():
    def __init__(self):
        self.admins = Admins.select(Admins.id)
        self.date = datetime.now(pytz.timezone('Europe/Moscow')).date()

    async def on(self, a):
        for admin in self.admins:
            try:
                current_time = time.strftime('%H:%M', time.localtime())
                me = await bot.get_me()
                await bot.send_message(admin, f"{self.date.strftime('%d.%m')} {current_time}: <i>{me.first_name}</i> is startup now.")
            except:
                pass
    
    async def off(self, a):
        for admin in self.admins:
            try:
                current_time = time.strftime('%H:%M', time.localtime())
                me = await bot.get_me()
                await bot.send_message(admin, f"{self.date.strftime('%d.%m')} {current_time}: <i>{me.first_name}</i> is shutdown now.")
            except:
                pass

def parse_args():
    parser = argparse.ArgumentParser(description='Bot Command Line Options')
    parser.add_argument('-i', '--info', action='store_true', help="Info to dev and bot")

    return parser.parse_args()

def print_info():
    info = """
    GPL-3.0 license

    - 2023.04.15 start echo

    Project on Mirai also Minch
    This is an echo bot for anonymous communication on Telegram.


    Create this bot: Mirai
                     https://t.me/wekosay/
                     https://github.com/hoangpungnyuga/
                      wekosay@dnmx.org
                      wekosay@gtfcy37qyzor7kb6blz2buwuu5u7qjkycasjdf3yaslibkbyhsxub4yd.onion | Hichiriki
    """

    print(info)


if __name__ == "__main__":
    args = parse_args()

    if args.info:
        print_info()
    else:
        init()
        print(Back.WHITE + Fore.BLUE + "/load" + Style.RESET_ALL)

        strike = Notification()
        executor.start_polling(dp, on_startup=strike.on, on_shutdown=strike.off, skip_updates=True)

