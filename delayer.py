from functools import wraps
from datetime import datetime, timedelta

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
