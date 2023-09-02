# ⚖️ GPL-3.0 license
# 🏳️‍⚧️ Project on Mirai :<https://github.com/hoangpungnyuga/>
import time
from playhouse.postgres_ext import PostgresqlExtDatabase
from peewee import Model, BooleanField, DateTimeField, IntegerField, TextField, BigAutoField
from lightdb import LightDB
from datetime import datetime, timedelta
from collections import defaultdict

rdb = LightDB("data/replies.json")
control = defaultdict(list)

Connect = {
    "database": 'echo',             # Имя вашей базы
    "user":     'hope',             # Имя пользователя для доступа к базе
    "password": 'mirai',            # Password от пользователя user
    "host":     '35.206.135.113',   # IP адрес хоста, либо localhost
    "port":      5432               # Port для подключения
}

db = PostgresqlExtDatabase(**Connect)

def connect_to_database():
    try:
        start_time = time.time()
        db.connect()
        end_time = time.time()
        connection_time = (end_time - start_time) * 1000
        print(f"Connected to the database in {connection_time:.2f} ms")
        return connection_time
    except Exception as e:
        print(f"Failed to connect to the database: {e}")
        return None


class BaseModel(Model):
    class Meta:
        database = db

class Users(BaseModel):
    id = BigAutoField()
    ban = BooleanField(default=False)
    mute = DateTimeField(default=datetime.now)
    warns = IntegerField(default=0)
    last_msg = TextField(null=True)
    tag = BooleanField(default=False)
    anon = BooleanField(default=False)

class Admins(BaseModel):
    id = BigAutoField(primary_key=True)
    name = TextField(default="Модератор")
    rights = TextField(default="mute;warn")

class Settings(BaseModel):
    kicked_dogs = BooleanField(default=True)

# Создание таблиц в PostgreSQL
with db:
    db.create_tables([Users, Admins, Settings])

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
