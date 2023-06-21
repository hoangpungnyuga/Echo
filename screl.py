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
    dirp = "image/rick_astley.jpg"
    photo = InputFile(dirp)
    ss = ("<tg-spoiler>never gonna give you up</tg-spoiler>\nЯ задумался, в чем смысл этой команды, если есть traceback?\nИменно поэтому команда была удалена. Тут нечего искать.")
    await bot.send_photo(message.chat.id, photo, caption=ss)

@dp.callback_query_handler(text="del")
async def UQ(call: CallbackQuery):
	await call.message.delete()