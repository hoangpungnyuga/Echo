from loader import bot, dp, support
import asyncio
import time
from peewee import DoesNotExist
from aiogram import types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from data.functions.models import Users, Admins, rdb, get_reply_id32, get_reply_data, is_flood
from aiogram.types.message_id import MessageId
from control import delayed_message, registered_only
from screl import check_floodwait, not_username, delete_msg_callback
from datetime import datetime, timedelta

log_file = "app.log"

upstart = datetime.now()

def format_timedelta(td):
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days} day{'s' if days != 1 else ''}, {hours:02}:{minutes:02}:{seconds:02}"

@dp.message_handler(commands=["rules"])
@delayed_message(rate_limit=2, rate_limit_interval=5)
async def rules(message: Message):
    keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(text="RULES", url="https://telegra.ph/Rules-Echo-to-Kim-04-30")) # type: ignore
    await message.reply(f"Правила этого бота\nТак же по поводу вопросов писать\n<b>>></b> {support}", reply_markup=keyboard)

@dp.message_handler(commands=["start"])
@delayed_message(rate_limit=2, rate_limit_interval=5)
async def start(message: Message):
    if message.chat.type != types.ChatType.PRIVATE:
        await message.reply(
        "Bot works only in private messages"
        "\nDone due to bugs.")
        return

    USER = f'<a href="https://{message.from_user.username}.t.me/">{message.from_user.full_name}</a>' if message.from_user.username else message.from_user.full_name

    if not Users.select().where(Users.id==message.from_user.id).exists():
        image = 'image/welcome.png' # Тут меняете путь изоображения на своё, либо просто замените файл.
        photo = InputFile(image)
        confrim = InlineKeyboardMarkup().add(InlineKeyboardButton(text="✅Подтверить регистрацию", callback_data=f"confirm_registration={message.from_user.id}")) # type: ignore
        url = 't.me/sensxn/6' # Тут тоже менять на своё
        se = (f'Салам, <i>{USER}</i>!'
             '\nТы попал в Echo<a href="https://mastergroosha.github.io/telegram-tutorial/docs/lesson_01/">&#185;</a>'
             '\n<b>Вы не зарегистрированы в этом боте, а значит вы не можете им пользоваться.'
            f'\nЧто это? Зачем это? см<a href="{url}">&#178;</a>'
             '\nТак же, для обширного ознакомления существует /help'
             '\nПожалуйста, подтвердите свою регистрацию, и убедитесь что вы прочитали наши правила бота, /rules</b>')
        await bot.send_photo(message.chat.id, photo, se, reply_markup=confrim)
    else:
        await message.reply(f'Салам, {USER}!'
                           '\nЭто эхо-бот от создателей <b>ILNAZ GOD</b> и <b>Ким</b>💖💖.'
                         '\n\nТвои сообщения будут отправляться всем пользователям Echo.'
                         '\n\nДля получения более подробной информации, пожалуйста, ознакомьтесь с правилами.'
                         '\n\n(Это точно Echo-to-All?) Точнее если быть -- <b>Echo to Kim</b>❤️)')

@dp.message_handler(commands=["users"])
@delayed_message(rate_limit=2, rate_limit_interval=5)
async def users(message: Message):
    users = Users.select()
    await message.reply(f"👾 На данный момент сейчас <code>{len(users)}</code> пользователей в боте")

