"""Logika progres, hasil misi, dan lencana (memakai DB, terpisah dari route)."""
from __future__ import annotations

import sqlite3
from collections import Counter

from soal_repo import BankSoal
from spldv.scoring import bintang

AREA = {
    "persamaan2": ("menyusun model matematika", "Latihan 2 dan Latihan 3"),
    "persamaan1": ("menyusun model matematika", "Latihan 3"),
    "tandai": ("menemukan informasi penting dalam soal", "Contoh 1"),
    "pengali": ("menyamakan koefisien saat eliminasi", "Latihan 1"),
    "substitusi": ("melakukan substitusi", "Latihan 1"),
    "angka": ("menghitung nilai variabel", "Contoh 1"),
    "pilihan": ("menafsirkan hasil dan memberi alasan", "Contoh 2"),
}

LENCANA = {
    "mandiri": ("Mandiri", "Menyelesaikan satu misi tanpa petunjuk"),
    "pemeriksa": ("Pemeriksa Teliti", "Memakai Cek Jawaban di 3 misi"),
    "penerjemah": ("Penerjemah Andal", "Model persamaan benar pada percobaan pertama di 3 misi"),
    "penjelas": ("Penjelas Hebat", "Menulis alasan sendiri di Misi 1 dan Misi 4"),
}


def status_layar(rows: list[sqlite3.Row]) -> dict[str, dict]:
    """Kelompokkan baris jawaban per layar menjadi status akhirnya."""
    hasil: dict[str, dict] = {}
    for r in rows:
        s = hasil.setdefault(r["layar_id"], {"percobaan": 0, "petunjuk_maks": 0, "skor": 0.0,
                                              "benar": False, "lewati": False})
        s["percobaan"] = max(s["percobaan"], r["percobaan"])
        s["petunjuk_maks"] = max(s["petunjuk_maks"], r["petunjuk_maks"])
        if r["benar"] or r["lewati"]:
            s["benar"] = bool(r["benar"])
            s["lewati"] = bool(r["lewati"])
            s["skor"] = r["skor"]
    return hasil


def hitung_hasil(db: sqlite3.Connection, bank_soal: BankSoal, main: sqlite3.Row) -> dict:
    soal = bank_soal.get(main["soal_id"])
    rows = db.execute("SELECT * FROM jawaban WHERE main_id = ? ORDER BY id", (main["id"],)).fetchall()
    status = status_layar(rows)
    pet = db.execute("SELECT COALESCE(MAX(tingkat), 0) AS m FROM petunjuk WHERE main_id = ?",
                     (main["id"],)).fetchone()["m"]

    daftar, lemah = [], Counter()
    for l in bank_soal.semua_layar(soal):
        s = status.get(l["id"])
        if s is None or not (s["benar"] or s["lewati"]):
            label = "belum"
        elif s["lewati"]:
            label = "dilihat"
        elif s["petunjuk_maks"] > 0:
            label = "petunjuk"
        else:
            label = "mandiri"
        if label != "mandiri":
            lemah[AREA.get(l["input"], ("", ""))] += 1
        daftar.append({"id": l["id"], "tahap": l["tahap"], "skor_maks": l.get("skor", 0),
                       "skor": s["skor"] if s else 0, "status": label,
                       "percobaan": s["percobaan"] if s else 0})

    skor = round(sum(d["skor"] for d in daftar), 2)
    skor_maks = bank_soal.skor_maks(soal)
    ada_lewati = any(d["status"] == "dilihat" for d in daftar)
    pet_efektif = 3 if ada_lewati else pet
    lengkap = all(d["status"] != "belum" for d in daftar)
    n_bintang = bintang(skor, skor_maks, pet_efektif) if lengkap else 0

    refleksi = None
    lemah.pop(("", ""), None)
    if lemah:
        (area, saran), _ = lemah.most_common(1)[0]
        refleksi = f"Bagian yang perlu dilatih: {area}. Coba {saran}."
    elif lengkap:
        refleksi = "Luar biasa! Semua langkah kamu kerjakan secara mandiri."

    return {
        "main_id": main["id"], "soal_id": soal["id"], "judul": soal["judul"], "mode": soal["mode"],
        "skor": skor, "skor_maks": skor_maks, "bintang": n_bintang, "lengkap": lengkap,
        "petunjuk_maks": pet_efektif, "layar": daftar, "refleksi": refleksi,
        "mandiri": sum(1 for d in daftar if d["status"] == "mandiri"), "jumlah_layar": len(daftar),
    }


