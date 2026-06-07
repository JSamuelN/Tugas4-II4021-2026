# Program Password Manager Terdistribusi dengan Shamir Secret Sharing

# Tugas4-II4021-2026

Tugas 4 II4021 Kriptografi - Semester II Tahun 2025/2026

## Deskripsi Program
Aplikasi ini adalah Password Manager berbasis Python yang mengamankan brankas kata sandi menggunakan enkripsi AES-GCM dan skema pembagian kunci Shamir's Secret Sharing (2,3). Master key dipecah menjadi tiga bagian (lokal, server, dan pemulihan), di mana minimal dua bagian diperlukan untuk membuka, menambah, atau mengubah data kata sandi.

Fitur utama meliputi:
**Shamir's Secret Sharing (2,3)**: Memecah kunci utama (*master key*) menjadi 3 bagian, yaitu untuk lokal, server, dan pemulihan, di mana diperlukan minimal 2 bagian untuk merekonstruksi kunci.
**Enkripsi (AES-GCM & PBKDF2)**: Mengamankan data brankas dengan enkripsi AES-GCM dan mengamankan kunci lokal menggunakan kata sandi utama yang diperkuat dengan metode PBKDF2
**Manajemen Brankas (CRUD)**: Memungkinkan pengguna untuk membuat brankas baru (*Create*), serta melihat (*View*), menambah (*Add*), mengubah (*Update*), dan menghapus (*Delete*) data akun atau kata sandi di dalamnya.
**Backup Mode**: Memungkinkan pengguna untuk tetap mengakses data brankas secara lokal menggunakan kunci pemulihan (*recovery share*) jika server sedang *offline*
**Pembuatan Kata Sandi Otomatis**: fitur untuk membuat kata sandi acak secara otomatis saat menambahkan data baru dengan panjang yang dapat ditentukan.
**Penyimpanan Ganda**: Menyimpan data brankas terenkripsi baik di sisi klien (*local* JSON) maupun di sisi server (SQLite *database*).

## Anggota Kelompok
1. **Jason Samuel** - 18223091

## TechStack
1. Python 3.12
2. SQLite3

## Dependensi
`pycryptodome`
```bash
   pip install pycryptodome
   ```

## Tata Cara Menjalankan Program
```bash
   git clone 
