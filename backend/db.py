"""Koneksi SQLite dan skema tabel (lihat docs/ARSITEKTUR.md §5)."""
import sqlite3

from flask import Flask, current_app, g

SKEMA = """
CREATE TABLE IF NOT EXISTS siswa (
  kode TEXT PRIMARY KEY,
  kelas TEXT,
  dibuat TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS sesi (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  kode_siswa TEXT NOT NULL REFERENCES siswa(kode),
  perangkat TEXT,
  mulai TEXT DEFAULT CURRENT_TIMESTAMP
);
-- Satu kali siswa mengerjakan satu soal (misi/latihan).
CREATE TABLE IF NOT EXISTS main (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sesi_id INTEGER NOT NULL REFERENCES sesi(id),
  kode_siswa TEXT NOT NULL,
  soal_id TEXT NOT NULL,
  mulai TEXT DEFAULT CURRENT_TIMESTAMP,
  selesai TEXT,
  skor REAL,
  skor_maks REAL,
  bintang INTEGER,
  petunjuk_maks INTEGER
);
CREATE TABLE IF NOT EXISTS jawaban (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  main_id INTEGER NOT NULL REFERENCES main(id),
  layar_id TEXT NOT NULL,
  tahap INTEGER,
  jawaban_json TEXT,
  benar INTEGER NOT NULL DEFAULT 0,
  lewati INTEGER NOT NULL DEFAULT 0,
  percobaan INTEGER NOT NULL,
  petunjuk_maks INTEGER NOT NULL DEFAULT 0,
  skor REAL NOT NULL DEFAULT 0,
  durasi_ms INTEGER,
  waktu TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS petunjuk (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  main_id INTEGER NOT NULL REFERENCES main(id),
  layar_id TEXT NOT NULL,
  tingkat INTEGER NOT NULL,
  waktu TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS peristiwa (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sesi_id INTEGER NOT NULL REFERENCES sesi(id),
  main_id INTEGER,
  tipe TEXT NOT NULL,
  soal_id TEXT,
  layar_id TEXT,
  data_json TEXT,
  waktu_klien TEXT,
  waktu TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS alasan_teks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  main_id INTEGER NOT NULL REFERENCES main(id),
  soal_id TEXT,
  layar_id TEXT,
  teks TEXT,
  skor_guru REAL,
  waktu TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_jawaban_main ON jawaban(main_id, layar_id);
CREATE INDEX IF NOT EXISTS idx_petunjuk_main ON petunjuk(main_id, layar_id);
CREATE INDEX IF NOT EXISTS idx_main_siswa ON main(kode_siswa, soal_id);
CREATE INDEX IF NOT EXISTS idx_peristiwa_sesi ON peristiwa(sesi_id);
"""


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DB_PATH"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exc=None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app: Flask) -> None:
    app.teardown_appcontext(close_db)
    with app.app_context():
        db = get_db()
        db.executescript(SKEMA)
        db.commit()
