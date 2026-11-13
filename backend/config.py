"""Konfigurasi aplikasi. Nilai sensitif dibaca dari variabel lingkungan."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent


class Config:
    DB_PATH = os.environ.get("DB_PATH", str(BASE_DIR / "app.db"))
    SOAL_DIR = BASE_DIR / "data" / "soal"
    CONTOH_DIR = BASE_DIR / "data" / "contoh"
    FRONTEND_DIR = ROOT_DIR / "frontend"

    # PIN halaman guru. WAJIB diganti saat uji coba: set GURU_PIN=xxxx
    GURU_PIN = os.environ.get("GURU_PIN", "1234")

    # Aturan penilaian (lihat docs/GAME.md §4.1).
    # Proporsi skor layar yang hilang berdasarkan tingkat petunjuk tertinggi yang dibuka.
    PENALTI_PETUNJUK = {0: 0.0, 1: 0.0, 2: 0.0, 3: 1.0}
    # True = skor hanya diberikan jika benar pada percobaan pertama.
    HITUNG_PERCOBAAN_PERTAMA = False
    # Mode Misi terbuka setelah latihan ini selesai.
    SYARAT_MISI = "L2"

    MAX_TEKS = 1000
    MAX_PERISTIWA_PER_KIRIM = 100
