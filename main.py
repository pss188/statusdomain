import requests
import time
import schedule
from datetime import datetime
import telegram
import os

# Ambil token dan chat id dari environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID"))

bot = telegram.Bot(token=BOT_TOKEN)

DOMAIN_TXT_URL = "https://raw.githubusercontent.com/pss188/statusdomain/refs/heads/main/domain.txt"  # Ganti URL ini

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
    domains = ambil_list_domain()
    if not domains:
        print(f"{datetime.now()}: Tidak dapat ambil daftar domain.")
        return

    down_domains = {}
    for domain in domains:
        status = cek_domain(domain)
        print(f"{datetime.now()}: {domain} -> {status}")
        if status != "UP":
            down_domains[domain] = status

    if down_domains:
        pesan = f"⚠️ Laporan Domain DOWN ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}):\n"
        for d, s in down_domains.items():
            pesan += f"- {d}: {s}\n"
        try:
            bot.send_message(chat_id=GROUP_CHAT_ID, text=pesan)
            print(f"{datetime.now()}: Laporan domain DOWN terkirim ke Telegram")
        except Exception as e:
            print(f"Error kirim laporan domain DOWN: {e}")
    else:
        print(f"{datetime.now()}: Semua domain UP, tidak kirim laporan.")

def job_lapor_status_bot():
    pesan = f"🤖 Bot status: Aktif dan berjalan baik ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
    try:
        bot.send_message(chat_id=GROUP_CHAT_ID, text=pesan)
        print(f"{datetime.now()}: Laporan status bot terkirim ke Telegram")
    except Exception as e:
        print(f"Error kirim laporan status bot: {e}")

def main():
    job_cek_domain()
    job_lapor_status_bot()

    schedule.every(5).minutes.do(job_cek_domain)
    schedule.every(60).minutes.do(job_lapor_status_bot)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
