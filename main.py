import requests
import asyncio
from datetime import datetime
import os
from telegram import Bot
from telegram.constants import ParseMode
import aiohttp

# Ambil token dan chat ID dari environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID"))

# Ganti dengan RAW URL domain.txt milikmu
DOMAIN_TXT_URL = "https://raw.githubusercontent.com/pss188/statusdomain/refs/heads/main/domain.txt"

bot = Bot(token=BOT_TOKEN)

async def kirim_pesan(pesan):
    try:
        await bot.send_message(chat_id=GROUP_CHAT_ID, text=pesan, parse_mode=ParseMode.MARKDOWN)
        print(f"{datetime.now()}: Pesan terkirim ke Telegram")
    except Exception as e:
        print(f"Error kirim pesan: {e}")

async def ambil_list_domain():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(DOMAIN_TXT_URL, timeout=10) as response:
                if response.status != 200:
                    raise Exception(f"HTTP status {response.status}")
                text = await response.text()
                domains = [d.strip() for d in text.strip().splitlines() if d.strip()]
                return domains
    except Exception as e:
        print(f"Error ambil domain.txt: {e}")
        return []

def cek_domain(domain):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(f"http://{domain}", timeout=5, headers=headers)
        if response.status_code == 200:
            return "UP"
        else:
            return f"DOWN (status code: {response.status_code})"
    except requests.RequestException:
        return "DOWN (no response)"

async def cek_domain_job():
    domains = await ambil_list_domain()
    if not domains:
        print(f"{datetime.now()}: Tidak ada domain yang bisa dicek.")
        return

    down = {}
    for domain in domains:
        status = cek_domain(domain)
        print(f"{datetime.now()}: {domain} -> {status}")
        if status != "UP":
            down[domain] = status

    if down:
        pesan = f"⚠️ *Laporan Domain DOWN* ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}):\n"
        for d, s in down.items():
            pesan += f"- {d}: {s}\n"
        await kirim_pesan(pesan)

async def lapor_status_bot():
    pesan = f"🤖 Bot aktif ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
    await kirim_pesan(pesan)

async def run_bot():
    print("🚀 Bot mulai dijalankan...")
    while True:
        now = datetime.now()

        # Cek domain tiap 5 menit
        if now.minute % 5 == 0:
            await cek_domain_job()

        # Lapor status tiap jam (saat menit == 0)
        if now.minute == 0:
            await lapor_status_bot()

        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(run_bot())
