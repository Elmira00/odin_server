# from telethon import TelegramClient
# import os

# api_id = 13082905
# api_hash = '08dd43a26927d34884c99ef456677a23'

# # Absolute path
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# SESSION_PATH = os.path.join(BASE_DIR, "scraper_session")  # extension otomatik eklenir

# client = TelegramClient(SESSION_PATH, api_id, api_hash)




from telethon import TelegramClient
from telethon.sessions import StringSession
import redis
import os

api_id = 13082905
api_hash = '08dd43a26927d34884c99ef456677a23'

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0


def get_telegram_client():
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    session_string = r.get("telegram_session")
    if not session_string:
        raise Exception("Session not found in Redis. Please run create_session.py first..")
    return TelegramClient(StringSession(session_string.decode()), api_id, api_hash)
