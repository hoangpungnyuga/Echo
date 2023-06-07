from loader import bot, dp, chat_log, support
import asyncio
import ping3
import logging
import psutil
import time
import pytz
import traceback
from peewee import DoesNotExist
from aiogram import types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from data.functions.models import *
from aiogram.types.message_id import MessageId
from delayer import delayed_message
from screl import UQ
from datetime import datetime, timedelta
logging.basicConfig(level=logging.DEBUG)

def get_mention(user):
	return f"t.me/{user.username}" if user.username else f"t.me/None"

@dp.message_handler(commands=["rules"])
@delayed_message(rate_limit=2, rate_limit_interval=5)
async def rules(message: Message):
	keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(text=f"RULES", url="https://telegra.ph/Rules-Echo-to-Kim-04-30")) # type: ignore
	await message.reply(f"Правила этого бота\nТак же по поводу вопросов писать\n<b>>></b> {support}", reply_markup=keyboard)

@dp.message_handler(commands=["users"])
@delayed_message(rate_limit=2, rate_limit_interval=5)
async def stats(message: Message):
	users = Users.select()
	await message.reply(f"👾 На данный момент сейчас <code>{len(users)}</code> пользователей в боте")

@dp.message_handler(commands=["nick"])
@delayed_message(rate_limit=2, rate_limit_interval=5)
async def nick(message: Message):
	await message.reply(f'Oops.. Это не юзабельно!😾 Вместо этого используй /tag')

@dp.message_handler(commands=["ban"])
@delayed_message(rate_limit=2, rate_limit_interval=5)
async def ban(message: Message):
	if Admins.get_or_none(id=message.chat.id):
		await message.reply("Теперь это /mute")
	else:
		return
@dp.message_handler(commands=["unban"])
@delayed_message(rate_limit=2, rate_limit_interval=5)
async def unban(message: Message):
	if Admins.get_or_none(id=message.chat.id):
		await message.reply('Теперь это /unmute')
	else:
		return

@dp.message_handler(commands=["help"])
@delayed_message(rate_limit=2, rate_limit_interval=5)
async def help(message: Message):
	await message.reply(
			'<b>Я буду отправлять твои сообщения всем юзерам.</b>\n\n'
			'<b>⌖ Все что вас может интересовать</b>\n'
			'<b>></b> /start , /rules\n\n'
			'<b>⌖ Когда будет обновление бота?</b>\n'
			'<b>><u> Завтра, если нет, то прочтите это сообщение еще раз!</u></b>', parse_mode="HTML")

@dp.message_handler(commands=["profile"])
@delayed_message(rate_limit=2, rate_limit_interval=5)
async def profile(message: Message):
	user = Users.get_or_none(Users.id == message.chat.id)
	users = Users.select()
	last_msg = message.message_id
	username = f'@{message.from_user.username}' if message.from_user.username else "undefined"
	delay = Users.get(Users.id==message.chat.id).mute - datetime.now()
	dur = str(delay).split(".")[0]
	if dur.startswith("-"):
		dur = "undefined"
	if Admins.get_or_none(id=message.chat.id):
		is_admin = True
	else:
		is_admin = False
	msgs_db = rdb.get("messages", [])
	await message.reply("Debug your profile info:\n"
				f"Name: {message.from_user.full_name}\n"
				f"ID: <code>{message.from_user.id}</code>\n"
				f"Username: {username}\n"
				f"Mute: {dur}\n"
				f"Warns: {user.warns}\n"
				f"Admin_status: {is_admin}\n"
				f"Use_tag: {user.tag}\n"
				f"Users: {len(users)}\n"
				f"lastmsg chat: {last_msg}, msg_sent: {len(msgs_db)}")

@dp.message_handler(commands=['warns'])
@delayed_message(rate_limit=2, rate_limit_interval=5)
async def warns(message: types.Message):
	user = Users.get_or_none(Users.id == message.chat.id)
	await message.reply(f'Warns: {user.warns}.\n3 варна - мут на 7 часов.')

