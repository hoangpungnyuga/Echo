from loader import bot, dp, support
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

upstart = datetime.now()

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
	user = Users.get_or_none(Users.id == message.chat.id)
	admin = Admins.get_or_none(id=message.chat.id)
	username = f'@{message.from_user.username}' if message.from_user.username else "<i>твой юзер</i>"
	IF = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Удалить", callback_data="del"))  # type: ignore
	WB = '<b>Я буду отправлять твои сообщения всем юзерам.</b>\n\n'
	WB += '<b>⌖ Все, что вас может интересовать:</b>\n'
	WB += '<b>></b> /start, /rules\n\n'
	WB += '<b>⌖ Когда будет обновление бота?</b>\n'
	WB += '<b>><u> Завтра, если нет, то прочтите это сообщение еще раз!</u></b>'
	if user:
		WB += '\n\n<b>Также гайд по командам:</b>\n'
		WB += '/start - <i>Старт бота</i>\n'
		WB += '/rules - <i>Правила этого бота</i>\n'
		WB += '/profile - <i>Твой профиль в боте</i>\n'
		WB += f'/tag - <i>On/Off кнопку с ссыланием на</i> {username}\n'
		WB += '/warns - <i>Сколько у тебя на данный момент варнов</i>\n'
		WB += '/life - <i>Состояние сервера</i>\n'
		WB += '/users - <i>Сколько юзеров в боте</i>\n'
		WB += '/ping - <i>Пинг от сервера до телеграм серверов, DNS</i>'		
		if admin:
			right = Admins.get(id=message.from_user.id).rights
			WB += '\n\n<b>Команды для <u>админов</u>:</b>\n'
			WB += '/admin - <i>Узнать какие есть права к командам</i>\n'
			if "view" in right:
				WB += '/wipe - <i>Удалить файл сообщений в DB бота</i> <b>【view】</b>\n'
			WB += '/restart - <i>Рестарт бота</i> <b>【ban】</b>\n'
			WB += '/pin &lt;reply&gt; - <i>Закрепить сообщение</i> <b>【ban】</b>\n'
			WB += '/unpin &lt;reply&gt; - <i>Открепить сообщение</i> <b>【ban】</b>\n'
			WB += '/del &lt;reply&gt; - <i>Удалить сообщение</i> <b>【purge】</b>\n'
			WB += '/mute &lt;reply&gt; &lt;Xs;m;h;d;y&gt; [reason] - <i>Замутить пользователя</i> <b>【mute】</b>\n'
			WB += 'ㅤㅤ X - <i>время</i>\nㅤㅤ s - <i>секунды</i>\nㅤㅤ m - <i>минуты</i>\nㅤㅤ h - <i>часы</i>\nㅤㅤ d - <i>дни</i>\nㅤㅤ y - <i>года</i>\n'
			WB += '/unmute &lt;id|reply&gt; [reason] - <i>Размутить пользователя</i> <b>【mute】</b>\n'
			WB += '/warn &lt;reply&gt; [reason] - <i>Дать один WARN пользователю</i> <b>【warn】</b>\n'
			WB += '/unwarn &lt;id|reply&gt; [reason] - <i>Снять один WARN пользователю</i> <b>【warn】</b>\n\n'
			WB += '<i>Ты можешь использовать</i>: '	
			if "ban" in right:
				WB += '/restart;/pin;/unpin'
			if "view" in right:
				WB += ';/wipe'
			if "purge" in right:
				WB += ';/del'
			if "mute" in right:
				WB += ';/mute;/unmute'
			if "warn" in right:
				WB += ';/warn;/unwarn'		
			WB += '\n\n<b>А это <a href="https://t.me/+Fywa1MPQ6MpkMGEy"><u>LOG CHAT</u></a> бота</b>'

	await message.reply(WB, reply_markup=IF, parse_mode="HTML")

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
		is_admin = "Yep:)"
	else:
		is_admin = "No.."
	flood, seconds = await check_floodwait(message)
	if flood:
		floodwait = f"Yes, {seconds} seconds"
	else:
		floodwait = "No detected"
	msgs_db = rdb.get("messages", [])
	await message.reply("Debug your profile info:\n"
				f"Name: {message.from_user.full_name}\n"
				f"ID: <code>{message.from_user.id}</code>\n"
				f"Username: {username}\n"
				f"Mute: {dur}\n"
				f"Warns: {user.warns}\n"
				f"U admin?: {is_admin}\n"
				f"Use_tag: {user.tag}\n"
				f"Users: {len(users)}\n"
				f"Floodwait?: {floodwait}\n"
				f"lastmsg chat: {last_msg}, msg_sent: {len(msgs_db)}")

