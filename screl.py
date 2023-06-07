from aiogram import types
from aiogram.types import CallbackQuery
from loader import dp, support

@dp.message_handler(commands=["fix"])
async def val(message: types.Message):
    await message.answer(f'Действительно, а вообще пока-что этой команды не существует, но будет в будущем))\nКак и говорилось, пишите {support}')

@dp.callback_query_handler(text="del")
async def UQ(call: CallbackQuery):
	await call.message.delete()