@dp.message_handler(commands=['ping'])
@delayed_message(rate_limit=2, rate_limit_interval=10)
async def ping_telegram(message: types.Message):
	pings = await message.reply("🤳PONG!")
	try:
		dc1 = ping3.ping('149.154.175.53')
		dc2 = ping3.ping('149.154.167.51')
		dc3 = ping3.ping('149.154.175.100')
		dc4 = ping3.ping('149.154.167.91')
		dc5 = ping3.ping('91.108.56.130')
		await pings.edit_text(f'🏓Пинг телеграм дата центров:\n\n\n'
							f'🇺🇸DC1 MIA, Miami FL, USA:<code>{dc1}</code>.ms\n\n'
							f'🇳🇱DC2 AMS, Amsterdam, NL:<code>{dc2}</code>.ms\n\n'
							f'🇺🇸DC3* MIA, Miami FL, USA:<code>{dc3}</code>.ms\n\n'
							f'🇳🇱DC4 AMS, Amsterdam, NL:<code>{dc4}</code>.ms\n\n'
							f'🇸🇬DC5 SIN, Singapore, SG:<code>{dc5}</code>.ms', parse_mode="HTML")
	except PermissionError as e:
		if isinstance(e, PermissionError) and str(e) == "[Errno 13] Permission denied":
			await pings.edit_text(f"Ошибка:(\nЭто - Permission denied\nПопробуй /fix\nЕсли же вы видите это, пишите {support}")
		else:
			error_message = traceback.format_exc()  # Получение полного сообщения об ошибке
			await pings.edit_text(f"Ошибка:(\n{error_message}\nПопробуй /fix\nЕсли же вы видите это, пишите {support}")

