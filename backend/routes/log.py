"""Route pencatatan peristiwa (log penelitian, lihat docs/EVALUASI.md §3)."""
import json

from flask import Blueprint, current_app, jsonify

from db import get_db
from routes.util import ambil_int, body, gagal

bp = Blueprint("log", __name__, url_prefix="/api")

TIPE = {
    "layar_buka", "layar_tutup", "periksa", "petunjuk", "lewati",
    "tempo_putar", "tempo_jeda", "tempo_lanjut", "tempo_ulang", "tempo_kembali",
    "tandai_segmen", "penerjemah", "cek_jawaban", "bantu_eliminasi", "tips_metode",
    "ringkasan_toggle", "soal_toggle", "simulasi_keranjang", "simulasi_tebak",
    "aplikasi_sembunyi", "aplikasi_tampil", "buka_terkunci",
}


def _str_atau_none(v, maks=40):
    return v[:maks] if isinstance(v, str) else None


@bp.post("/log")
def simpan_log():
    data = body()
    sesi_id = ambil_int(data, "sesi_id")
    daftar = data.get("peristiwa")
    if not isinstance(daftar, list):
        gagal("'peristiwa' harus berupa daftar.")
    if len(daftar) > current_app.config["MAX_PERISTIWA_PER_KIRIM"]:
        gagal("Terlalu banyak peristiwa dalam sekali kirim.")
    db = get_db()
    if db.execute("SELECT 1 FROM sesi WHERE id = ?", (sesi_id,)).fetchone() is None:
        gagal("Sesi tidak ditemukan.", 404)
    baris = []
    for p in daftar:
        if not isinstance(p, dict) or p.get("tipe") not in TIPE:
            continue
        main_id = p.get("main_id") if isinstance(p.get("main_id"), int) else None
        isi = p.get("data") if isinstance(p.get("data"), dict) else {}
        baris.append((sesi_id, main_id, p["tipe"], _str_atau_none(p.get("soal_id")),
                      _str_atau_none(p.get("layar_id")), json.dumps(isi, ensure_ascii=False)[:2000],
                      _str_atau_none(p.get("waktu"))))
    db.executemany(
        "INSERT INTO peristiwa (sesi_id, main_id, tipe, soal_id, layar_id, data_json, waktu_klien) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)", baris)
    db.commit()
    return jsonify(ok=True, disimpan=len(baris))
