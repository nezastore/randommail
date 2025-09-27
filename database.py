import sqlite3

# Nama file database
DB_NAME = 'main.db'

def setup_database():
    """Membuat tabel jika belum ada."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Membuat tabel untuk menyimpan email yang sudah di-generate
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS generated_emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    conn.close()
    print("Database siap digunakan.")

def is_email_generated(email):
    """Mengecek apakah email sudah ada di database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM generated_emails WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def add_generated_email(email):
    """Menambahkan email baru ke database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO generated_emails (email) VALUES (?)", (email,))
        conn.commit()
    except sqlite3.IntegrityError:
        # Email sudah ada, abaikan error
        pass
    finally:
        conn.close()
