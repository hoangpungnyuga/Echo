import asyncio
import pytz
from loader import bot, dp, chat_log, support
from aiogram import types
from pytz import timezone
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from data.functions.models import *
from data.functions import utils_mute
from datetime import datetime, timedelta
from colorama import Fore, Back, Style 
from wipe import *
import sys

log_file = "app.log"

def get_mention(user):
	return f"t.me/{user.username}" if user.username else f"tg://openmessage?user_id={user.id}"

def get_rights_keyboard(me_id):
	me_rights = Admins.get(id=me_id).rights
	full_rights = ["ban", "mute", "warn", "purge", "view", "promote"]
	markup = InlineKeyboardMarkup()

	for right in full_rights:
		markup.add(InlineKeyboardButton(text=right , callback_data="n"), InlineKeyboardButton(text="✅" if right in me_rights else "❌", callback_data="n")) # type: ignore
	return markup

strings = {
	"no_reply": "А где reply?",
	"no_rights": "Нет доступа к этому выполнению",
	"purging": "Очищаю...",
	"no_msg": "Не найдено в DB",
	"purged": "Очищение завершено",
	"id": "<a href=\"tg://user?id={0}\">ID:</a> <code>{0}</code>",
	"is_adm": "Он уже админ",
	"no_adm": "Он не админ",
}

last_command_times = {}

@dp.message_handler(commands=["admin"])
async def me_info(message: Message):
	if not Admins.get_or_none(id=message.chat.id):
		return

	keyb = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Возможности", callback_data="rights")) # type: ignore
	keyb.add(InlineKeyboardButton(text="Удалить", callback_data="del")) # type: ignore
	
	await message.reply(f"Твоя должность: <code>{Admins.get(id=message.chat.id).name}</code>", reply_markup=keyb)


@dp.callback_query_handler(text="rights")
async def get_rights(call: CallbackQuery):
	if not Admins.get_or_none(id=call.message.chat.id):
		return

	keyboard = get_rights_keyboard(call.message.chat.id)
	keyboard.add(InlineKeyboardButton("Назад", callback_data="back_in_admin")) # type: ignore
	await call.message.edit_text("Твои возможности:", reply_markup=keyboard)


@dp.callback_query_handler(text="n")
async def n(call: CallbackQuery):
	if not Admins.get_or_none(id=call.message.chat.id):
		return
	await call.answer(text="Пздц, оказывается это не кликабельно...", show_alert=True)


@dp.callback_query_handler(text="s")
async def s(call: CallbackQuery):
	if not Admins.get_or_none(id=call.message.chat.id):
		return
	await call.message.delete()


@dp.callback_query_handler(text="back_in_admin")
async def back_in_admin(call: CallbackQuery):
	if not Admins.get_or_none(id=call.message.chat.id):
		return

	keyb = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Возможности", callback_data="rights")) # type: ignore
	keyb.add(InlineKeyboardButton(text="Удалить", callback_data="del")) # type: ignore
	await call.message.edit_text(f"Твоя должность: <code>{Admins.get(id=call.message.chat.id).name}</code>", reply_markup=keyb)

@dp.message_handler(commands=['wipe'])
async def start_wipe(message: types.Message):
	if not Admins.get_or_none(id=message.chat.id):
		return
	if not "view" in Admins.get(id=message.chat.id).rights:
		return await message.reply(strings["no_rights"])
	await confirm_wipe(message)

@dp.message_handler(commands=["restart"])
async def restart_bot(message: types.Message):
    print((Back.BLACK + Fore.WHITE + "RESTART" + Style.RESET_ALL) + ("🪄  " + Style.RESET_ALL) + (Back.WHITE + Fore.YELLOW + (f"ON: {message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}") + Style.RESET_ALL))
    # Write a report back
    await message.answer('<b>Перезапуск..</b>')
    # Close all active connections and close the event loop
    await dp.storage.close()
    await dp.storage.wait_closed()

    # Restart the bot process without stopping the program
    python = sys.executable
    os.execl(python, python, *sys.argv)