@dp.message_handler(commands=['warns'])
@delayed_message(rate_limit=2, rate_limit_interval=5)
async def warns(message: types.Message):
	user = Users.get_or_none(Users.id == message.chat.id)
	await message.reply(f'Warns: {user.warns}.\n3 варна - мут на 7 часов.')

@dp.message_handler(commands=['ping'])
@delayed_message(rate_limit=1, rate_limit_interval=10)
async def ping_telegram(message: types.Message):
	pings = await message.reply("🌈PONG!🌈\n\n🏳️‍🌈Happy Pride Day! The U.S. reaffirms LGBTQI+ rights are human rights and no group should be excluded from those protections, regardless of race, ethnicity, sex, gender identity, sexual orientation, sex characteristics, disability status, age, religion or belief. The struggle to end violence, discrimination, criminalization, and stigma against LGBTQI+ persons is a global challenge.🏳️‍🌈")
	try:
		dc1 = ping3.ping('149.154.175.53', unit="ms", timeout=1)
		dc2 = ping3.ping('149.154.167.51', unit="ms", timeout=1)
		dc3 = ping3.ping('149.154.175.100', unit="ms", timeout=1)
		dc4 = ping3.ping('149.154.167.91', unit="ms", timeout=1)
		dc5 = ping3.ping('91.108.56.130', unit="ms",timeout=1)
		one = ping3.ping('1.1.1.1', unit="ms", timeout=1)
		google = ping3.ping('8.8.8.8', unit="ms", timeout=1)
		quad9 = ping3.ping('9.9.9.9', unit="ms", timeout=1)
		opendns = ping3.ping('208.67.222.222', unit="ms", timeout=1)
		cleanbrowsing = ping3.ping('185.228.168.9', unit="ms", timeout=1)
		comodo = ping3.ping('8.26.56.26', unit="ms", timeout=1)
		level3 = ping3.ping('209.244.0.3', unit="ms", timeout=1)
		opennic = ping3.ping('134.195.4.2', unit="ms", timeout=1)
#		yandex = ping3.ping('77.88.8.8', unit="ms", timeout=1)
		adguard = ping3.ping('94.140.14.14', unit="ms", timeout=1)
		watch = ping3.ping('84.200.69.80', unit="ms", timeout=1)
		verisign = ping3.ping('64.6.64.6', unit="ms", timeout=1)
		norton = ping3.ping('199.85.126.20', unit="ms", timeout=1)
		safe = ping3.ping('195.46.39.39', unit="ms", timeout=1)
		uncensored = ping3.ping('91.239.100.100', unit="ms", timeout=1)
		freenom = ping3.ping('80.80.80.80', unit="ms", timeout=1)
	
		XH = '🏓 Пинг телеграм дата центров:\n'
		XH += f'🇺🇸DC1 MIA, Miami FL, USA: <code>{dc1}</code> ms\n' if dc1 else '🇺🇸DC1 MIA, Miami FL, USA: <b>failed:(</b>\n'
		XH += f'🇳🇱DC2 AMS, Amsterdam, NL: <code>{dc2}</code> ms\n' if dc2 else '🇳🇱DC2 AMS, Amsterdam, NL: <b>failed:(</b>\n'
		XH += f'🇺🇸DC3* MIA, Miami FL, USA: <code>{dc3}</code> ms\n' if dc3 else '🇺🇸DC3* MIA, Miami FL, USA: <b>failed:(</b>\n'
		XH += f'🇳🇱DC4 AMS, Amsterdam, NL: <code>{dc4}</code> ms\n' if dc4 else '🇳🇱DC4 AMS, Amsterdam, NL: <b>failed:(</b>\n'
		XH += f'🇸🇬DC5 SIN, Singapore, SG: <code>{dc5}</code> ms\n' if dc5 else '🇸🇬DC5 SIN, Singapore, SG: <b>failed:(</b>\n'
		XH += '\n🐘 DNS сервера:\n'
		XH += f'🏳️‍🌈Cloudflare <i>1.1.1.1</i>: <code>{one}</code> ms\n' if one else '🌈Cloudflare <i>1.1.1.1</i>: <b>failed:(</b>\n'
		XH += f'🏳️‍🌈Google <i>8.8.8.8</i>: <code>{google}</code> ms\n' if google else '🌈Google <i>8.8.8.8</i>: <b>failed:(</b>\n'
		XH += f'🏳️‍🌈Quad9 <i>9.9.9.9</i>: <code>{quad9}</code> ms\n' if quad9 else '🌈Quad9 <i>9.9.9.9</i>: <b>failed:(</b>\n'
		XH += f'🏳️‍🌈OpenDNS/Cisco <i>208.67.222.222</i>: <code>{opendns}</code> ms\n' if opendns else '🌈OpenDNS <i>208.67.222.222</i>: <b>failed:(</b>\n'
		XH += f'🏳️‍🌈Cleanbrowsing <i>185.228.168.9</i>: <code>{cleanbrowsing}</code> ms\n' if cleanbrowsing else '🌈Cleanbrowsing <i>185.228.168.9</i>: <b>failed:(</b>\n'
		XH += f'🏳️‍🌈Comodo Secure DNS <i>8.26.56.26</i>: <code>{comodo}</code> ms\n' if comodo else '🌈Comodo Secure DNS <i>8.26.56.26</i>: <b>failed:(</b>\n'
		XH += f'🏳️‍🌈Level 3 <i>209.244.0.3</i>: <code>{level3}</code> ms\n' if level3 else '🌈Level 3 <i>209.244.0.3</i>: <b>failed:(</b>\n'
		XH += f'🏳️‍🌈OpenNIC <i>134.195.4.2</i>: <code>{opennic}</code> ms\n' if opennic else '🌈OpenNIC <i>134.195.4.2</i>: <b>failed:(</b>\n'
