"""Route pemeriksaan langkah, petunjuk, lewati, dan alat bantu."""
import json

from flask import Blueprint, current_app, jsonify

from db import get_db
from routes.util import ambil_int, ambil_str, bank, body, gagal
from spldv import helper
from spldv.checker import cek_layar, variabel
from spldv.parse import ParseError, parse_angka
from spldv.scoring import skor_layar
from spldv.solver import ke_persamaan

bp = Blueprint("cek", __name__, url_prefix="/api")


def _konteks(data: dict):
    """Ambil (main, soal, layar) dari body request dan validasi."""
    main_id = ambil_int(data, "main_id")
    layar_id = ambil_str(data, "layar_id", maks=10)
    db = get_db()
    main = db.execute("SELECT * FROM main WHERE id = ?", (main_id,)).fetchone()
    if main is None:
        gagal("Data pengerjaan tidak ditemukan.", 404)
    soal = bank().get(main["soal_id"])
    layar = bank().layar(soal, layar_id)
    if layar is None:
        gagal("Langkah tidak ditemukan.", 404)
    return main, soal, layar


def _sudah_selesai(main_id: int, layar_id: str) -> bool:
    row = get_db().execute(
        "SELECT 1 FROM jawaban WHERE main_id = ? AND layar_id = ? AND (benar = 1 OR lewati = 1)",
        (main_id, layar_id)).fetchone()
    return row is not None


def _petunjuk_maks(main_id: int, layar_id: str) -> int:
    return get_db().execute(
        "SELECT COALESCE(MAX(tingkat), 0) AS m FROM petunjuk WHERE main_id = ? AND layar_id = ?",
        (main_id, layar_id)).fetchone()["m"]


def _percobaan(main_id: int, layar_id: str) -> int:
    return get_db().execute(
        "SELECT COUNT(*) AS n FROM jawaban WHERE main_id = ? AND layar_id = ?",
        (main_id, layar_id)).fetchone()["n"] + 1


@bp.post("/cek-langkah")
def cek_langkah():
    data = body()
    main, soal, layar = _konteks(data)
    if main["selesai"] is not None or _sudah_selesai(main["id"], layar["id"]):
        gagal("Langkah ini sudah selesai.", 409)
    jawaban = data.get("jawaban")
    if not isinstance(jawaban, dict):
        gagal("'jawaban' harus berupa objek.")
    durasi = data.get("durasi_ms") if isinstance(data.get("durasi_ms"), int) else None

    hasil = cek_layar(soal, layar, jawaban)
    percobaan = _percobaan(main["id"], layar["id"])
    pet = _petunjuk_maks(main["id"], layar["id"])
    cfg = current_app.config
    skor = skor_layar(layar.get("skor", 0), hasil.benar, pet, percobaan,
                      cfg["PENALTI_PETUNJUK"], cfg["HITUNG_PERCOBAAN_PERTAMA"])

    db = get_db()
    db.execute(
        "INSERT INTO jawaban (main_id, layar_id, tahap, jawaban_json, benar, percobaan, petunjuk_maks, skor, durasi_ms) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (main["id"], layar["id"], layar["tahap"], json.dumps(jawaban, ensure_ascii=False)[:5000],
         int(hasil.benar), percobaan, pet, skor, durasi))
    teks = jawaban.get("teks")
    if hasil.benar and layar.get("teks_opsional") and isinstance(teks, str) and teks.strip():
        db.execute("INSERT INTO alasan_teks (main_id, soal_id, layar_id, teks) VALUES (?, ?, ?, ?)",
                   (main["id"], soal["id"], layar["id"], teks.strip()[:cfg["MAX_TEKS"]]))
    db.commit()

    respons = {"benar": hasil.benar, "pesan": hasil.pesan, "detail": hasil.detail,
               "percobaan": percobaan, "skor": skor}
    if hasil.benar:
        respons["ringkasan"] = layar.get("ringkasan")
    return jsonify(respons)


