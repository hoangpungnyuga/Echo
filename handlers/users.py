from loader import bot, dp
import asyncio
import ping3
import timeit
import logging
import time
from aiogram import types
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from data.functions.models import *
from aiogram.types.message_id import MessageId
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.markdown import link

logging.basicConfig(level=logging.DEBUG)

class States(StatesGroup):
	setnick = State()

def get_mention(user):
	return f"t.me/{user.username}" if user.username else f"t.me/None"

@dp.message_handler(commands=["rules"])
async def rules(message: Message):
	keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(text=f"RULES", url="https://telegra.ph/Rules-Echo-to-Kim-04-30"))
	await message.reply(f"Правила этого бота\nТак же по поводу вопросов писать @Sunzurai", reply_markup=keyboard)

@dp.message_handler(commands=["users"])
async def stats(message: Message):
	users = Users.select()
	await message.reply(f"👾На данный момент сейчас <code>{len(users)}</code> пользователей в боте")
@dp.message_handler(commands=["nick"])
async def nick(message: Message):
	await message.reply(f'Oops.. Это уже не юзабельно😾 Теперь используй /tag')

@dp.message_handler(commands=["ban"])
async def note(message: Message):
	if Admins.get_or_none(id=message.chat.id):
		await message.reply("Теперь это /mute")
	else:
		return
@dp.message_handler(commands=["unban"])
async def note(message: Message):
	if Admins.get_or_none(id=message.chat.id):
		await message.reply('Теперь это /unmute')
	else:
		return

@dp.message_handler(commands=["help"])
async def help(message: Message):
	await message.reply('<b>Я буду отправлять твои сообщения всем юзерам.</b>\n\n<b>⌖ Все что вас может интересовать</b>\n<b>></b> /start , /rules\n\n<b>⌖ Когда будет обновление бота?</b>\n<b>> <u>Завтра, если нет, то прочтите это сообщение еще раз!</u></b>', parse_mode="HTML")

@dp.message_handler(commands=["profile"])
async def profile(message: Message):
    users = Users.select() 
    user_id = message.from_user.id
    last_msg = message.message_id
    delay = Users.get(Users.id==message.chat.id).mute - datetime.now()
    dur = str(delay).split(".")[0]
    if dur.startswith("-"):
        dur = None
    username = message.from_user.username
    user = Users.get_or_none(Users.id == message.chat.id)
    tag_value = user.tag
    if Admins.get_or_none(id=message.chat.id):
        is_admin = True
    else:
        is_admin = False
    user = Users.get_or_none(id=user_id)
    if user:
        warns = user.warns
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    full_name = first_name
    if last_name:
        full_name += f' {last_name}'
    msgs_db = rdb.get("messages", [])
    await message.reply(f'Debug your profile info:\nName: {full_name}\nID:<code>{user_id}</code>\nUsername: @{username}\nMute:<code>{dur}</code>\nWarns:{warns}\nAdmin_status:{is_admin}\nUse_tag:{tag_value}\nUsers: {len(users)}\nlastmsg chat: {last_msg}, msg_sent: {len(msgs_db)}')

@dp.message_handler(commands=['warns'])
async def ping_telegram(message: types.Message):
    user_id = message.from_user.id
    user = Users.get_or_none(id=user_id)
    if user:
        warns = user.warns
        await message.reply(f'Warns: {warns}.\n3 варна - мут на 7 часов.')
    else:
        await message.reply("Looks like you didn't pass. please write /start")

@dp.message_handler(commands=['ping'])
async def ping_telegram(message: types.Message):
	pings = await message.reply("🤳PONG!")
	dc1 = ping3.ping('149.154.175.53')
	dc2 = ping3.ping('149.154.167.51')
	dc3 = ping3.ping('149.154.175.100')
	dc4 = ping3.ping('149.154.167.91')
	dc5 = ping3.ping('91.108.56.130')
	await pings.edit_text(f'🏓Пинг телеграм дата центров:\n\n\n🇺🇸DC1 MIA, Miami FL, USA:<code>{dc1}</code>.ms\n\n🇳🇱DC2 AMS, Amsterdam, NL:<code>{dc2}</code>.ms\n\n🇺🇸DC3* MIA, Miami FL, USA:<code>{dc3}</code>.ms\n\n🇳🇱DC4 AMS, Amsterdam, NL:<code>{dc4}</code>.ms\n\n🇸🇬DC5 SIN, Singapore, SG:<code>{dc5}</code>.ms', parse_mode="HTML")

@dp.message_handler(commands=["tag"])
async def toggle_tagging(message: Message):
	user, created = Users.get_or_create(id=message.chat.id)
	if user:
		if user.tag:
			Users.update(tag=False).where(Users.id==message.chat.id).execute()
			await message.reply("Ваши следующие сообщения <b>не</b> будут помечены вашим ником")
		else:
			Users.update(tag=True).where(Users.id==message.chat.id).execute()
			await message.reply("Ваши следующие сообщения будут помечены вашим ником и @username")

