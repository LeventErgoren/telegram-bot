import os
import asyncio
import asyncpg
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand

# Çevresel değişkenleri yükle
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Kanal ID'lerini al ve boşlukları temizle
CHANNEL_1_ID = int(os.getenv("CHANNEL_1_ID").strip())
CHANNEL_2_ID = int(os.getenv("CHANNEL_2_ID").strip())

# Veritabanı bilgileri
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST", "localhost")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db_pool = None # Veritabanı bağlantı havuzu

# --- VERİTABANI BAŞLATMA VE BAĞLANTI (RETRY MANTIĞI) ---
async def init_db():
    global db_pool
    while True:
        try:
            db_pool = await asyncpg.create_pool(
                user=DB_USER, password=DB_PASSWORD, database=DB_NAME, host=DB_HOST
            )
            async with db_pool.acquire() as conn:
                # Tablo yoksa oluşturur
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS yetkili_kullanicilar (
                        user_id BIGINT,
                        channel_id BIGINT,
                        PRIMARY KEY (user_id, channel_id)
                    )
                ''')
            print("✅ PostgreSQL Veritabanı bağlantısı başarılı ve tablo hazır.")
            break # Başarılı olursa döngüden çık
        except Exception as e:
            print(f"⏳ Veritabanı henüz hazır değil, 3 saniye sonra tekrar deneniyor... (Sistem Mesajı: {e})")
            await asyncio.sleep(3) # Çökmek yerine 3 saniye bekle ve tekrar dene

# --- MENÜ AYARLARI (OTOMATİK KOMUT GÖRÜNÜMÜ) ---
async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command="start", description="Botu başlat ve paketleri gör"),
        BotCommand(command="yardim", description="Sistem hakkında bilgi al"),
        BotCommand(command="iptal", description="İşlemi iptal et")
    ]
    await bot.set_my_commands(main_menu_commands)

# --- START KOMUTU VE VİZYON MENÜSÜ ---
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    klavye = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Kanal 1 VIP - 100$", callback_data="odeme_kanal1")],
        [InlineKeyboardButton(text="Kanal 2 Premium - 200$", callback_data="odeme_kanal2")],
        # Müşteriyi etkileyecek vizyon butonları:
        [InlineKeyboardButton(text="💼 Hesabım / Aboneliklerim", callback_data="hesabim")],
        [InlineKeyboardButton(text="📊 Kripto Analiz Araçları (Yakında)", callback_data="yakinda")]
    ])
    
    hosgeldin_mesaji = (
        f"Merhaba {message.from_user.first_name}, VIP panele hoş geldin! 🚀\n\n"
        "Lütfen işlem yapmak istediğiniz menüyü aşağıdan seçin:"
    )
    await message.answer(hosgeldin_mesaji, reply_markup=klavye)

# --- YARDIM VE BİLGİ KOMUTU ---
@dp.message(Command("yardim"))
async def send_help(message: types.Message):
    yardim_metni = (
        "💎 *Premium VIP Bot Sistemine Hoş Geldiniz*\n\n"
        "Bu bot, VIP gruplarımıza güvenli ve tam otomatik erişim sağlamanız için tasarlanmıştır.\n\n"
        "📌 *Sistem Nasıl Çalışır?*\n"
        "1️⃣ `/start` komutu ile üyelik paketlerini listeleyin.\n"
        "2️⃣ Size uygun olan VIP veya Premium kanalı seçin.\n"
        "3️⃣ Kripto ödeme adımını tamamlayın.\n"
        "4️⃣ Sistem ödemenizi ağ üzerinden otomatik doğrular.\n"
        "5️⃣ Size özel üretilen tek kullanımlık şifreli link ile kanala anında katılın.\n\n"
        "🔒 _Tüm işlemleriniz blockchain altyapısı ile güvence altındadır._\n\n"
        "Yardıma mı ihtiyacınız var? Aşağıdaki butonları kullanabilirsiniz:"
    )
    
    klavye = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❓ Sıkça Sorulan Sorular", callback_data="sss_bilgi")],
        # URL kısmına müşterinin kendi iletişim linkini koyabilirsin
        [InlineKeyboardButton(text="👨‍💻 Müşteri Temsilcisi", url="https://t.me/telegram")] 
    ])
    
    await message.answer(yardim_metni, reply_markup=klavye, parse_mode="Markdown")

# --- SAHTE (MOCK) BUTON İŞLEVLERİ (SUNUM İÇİN) ---
@dp.callback_query(F.data == "sss_bilgi")
async def send_faq(callback: types.CallbackQuery):
    await callback.answer()
    sss_metni = (
        "📌 *Sıkça Sorulan Sorular*\n\n"
        "*S: Hangi kripto paralarla ödeme yapabilirim?*\n"
        "C: Çok yakında USDT (TRC20) ve diğer popüler ağlar entegre edilecektir.\n\n"
        "*S: Ödememi yaptım ama link gelmedi, ne yapmalıyım?*\n"
        "C: Sistem blockchain onaylarını beklemektedir, genellikle 1-3 dakika içinde linkiniz otomatik iletilir."
    )
    await callback.message.answer(sss_metni, parse_mode="Markdown")

@dp.callback_query(F.data == "hesabim")
async def show_account(callback: types.CallbackQuery):
    await callback.answer()
    hesap_metni = (
        f"👤 *Kullanıcı:* {callback.from_user.first_name}\n"
        f"🆔 *ID:* `{callback.from_user.id}`\n\n"
        "⭐ *Aktif Abonelik:* Bulunmuyor\n"
        "💰 *Bağlı Cüzdan:* Henüz eklenmedi"
    )
    await callback.message.answer(hesap_metni, parse_mode="Markdown")

@dp.callback_query(F.data == "yakinda")
async def show_coming_soon(callback: types.CallbackQuery):
    # Ekranda pop-up olarak küçük bir uyarı çıkarır
    await callback.answer("Bu özellik şu anda geliştirme aşamasındadır. Çok yakında aktif olacak!", show_alert=True)

# --- ÖDEME VE LİNK ÜRETME (KANAL 1) ---
@dp.callback_query(F.data == "odeme_kanal1")
async def process_payment_kanal1(callback: types.CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    mesaj = await callback.message.answer("Kanal 1 VIP için ödeme işleniyor... Lütfen bekleyin.")
    await asyncio.sleep(2) # Ödeme simülasyonu
    
    try:
        # 1. Kullanıcıyı Veritabanına Kaydet
        async with db_pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO yetkili_kullanicilar (user_id, channel_id) 
                VALUES ($1, $2) ON CONFLICT DO NOTHING
            ''', user_id, CHANNEL_1_ID)
        
        # 2. Katılma İsteği Gerektiren Link Oluştur
        invite_link = await bot.create_chat_invite_link(chat_id=CHANNEL_1_ID, creates_join_request=True)
        await mesaj.edit_text(f"✅ Ödeme başarılı! Kanal 1 VIP için giriş linkiniz (Onay gerektirir):\n{invite_link.invite_link}")
    except Exception as e:
        print(f"Hata: {e}")
        await mesaj.edit_text("❌ İşlem başarısız. Bot yetkilerini kontrol edin.")

