from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import bot, USER_ID

scheduler = AsyncIOScheduler()

def send_reminder():
    scheduler.add_job(
        bot.send_message,
        "cron",
        hour="9-18",
        minute=0,
        args=[USER_ID, "Не забудь выполнить задание!"],
    )

def reset_reminders():
    scheduler.remove_all_jobs()
    send_reminder()