@dp.message_handler(commands=["help"])
@delayed_message(rate_limit=2, rate_limit_interval=5)
async def help(message: Message):
    user = Users.get_or_none(Users.id == message.chat.id)
    admin = Admins.get_or_none(id=message.chat.id)
    username = message.from_user.mention if message.from_user.username else "<i>твой юзер</i>"
    keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Удалить", callback_data="del"))  # type: ignore
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
        WB += '/users - <i>Сколько юзеров в боте</i>\n'		
        if admin:
            right = Admins.get(id=message.from_user.id).rights
            WB += '\n\n<b>Команды для <u>админов</u>:</b>\n'
            WB += '/admin - <i>Узнать какие есть права к командам</i>\n'
            WB += '/wipe - <i>Удалить файл сообщений в DB бота</i> <b>【view】</b>\n'
            WB += '/restart - <i>Рестарт бота</i> <b>【ban】</b>\n'
            WB += '/pin &lt;reply&gt; - <i>Закрепить сообщение</i> <b>【ban】</b>\n'
            WB += '/unpin &lt;reply&gt; - <i>Открепить сообщение</i> <b>【ban】</b>\n'
            WB += '/del &lt;reply&gt; - <i>Удалить сообщение</i> <b>【purge】</b>\n'
            WB += '/mute &lt;reply&gt; &lt;Xs;m;h;d;w;y&gt; [reason] - <i>Замутить пользователя</i> <b>【mute】</b>\n'
            WB += 'ㅤㅤ X - <i>время</i>\nㅤㅤ s - <i>секунды</i>\nㅤㅤ m - <i>минуты</i>\nㅤㅤ h - <i>часы</i>\nㅤㅤ d - <i>дни</i>\nㅤㅤ w - <i>недели</i>\nㅤㅤ y - <i>года</i>\n'
            WB += '/unmute &lt;id|reply&gt; [reason] - <i>Размутить пользователя</i> <b>【mute】</b>\n'
            WB += '/warn &lt;reply&gt; [reason] - <i>Дать один WARN пользователю</i> <b>【warn】</b>\n'
            WB += '/unwarn &lt;id|reply&gt; [reason] - <i>Снять один WARN пользователю</i> <b>【warn】</b>\n'
            WB += '/unstaff &lt;your_id&gt; - Снять себя с полномочия\n'
            WB += '\n<i>Ты можешь использовать</i>: '	
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
            if right:
                WB += ';/unstaff'
            WB += '\n\n<b>А это <a href="https://t.me/+Fywa1MPQ6MpkMGEy"><u>LOG CHAT</u></a> бота</b>'

    await message.reply(WB, reply_markup=keyboard, parse_mode="HTML")

@dp.message_handler(commands=["profile"])
@delayed_message(rate_limit=2, rate_limit_interval=5)

async def profile(message: Message):
    user = Users.get_or_none(Users.id == message.chat.id)

    users = Users.select()

    last_msg = message.message_id

    username = message.from_user.mention if message.from_user.username else "undefined"

    delay = Users.get(Users.id==message.chat.id).mute - datetime.now()

    dur = str(delay).split(".")[0]

    if dur.startswith("-"):
        dur = "undefined"

    if Admins.get_or_none(id=message.chat.id):
        is_admin = "Yeah."

    else:
        is_admin = "No.."

    flood, seconds = await check_floodwait(message)

    if flood:
        floodwait = f"Yes, {seconds} seconds"
    else:
        floodwait = "No detected"

    msgs_db = rdb.get("messages", [])

    msgs_your = sum(1 for msg in msgs_db if msg[0].get("sender_id") == message.from_user.id) # type: ignore

    user_date = "nothing."
    for msg in reversed(msgs_db):
        sender_id = msg[0].get("sender_id") # type: ignore
        if sender_id == message.from_user.id:
            user_date = msg[-1].get("time") # type: ignore
            user_date = datetime.strptime(user_date[:-7], "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%y %H:%M:%S")
            break

    await message.reply("Debug your profile info:\n"
                       f"Name: {message.from_user.full_name}\n"
                       f"ID: <code>{message.from_user.id}</code>\n"
                       f"Username: {username}\n"
                       f"Mute: {dur}\n"
                       f"Warns: {user.warns}\n"
                       f"You admin?: {is_admin}\n"
                       f"Use_tag: {user.tag}\n"
                       f"Msg Sent You: {msgs_your}\n"
                       f"Users: {len(users)}\n"
                       f"Floodwait?: {floodwait}\n"
                       f"lastmsg chats: {last_msg}, msg_sents: {len(msgs_db)}\n"
                       f"lastmsg your time: {user_date}")

@dp.message_handler(commands=['warns'])
@delayed_message(rate_limit=2, rate_limit_interval=5)
@registered_only
async def warns(message: types.Message):
    user = Users.get_or_none(Users.id == message.chat.id)
    await message.reply(f'Warns: {user.warns}.\n3 варна - мут на 7 часов.')

@dp.message_handler(commands=["tag"])
@delayed_message(rate_limit=2, rate_limit_interval=3)
async def toggle_tagging(message: Message):
    if message.chat.type != types.ChatType.PRIVATE:
        return

    try:
        user = Users.get(Users.id == message.from_user.id)
        if user:
            if user.tag:
                Users.update(tag=False).where(Users.id == message.from_user.id).execute()
                await message.reply("Ваши следующие сообщения <b>не</b> будут помечены вашим ником")
            else:
                Users.update(tag=True).where(Users.id == message.from_user.id).execute()
                await message.reply("Ваши следующие сообщения будут помечены вашим ником и @username")
    except DoesNotExist:
        # Если пользователя нет в Users (DATABASE), то добавить его.
        Users.create(id=message.from_user.id, tag=True)
        await message.reply("Ваши следующие сообщения будут помечены вашим ником и @username\nВы были зарегистрированы в боте.", parse_mode="HTML")

