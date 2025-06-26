import requests
import time
import schedule
from datetime import datetime
import telegram
import os

# Ambil token dan chat id dari environment variables (lebih aman)
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID"))

bot = telegram.Bot(token=BOT_TOKEN)

# Ganti URL ini sesuai lokasi domain.txt di GitHub kamu
DOMAIN_TXT_URL = "https://raw.githubusercontent.com/pss188/statusdomain/refs/heads/main/domain.txt"

status_results = {}

def ambil_list_domain():
    try:
        response = requests.get(DOMAIN_TXT_URL, timeout=10)
        response.raise_for_status()
        domains = response.text.strip().splitlines()
        domains = [d.strip() for d in domains if d.strip()]
        return domains
    except Exception as e:
        print(f"Error ambil domain.txt: {e}")
        return []

def cek_domain(domain):
    try:
        response = requests.get(f"http://{domain}", timeout=5)
        if response.status_code == 200:
            return "UP"
        else:
            return f"DOWN (status code: {response.status_code})"
    except requests.RequestException:
        return "DOWN (no response)"

def job_cek_domain():
    global status_results
    domains = ambil_list_domain()
    if not domains:
        print("Tidak dapat ambil daftar domain.")
        return
    for domain in domains:
        status = cek_domain(domain)
        status_results[domain] = status
        print(f"{datetime.now()}: {domain} -> {status}")

def job_kirim_laporan():
    if not status_results:
        print("Tidak ada hasil cek domain untuk dilaporkan.")
        return
    pesan = "Laporan Status Domain per jam:\n"
    for domain, status in status_results.items():
        pesan += f"- {domain}: {status}\n"
    bot.send_message(chat_id=GROUP_CHAT_ID, text=pesan)
    print(f"{datetime.now()}: Laporan terkirim ke Telegram")

def main():
    job_cek_domain()  # cek langsung saat mulai

    schedule.every(5).minutes.do(job_cek_domain)
    schedule.every(60).minutes.do(job_kirim_laporan)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