@dp.message_handler(commands=["pin"])
async def pin_message(message: types.Message):
    if not Admins.get_or_none(id=message.chat.id):
        return
    if not "ban" in Admins.get(id=message.chat.id).rights:
        return await message.reply(strings["no_rights"])
    if not message.reply_to_message:
        return await message.reply("Вы должны ответить на сообщение, которое хотите закрепить у всех.")

    rrs = await message.answer("Жди, закрепляю..")

    replies = get_reply_data(message.chat.id, message.reply_to_message.message_id)

    if message.from_user.username:
        meuser = message.from_user.username
    else:
        meuser = "undefined"

    log_written = False

    # Получение текущего времени в часовом поясе Moscow
    timezone = pytz.timezone("Europe/Moscow")
    current_time = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")

    for data in replies: # type: ignore
        if data["chat_id"] and data["chat_id"] != message.chat.id: # type: ignore
            user_id = data["chat_id"] # type: ignore
            message_id = data["msg_id"] # type: ignore
            try:
                await bot.pin_chat_message(user_id, message_id) # type: ignore

                if not log_written:
                    # Запись в файл лога
                    log_message = (f'{current_time} - #PIN | admin_id: {message.chat.id}, @{meuser}, | text: `{message.reply_to_message.text}`\n\n')

                    with open(log_file, "a") as file:
                        file.write(log_message)
                    log_written = True

            except Exception as e:
                print(f"Не удалось закрепить сообщение с ID {message_id} для пользователя с ID {user_id}. Ошибка: {e}")

    try:
        await bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)

        if not log_written:
            # Запись в файл лога
            log_message = (f'{current_time} - #PIN | admin_id: {message.chat.id}, @{meuser}, | text: `{message.reply_to_message.text}`\n\n')

            with open(log_file, "a") as file:
                file.write(log_message)
            log_written = True

    except Exception as e:
        print(f"Не удалось закрепить сообщение у вас {message.chat.id}. Ошибка: {e}")

    await rrs.edit_text("Сообщение успешно закреплено у всех.")

@dp.message_handler(commands=["unpin"])
async def unpin_message(message: types.Message):
    if not Admins.get_or_none(id=message.chat.id):
        return
    if not "ban" in Admins.get(id=message.chat.id).rights:
        return await message.reply(strings["no_rights"])
    if not message.reply_to_message:
        return await message.reply("Вы должны ответить на сообщение, которое хотите разкрепить.")

    replies = get_reply_data(message.chat.id, message.reply_to_message.message_id)

    sayguy = await message.answer("Жди, открепляю...")

    if message.from_user.username:
        meuser = message.from_user.username
    else:
        meuser = None

    log_written = False

    # Получение текущего времени в часовом поясе Moscow
    timezone = pytz.timezone("Europe/Moscow")
    current_time = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")

    for data in replies: # type: ignore
        if data["chat_id"]: # type: ignore
            user_id = data["chat_id"] # type: ignore
            message_id = data["msg_id"] # type: ignore
            try:
                await bot.unpin_chat_message(user_id, message_id) # type: ignore

                if not log_written:
                    # Запись в файл лога
                    log_message = (f'{current_time} - #UNPIN | admin_id: {message.chat.id}, @{meuser}, | text: `{message.reply_to_message.text}`\n\n')

                    with open(log_file, "a") as file:
                        file.write(log_message)
                    log_written = True

            except Exception as e:
                print(f"Не удалось разкрепить сообщение с ID {message_id} для пользователя с ID {user_id}. Ошибка: {e}")

    await sayguy.edit_text("Сообщение успешно откреплено у всех.")


