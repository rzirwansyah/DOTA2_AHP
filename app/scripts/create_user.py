# File: scripts/create_user.py
#
# Cara menjalankan script ini:
# 1. Pastikan Anda berada di direktori root proyek (dota_ahp_api/).
# 2. Pastikan virtual environment Anda aktif.
# 3. Jalankan perintah: python -m scripts.create_user

import sys
import os
import getpass
from sqlalchemy.orm import Session

# Menambahkan path root proyek ke sys.path agar bisa mengimpor dari 'app'
# Ini penting agar script bisa menemukan modul-modul aplikasi Anda
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

# Impor yang diperlukan dari aplikasi Anda
from app.db.session import SessionLocal
from app.models.models import Users
from app.core.security import get_password_hash

def create_user():
    """
    Fungsi utama untuk membuat user baru secara interaktif melalui terminal.
    """
    print("--- Pendaftaran User Baru ---")
    
    db: Session = SessionLocal()
    
    try:
        # Meminta input dari admin/user
        username = input("Masukkan Username: ").strip()
        if not username:
            print("Error: Username tidak boleh kosong.")
            return

        # Cek apakah username sudah ada
        user_exists = db.query(Users).filter(Users.username == username).first()
        if user_exists:
            print(f"Error: Username '{username}' sudah terdaftar. Silakan gunakan username lain.")
            return

        name = input("Masukkan Nama Lengkap: ").strip()
        if not name:
            print("Error: Nama Lengkap tidak boleh kosong.")
            return
            
        email = input("Masukkan Email: ").strip()
        if not email:
            print("Error: Email tidak boleh kosong.")
            return

        # Cek apakah email sudah ada
        email_exists = db.query(Users).filter(Users.email == email).first()
        if email_exists:
            print(f"Error: Email '{email}' sudah terdaftar.")
            return

        # Meminta password dengan aman (tidak akan terlihat saat diketik)
        password = getpass.getpass("Masukkan Password: ")
        if not password:
            print("Error: Password tidak boleh kosong.")
            return
            
        password_confirm = getpass.getpass("Konfirmasi Password: ")
        if password != password_confirm:
            print("Error: Password dan konfirmasi password tidak cocok.")
            return

        # Membuat user baru
        hashed_password = get_password_hash(password)
        new_user = Users(
            username=username,
            name=name,
            email=email,
            password=hashed_password
        )
        
        db.add(new_user)
        db.commit()
        
        print("\n========================================")
        print(f"Sukses! User '{username}' berhasil dibuat.")
        print("========================================")

    except Exception as e:
        print(f"\nTerjadi error: {e}")
        db.rollback()
    finally:
        db.close()
        print("Koneksi database ditutup.")

if __name__ == "__main__":
    create_user()