#		XH += f'🏳️‍🌈Yandex <i>77.88.8.8</i>: <code>{yandex}</code> ms\n' if yandex else '🌈Yandex <i>77.88.8.8</i>: <b>failed:(</b>\n'
		XH += f'🏳️‍🌈AdGuard <i>94.140.14.14</i>: <code>{adguard}</code> ms\n' if adguard else '🌈AdGuard <i>94.140.14.14</i>: <b>failed:(</b>\n'
		XH += f'🏳️‍🌈Watch <i>84.200.69.80</i>: <code>{watch}</code> ms\n' if watch else '🌈Watch <i>84.200.69.80</i>: <b>failed:(</b>\n'
		XH += f'🏳️‍🌈Verisign <i>64.6.64.6</i>: <code>{verisign}</code> ms\n' if verisign else '🌈Verisign <i>64.6.64.6</i>: <b>failed:(</b>\n'
		XH += f'🏳️‍🌈Norton ConnectSafe <i>199.85.126.20</i>: <code>{norton}</code> ms\n' if norton else '🌈Norton ConnectSafe <i>199.85.126.20</i>: <b>failed:(</b>\n'
		XH += f'🏳️‍🌈SafeDNS <i>195.46.39.39</i>: <code>{safe}</code> ms\n' if safe else '🌈SafeDNS <i>195.46.39.39</i>: <b>failed:(</b>\n'
		XH += f'🏳️‍🌈UncensoredDNS <i>91.239.100.100</i>: <code>{uncensored}</code> ms\n' if uncensored else '🌈UncensoredDNS <i>91.239.100.100</i>: <b>failed:(</b>\n'
		XH += f'🏳️‍🌈FreeNom <i>80.80.80.80</i>: <code>{freenom}</code> ms\n' if freenom else '🌈Freenom <i>80.80.80.80</i>: <b>failed:(</b>\n'
		SD = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Удалить", callback_data="del")) # type: ignore
		await pings.edit_text(XH, reply_markup=SD, parse_mode="HTML")
	except PermissionError as e:
		if isinstance(e, PermissionError) and str(e) == "[Errno 13] Permission denied":
			await pings.edit_text(f"Ошибка:(\nЭто - Permission denied\nПопробуй /fix\nЕсли же вы видите это, пишите {support}")
		else:
			error = traceback.format_exc()  # Получение полного сообщения об ошибке
			await pings.edit_text(f"Ошибка:(\n{error}\nПопробуй /fix\nЕсли же вы видите это, пишите {support}")

