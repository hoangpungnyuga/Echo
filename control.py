# ⚖️ GPL-3.0 license
# 🏳️‍⚧️ Project on Mirai :<https://github.com/hoangpungnyuga/>
from functools import wraps
from datetime import datetime, timedelta
from aiogram import types
from data.functions.models import Users

def delayed_message(rate_limit: int, rate_limit_interval: int):
    def decorator(func):
        call_history = []

        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_time = datetime.now()
            call_history.append(current_time)

            # Очистка старых записей в истории вызовов
            call_history[:] = [call for call in call_history if current_time - call <= timedelta(seconds=rate_limit_interval)]

            if len(call_history) > rate_limit:
                return

            return await func(*args, **kwargs)

        return wrapper

    return decorator

def registered_only(func):
    async def wrapper(message: types.Message):
        user_id = message.chat.id

        if not Users.select().where(Users.id == user_id).exists():

            USER = f'<a href="https://t.me/{message.from_user.username}/">You</a>' if message.from_user.username else 'You'
            await message.answer(
                f"{USER} are not registered in the bot."
                "\nTo register type /start"
            )

            return

        return await func(message)

    return wrapper