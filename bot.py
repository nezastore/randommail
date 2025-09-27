import logging
import random
import string
import database as db

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

# Daftar domain email yang bisa dipilih
EMAIL_DOMAINS = {
    'gmail': '@gmail.com',
    'outlook': '@outlook.com',
    'hotmail': '@hotmail.com',
    'neza': '@nezastore.com'
}

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Memuat daftar nama dari file
try:
    with open('names.txt', 'r') as f:
        NAMES_LIST = [line.strip() for line in f if line.strip()]
    if not NAMES_LIST:
        raise ValueError("File names.txt kosong atau tidak ditemukan.")
except (FileNotFoundError, ValueError) as e:
    logger.error(f"Error: {e}. Pastikan file 'names.txt' ada dan berisi nama.")
    NAMES_LIST = ["user", "guest", "test", "demo"]

# --- State untuk ConversationHandler ---
SELECTING_DOMAIN, GENERATING_EMAIL = range(2)

# --- FUNGSI GENERATOR (BAGIAN YANG DIUBAH) ---
def generate_unique_email(domain):
    """
    Fungsi utama untuk menghasilkan email unik dengan panjang 10-15 karakter
    dan HANYA menggunakan huruf.
    """
    while True:
        # Tentukan target panjang total secara acak antara 10 dan 15 karakter
        target_length = random.randint(10, 15)

        # 1. Mulai dengan 1 atau 2 nama acak sebagai dasar
        num_starting_names = random.randint(1, 2)
        base_names = random.sample(NAMES_LIST, min(num_starting_names, len(NAMES_LIST)))
        base_name_str = "".join(base_names)

        # 2. Potong nama dasar jika sudah lebih panjang dari target
        if len(base_name_str) > target_length:
            base_name_str = base_name_str[:target_length]

        # 3. Hitung berapa banyak karakter acak yang perlu ditambahkan
        remaining_length = target_length - len(base_name_str)
        
        random_part = ''
        if remaining_length > 0:
            # Menggunakan string.ascii_lowercase SAJA (tanpa string.digits)
            random_part = ''.join(random.choices(string.ascii_lowercase, k=remaining_length))

        # 4. Gabungkan semuanya
        generated_name = base_name_str + random_part
        full_email = generated_name + domain

        # 5. Cek ke database untuk memastikan keunikan
        if not db.is_email_generated(full_email):
            db.add_generated_email(full_email)
            return full_email

# --- FUNGSI HANDLER BOT ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Memulai bot dan menampilkan pilihan domain."""
    user = update.effective_user
    
    welcome_text = (
        f"👋 *Selamat Datang, {user.first_name}!* \n\n"
        "Saya adalah Bot Generator Email Profesional. Silakan pilih domain email yang Anda inginkan dari daftar di bawah ini."
    )
    
    keyboard = [
        [InlineKeyboardButton("Gmail", callback_data='domain_gmail'), InlineKeyboardButton("Outlook", callback_data='domain_outlook')],
        [InlineKeyboardButton("Hotmail", callback_data='domain_hotmail'), InlineKeyboardButton("Nezastore", callback_data='domain_neza')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Jika dipanggil via /start, kirim pesan baru. Jika dari state lain, edit pesan.
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

    return SELECTING_DOMAIN

async def select_domain(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Menangani pemilihan domain dan menampilkan tombol generate."""
    query = update.callback_query
    await query.answer()

    # Ekstrak pilihan domain dari callback_data (cth: 'domain_gmail' -> 'gmail')
    domain_key = query.data.split('_')[1]
    selected_domain = EMAIL_DOMAINS[domain_key]
    
    # Simpan domain yang dipilih di context user data untuk digunakan nanti
    context.user_data['selected_domain'] = selected_domain

    text = (
        f"✅ Domain dipilih: *{selected_domain}*\n\n"
        "Sekarang Anda siap untuk membuat email. Klik tombol di bawah ini untuk memulai prosesnya."
    )

    keyboard = [
        [InlineKeyboardButton("🚀 Generate Email", callback_data='generate_email')],
        [InlineKeyboardButton("🔙 Kembali (Pilih Domain Lain)", callback_data='back_to_start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='Markdown')
    
    return GENERATING_EMAIL

async def generate_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Menangani klik tombol generate email."""
    query = update.callback_query
    await query.answer()

    selected_domain = context.user_data.get('selected_domain')
    if not selected_domain:
        # Jika karena suatu hal domain tidak tersimpan, kembalikan ke awal
        await query.edit_message_text(text="Terjadi kesalahan. Silakan mulai lagi.")
        return await start(update, context)

    # Tampilkan pesan loading
    await query.edit_message_text(text=f"⏳ *Memproses...*\n\n_Mencari kombinasi unik dengan domain {selected_domain}..._", parse_mode='Markdown')

    # Generate email baru
    new_email = generate_unique_email(selected_domain)

    # Tampilkan hasil dengan format yang mudah disalin
    result_text = (
        f"✅ *Berhasil! Email Unik Anda Siap Digunakan:*\n\n"
        f"Berikut adalah email yang telah dibuat:\n\n"
        f"`{new_email}`\n\n"
        f"*(Klik pada alamat email di atas untuk menyalinnya secara otomatis)*\n"
    )

    keyboard = [
        [InlineKeyboardButton("🔄 Generate Lagi", callback_data='generate_email')],
        [InlineKeyboardButton("🔙 Kembali (Pilih Domain Lain)", callback_data='back_to_start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text=result_text, reply_markup=reply_markup, parse_mode='Markdown')

    return GENERATING_EMAIL

async def end_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Mengakhiri percakapan (opsional, untuk perintah /cancel)."""
    await update.message.reply_text("Proses dibatalkan. Ketik /start untuk memulai lagi.")
    return ConversationHandler.END


def main() -> None:
    """Fungsi utama untuk menjalankan bot."""
    # Setup database
    db.setup_database()

    application = Application.builder().token(BOT_TOKEN).build()
    
    # Menggunakan ConversationHandler untuk alur yang lebih kompleks
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING_DOMAIN: [
                CallbackQueryHandler(select_domain, pattern='^domain_')
            ],
            GENERATING_EMAIL: [
                CallbackQueryHandler(generate_button_click, pattern='^generate_email$'),
                CallbackQueryHandler(start, pattern='^back_to_start$') # Kembali ke fungsi start
            ],
        },
        fallbacks=[CommandHandler("start", start)], # Jika pengguna mengirim /start di tengah proses
    )

    application.add_handler(conv_handler)

    logger.info("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
