# telegram_bot.py
import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
import aiosqlite
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
DB_PATH = os.getenv("DB_PATH", "monitor.db")

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def send_alert_message(text: str):
    try:
        if ADMIN_ID:
            await bot.send_message(chat_id=ADMIN_ID, text=text)
    except Exception as e:
        logging.error(f"Ошибка отправки в Telegram: {e}")

@dp.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer("Hello!")

@dp.message(Command("status"))
async def cmd_status(message: Message):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT cpu, ram, disk, timestamp FROM metrics ORDER BY timestamp DESC LIMIT 1") as cursor:
            row = await cursor.fetchone()

    if not row:
        await message.answer("⚠️ Данных пока нет. Монитор запущен?")
        return

    cpu, ram, disk, timestamp = row
    
    text = (
        f"🖥 <b>Server Status</b>\n"
        f"🕒 <i>{timestamp}</i>\n\n"
        f"⚙️ <b>CPU:</b> {cpu}%\n"
        f"🧠 <b>RAM:</b> {ram}%\n"
        f"💾 <b>Disk:</b> {disk}%"
    )
    
    await message.answer(text, parse_mode="HTML")