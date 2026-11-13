"""Route sesi siswa, soal, progres, dan pengerjaan (main)."""
import re

from flask import Blueprint, current_app, jsonify, request

import layanan
from db import get_db
from routes.util import ambil_int, ambil_str, bank, body, gagal

bp = Blueprint("siswa", __name__, url_prefix="/api")

POLA_KODE = re.compile(r"^[A-Za-z0-9_-]{1,20}$")


def _sesi(sesi_id: int):
    row = get_db().execute("SELECT * FROM sesi WHERE id = ?", (sesi_id,)).fetchone()
    if row is None:
        gagal("Sesi tidak ditemukan. Silakan masuk lagi.", 404)
    return row


def _main(main_id: int):
    row = get_db().execute("SELECT * FROM main WHERE id = ?", (main_id,)).fetchone()
    if row is None:
        gagal("Data pengerjaan tidak ditemukan.", 404)
    return row


@bp.post("/sesi")
def buat_sesi():
    data = body()
    kode = ambil_str(data, "kode_siswa", maks=20).upper()
    if not POLA_KODE.match(kode):
        gagal("Kode siswa hanya boleh berisi huruf, angka, - atau _.")
    kelas = ambil_str(data, "kelas", maks=20, wajib=False) or ""
    perangkat = data.get("perangkat") if data.get("perangkat") in ("mobile", "desktop") else None
    db = get_db()
    db.execute("INSERT INTO siswa (kode, kelas) VALUES (?, ?) "
               "ON CONFLICT(kode) DO UPDATE SET kelas = COALESCE(NULLIF(excluded.kelas, ''), siswa.kelas)",
               (kode, kelas))
    cur = db.execute("INSERT INTO sesi (kode_siswa, perangkat) VALUES (?, ?)", (kode, perangkat))
    db.commit()
    return jsonify(sesi_id=cur.lastrowid, kode_siswa=kode)


@bp.get("/progres")
def progres():
    sesi_id = request.args.get("sesi_id", type=int)
    if sesi_id is None:
        gagal("'sesi_id' wajib diisi.")
    sesi = _sesi(sesi_id)
    return jsonify(layanan.progres(get_db(), bank(), sesi["kode_siswa"], current_app.config["SYARAT_MISI"]))


@bp.get("/soal")
def daftar_soal():
    mode = request.args.get("mode")
    return jsonify([bank().ringkas(s) for s in bank().daftar(mode)])


@bp.get("/soal/<soal_id>")
def detail_soal(soal_id: str):
    soal = bank().get(soal_id)
    if soal is None:
        gagal("Soal tidak ditemukan.", 404)
    return jsonify(bank().publik(soal))


@bp.get("/contoh/<contoh_id>")
def detail_contoh(contoh_id: str):
    contoh = bank().contoh.get(contoh_id)
    if contoh is None:
        gagal("Contoh soal tidak ditemukan.", 404)
    return jsonify(contoh)


@bp.post("/main")
def mulai_main():
    data = body()
    sesi = _sesi(ambil_int(data, "sesi_id"))
    soal_id = ambil_str(data, "soal_id", maks=20)
    soal = bank().get(soal_id)
    if soal is None:
        gagal("Soal tidak ditemukan.", 404)
    db = get_db()
    cur = db.execute(
        "INSERT INTO main (sesi_id, kode_siswa, soal_id, skor_maks) VALUES (?, ?, ?, ?)",
        (sesi["id"], sesi["kode_siswa"], soal_id, bank().skor_maks(soal)))
    db.commit()
    return jsonify(main_id=cur.lastrowid, soal=bank().publik(soal))


@bp.post("/main/<int:main_id>/selesai")
def selesai_main(main_id: int):
    main = _main(main_id)
    db = get_db()
    hasil = layanan.hitung_hasil(db, bank(), main)
    if not hasil["lengkap"]:
        gagal("Masih ada langkah yang belum diselesaikan.", 409)
    if main["selesai"] is None:
        db.execute("UPDATE main SET selesai = CURRENT_TIMESTAMP, skor = ?, bintang = ?, petunjuk_maks = ? "
                   "WHERE id = ?", (hasil["skor"], hasil["bintang"], hasil["petunjuk_maks"], main_id))
        db.commit()
    return jsonify(hasil)


@bp.get("/main/<int:main_id>/hasil")
def hasil_main(main_id: int):
    return jsonify(layanan.hitung_hasil(get_db(), bank(), _main(main_id)))
