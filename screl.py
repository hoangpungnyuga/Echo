import asyncio
from aiogram import types
from data.functions.models import Users
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram.dispatcher import FSMContext
from loader import dp, bot, chat_log
from data.functions.models import get_reply_data, get_reply_sender
from control import delayed_message

@dp.message_handler(lambda message: message.chat.type != types.ChatType.PRIVATE and str(message.chat.id) != str(chat_log))
async def leave_non_private_chats(message: types.Message):
    photo_path = "image/eurobeat.jpg"
    photo = InputFile(photo_path)
    ss = (
		"<b>I don't work in chats"
        "\nSince it's an anonymous echo bot.."
        "\nWrite to PM"
        "\nI'm leave..</b>"
		)
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

    await call.message.delete()

@dp.callback_query_handler(lambda call: call.data == f"confirm_registration={call.from_user.id}")
async def registration(call: types.CallbackQuery):
	user_id = call.from_user.id

	if not Users.select().where(Users.id == user_id).exists():
		try:
			Users.create(id=user_id)
		except Exception as e:
			return await call.message.answer(str(e))

		await bot.answer_callback_query(call.id, "Регистрация подтверждена.🔗")
		await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
		await bot.send_message(
			call.message.chat.id,
				"<b>Отлично, вы зарегистрированы."
				"\nТеперь вы можете писать всем юзерам этого бота."
				"\n\nДля более подробных деталей о командах и прочих, вы можете воспользоваться командой /help</b>"
		)

	else:
		await bot.answer_callback_query(call.id, "Вы уже зарегистрированы в боте.")
		await bot.delete_message(call.message.chat.id, call.message.message_id)

@dp.callback_query_handler(lambda c: c.data == 'not0username!')
@delayed_message(rate_limit=1, rate_limit_interval=15)
async def not_username(callback_query: types.CallbackQuery):
    gif_url = 'https://raw.githubusercontent.com/hoangpungnyuga/hoangpungnyuga/main/any/project-mirai/rick-rolled-surprise.gif'
    debug = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text="#DEBUG", url="http://news.rr.nihalnavath.com/posts/--28613ab8")) # type: ignore
    commit = '<i>У этого пользователя username отсутствует.</i>'
    await bot.send_animation(callback_query.from_user.id, gif_url, caption=commit, reply_markup=debug, has_spoiler=True)

@dp.callback_query_handler(lambda query: query.data.startswith("delete_msg="))
async def delete_msg_callback(query: CallbackQuery):
    message_id = int(query.data.split('=')[1])
    replies = get_reply_data(query.from_user.id, message_id)
    sender_id = get_reply_sender(query.from_user.id, message_id)

    notificate = await query.message.answer(
        "Удаляю это сообщение..",
        reply=True
    )

    async def delete_messages():
        try:
            await asyncio.gather(*[
                bot.delete_message(data["chat_id"], data["msg_id"]) # type: ignore
                for data in replies # type: ignore
                if data["chat_id"] != sender_id and data["chat_id"] != query.from_user.id # type: ignore
            ], return_exceptions=True)
        except Exception as e:
            await notificate.edit_text(f"Удалить у всех не получилось. По причине: {e}")

    # Запуск асинхронной задачи в фоне
    asyncio.create_task(delete_messages())

    await bot.edit_message_reply_markup(notificate.chat.id, notificate.reply_to_message.message_id, reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("DELETED", callback_data="s"))) # type: ignore

    try:
        await notificate.edit_text("🗑️ Удалено")
        await asyncio.sleep(5)
        await bot.delete_message(notificate.chat.id, notificate.message_id)
    except Exception as e:
        await bot.send_message(query.from_user.id, f"Возникла ошибка при удалении: {e}")