@dp.message_handler(commands=["life"])
@delayed_message(rate_limit=2, rate_limit_interval=9)
async def get_system_stats(message: types.Message):
	hey = await message.reply("I'm counting..")
	try:
		user = Users.get_or_none(Users.id == message.chat.id)
		if user:
			was = datetime.now()
			uptime = was - upstart
			start_time = time.monotonic()
			formatted_uptime = str(uptime).split(".")[0]
			if uptime.days > 0:
				days = uptime.days
				hours, remainder = divmod(uptime.seconds, 3600)
				minutes, seconds = divmod(remainder, 60)
				formatted_uptime = f"{days} дней {hours} часов {minutes} минут {seconds} секунд"
			elif uptime.seconds >= 3600:
				hours = uptime.seconds // 3600
				minutes = (uptime.seconds % 3600) // 60
				seconds = uptime.seconds % 60
				formatted_uptime = f"{hours} часов {minutes} минут {seconds} секунд"
			elif uptime.seconds >= 60:
				minutes = uptime.seconds // 60
				seconds = uptime.seconds % 60
				formatted_uptime = f"{minutes} минут {seconds} секунд"
			else:
				formatted_uptime = f"{uptime.seconds} секунд"
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
		
			if cpu_percent > 97: response += f"‼️CPU: {cpu_percent}%‼️\n"
			else: response += f">CPU: {cpu_percent}%\n"
		
			if mem_percent > 96: response += f"‼️RAM: {mem_percent:.1f}% / Free: {mem_free_percent:.1f}%‼️\n"
			else: response += f">RAM: {mem_percent:.1f}% / Free: {mem_free_percent:.1f}%\n"
		
			if not swap_percent == 0: response += f">Swap: {swap_percent:.1f}% / Free: {swap_free_percent:.1f}%\n"
			else: pass
		
			if disk_percent > 98: response += f"‼️Disk Usage: {disk_percent:.1f}% / Free: {disk_free_percent:.1f}%‼️\n"
			else: response += f">Disk Usage: {disk_percent:.1f}% / Free: {disk_free_percent:.1f}%\n"
		
			response += f"`Uptime bot: {formatted_uptime}\n"
			response += f"`Current date and time in RU Donetsk: {format_date}"
			DS = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Удалить", callback_data="del")) # type: ignore
			await hey.edit_text(response, reply_markup=DS)
	except PermissionError as e:
		if isinstance(e, PermissionError) and str(e) == "[Errno 13] Permission denied":
			await hey.edit_text(f"Ошибка:(\nЭто - Permission denied\nПопробуй /fix\nЕсли же вы видите это, пишите {support}")
		else:
			error = traceback.format_exc()
			await hey.edit_text(f"Ошибка:(\n{error}\nЕсли же вы видите это, пишите {support}")

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
		await message.reply("Ваши следующие сообщения будут помечены вашим ником и @username\nВы были зарегистрированы в боте.", parse_mode="HTML")

@dp.message_handler(commands=["start"])
@delayed_message(rate_limit=2, rate_limit_interval=5)
async def start(message: Message):
	if not Users.select().where(Users.id==message.chat.id).exists():
		Users.create(id=message.chat.id)

	USER = f'<a href="https://{message.from_user.username}.t.me/">{message.from_user.full_name}</a>' if message.from_user.username else message.from_user.full_name
	await message.reply(f'Салам, {USER}!'
			'\nЭто эхо-бот от создателей <b>ILNAZ GOD</b> и <b>Ким</b>💖💖.'
			'\n\nТвои сообщения будут отправляться всем пользователям Echo.'
			'\n\nДля получения более подробной информации, пожалуйста, ознакомьтесь с правилами.'
			'\n\n(Это точно Echo-to-All?) Точнее если быть -- <b>Echo to Kim</b>❤️)')

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
		username = message.from_user.username if message.from_user.username else None
		keyboard = InlineKeyboardMarkup().add(
		InlineKeyboardButton(f"{full_name}", url=f"https://t.me/{username}/") # type: ignore
		)
		if Admins.get_or_none(id=message.chat.id):
			keyboard.add(
			InlineKeyboardButton("ADMIN", url=f"https://t.me/{username}/") # type: ignore
			)
	else:
		keyboard = None

	if not Users.select().where(Users.id==message.chat.id).exists():
		USER = f'<a href="https://{message.from_user.username}.t.me/">You</a>' if message.from_user.username else 'You'
		await message.answer(f"{USER} are not registered in the bot."
								"\nTo register type /start")
		return

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
		return

	users = Users.select()
	haha = await message.reply("Send...\n<tg-spoiler>У меня оч хуевый интернет, так что отправка возможно будет долгой</tg-spoiler>")
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
		send_duration_str = f"{send_duration_min} минут {send_duration_sec} секунд"

	await haha.edit_text(f"Твоё сообщение было отправлено {len(users)} пользователям бота за <b>{send_duration_str}</b>", parse_mode="HTML")