def remove_dogs(user_id, e):
    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"{current_time} - Removed user in Users. Reason: {e}"

        Users.delete().where(Users.id == user_id).execute()

        with open(log_file, "a") as file:
            file.write(log_message + "\n")

        print(f"User with blocked successfully removed from Users.")
    except Exception as e:
        print(f"Error occurred while removing user: {str(e)}")

async def send(message, *args, **kwargs):
    return (await message.copy_to(*args, **kwargs)), args[0]

async def Send(message, keyboard, keyboard_del_my_msg, reply_data):
    result = [{"sender_id": message.from_user.id}]
    tasks = {}

    for user in Users.select(Users.id):
        if user.id != message.from_user.id:
            task = asyncio.create_task(
                send(
                    message,
                    user.id,
                    reply_markup=keyboard,
                    reply_to_message_id=get_reply_id32(reply_data, user.id) if message.reply_to_message else None
                )
            )
            tasks[task] = user.id

        if user.id == message.from_user.id:
            task = asyncio.create_task(
                send(
                    message,
                    message.from_user.id,
                    reply_markup=keyboard_del_my_msg,
                    reply_to_message_id=get_reply_id32(reply_data, user.id) if message.reply_to_message else None
                )
            )
            tasks[task] = user.id

    for task in tasks:
        try:
            msg_obj = await task
            if isinstance(msg_obj, tuple):
                msg, user_id = msg_obj
                if isinstance(msg, MessageId):
                    result.append({"time": str(datetime.now()), "chat_id": user_id, "msg_id": msg.message_id})
        except Exception as e:
            if (("bot was blocked by the user" in str(e).lower() and not (Users.get(Users.id==tasks[task]).mute > datetime.now() or Users.get(Users.id==tasks[task]).warns >= 1)) or 
                "user is deactivated" in str(e).lower()):
                blocked_user_id = tasks[task]
                remove_dogs(blocked_user_id, e)

    result.append({"time": str(datetime.now()), "chat_id": message.chat.id, "msg_id": message.message_id})

    for item in result:
        time = item.get('time', '')
        msg_id = item.get('msg_id', '')

        if time and msg_id:
            print(f"{time}, Message ID: {msg_id}")
            break

    msgs_db = rdb.get("messages", [])
    msgs_db.append(result) # type: ignore
    rdb.set("messages", msgs_db)


