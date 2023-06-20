from aiogram import types
from aiogram.types import CallbackQuery, InputFile
from loader import dp, bot, support, chat_log

@dp.message_handler(lambda message: message.chat.type != types.ChatType.PRIVATE and str(message.chat.id) != str(chat_log))
async def leave_non_private_chats(message: types.Message):
    photo_path = "image/eurobeat.jpg"
    photo = InputFile(photo_path)
    ss = ("<b>I don't work in chats"
        "\nSince it's an anonymous echo bot.."
        "\nWrite to PM"
        "\nI'm leave..</b>")
    await bot.send_photo(message.chat.id, photo, caption=ss)
    await message.bot.leave_chat(message.chat.id)

@dp.message_handler(commands=["fix"])
async def val(message: types.Message):
    await message.answer(f'Действительно, а вообще пока-что этой команды не существует, но будет в будущем))\nКак и говорилось, пишите {support}')

@dp.callback_query_handler(text="del")
async def UQ(call: CallbackQuery):
	await call.message.delete()