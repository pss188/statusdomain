import requests
import asyncio
from datetime import datetime
import os
from telegram import Bot
from telegram.constants import ParseMode
import logging

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID"))

bot = Bot(token=BOT_TOKEN)

def baca_domain():
    try:
        with open("domain.txt", "r") as f:
            domains = [line.strip() for line in f if line.strip()]
            return domains
    except Exception as e:
        logger.error(f"Error baca domain: {e}")
        return []

def cek_domain(domain):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(f"http://{domain}", timeout=5, headers=headers)
        # Anggap domain UP selama ada respons HTTP apapun
        return "UP"
    except requests.RequestException:
        return "Kayaknya Gak Bisa Dibuka, Tolong Cek? Kalau masih bisa abaikan aja"

async def kirim_pesan(pesan):
    try:
        await bot.send_message(chat_id=GROUP_CHAT_ID, text=pesan, parse_mode=ParseMode.MARKDOWN)
        logger.info(f"{datetime.now()}: Pesan terkirim ke Telegram")
    except Exception as e:
        logger.error(f"Error kirim pesan: {e}")

async def cek_domain_job():
    domains = baca_domain()
    if not domains:
        logger.warning(f"{datetime.now()}: Tidak ada domain yang bisa dicek.")
        return

    down = {}
    for domain in domains:
        status = cek_domain(domain)
        logger.info(f"{datetime.now()}: {domain} -> {status}")
        if status != "UP":
            down[domain] = status

    if down:
        pesan = f"⚠️ *Laporan Domain DOWN* ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}):\n"
        for d, s in down.items():
            pesan += f"- {d}: {s}\n"
        await kirim_pesan(pesan)

async def lapor_status_bot():
    pesan = f"🤖 Bot Cek Domain Masih Hidup ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
    await kirim_pesan(pesan)

async def run_bot():
    logger.info("🚀 Bot mulai dijalankan...")
    while True:
        now = datetime.now()

        # Cek domain tiap 5 menit
        if now.minute % 5 == 0:
            await cek_domain_job()

        # Lapor status tiap jam (menit = 0)
        if now.minute == 0:
            await lapor_status_bot()

        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(run_bot())