# --- ÖDEME VE LİNK ÜRETME (KANAL 2) ---
@dp.callback_query(F.data == "odeme_kanal2")
async def process_payment_kanal2(callback: types.CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    mesaj = await callback.message.answer("Kanal 2 Premium için ödeme işleniyor... Lütfen bekleyin.")
    await asyncio.sleep(2)
    
    try:
        async with db_pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO yetkili_kullanicilar (user_id, channel_id) 
                VALUES ($1, $2) ON CONFLICT DO NOTHING
            ''', user_id, CHANNEL_2_ID)
            
        invite_link = await bot.create_chat_invite_link(chat_id=CHANNEL_2_ID, creates_join_request=True)
        await mesaj.edit_text(f"✅ Ödeme başarılı! Kanal 2 Premium için giriş linkiniz (Onay gerektirir):\n{invite_link.invite_link}")
    except Exception as e:
        print(f"Hata: {e}")
        await mesaj.edit_text("❌ İşlem başarısız. Bot yetkilerini kontrol edin.")

# --- KATILMA İSTEĞİ (JOIN REQUEST) KONTROLÜ ---
@dp.chat_join_request()
async def handle_join_request(update: types.ChatJoinRequest):
    user_id = update.from_user.id
    channel_id = update.chat.id
    
    # Kapıdaki kişinin ID'sini veritabanında arıyoruz
    async with db_pool.acquire() as conn:
        kayit = await conn.fetchval('''
            SELECT 1 FROM yetkili_kullanicilar 
            WHERE user_id = $1 AND channel_id = $2
        ''', user_id, channel_id)
        
    if kayit:
        # Ödemesi var, içeri al.
        await update.approve()
        print(f"✅ Kullanıcı {user_id} kanala ({channel_id}) alındı.")
    else:
        # Ödemesi yok (Linki başkasından bulmuş), reddet.
        await update.decline()
        print(f"❌ Kullanıcı {user_id} kanala ({channel_id}) girmeye çalıştı ama reddedildi (Ödeme yok).")

# --- ANA ÇALIŞTIRMA DÖNGÜSÜ ---
async def main():
    print("Sistem başlatılıyor...")
    await init_db()           # Önce veritabanına bağlanmayı bekle
    await set_main_menu(bot)  # Sonra menüleri ayarla
    print("Profesyonel Bot çalışmaya başladı...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())