import os
import requests
import time
from telegram import Bot
from telegram.error import TelegramError

# Konfigurasi
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Token bot Telegram
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")     # ID grup Telegram
CHECK_INTERVAL = 300                                # 5 menit (dalam detik)
DOMAIN_FILE = "domain.txt"                          # File berisi daftar domain

def load_domains():
    """Baca daftar domain dari file"""
    try:
        with open(DOMAIN_FILE, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: File {DOMAIN_FILE} tidak ditemukan!")
        return []

def ping_website(url):
    """Cek status website"""
    try:
        response = requests.get(url, timeout=10)
        return response.status_code < 400  # Anggap status 4xx/5xx sebagai down
    except (requests.ConnectionError, requests.Timeout, requests.RequestException):
        return False

def send_telegram_alert(message):
    """Kirim notifikasi ke Telegram"""
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except TelegramError as e:
        print(f"Gagal mengirim alert ke Telegram: {e}")

def monitor_domains():
    domains = load_domains()
    if not domains:
        print("Tidak ada domain yang dimonitor. Keluar...")
        return

    print(f"Memulai monitoring {len(domains)} domain...")
    while True:
        for domain in domains:
            status = ping_website(domain)
            if not status:
                alert_msg = f"🚨 **Website DOWN**\nDomain: {domain}\nWaktu: {time.strftime('%Y-%m-%d %H:%M:%S')}"
                send_telegram_alert(alert_msg)
                print(f"Alert terkirim: {domain} DOWN")
            else:
                print(f"{domain} ✅ UP")
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor_domains()
