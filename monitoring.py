import asyncio
import aiosqlite
import psutil
import logging
import os
from datetime import datetime, timedelta 

from telegram_bot import bot, dp, send_alert_message

logging.basicConfig(level=logging.INFO)

DB_PATH = os.getenv("DB_PATH", "monitor.db")

last_alert_times = {}
ALERT_COOLDOWN = timedelta(minutes=10)

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                cpu REAL,
                ram REAL,
                disk REAL
            )
        """)
        await db.commit()

async def handle_alert(key, message):
    now = datetime.now()
    last_time = last_alert_times.get(key)
    
    if last_time is None or (now - last_time) > ALERT_COOLDOWN:
        logging.warning(f"ALERT: {message}")
        await send_alert_message(message)
        last_alert_times[key] = now

async def save_to_db(cpu, ram, disk):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO metrics (cpu, ram, disk) VALUES (?, ?, ?)",
                (cpu, ram, disk)
            )
            await db.commit()
    except Exception as e:
        logging.error(f"Ошибка записи в БД: {e}")


async def check_cpu(threshold=80):
    cpu_usage = await asyncio.to_thread(psutil.cpu_percent, interval=1)
    if cpu_usage > threshold:
        await handle_alert("cpu", f"🔥 High CPU usage: {cpu_usage}%")
    return cpu_usage

async def check_memory(threshold=85):
    memory_usage = psutil.virtual_memory().percent
    if memory_usage > threshold:
        await handle_alert("ram", f"⚠️ High Memory usage: {memory_usage}%")
    return memory_usage

async def check_disk(path='/host', threshold=90):
    target_path = path if os.path.exists(path) else '/'
    
    disk_usage = psutil.disk_usage(target_path).percent
    if disk_usage > threshold:
        await handle_alert("disk", f"💾 Low disk space: {disk_usage}% used")
    return disk_usage


async def monitoring_cycle():
    while True:
        cpu_task = asyncio.create_task(check_cpu())
        memory_task = asyncio.create_task(check_memory())
        disk_task = asyncio.create_task(check_disk())

        cpu = await cpu_task
        mem = await memory_task
        disk = await disk_task

        logging.info(f"Metrics: CPU:{cpu}% RAM:{mem}% Disk:{disk}%")
        await save_to_db(cpu, mem, disk)
        
        await asyncio.sleep(60)

async def main():
    await init_db()

    await asyncio.gather(
        monitoring_cycle(),       
        dp.start_polling(bot)     
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")