import os
import requests
import asyncio
import time
from datetime import datetime
from telegram import Bot
from telegram.error import InvalidToken
from dotenv import load_dotenv

# Load .env (untuk lokal, di Railway abaikan ini)
load_dotenv()

TOKEN_BOT = os.getenv("TOKEN_BOT_TELEGRAM")
ID_GRUP = os.getenv("ID_GRUP_TELEGRAM")
FILE_DOMAIN = "domain.txt"
INTERVAL_CHEK = 300  # detik (5 menit)
INTERVAL_LAPORAN = 3600  # detik (1 jam)

IKON = {
    "aktif": "🟢",
    "down": "🔴",
    "bot": "🤖",
    "waktu": "🕒",
    "laporan": "📊",
    "peringatan": "🚨",
    "error": "❗"
}

print("🚀 Program mulai dijalankan...")

def muat_domain():
    try:
        with open(FILE_DOMAIN, 'r') as f:
            return [baris.strip() for baris in f if baris.strip()]
    except FileNotFoundError:
        print(f"{IKON['error']} File {FILE_DOMAIN} tidak ditemukan!")
        return []

def cek_situs(url):
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        return response.status_code < 400
    except Exception as e:
        print(f"{IKON['error']} Error cek {url}: {type(e).__name__}")
        return False

async def kirim_notifikasi(bot, pesan):
    try:
        await bot.send_message(
            chat_id=ID_GRUP,
            text=pesan,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        return True
    except Exception as e:
        print(f"{IKON['error']} Gagal kirim notifikasi: {type(e).__name__}")
        return False

def buat_laporan(daftar_domain):
    header = f"{IKON['laporan']} *LAPORAN MONITORING*"
    waktu = f"{IKON['waktu']} {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    body = []
    for domain in daftar_domain:
        status = cek_situs(domain)
        icon = IKON['aktif'] if status else IKON['down']
        body.append(f"{icon} `{domain}`")
    footer = f"\n{IKON['bot']} *Bot aktif* | Laporan berikutnya dalam 1 jam"
    return "\n".join([header, waktu, ""] + body + [footer])

async def monitor():
    if not TOKEN_BOT or not TOKEN_BOT.startswith("bot"):
        raise InvalidToken("❌ Token tidak valid! Harus diawali 'bot'")
    if not ID_GRUP:
        raise ValueError("❌ ID grup Telegram belum di-set")

    bot = Bot(token=TOKEN_BOT)
    try:
        info = await bot.get_me()
        print(f"{IKON['bot']} Bot {info.username} siap monitoring!")
    except Exception as e:
        print(f"{IKON['error']} Token gagal digunakan: {e}")
        return

    daftar_domain = muat_domain()
    if not daftar_domain:
        await kirim_notifikasi(bot, f"{IKON['error']} Tidak ada domain yang dimonitor!")
        return

    print(f"{IKON['waktu']} Memulai monitoring {len(daftar_domain)} domain...")
    await kirim_notifikasi(bot, f"{IKON['bot']} *Bot memulai monitoring*")

    waktu_lapor = time.time()

    while True:
        try:
            for domain in daftar_domain:
                if not cek_situs(domain):
                    pesan = (
                        f"{IKON['peringatan']} *WEBSITE DOWN!*\n"
                        f"• Domain: `{domain}`\n"
                        f"• Waktu: {datetime.now().strftime('%H:%M:%S')}\n"
                        f"• Status: {IKON['down']} OFFLINE"
                    )
                    await kirim_notifikasi(bot, pesan)

            if time.time() - waktu_lapor >= INTERVAL_LAPORAN:
                laporan = buat_laporan(daftar_domain)
                if await kirim_notifikasi(bot, laporan):
                    waktu_lapor = time.time()

            await asyncio.sleep(INTERVAL_CHEK)
        except Exception as e:
            print(f"{IKON['error']} Error utama: {type(e).__name__}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(monitor())
    except KeyboardInterrupt:
        print("\n🤖 Bot dihentikan manual")
    except Exception as e:
        print(f"❗ Error fatal: {e}")
