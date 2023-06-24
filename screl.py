from aiogram import types
from data.functions.models import Users
from aiogram.types import CallbackQuery, InputFile
from loader import dp, bot, chat_log
from control import delayed_message

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

async def check_floodwait(message):
	try:
		await bot.send_chat_action(chat_id=message.chat.id, action=types.ChatActions.TYPING)
		return False, 0
	except Exception as e:
		if "FloodWait" in str(e):
			seconds = int(str(e).split()[1])
			return True, seconds
		else:
			return False, 0

@dp.message_handler(commands=["fix"])
@delayed_message(rate_limit=2, rate_limit_interval=5)
async def val(message: types.Message):
    file = "image/rick_astley.jpg"
    photo = InputFile(file)
    ss = ("<tg-spoiler>never gonna give you up</tg-spoiler>\nЯ задумался, в чем смысл этой команды, если есть traceback?\nИменно поэтому команда была удалена. Тут нечего искать.")
    await bot.send_photo(message.chat.id, photo, caption=ss)

@dp.callback_query_handler(text="del")
async def UQ(call: CallbackQuery):
    message = call.message

    if message.pinned_message:
        await call.bot.unpin_chat_message(chat_id=message.chat.id)

    await call.message.delete()

@dp.callback_query_handler(lambda call: call.data == f"confirm_registration={call.from_user.id}")
async def registration(callback_query: types.CallbackQuery):
	user_id = callback_query.from_user.id

	if not Users.select().where(Users.id == user_id).exists():
		try:
			Users.create(id=user_id)
		except:
			pass
		
		await bot.answer_callback_query(callback_query.id, "Регистрация подтверждена.🔗")
		await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
		await bot.send_message(
			callback_query.message.chat.id,
				"<b>Отлично, вы зарегистрированы."
				"\nТеперь вы можете писать всем юзерам Echo."
				"\n\nДля более подробных деталей о командах и прочих, вы можете воспользоваться командой /help</b>"
		)

	else:
		await bot.answer_callback_query(callback_query.id, "Вы уже зарегистрированы в боте.")
		await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
