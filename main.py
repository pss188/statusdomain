import os
import asyncio
import requests
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError, InvalidToken

# Konfigurasi
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TOKEN_BOT_TELEGRAM") or "bot7658399639:AAEoNPljoAfZXWM7TeksXpHcdTPqv3OAvw4"
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or os.getenv("ID_GRUP_TELEGRAM")

async def main():
    try:
        # Validasi token
        if not TOKEN.startswith('bot'):
            TOKEN = f'bot{TOKEN}'
        
        bot = Bot(token=TOKEN)
        
        # Test koneksi
        me = await bot.get_me()
        print(f"🤖 Bot @{me.username} berhasil terhubung!")
        
        # Kirim test notifikasi
        await bot.send_message(
            chat_id=CHAT_ID,
            text=f"🟢 Bot aktif!\nWaktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        print("✅ Semua sistem berfungsi!")
        
    except InvalidToken:
        print("\n❌ TOKEN TIDAK VALID! Perbaiki:")
        print("1. Pastikan token diawali dengan 'bot'")
        print("2. Format: bot<angka>:<string>")
        print(f"3. Token Anda: {TOKEN[:10]}...")
        print("\n💡 Dapatkan token baru dari @BotFather")
    except Exception as e:
        print(f"\n⚠️ ERROR: {type(e).__name__} - {e}")

if __name__ == "__main__":
    print("🚀 Memulai sistem monitoring...")
    asyncio.run(main())