@bp.post("/petunjuk")
def petunjuk():
    data = body()
    main, soal, layar = _konteks(data)
    tingkat = ambil_int(data, "tingkat")
    sekarang = _petunjuk_maks(main["id"], layar["id"])
    if tingkat < 1 or tingkat > 3:
        gagal("Tingkat petunjuk harus 1, 2, atau 3.")
    if tingkat > sekarang + 1:
        gagal("Buka petunjuk secara berurutan.")
    if tingkat > sekarang and not _sudah_selesai(main["id"], layar["id"]):
        db = get_db()
        db.execute("INSERT INTO petunjuk (main_id, layar_id, tingkat) VALUES (?, ?, ?)",
                   (main["id"], layar["id"], tingkat))
        db.commit()
    return jsonify(tingkat=tingkat, teks=layar["petunjuk"][tingkat - 1], ada_lagi=tingkat < 3)


def _jawaban_tampil(soal: dict, layar: dict):
    """Persamaan kunci untuk layar model, agar alat bantu tetap bisa dipakai setelah dilewati."""
    if layar["input"] == "persamaan2":
        return {"persamaan": [[str(v) for v in e] for e in layar["kunci"].get("persamaan", soal["model"])]}
    if layar["input"] == "persamaan1":
        return {"persamaan": [[str(v) for v in layar["kunci"]["persamaan"]]]}
    return None


@bp.post("/lewati")
def lewati():
    data = body()
    main, soal, layar = _konteks(data)
    if main["selesai"] is not None or _sudah_selesai(main["id"], layar["id"]):
        gagal("Langkah ini sudah selesai.", 409)
    db = get_db()
    db.execute(
        "INSERT INTO jawaban (main_id, layar_id, tahap, jawaban_json, benar, lewati, percobaan, petunjuk_maks, skor) "
        "VALUES (?, ?, ?, NULL, 0, 1, ?, ?, 0)",
        (main["id"], layar["id"], layar["tahap"], _percobaan(main["id"], layar["id"]),
         _petunjuk_maks(main["id"], layar["id"])))
    db.commit()
    return jsonify(ringkasan=layar.get("ringkasan"), jawaban=_jawaban_tampil(soal, layar),
                   pesan="Jawaban langkah ini ditampilkan. Pelajari, lalu lanjutkan ke langkah berikutnya.")


# ---------- alat bantu ----------

def _alat_input(data: dict):
    soal_id = data.get("soal_id")
    soal = bank().get(soal_id) if isinstance(soal_id, str) else None
    var = variabel(soal) if soal else ("x", "y")
    try:
        persamaan = [ke_persamaan(e) for e in data.get("persamaan") or []]
    except (ParseError, ValueError):
        gagal("Persamaan belum lengkap atau formatnya salah.")
    if len(persamaan) != 2:
        gagal("Susun dulu dua persamaan (model matematika) sebelum memakai alat ini.")
    return var, persamaan


@bp.post("/alat/cek-jawaban")
def alat_cek_jawaban():
    data = body()
    var, persamaan = _alat_input(data)
    nilai = data.get("nilai") or {}
    try:
        v1, v2 = parse_angka(nilai.get(var[0], "")), parse_angka(nilai.get(var[1], ""))
    except ParseError:
        gagal(f"Isi nilai {var[0]} dan {var[1]} dengan angka.")
    return jsonify(helper.cek_jawaban(persamaan, v1, v2, var))


@bp.post("/alat/bantu-eliminasi")
def alat_bantu_eliminasi():
    data = body()
    var, persamaan = _alat_input(data)
    hilangkan = data.get("hilangkan")
    if hilangkan not in var:
        gagal(f"Pilih variabel yang akan dihilangkan: {var[0]} atau {var[1]}.")
    return jsonify(helper.bantu_eliminasi(persamaan[0], persamaan[1], var.index(hilangkan), var))


@bp.post("/alat/tips-metode")
def alat_tips_metode():
    data = body()
    var, persamaan = _alat_input(data)
    return jsonify(helper.tips_metode(persamaan[0], persamaan[1], var))
