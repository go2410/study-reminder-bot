from aiogram import Bot, Dispatcher, types
from fastapi import FastAPI, Request
from aiogram.types import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from config import API_TOKEN, WEBHOOK_URL
from scheduler import scheduler, send_reminder, reset_reminders
from config import bot, dp

bot.set_current(bot)
dp.set_current(dp)

app = FastAPI()

# Кнопка "Сбросить напоминания"
reset_button = InlineKeyboardMarkup().add(
    InlineKeyboardButton("🔄 Сбросить напоминания", callback_data="reset_reminders")
)

# Обработка команды /start
@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer(
        "Привет! Я буду напоминать тебе выполнять задания.",
        reply_markup=reset_button
    )
    send_reminder()

# Обработка команды /done
@dp.message_handler(commands=["done"])
async def done_handler(message: types.Message):
    await message.answer("Отлично! Напоминания сегодня отключены.")
    scheduler.remove_all_jobs()

# ✅ Обработка нажатия на кнопку "Сбросить напоминания"
@dp.callback_query_handler(lambda c: c.data == "reset_reminders")
async def reset_callback(callback_query: CallbackQuery):
    reset_reminders()
    await callback_query.answer("Напоминания перезапущены!")
    await callback_query.message.answer("🔔 Напоминания сброшены и начнутся заново.")

# Webhook
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update(**data)
    await dp.process_update(update)
    return {"ok": True}

# Startup
@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)
    scheduler.start()
    send_reminder()

# Shutdown
@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()
