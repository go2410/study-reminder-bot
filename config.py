import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
USER_ID = int(os.getenv("USER_ID"))

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