@dp.message_handler(commands=["life"])
@delayed_message(rate_limit=2, rate_limit_interval=5)
async def get_system_stats(message: types.Message):
	hey = await message.reply("I'm counting..")
	await asyncio.sleep(1)
	try:
		user = Users.get_or_none(Users.id == message.chat.id)
		if user:
			start_time = time.monotonic()
			cpu_percent = psutil.cpu_percent()
			mem_info = psutil.virtual_memory()
			mem_percent = mem_info.percent
			mem_free_percent = mem_info.available * 100 / mem_info.total
			swap_info = psutil.swap_memory()
			swap_percent = swap_info.percent
			swap_free_percent = swap_info.free * 100 / swap_info.total
			disk_usage = psutil.disk_usage('/')
			disk_percent = disk_usage.percent
			disk_free_percent = 100 - disk_percent
			tz = pytz.timezone('Europe/Moscow') # Менять на своё усмотрение.
			now_eest = datetime.now(tz)
			format_date = now_eest.strftime("%Y-%m-%d %H:%M:%S")
			end_time = time.monotonic()
			vol_duration = end_time - start_time
			if vol_duration < 1:
					vol_duration_str = f"{int(vol_duration * 1000)} ms"
			elif vol_duration < 60:
				vol_duration_str = f"{int(vol_duration)} s"
			else:
				vol_duration_min = int(vol_duration // 60)
				vol_duration_sec = int(vol_duration % 60)
				vol_duration_str = f"{vol_duration_min} m {vol_duration_sec} s"

			google = ping3.ping('8.8.8.8', unit="ms", timeout=1) or "failed:(" # DNS Google.
			"""Если же это не работает, проверь - 'ping 8.8.8.8'
			Если ответ - 'ping: socket: Operation not permitted'
			Попробуй ' sudo sysctl -w net.ipv4.ping_group_range='0 2147483647' '"""

			response = f"Status machine life🕊\nCommand completed in {vol_duration_str}.\n\n"

			response += f"Time ping <code>8.8.8.8</code> completed in <code>{google:.3f}</code>.ms\n"
			if cpu_percent > 97:
				response += f"‼️CPU: {cpu_percent}%‼️\n"
			else:
				response += f">CPU: {cpu_percent}%\n"

			if mem_percent > 96:
				response += f"‼️RAM: {mem_percent:.1f}% / Free: {mem_free_percent:.1f}%‼️\n"
			else:
				response += f">RAM: {mem_percent:.1f}% / Free: {mem_free_percent:.1f}%\n"

			if not swap_percent == 0:
				response += f">Swap: {swap_percent:.1f}% / Free: {swap_free_percent:.1f}%\n"
			else:
				pass

			if disk_percent > 98:
				response += f"‼️Disk Usage: {disk_percent:.1f}% / Free: {disk_free_percent:.1f}%‼️\n"
			else:
				response += f">Disk Usage: {disk_percent:.1f}% / Free: {disk_free_percent:.1f}%\n"

			response += f"`Current date and time in RU Donetsk: {format_date}"
			DS = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Удалить", callback_data="del")) # type: ignore
			await hey.edit_text(response, reply_markup=DS)
	except PermissionError as e:
		if isinstance(e, PermissionError) and str(e) == "[Errno 13] Permission denied":
			await hey.edit_text(f"Ошибка:(\nЭто - Permission denied\nПопробуй /fix\nЕсли же вы видите это, пишите {support}")
		else:
			error_message = traceback.format_exc()
			await hey.edit_text(f"Ошибка:(\n{error_message}\nЕсли же вы видите это, пишите {support}")

@dp.message_handler(commands=["tag"])
@delayed_message(rate_limit=2, rate_limit_interval=3)
async def toggle_tagging(message: Message):
    try:
        user = Users.get(Users.id == message.chat.id)
        if user:
            if user.tag:
                Users.update(tag=False).where(Users.id == message.chat.id).execute()
                await message.reply("Ваши следующие сообщения <b>не</b> будут помечены вашим ником")
            else:
                Users.update(tag=True).where(Users.id == message.chat.id).execute()
                await message.reply("Ваши следующие сообщения будут помечены вашим ником и @username")
    except DoesNotExist:
        # Если пользователя нет в Users (DATABASE), то добавить его.
        Users.create(id=message.chat.id, tag=True)
        await message.reply("Ваши следующие сообщения будут помечены вашим ником и @username\n<tg-spoiler>Вы были зарегистрированы в боте.</tg-spoiler>", parse_mode="HTML")

@dp.message_handler(commands=["start"])
@delayed_message(rate_limit=2, rate_limit_interval=5)
async def start(message: Message):
	if not Users.select().where(Users.id==message.chat.id).exists():
		Users.create(id=message.chat.id)
	await message.reply('Салам, это эхо-бот от создателей ILNAZ GOD и Ким💖💖.\n\n'
			'Твои сообщения будут отправляться всем пользователям Echo.\n\n'
			'Для получения более подробной информации, пожалуйста, ознакомьтесь с правилами.\n\n'
			'(Это точно Echo-to-All?) Точнее если быть -- <b>Echo to Kim</b>❤️)')

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
	msgs_db.append(result) # type: ignore
	rdb.set("messages", msgs_db)

@dp.message_handler(content_types="any")
async def any(message: Message):
	if message.content_type == "pinned_message":
		return
	if datetime.now() < Users.get(Users.id==message.chat.id).mute:
		delay = Users.get(Users.id == message.chat.id).mute - datetime.now()
		duration = delay.total_seconds()

		seconds = int(duration % 60)
		minutes = int((duration // 60) % 60)
		hours = int((duration // 3600) % 24)
		days = int((duration // 86400) % 30.4375)  # средняя продолжительность месяца
		months = int((duration // 2629800) % 12)  # средняя продолжительность года
		years = int(duration // 31557600)  # продолжительность года

		duration_string = ""
		if years > 0:
			duration_string += f"{years} год{'' if years == 1 else 'ов'} "
		if months > 0:
			duration_string += f"{months} месяц{'' if months == 1 else 'ев'} "
		if days > 0:
			duration_string += f"{days} д{'ень ' if days == 1 else 'ней '}"
		if hours > 0:
			duration_string += f"{hours} час{' ' if hours == 1 else 'ов '}"
		if minutes > 0:
			duration_string += f"{minutes} минут{' ' if minutes == 1 else ' '}"
		if seconds > 0:
			duration_string += f"{seconds} секунд{'а' if seconds == 1 else ''}"

		umute = InlineKeyboardMarkup().add(InlineKeyboardButton(text="#IT'S MUTE", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")) # type: ignore
		return await message.reply(f"Ты сможешь писать только через {duration_string}", reply_markup=umute)

	if Users.get(Users.id==message.chat.id).tag:
		full_name = message.from_user.full_name
		username = message.from_user.username
		keyboard = InlineKeyboardMarkup().add(
		InlineKeyboardButton(f"{full_name}", url=f"t.me/{username}" if username else f"t.me/None") # type: ignore
		)
		if Admins.get_or_none(id=message.chat.id):
			keyboard.add(
			InlineKeyboardButton("ADMIN", url=f"t.me/{username}" if username else f"t.me/None") # type: ignore
			)
	else:
		keyboard = None

	Users.update(mute=datetime.now()).where(Users.id==message.chat.id).execute()
	if message.reply_to_message:
		reply_data = get_reply_data(message.chat.id, message.reply_to_message.message_id)
	else:
		reply_data = None

	if message.text or message.caption:
		if Users.get(Users.id==message.chat.id).last_msg == (message.text or message.caption):
			return await message.reply("Ваше сообщение похоже на предыдущее.")
		Users.update(last_msg=message.text or message.caption).where(Users.id==message.chat.id).execute()

	if is_flood(message.chat.id):
		Users.update(mute=datetime.now() + timedelta(hours=1)).where(Users.id==message.chat.id).execute()
		minchgod = InlineKeyboardMarkup().add(InlineKeyboardButton(text=f"#FLOOD", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")) # type: ignore
		ims = await message.reply("Это флуд.\nВы были отключены от чата на 1 час", reply_markup=minchgod)
		await bot.pin_chat_message(ims.chat.id, ims.message_id)
		user_id = message.from_user.id
		try:
			await bot.send_message(chat_log, f"#FLOOD\n<b>ID:</b>{user_id}</b>")
		except: pass
		return

	users = Users.select()
	haha = await message.reply("Send...")
	start_time = time.monotonic()
	await Send(message, keyboard, reply_data)
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
