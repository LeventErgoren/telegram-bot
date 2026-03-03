import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

CHANNEL_1_ID = int(os.getenv("CHANNEL_1_ID").strip())
CHANNEL_2_ID = int(os.getenv("CHANNEL_2_ID").strip())

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    klavye = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Kanal 1 VIP - 100$", callback_data="odeme_kanal1")],
        [InlineKeyboardButton(text="Kanal 2 Premium - 200$", callback_data="odeme_kanal2")]
    ])
    
    await message.answer("Merhaba! Lütfen satın almak istediğiniz paketi seçin:", reply_markup=klavye)


@dp.callback_query(F.data.in_(["odeme_kanal1", "odeme_kanal2"]))
async def handle_payment_simulation(callback: types.CallbackQuery):
    await callback.answer("Ödemeniz kontrol ediliyor...")
    
    if callback.data == "odeme_kanal1":
        hedef_kanal = CHANNEL_1_ID
        paket_adi = "Kanal 1 VIP (100$)"
    else:
        hedef_kanal = CHANNEL_2_ID
        paket_adi = "Kanal 2 Premium (200$)"

    try:
        invite_link = await bot.create_chat_invite_link(
            chat_id=hedef_kanal,
            member_limit=1
        )
        
        cevap_metni = (
            f"✅ {paket_adi} ödemeniz başarıyla onaylandı!\n\n"
            "Aşağıdaki link tek kullanımlıktır ve sadece sizin içindir. "
            f"Lütfen tıklayarak kanala katılın:\n{invite_link.invite_link}"
        )
        
        await bot.send_message(chat_id=callback.from_user.id, text=cevap_metni)
        
    except Exception as e:
        await bot.send_message(
            chat_id=callback.from_user.id, 
            text="Link üretilirken bir sorun oluştu. Lütfen botun kanalda 'Yönetici' olduğundan emin olun."
        )
        print(f"Hata detayı: {e}")

async def main():
    print("Profesyonel Bot çalışmaya başladı...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())