@dp.message_handler(commands=["start"])
async def hello(message: Message):
	if not Users.select().where(Users.id==message.chat.id).exists():
		Users.create(id=message.chat.id)
	await message.reply("Салам, это эхо-бот от создателей ILNAZ GOD и Ким💖💖.\n\nТвои сообщения будут отправляться всем пользователям Echo.\n\nДля получения более подробной информации, пожалуйста, ознакомьтесь с правилами.\n\n(Это точно Echo-to-All?) Точнее если быть -- <b>Echo to Kim</b>❤️")

async def send(message, *args, **kwargs):
	return (await message.copy_to(*args, **kwargs)), args[0]

async def Send(message, keyboard, reply_data):
	result = [{"sender_id": message.chat.id}]
	msgs = await asyncio.gather(*[
		send(message, user.id, reply_markup=keyboard, reply_to_message_id=get_reply_id(reply_data, user.id) if message.reply_to_message else None)
		for user in Users.select(Users.id)
        if user.id != message.chat.id or user.id == message.chat.id and (user.id != 5885645595 or message.chat.id != 5885645595)
	], return_exceptions=True)

	for msg_obj in msgs:
		if isinstance(msg_obj, tuple):
			msg, user_id = msg_obj
			if isinstance(msg, MessageId):
				result.append({"chat_id": user_id, "msg_id": msg.message_id})
	else:
		result.append({"chat_id": message.chat.id, "msg_id": message.message_id})
	print(result)
	msgs_db = rdb.get("messages", [])
	msgs_db.append(result)
	rdb.set("messages", msgs_db)

@dp.message_handler(content_types="any")
async def any(message: Message):
	if message.content_type == "pinned_message":
		return
	if datetime.now() < Users.get(Users.id==message.chat.id).mute and not Admins.get_or_none(id=message.chat.id):
		delay = Users.get(Users.id==message.chat.id).mute - datetime.now()
		dur = str(delay).split(".")[0]
		keyrules = InlineKeyboardMarkup().add(InlineKeyboardButton(text=f"RULES", url="https://telegra.ph/Rules-Echo-to-Kim-04-30"))
		return await message.reply(f"Ты сможешь писать только через {dur}\nПожалуйста, соблюдайте правила.", reply_markup=keyrules)
	if Users.get(Users.id==message.chat.id).tag:
		full_name = message.from_user.full_name
		username = message.from_user.username
		keyboard = InlineKeyboardMarkup().add(
		InlineKeyboardButton(f"{full_name}", url=f"t.me/{username}" if username else f"t.me/None")
		)
		if Admins.get_or_none(id=message.chat.id):
			keyboard.add(
			InlineKeyboardButton("ADMIN", url=f"t.me/{username}" if username else f"t.me/None")
			)
	else:
		keyboard = None

	Users.update(mute=datetime.now()).where(Users.id==message.chat.id).execute()
	if message.reply_to_message:
		reply_data = get_reply_data(message.chat.id, message.reply_to_message.message_id)
	if message.text or message.caption:
		if Users.get(Users.id==message.chat.id).last_msg == (message.text or message.caption):
			return await message.reply("Ваше сообщение похоже на предыдущее.")
		Users.update(last_msg=message.text or message.caption).where(Users.id==message.chat.id).execute()
	if is_flood(message.chat.id):
		Users.update(mute=datetime.now() + timedelta(hours=1)).where(Users.id==message.chat.id).execute()
		minchgod = InlineKeyboardMarkup().add(InlineKeyboardButton(text=f"#DEBUG", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
		ims = await message.reply("Это флуд. Вы были отключены от чата на 1 час", reply_markup=minchgod)
		await bot.pin_chat_message(ims.chat.id, ims.message_id)
		user_id = message.from_user.id
		message_id = message.reply_to_message.message_id
		try:
			await bot.send_message(-1001909107950, f"#FLOOD\n<b>ID:</b>{user_id}</b>")
		except: pass
		return
	users = Users.select()
	haha = await message.reply("Send...")
	start_time = time.monotonic()

	await Send(message, keyboard, reply_data if message.reply_to_message else None)
	end_time = time.monotonic()
	send_duration = end_time - start_time

	if send_duration < 1:
		send_duration_str = f"{int(send_duration * 1000)} миллисекунд"
	elif send_duration < 60:
		send_duration_str = f"{int(send_duration)} секунд"
	else:
		send_duration_min = int(send_duration // 60)
		send_duration_sec = int(send_duration % 60)
		send_duration_str = f"{send_duration_min} минуту {send_duration_sec} секунд"

	await haha.edit_text(f"Твоё сообщение было отправлено {len(users)} пользователям бота за <b>{send_duration_str}</b>", parse_mode="HTML")

#	await haha.delete()
