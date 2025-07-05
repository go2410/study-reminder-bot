from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from config import API_TOKEN, USER_ID

scheduler = AsyncIOScheduler()
bot = Bot(token=API_TOKEN)

def send_reminder():
    scheduler.add_job(bot.send_message, "cron", hour="9-18", minute=0, args=[USER_ID, "Не забудь выполнить задание!"])

def reset_reminders():
    scheduler.remove_all_jobs()
    send_reminder()
