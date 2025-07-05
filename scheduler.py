from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError
from aiogram import Bot
from config import API_TOKEN, USER_ID
from pytz import timezone

# Инициализация планировщика и бота
scheduler = AsyncIOScheduler(timezone=timezone("Asia/Almaty"))
bot = Bot(token=API_TOKEN)

# Добавление напоминаний
def send_reminder():
    scheduler.add_job(
        bot.send_message,
        "cron",
        hour="9-18",  # каждый час с 09:00 до 18:00
        minute=0,
        args=[USER_ID, "⏰ Напоминание: не забудь выполнить задание!"],
        id="reminder_job",
        replace_existing=True,
    )

# Сброс и перезапуск
def reset_reminders():
    try:
        scheduler.remove_job("reminder_job")
    except JobLookupError:
        pass
    send_reminder()
