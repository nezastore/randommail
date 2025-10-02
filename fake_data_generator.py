import random
from datetime import datetime, timedelta

# --- SUMBER DATA ---
# Anda bisa memperluas daftar ini untuk hasil yang lebih beragam
try:
    with open('names.txt', 'r', encoding='utf-8') as f:
        NAMES_LIST = [line.strip() for line in f if line.strip()]
    if not NAMES_LIST:
        raise FileNotFoundError
except FileNotFoundError:
    NAMES_LIST = ["Budi", "Ani", "Citra", "Dedi", "Eka", "Firmansyah", "Gunawan", "Herawati", "Indra", "Jaya"]

CITIES_PROVINCES = {
    "DKI Jakarta": ["Jakarta Pusat", "Jakarta Barat", "Jakarta Selatan", "Jakarta Timur", "Jakarta Utara"],
    "Jawa Barat": ["Bandung", "Bekasi", "Bogor", "Depok", "Cirebon"],
    "Jawa Tengah": ["Semarang", "Surakarta", "Magelang", "Pekalongan"],
    "Jawa Timur": ["Surabaya", "Malang", "Sidoarjo", "Jember"],
    "Kalimantan Timur": ["Samarinda", "Balikpapan", "Bontang", "Tenggarong"],
    "Sulawesi Selatan": ["Makassar", "Parepare", "Palopo"],
}
STREET_NAMES = ["Pahlawan", "Merdeka", "Sudirman", "Diponegoro", "Gajah Mada", "Kartini", "Dahlia", "Kenanga"]
DISTRICT_NAMES = ["Barat", "Timur", "Pusat", "Utara", "Selatan", "Indah", "Baru", "Lama"]

# --- FUNGSI PEMBANTU ---
def generate_names():
    """Menghasilkan nama depan, belakang, dan lengkap."""
    first_name = random.choice(NAMES_LIST)
    last_name = random.choice(NAMES_LIST)
    # Pastikan nama depan dan belakang tidak sama
    while first_name == last_name:
        last_name = random.choice(NAMES_LIST)
    return {
        "nama_depan": first_name,
        "nama_belakang": last_name,
        "nama_lengkap": f"{first_name} {last_name}"
    }

def generate_username(first_name, last_name):
    """Membuat username dari nama."""
    num = random.randint(10, 9999)
    # Hapus spasi dan ubah ke huruf kecil
    fn_clean = first_name.lower().replace(" ", "")
    ln_clean = last_name.lower().replace(" ", "")
    
    formats = [
        f"{fn_clean}{ln_clean}{num}",
        f"{fn_clean}.{ln_clean}{num}",
        f"{ln_clean}{fn_clean}{num}",
    ]
    return random.choice(formats)

def generate_dob():
    """Menghasilkan tanggal lahir acak (usia 18-60 tahun)."""
    today = datetime.now()
    start_date = today - timedelta(days=60*365) # 60 tahun lalu
    end_date = today - timedelta(days=18*365)   # 18 tahun lalu
    random_date = start_date + (end_date - start_date) * random.random()
    return random_date.strftime("%d-%m-%Y")

def generate_nik(dob_str):
    """Menghasilkan NIK 16 digit."""
    # Format NIK: [6 digit kode wilayah] + [ddmmyy] + [4 digit nomor urut]
    kode_wilayah = str(random.randint(110101, 921209))
    # Ambil ddmmyy dari tanggal lahir
    dd, mm, yyyy = dob_str.split('-')
    yy = yyyy[-2:]
    
    # Nomor urut acak
    nomor_urut = str(random.randint(1, 9999)).zfill(4)
    
    return f"{kode_wilayah}{dd}{mm}{yy}{nomor_urut}"

def generate_address():
    """Menghasilkan alamat lengkap."""
    provinsi = random.choice(list(CITIES_PROVINCES.keys()))
    kota = random.choice(CITIES_PROVINCES[provinsi])
    kecamatan = f"{kota} {random.choice(DISTRICT_NAMES)}"
    jalan = f"Jl. {random.choice(STREET_NAMES)} No {random.randint(1, 200)}"
    kode_pos = str(random.randint(10000, 99999))
    return {
        "provinsi": provinsi,
        "kota": kota,
        "kecamatan": kecamatan,
        "alamat": jalan,
        "kode_pos": kode_pos,
    }

def generate_phone():
    """Menghasilkan nomor telepon Indonesia."""
    return f"628{random.randint(100000000, 999999999)}"

# --- FUNGSI UTAMA ---
def generate_all_data():
    """Menggabungkan semua generator untuk membuat satu set data."""
    names = generate_names()
    address = generate_address()
    dob = generate_dob()

    all_data = {
        "nama_depan": names["nama_depan"],
        "nama_belakang": names["nama_belakang"],
        "nama_lengkap": names["nama_lengkap"],
        "username": generate_username(names["nama_depan"], names["nama_belakang"]),
        "nik": generate_nik(dob),
        "tanggal_lahir": dob,
        "tempat_lahir": address["kota"],
        "alamat": address["alamat"],
        "kecamatan": address["kecamatan"],
        "kota": address["kota"],
        "provinsi": address["provinsi"],
        "kode_pos": address["kode_pos"],
        "telepon": generate_phone(),
    }
    return all_data