def lencana(db: sqlite3.Connection, bank_soal: BankSoal, kode: str) -> list[dict]:
    misi_ids = {s["id"] for s in bank_soal.daftar("misi")}
    dapat = set()

    selesai = db.execute("SELECT soal_id, petunjuk_maks FROM main WHERE kode_siswa = ? AND selesai IS NOT NULL",
                         (kode,)).fetchall()
    if any(r["soal_id"] in misi_ids and r["petunjuk_maks"] == 0 for r in selesai):
        dapat.add("mandiri")

    cek = db.execute(
        "SELECT DISTINCT p.soal_id FROM peristiwa p JOIN sesi s ON s.id = p.sesi_id "
        "WHERE s.kode_siswa = ? AND p.tipe = 'cek_jawaban'", (kode,)).fetchall()
    if len({r["soal_id"] for r in cek} & misi_ids) >= 3:
        dapat.add("pemeriksa")

    model_layar = {(s["id"], l["id"]) for s in bank_soal.daftar("misi")
                   for l in bank_soal.semua_layar(s) if l.get("jenis") == "model"}
    benar1 = db.execute(
        "SELECT DISTINCT m.soal_id, j.layar_id FROM jawaban j JOIN main m ON m.id = j.main_id "
        "WHERE m.kode_siswa = ? AND j.benar = 1 AND j.percobaan = 1 AND j.petunjuk_maks = 0", (kode,)).fetchall()
    if len({r["soal_id"] for r in benar1 if (r["soal_id"], r["layar_id"]) in model_layar}) >= 3:
        dapat.add("penerjemah")

    teks = db.execute(
        "SELECT DISTINCT a.soal_id FROM alasan_teks a JOIN main m ON m.id = a.main_id "
        "WHERE m.kode_siswa = ? AND LENGTH(TRIM(a.teks)) > 0", (kode,)).fetchall()
    if {"M1", "M4"} <= {r["soal_id"] for r in teks}:
        dapat.add("penjelas")

    return [{"id": k, "nama": n, "syarat": d, "dapat": k in dapat} for k, (n, d) in LENCANA.items()]


def progres(db: sqlite3.Connection, bank_soal: BankSoal, kode: str, syarat_misi: str) -> dict:
    rows = db.execute(
        "SELECT soal_id, skor, bintang, id FROM main WHERE kode_siswa = ? AND selesai IS NOT NULL ORDER BY id",
        (kode,)).fetchall()
    per_soal: dict[str, list] = {}
    for r in rows:
        per_soal.setdefault(r["soal_id"], []).append(r)

    def sudah(soal_id: str) -> bool:
        return soal_id in per_soal

    hasil = {}
    for mode in ("latihan", "misi"):
        daftar = []
        sebelumnya = None
        for s in bank_soal.daftar(mode):
            if sebelumnya is None:
                terbuka = True if mode == "latihan" else sudah(syarat_misi)
            else:
                terbuka = sudah(sebelumnya)
            runs = per_soal.get(s["id"], [])
            daftar.append({
                **bank_soal.ringkas(s),
                "selesai": bool(runs),
                "terbuka": terbuka,
                "skor_pertama": runs[0]["skor"] if runs else None,
                "skor_terbaik": max((r["skor"] for r in runs), default=None),
                "bintang": max((r["bintang"] or 0 for r in runs), default=0),
                "dikerjakan": len(runs),
            })
            sebelumnya = s["id"]
        hasil[mode] = daftar
    hasil["contoh"] = [{"id": c["id"], "judul": c["judul"], "deskripsi": c.get("deskripsi", "")}
                       for c in sorted(bank_soal.contoh.values(), key=lambda c: c["urutan"])]
    hasil["lencana"] = lencana(db, bank_soal, kode)
    return hasil