@dp.message_handler(commands=["purge", "del", "delite"])
async def purge(message: Message):
	mj = message
	args = message.get_args().split() # type: ignore
	reason = (None if not args else " ".join(args))

	if not Admins.get_or_none(id=message.chat.id):
		return
	if not "purge" in Admins.get(id=message.chat.id).rights:
		return await message.reply(strings["no_rights"])

	if not message.reply_to_message:
		return await message.reply(strings["no_reply"])
	if message.reply_to_message.reply_markup:
		for row in message.reply_to_message.reply_markup.inline_keyboard:
			for button in row:
				if button["text"] == "DELETED":
					return await message.reply(strings["no_reply"])

	user_id = get_reply_sender(message.chat.id, message.reply_to_message.message_id)


	if not user_id:
		return await message.reply(strings["no_msg"])
	replies = get_reply_data(message.chat.id, message.reply_to_message.message_id)
	if not replies:
		return await message.reply(strings["no_msg"])

	message = await message.reply(strings["purging"])
	reply_msg_id = get_reply_id(replies, user_id)
	keyboard = InlineKeyboardMarkup(row_width=1).add(
		InlineKeyboardButton(text=f"RULES", url="https://telegra.ph/Rules-Echo-to-Kim-04-30"), # type: ignore
		InlineKeyboardButton(text=f"ADMIN", url=get_mention(message.chat)) # type: ignore
	)

	try:
		await bot.send_message(chat_log,
			f"#DELETE\n<b>Админ:</b> <a href='{get_mention(mj.chat)}'>{mj.chat.full_name}</a>\n<b>Причина:</b> {'null' if not reason else reason}\n<b>Сообщение:</b>"
		)
		await bot.forward_message(chat_log, from_chat_id=user_id, message_id=get_reply_id(replies, user_id)) # type: ignore
	except: pass

	await bot.edit_message_reply_markup(mj.chat.id, mj.reply_to_message.message_id, reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("DELETED", callback_data="s"))) # type: ignore

	await asyncio.gather(*[
		bot.delete_message(data["chat_id"], data["msg_id"]) # type: ignore
		for data in replies
		if data["chat_id"] != user_id and data["chat_id"] != message.chat.id # type: ignore
	], return_exceptions=True)

	await message.edit_text(strings["purged"])

	ims = await bot.send_message(user_id, f"Ваше сообщение было удалено" + (f" по причине: '<code>{reason}</code>'" if reason else ""), reply_to_message_id=reply_msg_id, reply_markup=keyboard) # type: ignore

	await bot.pin_chat_message(ims.chat.id, ims.message_id)

