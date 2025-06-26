import os
import requests
import time
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CHECK_INTERVAL = 300  # 5 minutes (in seconds)
DOMAIN_FILE = "domain.txt"
REPORT_INTERVAL = 3600  # 1 hour (in seconds)

# Icons for status reports
ICONS = {
    "up": "🟢",
    "down": "🔴",
    "bot": "🤖",
    "time": "🕒",
    "report": "📊",
    "alert": "🚨"
}

def load_domains():
    """Load domains from file"""
    try:
        with open(DOMAIN_FILE, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: {DOMAIN_FILE} not found!")
        return []

def check_website(url):
    """Check if website is up"""
    try:
        response = requests.get(url, timeout=10)
        return response.status_code < 400  # Consider 4xx/5xx as down
    except (requests.ConnectionError, requests.Timeout, requests.RequestException):
        return False

def send_telegram_message(message):
    """Send message to Telegram"""
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode="Markdown"
        )
    except TelegramError as e:
        print(f"Failed to send Telegram message: {e}")

def generate_status_report(domains):
    """Generate hourly status report"""
    report = [
        f"{ICONS['report']} *Hourly Domain Status Report*",
        f"{ICONS['time']} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ""
    ]
    
    for domain in domains:
        status = check_website(domain)
        icon = ICONS['up'] if status else ICONS['down']
        report.append(f"{icon} `{domain}`")
    
    report.extend([
        "",
        f"{ICONS['bot']} *Bot Cek Domain Aktif* ✅",
        f"Laporan selanjutnya 1 jam lagi"
    ])
    
    return "\n".join(report)

def monitor_domains():
    domains = load_domains()
    if not domains:
        print("No domains to monitor. Exiting...")
        return

    last_report_time = time.time()
    print(f"Monitoring {len(domains)} domains...")

    while True:
        current_time = time.time()
        
        # Check all domains
        for domain in domains:
            if not check_website(domain):
                alert_msg = (
                    f"{ICONS['alert']} *Website Down Alert*\n"
                    f"• Domain: `{domain}`\n"
                    f"• Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"• Status: {ICONS['down']} Offline"
                )
                send_telegram_message(alert_msg)
                print(f"Alert sent: {domain} is DOWN")

        # Send hourly report
        if current_time - last_report_time >= REPORT_INTERVAL:
            report = generate_status_report(domains)
            send_telegram_message(report)
            last_report_time = current_time
            print(f"Hourly report sent at {datetime.now()}")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor_domains()
