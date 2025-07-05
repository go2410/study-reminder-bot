import os
import json
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from datetime import datetime
from scheduler import scheduler

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
USER_ID = int(os.getenv("USER_ID"))

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
bot.set_current(bot)
dp.set_current(dp)

app = FastAPI()

TASKS_FILE = "tasks.json"

DAILY_TASKS = {
    '1': 'Изучи переменные и напиши калькулятор.',
    '2': 'Условия: напиши программу, которая определяет, можно ли водить машину.',
    '3': 'Циклы и строки: посчитай частоту слова в тексте.',
    '4': 'Списки и словари: сделай список покупок.',
    '5': 'Собери анализатор текста.'
}

keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton("Показать задание снова"))
keyboard.add(KeyboardButton("Я выполнил задание"))

inline_keyboard = InlineKeyboardMarkup().add(
    InlineKeyboardButton("Повторить задание", callback_data="repeat_task"),
    InlineKeyboardButton("Сбросить сессию", callback_data="reset_session")
)

def load_tasks():
    try:
        with open(TASKS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_tasks(data):
    with open(TASKS_FILE, 'w') as f:
        json.dump(data, f)

def is_task_completed(date_str):
    tasks = load_tasks()
    return tasks.get(date_str, False)

def mark_task_completed(date_str):
    tasks = load_tasks()
    tasks[date_str] = True
    save_tasks(tasks)

async def send_task():
    today = datetime.now().date().isoformat()
    if is_task_completed(today):
        return
    day_num = str((datetime.now().date() - datetime(2025, 7, 4).date()).days + 1)
    task = DAILY_TASKS.get(day_num, "Сегодня выходной! :)")
    await bot.send_message(USER_ID, f"🔔 Задание на сегодня:\n{task}", reply_markup=keyboard)

async def send_reminder():
    today = datetime.now().date().isoformat()
    if not is_task_completed(today):
        await bot.send_message(USER_ID, "⏰ Не забудь выполнить задание дня!", reply_markup=keyboard)

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer("Привет! Я буду присылать тебе задания и напоминать, пока ты не сделаешь их.", reply_markup=keyboard)
    await send_task()

@dp.message_handler(lambda m: m.text == "Показать задание снова")
async def show_task(message: types.Message):
    await send_task()

@dp.message_handler(lambda m: m.text == "Я выполнил задание")
async def complete_task(message: types.Message):
    today = datetime.now().date().isoformat()
    mark_task_completed(today)
    await message.answer("✅ Отлично! Напоминания отключены на сегодня. Горжусь тобой! ✊")

@dp.message_handler(commands=["reset"])
async def reset_handler(message: types.Message):
    scheduler.remove_all_jobs()
    await message.answer("Сессия сброшена. Напоминания начнутся заново.")
    await send_task()

@dp.callback_query_handler(lambda c: c.data == "repeat_task")
async def inline_repeat(callback_query: types.CallbackQuery):
    await send_task()
    await callback_query.answer("Задание отправлено повторно.")

@dp.callback_query_handler(lambda c: c.data == "reset_session")
async def inline_reset(callback_query: types.CallbackQuery):
    scheduler.remove_all_jobs()
    await callback_query.message.answer("Сессия сброшена. Напоминания начнутся заново.")
    await send_task()
    await callback_query.answer("Сессия сброшена")

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update(**data)
    bot.set_current(bot)
    dp.set_current(dp)
    await dp.process_update(update)
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)
    scheduler.start()
    scheduler.add_job(send_task, 'cron', hour=4, minute=0)
    for hour in range(5, 14):
        scheduler.add_job(send_reminder, 'cron', hour=hour, minute=0)
    await send_task()

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()