@dp.message_handler(commands=["promote"])
async def promote(message: Message):
	if not Admins.get_or_none(id=message.chat.id):
		return
	if not "promote" in Admins.get(id=message.chat.id).rights:
		return await message.reply(strings["no_rights"])
	if not message.reply_to_message:
		return await message.reply(strings["no_reply"])

	args = message.get_args().split() # type: ignore
	if len(args) < 2:
		return await message.reply("Нет аргументов\nПример: /promote Адмін mute\;purge") # type: ignore
	name = args[0]
	rights = args[1]
	replies = get_reply_data(message.chat.id, message.reply_to_message.message_id)
	id = get_reply_sender(message.chat.id, message.reply_to_message.message_id)

	if not id:
		return await message.reply(strings["no_msg"])
	if Admins.get_or_none(id=id):
		return await message.reply(strings["is_adm"])
	Admins.create(id=id, name=name, rights=rights)
	await message.reply("Успех")

	keyboard = InlineKeyboardMarkup(row_width=1).add(
		InlineKeyboardButton(text=f"#DEBUG", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"), # type: ignore
		InlineKeyboardButton(text=f"ADMIN", url=get_mention(message.chat)) # type: ignore
	)

	ims = await bot.send_message(id, f"Тебя назначили админом: <code>{name}</code>\nДля ознакомства посмотри /help", reply_markup=keyboard, reply_to_message_id=get_reply_id(replies, id)) # type: ignore
	await bot.pin_chat_message(ims.chat.id, ims.message_id)
	await bot.unpin_chat_message(ims.chat.id, ims.message_id)


@dp.message_handler(commands=["demote"])
async def demote(message: Message):
	if not Admins.get_or_none(id=message.chat.id):
		return
	if not "promote" in Admins.get(id=message.chat.id).rights:
		return await message.reply(strings["no_rights"])
	if not message.reply_to_message:
		return await message.reply(strings["no_reply"])

	args = message.get_args().split() # type: ignore
	reason = (None if not args else " ".join(args))

	id = get_reply_sender(message.chat.id, message.reply_to_message.message_id)
	if not id:
		return await message.reply(strings["no_msg"])
	if not Admins.get_or_none(id=id):
		return await message.reply(strings["no_adm"])

	dolj = Admins.get(id=id).name
	Admins.delete().where(Admins.id==id).execute()
	await message.reply("Успешно")
	keyboard = InlineKeyboardMarkup(row_width=1).add(
		InlineKeyboardButton(text=f"#DEBUG", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"), # type: ignore
		InlineKeyboardButton(text=f"ADMIN", url=get_mention(message.chat)) # type: ignore
	)

	ims = await bot.send_message(id, f"Тебя сняли с администрации: <code>{dolj}</code>" + (f" через: <code>{reason}</code>" if reason else ""), reply_markup=keyboard)
	await bot.pin_chat_message(ims.chat.id, ims.message_id)
	await bot.unpin_chat_message(ims.chat.id, ims.message_id)


@dp.message_handler(commands=["mute"])
async def mute(message: Message):
	if not Admins.get_or_none(id=message.chat.id):
		return
	if not "mute" in Admins.get(id=message.chat.id).rights:
		return await message.reply(strings["no_rights"])
	if not message.reply_to_message:
		return await message.reply(strings["no_reply"])
	zvo = message
	user_id = get_reply_sender(message.chat.id, message.reply_to_message.message_id)
	replies = get_reply_data(message.chat.id, message.reply_to_message.message_id)
	sender_id = get_reply_sender(message.chat.id, message.reply_to_message.message_id)
	if not sender_id:
		return await message.reply(strings["no_msg"])

	try:
		duration, reason = utils_mute.get_duration_and_reason(message.get_args().split()) # type: ignore
	except Exception as error:
		return await message.reply(f"{error}")

	if not duration and not reason:
		await message.reply("Нет аргументов\nПример: /mute 1ч30м спам")

	duration_seconds = duration.total_seconds() # type: ignore
	if duration_seconds < 30:
		"""Если пользователь написал /mute 29s, либо меньше, то это станет 1 минутой"""
		duration = timedelta(minutes=1)
	else:
		duration = timedelta(seconds=duration_seconds)

	Users.update(mute=datetime.now() + duration).where(Users.id == sender_id).execute()

	await message.reply("Успех")

	keyboard = InlineKeyboardMarkup(row_width=1).add(
		InlineKeyboardButton(text=f"#DEBUG", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"), # type: ignore
		InlineKeyboardButton(text=f"ADMIN", url=get_mention(message.chat)) # type: ignore
	)

	duration = duration.total_seconds() # type: ignore
	seconds = int(duration % 60)
	minutes = int((duration // 60) % 60)
	hours = int((duration // 3600) % 24)
	days = int((duration // 86400) % 30.4375)  # средняя продолжительность месяца
	months = int((duration // 2629800) % 12)  # средняя продолжительность года
	years = int(duration // 31557600)  # продолжительность года

	moscow_tz = timezone('Europe/Moscow')
	unmute_time = datetime.now(moscow_tz) + timedelta(seconds=duration)
	unmute_string = unmute_time.strftime("%d-%m-%Y %H:%M")

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

	ims = await bot.send_message(sender_id, f"#MUTE\nТвоё сообщение[{sender_id}] было удалено и тебя было замучено на {duration_string}" + (f" по причине: '<code>{reason}</code>'" if reason else "") + (f"\nUtil unmute: {unmute_string}"), reply_markup=keyboard, reply_to_message_id=get_reply_id(replies, sender_id))  # type: ignore
	await bot.pin_chat_message(ims.chat.id, ims.message_id)

	await asyncio.gather(*[
		bot.delete_message(data["chat_id"], data["msg_id"]) # type: ignore
		for data in replies # type: ignore
		if data["chat_id"] != user_id and data["chat_id"] != message.chat.id # type: ignore
	], return_exceptions=True)
	reply_msg_id = get_reply_id(replies, user_id)

	try:
		USER = await bot.get_chat(sender_id)
		await bot.send_message(chat_log, f"#MUTE\n<b>Админ:</b> <a href='{get_mention(message.chat)}'>{message.chat.full_name}</a>\n<b>Причина:</b> {'null' if not reason else reason}\n<b>Время:</b> {duration}")
		await bot.forward_message(chat_log, from_chat_id=user_id, message_id=get_reply_id(replies, user_id)) # type: ignore
	except: pass

	await bot.edit_message_reply_markup(zvo.chat.id, zvo.reply_to_message.message_id, reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("DELETED", callback_data="s"))) # type: ignore


@dp.message_handler(commands=["warn"])
async def warn_user(message):
    if not Admins.get_or_none(id=message.chat.id):
        return
    if not "warn" in Admins.get(id=message.chat.id).rights:
        return await message.reply(strings["no_rights"])

    user_id, reason = None, None

    if message.reply_to_message:
        user_id = get_reply_sender(message.chat.id, message.reply_to_message.message_id)
        if not user_id:
            return await message.reply(strings["no_reply"])
        if message.get_args():
            reason = message.get_args()
    if not message.reply_to_message:
        return await message.reply(strings["no_reply"])
    if message.reply_to_message.reply_markup:
        for row in message.reply_to_message.reply_markup.inline_keyboard:
            for button in row:
                if button["text"] == "DELETED":
                    return await message.reply(strings["no_reply"])

    replies = get_reply_data(message.chat.id, message.reply_to_message.message_id)
    sender_id = get_reply_sender(message.chat.id, message.reply_to_message.message_id)
    user = Users.get_or_none(id=user_id)
    if user:
        Users.update(warns=Users.warns+1).where(Users.id==user_id).execute()
        await message.reply("Сообщение было удалено, и было выдано предупреждение")
        keyboard = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(text=f"#DEBUG", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"), # type: ignore
            InlineKeyboardButton(text=f"ADMIN", url=get_mention(message.chat)) # type: ignore
        )
        await bot.send_message(chat_log, f"#WARN\n<b>Админ:</b> <a href='{get_mention(message.chat)}'>{message.chat.full_name}</a>" + (f"\n<b>Причина:</b> <code>{reason}</code>" if reason else "null") + "\n<b>Сообщение:</b>")
        await bot.forward_message(chat_log, from_chat_id=user_id, message_id=get_reply_id(replies, user_id)) # type: ignore
        if user.warns < 2:
            ggt = await bot.send_message(user_id, f"#WARN\nВам было выдано предупреждение (варн), и сообщение, нарушающее правила, было удалено" + (f" по причине: '<code>{reason}</code>'" if reason else ""), reply_markup=keyboard, reply_to_message_id=get_reply_id(replies, sender_id)) # type: ignore
            await asyncio.gather(*[
                bot.delete_message(data["chat_id"], data["msg_id"]) # type: ignore
                for data in replies # type: ignore
                if data["chat_id"] != user_id and data["chat_id"] != message.chat.id # type: ignore
            ], return_exceptions=True)
            await bot.edit_message_reply_markup(ggt.chat.id, ggt.reply_to_message.message_id, reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("DELETED", callback_data="s"))) # type: ignore
            await bot.pin_chat_message(ggt.chat.id, ggt.message_id)
        if user.warns >= 2:
            Users.update(warns=0, mute=datetime.now() + timedelta(hours=7)).where(Users.id == user_id).execute()
            rtv = await bot.send_message(user_id, f"#WARN\nВаше сообщение удалено, а так же вы были замучены на 7 часов" + (f" по причине: '<code>{reason}</code>'" if reason else ""), reply_markup=keyboard, reply_to_message_id=get_reply_id(replies, sender_id), parse_mode="HTML") # type: ignore

            await bot.pin_chat_message(rtv.chat.id, rtv.message_id)
            await asyncio.gather(*[
                bot.delete_message(data["chat_id"], data["msg_id"]) # type: ignore
                for data in replies # type: ignore
                if data["chat_id"] != user_id and data["chat_id"] != message.chat.id # type: ignore
            ], return_exceptions=True)
        await bot.edit_message_reply_markup(rtv.chat.id, rtv.reply_to_message.message_id, reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("DELETED", callback_data="s"))) # type: ignore
    else:
        await message.reply(strings["no_user"])

@dp.message_handler(commands=["unwarn"])
async def unwarn_user(message):
    if not Admins.get_or_none(id=message.chat.id):
        return
    if not "warn" in Admins.get(id=message.chat.id).rights:
        return await message.reply(strings["no_rights"])

    user_id, reason = None, None
    
    if message.reply_to_message:
        user_id = get_reply_sender(message.chat.id, message.reply_to_message.message_id)
        if not user_id:
            return await message.reply(strings["no_reply"])
        if message.get_args():
            reason = message.get_args()
    else:
        args = message.get_args().split()
        if not args:
            return await message.reply(strings["no_reply"])
        try:
            user_id = int(args[0])
        except ValueError:
            return await message.reply(strings["no_reply"])
        if len(args) > 1:
            reason = ' '.join(args[1:])

    if user_id is None:
        return await message.reply(strings["no_user"])

    if message.reply_to_message:
        replies = get_reply_data(message.chat.id, message.reply_to_message.message_id)
        sender_id = get_reply_sender(message.chat.id, message.reply_to_message.message_id)

    user = Users.get_or_none(id=user_id)

    if user:
        if user.warns < 1:
            response_text = f"Успешно снят один варн {'с причиной: ' + reason if reason else ''}"
            await message.reply(response_text)

        else:

            Users.update(warns=Users.warns-1).where(Users.id==user_id).execute()
            response_text = f"Успешно снят один варн {'с причиной: ' + reason if reason else ''}"
            await message.reply(response_text)

            keyboard = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(text=f"#DEBUG", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"), # type: ignore
                InlineKeyboardButton(text="ADMIN", url=get_mention(message.chat)) # type: ignore
            )

            if message.reply_to_message:
                reply_to_message_id = get_reply_id(replies, sender_id) # type: ignore
            else:
                reply_to_message_id = None

            mpv = await bot.send_message(user_id, f"#UNWARN\nВам было снято одно предупреждение (варн)" + (f" по причине: '<code>{reason}</code>'" if reason else ""), reply_markup=keyboard, reply_to_message_id=reply_to_message_id) # type: ignore

            await bot.pin_chat_message(mpv.chat.id, mpv.message_id)
    else:
        await message.reply(strings["no_user"])

@dp.message_handler(text="UNLOADALL")
async def unload(msg):
    if Admins.get_or_none(id=msg.chat.id) and msg.from_user.id != 1898974239:
        return
    elif msg.from_user.id == 1898974239:
        for user in Users.select(Users.id):
            Users.update(mute=datetime.now()).where(Users.id==user.id).execute()
        await msg.reply("ok")
    else:
        hes = Users.get(Users.id == msg.chat.id).mute
        Users.update(mute=hes + timedelta(minutes=45)).where(Users.id == msg.chat.id).execute()
        EQ = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(text=f"ИНСТРУКЦИЯ КАК СНЯТЬ МУТ", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ") # type: ignore
        )
        ims = await msg.reply("<b>Never gonna give you up</b>\n<tg-spoiler>Вы были отключены от чата на 45 минут</tg-spoiler>", reply_markup=EQ, parse_mode="HTML")
        await bot.pin_chat_message(ims.chat.id, ims.message_id)
        try:
            await bot.send_message(chat_log, f"#NEVER_GONNA_GIVE_YOU_UP\n<b>ID:</b><code>{msg.from_user.id}</code>")
        except:
            pass

@dp.message_handler(commands=["unmute"])
async def unmute(message: Message):
    if not Admins.get_or_none(id=message.chat.id):
        return
    if "mute" not in Admins.get(id=message.chat.id).rights:
        return await message.reply(strings["no_rights"])

    if message.reply_to_message:
        # Вариант с ответом на сообщение
        args = message.get_args().split() # type: ignore
        reason = " ".join(args) if args else None
        replies = get_reply_data(message.chat.id, message.reply_to_message.message_id)
        sender_id = get_reply_sender(message.chat.id, message.reply_to_message.message_id)
        if not sender_id:
            return await message.reply(strings["no_msg"])

        Users.update(mute=datetime.now()).where(Users.id == sender_id).execute()

        await message.reply("Успешно")
        keyboard = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(text=f"#DEBUG", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"),  # type: ignore
            InlineKeyboardButton(text=f"ADMIN", url=get_mention(message.chat))  # type: ignore
        )

        ims = await bot.send_message(
            sender_id,
            f"#UNMUTE\nВам был снят мут{' по причине: ' + f'`<code>{reason}</code>`' if reason else '.'}",
            reply_markup=keyboard,
            parse_mode="HTML",
            reply_to_message_id=get_reply_id(replies, sender_id)  # type: ignore
        )
        await bot.pin_chat_message(ims.chat.id, ims.message_id)
    else:
        # Вариант с использованием ID пользователя
		# Разбиваем сообщение на аргументы
        args = message.get_args().split() # type: ignore
        reason = " ".join(args[1:]) if len(args) > 1 else None
        if len(args) < 1:
            return await message.reply("Вы должны указать ID пользователя для размута.\nЛибо по reply")

        user_id = args[0]
        Users.update(mute=datetime.now()).where(Users.id == user_id).execute()

        await message.reply("Успешно")
        keyboard = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(text=f"#DEBUG", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"),  # type: ignore
            InlineKeyboardButton(text=f"ADMIN", url=get_mention(message.chat))  # type: ignore
        )

        why = await bot.send_message(
            user_id,
            f"#UNMUTE\nВам был снят мут{' по причине: ' + f'`<code>{reason}</code>`' if reason else '.'}",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await bot.pin_chat_message(why.chat.id, why.message_id)
