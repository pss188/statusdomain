import os
import asyncio
from telegram import Bot
from telegram.error import TelegramError, InvalidToken

async def main():
    try:
        # 1. Ambil token dari environment variable
        TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "bot7658399639:AAEoNPljoAfZXWM7TeksXpHcdTPqv3OAvw4"
        
        if not TOKEN:
            raise ValueError("Token tidak ditemukan! Set ENV 'TELEGRAM_BOT_TOKEN'")
        
        # 2. Pastikan format token benar
        if not TOKEN.startswith('bot'):
            TOKEN = f'bot{TOKEN}'
            print(f"⚠️  Token diperbaiki: {TOKEN[:15]}...")
        
        # 3. Inisialisasi bot
        bot = Bot(token=TOKEN)
        me = await bot.get_me()
        print(f"🤖 Bot @{me.username} berhasil terhubung!")
        
        # 4. Kirim test message
        CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
        if CHAT_ID:
            await bot.send_message(
                chat_id=CHAT_ID,
                text="✅ Bot berhasil diaktifkan!"
            )
        
        print("🚀 Sistem monitoring siap berjalan!")
        
    except InvalidToken as e:
        print(f"❌ Token tidak valid: {e}\n"
              "💡 Dapatkan token baru dari @BotFather")
    except Exception as e:
        print(f"⚠️  Error tak terduga: {type(e).__name__} - {e}")

if __name__ == "__main__":
    print("🔍 Memulai inisialisasi...")
    asyncio.run(main())
