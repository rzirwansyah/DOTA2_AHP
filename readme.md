Tentu, mohon maaf atas kendala tersebut. Berikut adalah isi lengkap dari file `README.md` yang bisa Anda salin langsung:

-----

# Dota 2 Hero Recommendation API (AHP)

Ini adalah sebuah REST API yang dibangun menggunakan Python dan FastAPI untuk memberikan rekomendasi hero Dota 2 yang dipersonalisasi. Sistem ini menggunakan metode *Analytic Hierarchy Process* (AHP) untuk menghitung dan mengurutkan hero alternatif berdasarkan preferensi dan penilaian yang diberikan oleh pengguna.

## Fitur Utama

  - **Otentikasi Pengguna**: Sistem aman dengan otentikasi berbasis token JWT (Login).
  - **Manajemen Pertandingan**: Pengguna dapat merekam detail pertandingan, termasuk tim kawan dan lawan.
  - **Referensi Data**: Menyediakan endpoint untuk mendapatkan daftar semua hero dan struktur model kriteria AHP.
  - **Input Preferensi Dinamis**: Pengguna dapat mengurutkan prioritas kriteria dan sub-kriteria untuk setiap pertandingan.
  - **Penilaian Alternatif**: Pengguna memberikan skor untuk 5 hero alternatif terhadap semua sub-kriteria.
  - **Perhitungan AHP**: Secara otomatis menghitung *pairwise comparison*, bobot lokal dan global, serta melakukan uji konsistensi.
  - **Rekomendasi Terpersonalisasi**: Menghasilkan urutan hero yang direkomendasikan berdasarkan skor akhir AHP.
  - **Riwayat Pertandingan**: Merekam hasil pertandingan dan hero yang digunakan untuk referensi di masa depan.

## Teknologi yang Digunakan

  - **Backend**: Python 3.9+
  - **Framework**: FastAPI
  - **Database**: PostgreSQL
  - **ORM**: SQLAlchemy
  - **Validasi Data**: Pydantic
  - **Perhitungan Numerik**: NumPy
  - **Server**: Uvicorn (ASGI)
  - **Keamanan**: Passlib (hashing), Python-JOSE (JWT)

-----

## Instalasi dan Setup

Ikuti langkah-langkah berikut untuk menjalankan proyek ini di lingkungan lokal Anda.

### 1\. Prasyarat

  - Python 3.9 atau yang lebih baru
  - PostgreSQL server yang sedang berjalan
  - Git

### 2\. Clone Repositori

```bash
git clone <URL_REPOSITORI_ANDA>
cd dota_ahp_api
```

### 3\. Buat dan Aktifkan Virtual Environment

Sangat direkomendasikan untuk menggunakan *virtual environment* untuk mengisolasi dependensi proyek.

**Windows:**

```bash
python -m venv venv
.\venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4\. Install Dependensi

Install semua library yang dibutuhkan menggunakan `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 5\. Konfigurasi Environment

Buat file `.env` di direktori root proyek. Salin konten dari `.env.example` (jika ada) atau gunakan template di bawah ini.

```env
# Ganti dengan kredensial database PostgreSQL Anda
DATABASE_URL="postgresql://user:password@host:port/database_name"

# Ganti dengan kunci rahasia yang kuat dan acak
SECRET_KEY="<GANTI_DENGAN_KUNCI_RAHASIA_YANG_SANGAT_KUAT>"

# Algoritma dan waktu expired token (dalam menit)
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440 # 24 jam
```

**Penting**: Pastikan database yang Anda tuju di `DATABASE_URL` sudah dibuat di PostgreSQL dan semua tabel dari proyek sudah ada.

### 6\. Jalankan Aplikasi

Gunakan Uvicorn untuk menjalankan server FastAPI.

```bash
uvicorn app.main:app --reload
```

Aplikasi sekarang berjalan dan dapat diakses di `http://127.0.0.1:8000`.

-----

## Penggunaan API

### Dokumentasi Interaktif

Setelah server berjalan, buka browser Anda dan akses salah satu URL berikut untuk melihat dokumentasi API interaktif:

  - **Swagger UI**: `http://127.0.0.1:8000/docs`
  - **ReDoc**: `http://127.0.0.1:8000/redoc`

Melalui antarmuka ini, Anda dapat melihat semua endpoint yang tersedia, detail request dan response, serta menguji API secara langsung.

### Alur Kerja Umum

1.  **Login**: Gunakan endpoint `POST /api/v1/authentication` dengan `username` dan `password` untuk mendapatkan `access_token`.
2.  **Authorize**: Klik tombol "Authorize" di Swagger UI dan masukkan token Anda dengan format `Bearer <access_token>`.
3.  **Buat Pertandingan**: Gunakan `POST /api/v1/matches` untuk merekam detail pertandingan. Simpan `matchId` yang didapat.
4.  **Kirim Preferensi**: Gunakan `POST /api/v1/recommendations/preferences` untuk mengirim urutan prioritas kriteria.
5.  **Kirim Alternatif**: Gunakan `POST /api/v1/recommendations/alternatives` untuk mengirim penilaian 5 hero.
6.  **Dapatkan Rekomendasi**: Gunakan `GET /api/v1/recommendations/{match_id}` untuk melihat hasil akhir.
7.  **Kirim Hasil**: Setelah bermain, gunakan `POST /result` untuk menyimpan hasil pertandingan.
8.  **Lihat Riwayat**: Gunakan `GET /history` untuk melihat semua riwayat pertandingan Anda.