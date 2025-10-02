import logging
import random
import string
import database as db
import fake_data_generator as fake

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
)

# --- KONFIGURASI ---
# Ganti dengan token bot Anda
BOT_TOKEN = "8031557668:AAGeXCvMv4724G6WNboGer0vlT4HVqXIynM"
EMAIL_DOMAIN = "@nezastore.com"

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- State untuk ConversationHandler ---
GENERATING = 0

# --- FUNGSI GENERATOR ---
def generate_unique_email(base_name):
    """
    Menghasilkan email unik berdasarkan nama dasar yang diberikan.
    Format: [base_name][3_angka_acak]@nezastore.com
    """
    while True:
        # Hasilkan 3 angka acak
        three_random_digits = str(random.randint(0, 999)).zfill(3)
        
        # Gabungkan nama dasar dengan angka
        generated_name = base_name + three_random_digits
        full_email = generated_name.lower().replace(" ", "") + EMAIL_DOMAIN

        # Cek keunikan di database
        if not db.is_email_generated(full_email):
            db.add_generated_email(full_email)
            return full_email

# --- FUNGSI HANDLER BOT ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Memulai bot dan menampilkan tombol generate."""
    user = update.effective_user
    
    welcome_text = (
        f"👋 *Selamat Datang, {user.first_name}!* \n\n"
        "Saya adalah Bot Generator Data Profesional.\n\n"
        "Klik tombol di bawah untuk membuat satu set data pribadi lengkap secara acak."
    )
    
    keyboard = [
        [InlineKeyboardButton("🚀 Buat Data Lengkap", callback_data='generate_data')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text=welcome_text, reply_markup=reply_markup, parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            welcome_text, reply_markup=reply_markup, parse_mode='Markdown'
        )

    return GENERATING

async def generate_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Menangani pembuatan data palsu dan email."""
    query = update.callback_query
    await query.answer()

    # Tampilkan pesan loading
    await query.edit_message_text(
        text="⏳ *Memproses...*\n\n_Mencari kombinasi data unik untuk Anda..._", 
        parse_mode='Markdown'
    )

    # 1. Generate semua data palsu
    fake_data = fake.generate_all_data()
    
    # 2. Generate email unik berdasarkan username
    new_email = generate_unique_email(fake_data['username'])

    # 3. Format teks hasil
    result_text = (
        f"✅ *Data Berhasil Dibuat:*\n\n"
        f"*Nama Depan*:\n`{fake_data['nama_depan']}`\n\n"
        f"*Nama Belakang*:\n`{fake_data['nama_belakang']}`\n\n"
        f"*Nama Lengkap*:\n`{fake_data['nama_lengkap']}`\n\n"
        f"*Username*:\n`{fake_data['username']}`\n\n"
        f"*NIK*:\n`{fake_data['nik']}`\n\n"
        f"*Tanggal Lahir*:\n`{fake_data['tanggal_lahir']}`\n\n"
        f"*Tempat Lahir*:\n`{fake_data['tempat_lahir']}`\n\n"
        f"*Alamat*:\n`{fake_data['alamat']}`\n\n"
        f"*Kecamatan*:\n`{fake_data['kecamatan']}`\n\n"
        f"*Kota*:\n`{fake_data['kota']}`\n\n"
        f"*Provinsi*:\n`{fake_data['provinsi']}`\n\n"
        f"*Kode Pos*:\n`{fake_data['kode_pos']}`\n\n"
        f"*Telepon*:\n`{fake_data['telepon']}`\n\n"
        f"--- \n\n"
        f"*Email*:\n`{new_email}`\n\n"
        f"_(Klik pada teks di atas untuk menyalinnya)_"
    )

    keyboard = [
        [InlineKeyboardButton("🔄 Buat Lagi", callback_data='generate_data')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=result_text, reply_markup=reply_markup, parse_mode='Markdown'
    )

    return GENERATING

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Membatalkan percakapan."""
    await update.message.reply_text("Proses dibatalkan. Ketik /start untuk memulai lagi.")
    return ConversationHandler.END

def main() -> None:
    """Fungsi utama untuk menjalankan bot."""
    # Setup database
    db.setup_database()

    application = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GENERATING: [
                CallbackQueryHandler(generate_data_handler, pattern='^generate_data$')
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)

    logger.info("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
