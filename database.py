import sqlite3

DATABASE_FILE = "generated_emails.db"

def setup_database():
    """Membuat tabel jika belum ada."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_address TEXT NOT NULL UNIQUE
        )
    """)
    conn.commit()
    conn.close()

def add_generated_email(email):
    """Menambahkan email baru ke database."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO emails (email_address) VALUES (?)", (email,))
        conn.commit()
    except sqlite3.IntegrityError:
        # Email sudah ada, tidak masalah.
        pass
    finally:
        conn.close()

def is_email_generated(email):
    """Mengecek apakah email sudah ada di database."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM emails WHERE email_address = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    return result is not None
