import os
import requests
import asyncio
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError, InvalidToken

# ========== KONFIGURASI ==========
TOKEN_BOT = os.getenv("TOKEN_BOT_TELEGRAM")  # Token dari @BotFather
ID_GRUP = os.getenv("ID_GRUP_TELEGRAM")      # ID grup Telegram
FILE_DOMAIN = "domain.txt"                   # File berisi daftar domain
INTERVAL_CHEK = 300                          # 5 menit (dalam detik)
INTERVAL_LAPORAN = 3600                      # 1 jam (dalam detik)

# ========== IKON UNTUK NOTIFIKASI ==========
IKON = {
    "aktif": "🟢",
    "down": "🔴",
    "bot": "🤖",
    "waktu": "🕒",
    "laporan": "📊",
    "peringatan": "🚨",
    "error": "❗"
}

# ========== FUNGSI UTAMA ==========
def muat_domain():
    """Muat daftar domain dari file"""
    try:
        with open(FILE_DOMAIN, 'r') as f:
            return [baris.strip() for baris in f if baris.strip()]
    except FileNotFoundError:
        pesan_error = f"{IKON['error']} File {FILE_DOMAIN} tidak ditemukan!"
        print(pesan_error)
        return []

def cek_situs(url):
    """Periksa status website"""
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        return response.status_code < 400  # Anggap 4xx/5xx sebagai down
    except Exception as e:
        print(f"{IKON['error']} Error cek {url}: {type(e).__name__}")
        return False

async def kirim_notifikasi(bot, pesan):
    """Kirim pesan ke Telegram dengan error handling"""
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
    """Generate laporan status"""
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
    """Fungsi utama untuk monitoring"""
    # Validasi token
    if not TOKEN_BOT or not TOKEN_BOT.startswith("bot"):
        raise InvalidToken("Format token tidak valid! Harus diawali 'bot'")
    
    if not ID_GRUP:
        raise ValueError("ID grup Telegram belum di-set")
    
    # Inisialisasi bot
    bot = Bot(token=TOKEN_BOT)
    info = await bot.get_me()
    print(f"{IKON['bot']} Bot {info.username} siap monitoring!")
    
    daftar_domain = muat_domain()
    if not daftar_domain:
        await kirim_notifikasi(bot, f"{IKON['error']} Tidak ada domain yang dimonitor!")
        return
    
    print(f"{IKON['waktu']} Memulai monitoring {len(daftar_domain)} domain...")
    await kirim_notifikasi(bot, f"{IKON['bot']} *Bot memulai monitoring*")
    
    waktu_lapor = time.time()
    
    while True:
        try:
            # Periksa semua domain
            for domain in daftar_domain:
                if not cek_situs(domain):
                    pesan = (
                        f"{IKON['peringatan']} *WEBSITE DOWN!*\n"
                        f"• Domain: `{domain}`\n"
                        f"• Waktu: {datetime.now().strftime('%H:%M:%S')}\n"
                        f"• Status: {IKON['down']} OFFLINE"
                    )
                    await kirim_notifikasi(bot, pesan)
            
            # Laporan berkala
            if time.time() - waktu_lapor >= INTERVAL_LAPORAN:
                laporan = buat_laporan(daftar_domain)
                if await kirim_notifikasi(bot, laporan):
                    waktu_lapor = time.time()
            
            await asyncio.sleep(INTERVAL_CHEK)
            
        except Exception as e:
            print(f"{IKON['error']} Error utama: {type(e).__name__}")
            await asyncio.sleep(60)  # Tunggu 1 menit jika ada error

# ========== JALANKAN PROGRAM ==========
if __name__ == "__main__":
    print(f"{IKON['waktu']} Memulai program monitoring...")
    try:
        asyncio.run(monitor())
    except KeyboardInterrupt:
        print(f"\n{IKON['bot']} Bot dihentikan manual")
    except Exception as e:
        print(f"{IKON['error']} Error fatal: {type(e).__name__}")
