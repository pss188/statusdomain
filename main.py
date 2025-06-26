import requests
import asyncio
from datetime import datetime
import os
from telegram import Bot
from telegram.constants import ParseMode
import aiohttp
import schedule
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID"))

bot = Bot(token=BOT_TOKEN)

DOMAIN_TXT_URL = "https://raw.githubusercontent.com/pss188/statusdomain/refs/heads/main/domain.txt"  # Ganti ini dengan RAW GitHub URL kamu

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

def cek_domain_sync(domain):
    try:
        response = requests.get(f"http://{domain}", timeout=5)
        if response.status_code == 200:
            return "UP"
        else:
            return f"DOWN (status code: {response.status_code})"
    except requests.RequestException:
        return "DOWN (no response)"

async def job_cek_domain():
    domains = await ambil_list_domain()
    if not domains:
        return

    down_domains = {}
    for domain in domains:
        status = cek_domain_sync(domain)
        print(f"{datetime.now()}: {domain} -> {status}")
        if status != "UP":
            down_domains[domain] = status

    if down_domains:
        pesan = f"⚠️ *Laporan Domain DOWN* ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}):\n"
        for d, s in down_domains.items():
            pesan += f"- {d}: {s}\n"
        await kirim_pesan(pesan)
    else:
        print(f"{datetime.now()}: Semua domain UP.")

async def job_lapor_status_bot():
    pesan = f"✅ Bot masih aktif ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
    await kirim_pesan(pesan)

async def run_async_jobs():
    await job_cek_domain()
    await job_lapor_status_bot()

    while True:
        schedule.run_pending()
        await asyncio.sleep(1
