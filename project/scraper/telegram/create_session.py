from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import redis
from django.conf import settings

api_id = 13082905
api_hash = '08dd43a26927d34884c99ef456677a23'
phone_number = '+994997452565'

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0


r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

with TelegramClient(StringSession(), api_id, api_hash) as client:
    client.start(phone=phone_number)  
    session_string = client.session.save()

    r.set("telegram_session", session_string)
    print("Session created and saved.")
