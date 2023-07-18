# ⚖️ GPL-3.0 license
# 🏳️‍⚧️ Project on Mirai :<https://github.com/hoangpungnyuga/>
import os
import time
import platform
from aiogram import types, __version__
from data.functions.models import Users
from aiogram.types import CallbackQuery, InputFile
from loader import dp, bot, chat_log
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
		except:
			pass
		
		await bot.answer_callback_query(call.id, "Регистрация подтверждена.🔗")
		await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
		await bot.send_message(
			call.message.chat.id,
				"<b>Отлично, вы зарегистрированы."
				"\nТеперь вы можете писать всем юзерам Echo."
				"\n\nДля более подробных деталей о командах и прочих, вы можете воспользоваться командой /help</b>"
		)

	else:
		await bot.answer_callback_query(call.id, "Вы уже зарегистрированы в боте.")
		await bot.delete_message(call.message.chat.id, call.message.message_id)

@dp.message_handler(commands=['info', 'version', 'v'], commands_prefix='!-/')
@delayed_message(rate_limit=2, rate_limit_interval=5)
async def versions(message: types.Message):
	v = "14.1"

	edit = time.ctime(os.path.getmtime('screl.py'))

	photo = InputFile('image/initialD.jpg')

	if platform.system() == 'Linux':
		s = f", {platform.freedesktop_os_release().get('NAME', '')}"

	elif platform.system() == 'Windows':
		s = f", {platform.win32_ver()[0]}"

	else:
		s = ""

	try:
		await message.answer_photo(

		photo=photo,

		caption=(
		"<code>🏳️‍🌈Mirai project: Echo🏳️‍⚧️</code>"
		f"\nVersion echo: <i>{v}</i>"
		f"\nVersion edition on: <i>{edit}</i>"
		"\nOS platform: <i>%s{}</i>"
		f"\nPython V: <i>{platform.python_version()}</i>"
		f"\nAiogram V: {__version__}"
		"\n\nProject on mirai, also minch"
		"\nCode to t.me/untitled7bot closed."
		"\nSup in the github on mirai. github.com/hoangpungnyuga".format(s)
		% platform.system())
		)

	except Exception as e:
		await message.answer(str(e))

@dp.message_handler(commands=['mirai', 'minch', 'child'])
async def dev(message: types.Message):
	if message.text == "/mirai":
		await message.answer("да, кстати это @Sunzurai")

	elif message.text == "/minch":
		await message.answer("ну, это уже @wekosay")

	elif message.text == "/child":
		await message.answer("Пока ты спишь, твоя мать ночами деньги ртом зарабатывает, а ты в это время пишешь такое?!..", reply=True)
	

@dp.callback_query_handler(lambda c: c.data == 'not0username!')
@delayed_message(rate_limit=1, rate_limit_interval=15)
async def not_username(callback_query: types.CallbackQuery):
    gif_url = 'https://raw.githubusercontent.com/hoangpungnyuga/hoangpungnyuga/main/any/project-mirai/rick-rolled-surprise.gif'
    debug = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text="#DEBUG", url="http://news.rr.nihalnavath.com/posts/--28613ab8")) # type: ignore
    commit = '<i>У этого пользователя username отсутствует.</i>'
    await bot.send_animation(callback_query.from_user.id, gif_url, caption=commit, reply_markup=debug, has_spoiler=True)