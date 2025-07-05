import os
import json
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
from dotenv import load_dotenv

from config import API_TOKEN, WEBHOOK_URL, USER_ID
from scheduler import scheduler, send_reminder

load_dotenv()

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
bot.set_current(bot)
dp.set_current(dp)

app = FastAPI()

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer("Привет! Я буду напоминать тебе выполнять задания.")
    send_reminder()

@dp.message_handler(commands=["reset"])
async def reset_handler(message: types.Message):
    scheduler.remove_all_jobs()
    send_reminder()
    await message.answer("Сессия сброшена. Напоминания начнутся заново.")

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
    send_reminder()

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()
