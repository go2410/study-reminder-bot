from aiogram import Bot, Dispatcher, types
from fastapi import FastAPI, Request
from aiogram.types import Update
from config import API_TOKEN, WEBHOOK_URL
from scheduler import scheduler, send_reminder
import asyncio

# Создаём бота и диспетчер
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Устанавливаем текущие экземпляры
bot.set_current(bot)
dp.set_current(dp)

app = FastAPI()

# Команды
@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer("Привет! Я буду напоминать тебе выполнять задания.")
    send_reminder()

@dp.message_handler(commands=["done"])
async def done_handler(message: types.Message):
    await message.answer("Отлично! Напоминания сегодня отключены.")
    scheduler.remove_all_jobs()

# Webhook приём
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update(**data)
    await dp.process_update(update)
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)
    scheduler.start()
    send_reminder()

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()
