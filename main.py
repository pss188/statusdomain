import os
import requests
import time
import asyncio
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError

# Konfigurasi
TOKEN_BOT_TELEGRAM = os.getenv("TOKEN_BOT_TELEGRAM")
ID_GRUP_TELEGRAM = os.getenv("ID_GRUP_TELEGRAM")
INTERVAL_PEMERIKSAAN = 300  # 5 menit (dalam detik)
FILE_DOMAIN = "domain.txt"
INTERVAL_LAPORAN = 3600  # 1 jam (dalam detik)

# Ikon untuk laporan
IKON = {
    "aktif": "🟢",
    "down": "🔴",
    "bot": "🤖",
    "waktu": "🕒",
    "laporan": "📊",
    "peringatan": "🚨"
}

def muat_domain():
    """Muat daftar domain dari file"""
    try:
        with open(FILE_DOMAIN, 'r') as f:
            return [baris.strip() for baris in f if baris.strip()]
    except FileNotFoundError:
        print(f"Error: File {FILE_DOMAIN} tidak ditemukan!")
        return []

def periksa_situs(url):
    """Periksa status website"""
    try:
        response = requests.get(url, timeout=10)
        return response.status_code < 400  # Anggap status 4xx/5xx sebagai down
    except (requests.ConnectionError, requests.Timeout, requests.RequestException):
        return False

async def kirim_pesan_telegram(pesan):
    """Kirim pesan ke Telegram"""
    bot = Bot(token=TOKEN_BOT_TELEGRAM)
    try:
        await bot.send_message(
            chat_id=ID_GRUP_TELEGRAM,
            text=pesan,
            parse_mode="Markdown"
        )
    except TelegramError as e:
        print(f"Gagal mengirim pesan Telegram: {e}")

def buat_laporan_status(domain_list):
    """Buat laporan status berkala"""
    laporan = [
        f"{IKON['laporan']} *Laporan Status Website*",
        f"{IKON['waktu']} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ""
    ]
    
    for domain in domain_list:
        status = periksa_situs(domain)
        ikon = IKON['aktif'] if status else IKON['down']
        laporan.append(f"{ikon} `{domain}`")
    
    laporan.extend([
        "",
        f"{IKON['bot']} *Bot sedang berjalan* ✅",
        f"Laporan berikutnya dalam 1 jam"
    ])
    
    return "\n".join(laporan)

async def monitor_domain():
    daftar_domain = muat_domain()
    if not daftar_domain:
        print("Tidak ada domain yang dimonitor. Keluar...")
        return

    waktu_laporan_terakhir = time.time()
    print(f"Memantau {len(daftar_domain)} domain...")

    while True:
        waktu_sekarang = time.time()
        
        # Periksa semua domain
        for domain in daftar_domain:
            if not periksa_situs(domain):
                pesan_peringatan = (
                    f"{IKON['peringatan']} *Website Down!*\n"
                    f"• Domain: `{domain}`\n"
                    f"• Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"• Status: {IKON['down']} Offline"
                )
                await kirim_pesan_telegram(pesan_peringatan)
                print(f"Peringatan terkirim: {domain} DOWN")

        # Kirim laporan berkala
        if waktu_sekarang - waktu_laporan_terakhir >= INTERVAL_LAPORAN:
            laporan = buat_laporan_status(daftar_domain)
            await kirim_pesan_telegram(laporan)
            waktu_laporan_terakhir = waktu_sekarang
            print(f"Laporan terkirim pada {datetime.now()}")

        await asyncio.sleep(INTERVAL_PEMERIKSAAN)

if __name__ == "__main__":
    asyncio.run(monitor_domain())
