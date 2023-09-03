# ⚖️ GPL-3.0 license
# 🏳️‍⚧️ Project on Mirai :<https://github.com/hoangpungnyuga/>
from peewee import SqliteDatabase, Model, PrimaryKeyField, BooleanField, DateTimeField, TextField, IntegerField
from lightdb import LightDB
from datetime import datetime, timedelta
from collections import defaultdict

db = SqliteDatabase("data/db.sql")
rdb = LightDB("data/replies.json")
control = defaultdict(list)

class BaseModel(Model):
	class Meta:
		database = db

class Users(BaseModel):
	id = PrimaryKeyField()
	ban = BooleanField(default=False)
	mute = DateTimeField(default=datetime.now())
	name = TextField(null=True)
	warns = IntegerField(default=0)
	last_msg = TextField(null=True)
	tag = BooleanField(default=False)

class Admins(BaseModel):
	id = PrimaryKeyField()
	name = TextField(default="Модератор")
	rights = TextField(default="mute;warn")

with db:
	db.create_tables([Users, Admins])

def get_reply_data(chat_id, msg_id):
	for msg in rdb.get("messages", []):
		for i in msg[1:]:
			if i["chat_id"] == chat_id and i["msg_id"] == msg_id:
				return msg[1:]

def get_reply_id(data, chat_id):
        if not data:
                return
        for i in data:
                if i["chat_id"] == chat_id:
                        return i["msg_id"]

def get_reply_id32(data, chat_id):
    if not data:
        return
    current_time = datetime.now()
    ten_hours_ago = current_time - timedelta(hours=32)
    for i in reversed(data):
        if i.get("chat_id") == chat_id:
            message_time = datetime.fromisoformat(i.get("time"))
            if message_time >= ten_hours_ago:
                return i.get("msg_id")

def get_reply_sender(chat_id, msg_id):
	for msg in rdb.get("messages", []):
		for i in msg[1:]: 
			if i["chat_id"] == chat_id and i["msg_id"] == msg_id:
				return msg[0]["sender_id"]

def is_flood(chat_id): # проверяем есть ли флуд
	control[chat_id].append(datetime.now()) # запоминаем время
	times = filter(lambda time: datetime.now() - time < timedelta(seconds=5), control[chat_id]) # проверяем время
	return len(list(times)) > 5 # если больше 5 секунд, то флуд
