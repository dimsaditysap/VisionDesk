# VisionDesk - Pengenalan Bahasa Isyarat

Aplikasi ini menggunakan webcam Anda untuk mengenali angka bahasa isyarat (1, 2, 3).

## ⚠️ Penting: Menjalankan di Windows vs WSL

**Anda harus menjalankan aplikasi ini secara native di Windows (Command Prompt atau PowerShell).**

Aplikasi ini saat ini **tidak akan bekerja** di WSL (Windows Subsystem for Linux) tanpa konfigurasi rumit karena secara default WSL tidak dapat mengakses webcam Anda.

## Panduan Instalasi & Penggunaan

Ikuti langkah-langkah berikut untuk menjalankan aplikasi:

1.  **Buka Windows PowerShell** atau Terminal.
2.  Masuk ke folder project:
    ```powershell
    cd C:\VisionDesk
    ```
3.  Buat dan aktifkan **Virtual Environment** (Disarankan):
    ```powershell
    # Membuat virtual environment bernama 'venv'
    python -m venv venv
    
    # Mengaktifkan venv (Windows)
    .\venv\Scripts\activate
    ```
    *Jika berhasil, Anda akan melihat tanda `(venv)` di awal baris terminal Anda.*

4.  Install library yang dibutuhkan:
    ```powershell
    pip install -r requirements.txt
    ```

5.  Jalankan aplikasi:
    ```powershell
    python main.py
    ```

## Kontrol
- Tekan tombol **Esc** atau **q** pada keyboard untuk menutup aplikasi.
