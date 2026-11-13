"""Route halaman guru/peneliti: rekap dan ekspor CSV (dilindungi PIN)."""
import csv
import hmac
import io

from flask import Blueprint, Response, current_app, jsonify, request

from db import get_db
from routes.util import bank, gagal

bp = Blueprint("guru", __name__, url_prefix="/api/guru")

TABEL_EKSPOR = {
    "jawaban": "SELECT j.*, m.kode_siswa, m.soal_id FROM jawaban j JOIN main m ON m.id = j.main_id ORDER BY j.id",
    "peristiwa": "SELECT p.*, s.kode_siswa FROM peristiwa p JOIN sesi s ON s.id = p.sesi_id ORDER BY p.id",
    "alasan": "SELECT a.*, m.kode_siswa FROM alasan_teks a JOIN main m ON m.id = a.main_id ORDER BY a.id",
    "main": "SELECT * FROM main ORDER BY id",
}


@bp.before_request
def cek_pin():
    pin = request.headers.get("X-PIN", "")
    if not hmac.compare_digest(pin.encode(), str(current_app.config["GURU_PIN"]).encode()):
        gagal("PIN salah.", 401)


def _rekap() -> list[dict]:
    db = get_db()
    misi = [s["id"] for s in bank().daftar("misi")]
    hasil = []
    for siswa in db.execute("SELECT * FROM siswa ORDER BY kode").fetchall():
        kode = siswa["kode"]
        baris = {"kode_siswa": kode, "kelas": siswa["kelas"]}
        total = 0.0
        for m in misi:
            # Skor yang dipakai adalah pengerjaan PERTAMA yang selesai (ulangan tidak menimpa).
            r = db.execute("SELECT skor FROM main WHERE kode_siswa = ? AND soal_id = ? AND selesai IS NOT NULL "
                           "ORDER BY id LIMIT 1", (kode, m)).fetchone()
            baris[f"skor_{m}"] = r["skor"] if r else None
            total += r["skor"] if r else 0
        baris["total"] = total
        for t in (1, 2, 3):
            baris[f"petunjuk_t{t}"] = db.execute(
                "SELECT COUNT(*) AS n FROM petunjuk p JOIN main m ON m.id = p.main_id "
                "WHERE m.kode_siswa = ? AND p.tingkat = ?", (kode, t)).fetchone()["n"]
        baris["pakai_cek_jawaban"] = db.execute(
            "SELECT COUNT(*) AS n FROM peristiwa p JOIN sesi s ON s.id = p.sesi_id "
            "WHERE s.kode_siswa = ? AND p.tipe = 'cek_jawaban'", (kode,)).fetchone()["n"]
        baris["tempo_ulang"] = db.execute(
            "SELECT COUNT(*) AS n FROM peristiwa p JOIN sesi s ON s.id = p.sesi_id "
            "WHERE s.kode_siswa = ? AND p.tipe = 'tempo_ulang'", (kode,)).fetchone()["n"]
        durasi = db.execute(
            "SELECT COALESCE(SUM(j.durasi_ms), 0) AS d FROM jawaban j JOIN main m ON m.id = j.main_id "
            "WHERE m.kode_siswa = ?", (kode,)).fetchone()["d"]
        baris["durasi_total_menit"] = round(durasi / 60000, 1)
        hasil.append(baris)
    return hasil


@bp.get("/rekap")
def rekap():
    return jsonify(rekap=_rekap(), misi=[bank().ringkas(s) for s in bank().daftar("misi")])


@bp.get("/ekspor.csv")
def ekspor():
    tabel = request.args.get("tabel", "rekap")
    if tabel == "rekap":
        rows = _rekap()
        kolom = list(rows[0].keys()) if rows else ["kode_siswa"]
    elif tabel in TABEL_EKSPOR:
        cur = get_db().execute(TABEL_EKSPOR[tabel])
        kolom = [d[0] for d in cur.description]
        rows = [dict(r) for r in cur.fetchall()]
    else:
        gagal("Tabel tidak dikenal.")
    buf = io.StringIO()
    buf.write("﻿")  # BOM agar Excel membaca UTF-8 dengan benar
    w = csv.DictWriter(buf, fieldnames=kolom, delimiter=";")
    w.writeheader()
    w.writerows(rows)
    return Response(buf.getvalue(), mimetype="text/csv; charset=utf-8",
                    headers={"Content-Disposition": f"attachment; filename={tabel}.csv"})