@dp.message_handler(content_types="any")
@registered_only
async def any(message: Message):
    if message.content_type == "pinned_message":
        return

    user_id = message.from_user.id

    if datetime.now() < Users.get(Users.id==user_id).mute:
        delay = Users.get(Users.id == user_id).mute - datetime.now()
        duration = delay.total_seconds()

        seconds = int(duration % 60)
        minutes = int((duration // 60) % 60)
        hours = int((duration // 3600) % 24)
        days = int((duration // 86400) % 30.4375)  # средняя продолжительность месяца
        months = int((duration // 2629800) % 12)  # средняя продолжительность года
        years = int(duration // 31557600)  # продолжительность года

        duration_string = ""
        if years > 0:
            duration_string += f"{years} год{' ' if years == 1 else 'а ' if 2 <= years <= 4 else 'ов '}"
        if months > 0:
            duration_string += f"{months} месяц{' ' if months == 1 else 'а ' if 2 <= months <= 4 else 'ев '}"
        if days > 0:
            duration_string += f"{days} д{'ень ' if days == 1 else 'ня ' if 2 <= days <= 4 else 'ней '}"
        if hours > 0:
            duration_string += f"{hours} час{' ' if hours == 1 else 'а ' if 2 <= hours <= 4 else 'ов '}"
        if minutes > 0:
            duration_string += f"{minutes} минут{'а ' if minutes == 1 else 'ы ' if 2 <= minutes <= 4 else ' '}"
        if seconds > 0:
            duration_string += f"{seconds} секунд{'а' if seconds == 1 else ''}"

        umute = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Mute .", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")) # type: ignore
        return await message.reply(f"Ты сможешь писать только через {duration_string}", reply_markup=umute)
    if message.text and (
        "цп" in message.text.lower()
        or "цэпэ" in message.text.lower()
        or "цэпе" in message.text.lower()
        or "цепэ" in message.text.lower()
        or "цопэ" in message.text.lower()
        or "дeтское" in message.text.lower()
        or "дeтское" in message.text.lower()
        or "дeтcкoе" in message.text.lower()
        or "дeтcкoe" in message.text.lower()
        or "детское" in message.text.lower()
        or "детское" in message.text.lower()
        or "детское" in message.text.lower()
        or "детское" in message.text.lower()
        or "детское" in message.text.lower()
        or "детское" in message.text.lower()
        or "детское" in message.text.lower()
        or "детское" in message.text.lower()
        or "child" in message.text.lower()
        or "детского" == message.text
        or "детского порно" == message.text
        or "Детского" == message.text
        or "children's" == message.text
        or "children's porn" == message.text
        or "children porn" == message.text
        or "childrens porn" == message.text
        or "children" == message.text):
        with open("handlers/content/stop.txt", "r") as file:
            fsb = file.read()
        await message.reply(fsb)
        return

    if message.text and "ㅤ" in message.text.lower():
        return

    if Users.get(Users.id==user_id).tag and (message.from_user.full_name == "#DEBUG" 
                                          or message.from_user.full_name == "#Debug"
                                          or message.from_user.full_name == "DEBUG"
                                          or message.from_user.full_name == "Debug"
                                          ):
        await message.reply(
            "Твоё имя не разрешено, смени его\n"
            "Либо, выключи /tag")
        return

    if Users.get(Users.id==user_id).tag:
        name = message.from_user.full_name
        username_or_rickroll = f"https://t.me/{message.from_user.username}/" if message.from_user.username else "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        also = f"https://t.me/{message.from_user.username}/" if message.from_user.username else "not0username!"
        keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text=name, url=also if also.startswith("https") else None, callback_data=also if not also.startswith("https") else None) # type: ignore
        )
        if Admins.get_or_none(id=user_id):
            keyboard.add(
            InlineKeyboardButton("ADMIN", username_or_rickroll) # type: ignore
            )
    else:
        keyboard = None

    keyboard_del_my_msg = None

    if message.from_user.id:
        text = "DELETE THIS MESSAGE"
        if Users.get(Users.id==user_id).tag:
            name = message.from_user.full_name
            username_or_rickroll = f"https://t.me/{message.from_user.username}/" if message.from_user.username else "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            also = f"https://t.me/{message.from_user.username}/" if message.from_user.username else "not0username!"
            keyboard_del_my_msg = InlineKeyboardMarkup().add(
            InlineKeyboardButton(text=name, url=also if also.startswith("https") else None, callback_data=also if not also.startswith("https") else None) # type: ignore
            )
            if Admins.get_or_none(id=user_id):
                keyboard_del_my_msg.add(
                InlineKeyboardButton("ADMIN", username_or_rickroll) # type: ignore
                )
            keyboard_del_my_msg.add(
                    InlineKeyboardButton(text , callback_data=f"delete_msg={message.message_id}") # type: ignore
                )
        else:
            keyboard_del_my_msg = InlineKeyboardMarkup().add(
                InlineKeyboardButton(text , callback_data=f"delete_msg={message.message_id}") # type: ignore
            )

    if message.reply_to_message:
        reply_data = get_reply_data(message.chat.id, message.reply_to_message.message_id)
    else:
        reply_data = None

    if message.text or message.caption:
        if Users.get(Users.id==user_id).last_msg == (message.text or message.caption):
            return await message.reply("Сообщение совпадает с предыдущим.")
        Users.update(last_msg=message.text or message.caption).where(Users.id==user_id).execute()

    if is_flood(message.chat.id):
        Users.update(mute=datetime.now() + timedelta(minutes=3)).where(Users.id==message.chat.id).execute()
        minchgod = InlineKeyboardMarkup().add(InlineKeyboardButton(text=f"#FLOOD", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")) # type: ignore
        ims = await message.reply("Это флуд.\nВы были отключены от чата на 3 минуты", reply_markup=minchgod)
        await bot.pin_chat_message(ims.chat.id, ims.message_id)
        return

    users = Users.select()
    hey = await message.reply("Send..")
    start_time = time.monotonic()
    await Send(message, keyboard, keyboard_del_my_msg, reply_data)
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

    await hey.edit_text(f"Твоё сообщение было отправлено {len(users)} пользователям бота за <b>{send_duration_str}</b>", parse_mode="HTML")

    Users.update(mute=datetime.now()).where(Users.id==user_id).execute()