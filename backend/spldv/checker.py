"""Pemeriksa jawaban siswa untuk setiap jenis input layar (lihat docs/BANK_SOAL.md §1)."""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any

from .helper import cek_pengali
from .parse import ParseError, format_angka, parse_angka
from .solver import Persamaan, ke_persamaan

PESAN_FORMAT = "Ada isian yang belum diisi atau formatnya tidak dikenali. Contoh yang benar: 19000 atau 19.000."


@dataclass
class HasilCek:
    benar: bool
    pesan: str
    detail: dict[str, Any] = field(default_factory=dict)


# ---------- persamaan setara ----------

def setara(e: Persamaan, k: Persamaan) -> bool:
    """True jika (a, b, c) sebanding dengan (p, q, r) dan tidak semuanya nol."""
    if all(v == 0 for v in e) or all(v == 0 for v in k):
        return False
    a, b, c = e
    p, q, r = k
    return a * q == b * p and a * r == c * p and b * r == c * q


def cek_pasangan(siswa: list[Persamaan], kunci: list[Persamaan]) -> list[bool]:
    """Status per persamaan siswa; urutan kedua persamaan bebas."""
    s1, s2 = siswa
    k1, k2 = kunci
    if (setara(s1, k1) and setara(s2, k2)) or (setara(s1, k2) and setara(s2, k1)):
        return [True, True]
    d1 = setara(s1, k1) or setara(s1, k2)
    d2 = setara(s2, k1) or setara(s2, k2)
    if d1 and d2:  # keduanya setara dengan persamaan kunci yang sama
        d2 = False
    return [d1, d2]


def kunci_belum_terpenuhi(siswa: list[Persamaan], kunci: list[Persamaan]) -> list[int]:
    """Indeks persamaan kunci yang belum ditulis siswa."""
    sisa = []
    for j, k in enumerate(kunci):
        if not any(setara(s, k) for s in siswa):
            sisa.append(j)
    return sisa


# ---------- utilitas ----------

def variabel(soal: dict) -> tuple[str, str]:
    v = soal["variabel"]
    return v[0]["simbol"], v[1]["simbol"]


def model(soal: dict) -> list[Persamaan]:
    return [ke_persamaan(e) for e in soal["model"]]


def _parse_persamaan_list(data, jumlah: int) -> list[Persamaan]:
    if not isinstance(data, list) or len(data) != jumlah:
        raise ParseError("jumlah persamaan tidak sesuai")
    return [ke_persamaan(e) for e in data]


# ---------- pemeriksa per jenis input ----------

def _cek_pilihan(soal, layar, jawaban) -> HasilCek:
    kunci = layar["kunci"]["pilihan"]
    kunci_set = set(kunci) if isinstance(kunci, list) else {kunci}
    pilihan = jawaban.get("pilihan")
    if pilihan is None:
        return HasilCek(False, "Pilih salah satu jawaban dulu.")
    if pilihan in kunci_set:
        return HasilCek(True, layar.get("umpan_benar", "Tepat!"))
    pesan = layar.get("umpan_salah", {}).get(str(pilihan),
                                              "Belum tepat. Baca lagi soalnya, lalu coba pilihan lain.")
    return HasilCek(False, pesan)


def _cek_angka(soal, layar, jawaban) -> HasilCek:
    kunci = layar["kunci"]["nilai"]
    isian = jawaban.get("nilai") or {}
    detail: dict[str, bool] = {}
    nilai: dict[str, Fraction] = {}
    format_salah = False
    for nama, benar in kunci.items():
        try:
            nilai[nama] = parse_angka(isian.get(nama, ""))
            detail[nama] = nilai[nama] == parse_angka(benar)
        except ParseError:
            detail[nama] = False
            format_salah = True
    if all(detail.values()):
        return HasilCek(True, layar.get("umpan_benar", "Tepat!"), {"isian": detail})
    if format_salah:
        return HasilCek(False, PESAN_FORMAT, {"isian": detail})
    for aturan in layar.get("umpan_khusus", []):
        jika = aturan["jika"]
        if all(nama in nilai and nilai[nama] == parse_angka(v) for nama, v in jika.items()):
            return HasilCek(False, aturan["pesan"], {"isian": detail})
    umpan = layar.get("umpan_salah", {})
    for nama, ok in detail.items():
        if not ok and nama in umpan:
            return HasilCek(False, umpan[nama], {"isian": detail})
    return HasilCek(False, umpan.get("umum", "Belum tepat. Periksa lagi isian yang ditandai merah."),
                    {"isian": detail})


def _cek_persamaan2(soal, layar, jawaban) -> HasilCek:
    kunci = [ke_persamaan(e) for e in layar["kunci"].get("persamaan", soal["model"])]
    try:
        siswa = _parse_persamaan_list(jawaban.get("persamaan"), 2)
    except (ParseError, ValueError):
        return HasilCek(False, PESAN_FORMAT, {"persamaan": [False, False]})
    detail = cek_pasangan(siswa, kunci)
    if all(detail):
        return HasilCek(True, layar.get("umpan_benar", "Tepat! Model matematikanya benar."),
                        {"persamaan": detail})
    umpan = layar.get("umpan_salah", {})
    sisa = kunci_belum_terpenuhi(siswa, kunci)
    if detail == [False, False]:
        pesan = umpan.get("umum", "Kedua persamaan belum tepat. Mulai dari satu kalimat soal yang memuat angka total.")
    else:
        salah = 1 if not detail[0] else 2
        khusus = umpan.get(f"kunci{sisa[0] + 1}") if sisa else None
        pesan = f"Persamaan ({salah}) belum tepat. " + (khusus or "Cocokkan lagi dengan kalimat soal.")
    return HasilCek(False, pesan, {"persamaan": detail})


def _cek_persamaan1(soal, layar, jawaban) -> HasilCek:
    kunci = ke_persamaan(layar["kunci"]["persamaan"])
    try:
        siswa = _parse_persamaan_list(jawaban.get("persamaan"), 1)[0]
    except (ParseError, ValueError):
        return HasilCek(False, PESAN_FORMAT, {"persamaan": [False]})
    if setara(siswa, kunci):
        return HasilCek(True, layar.get("umpan_benar", "Tepat!"), {"persamaan": [True]})
    return HasilCek(False, layar.get("umpan_salah", {}).get(
        "umum", "Belum tepat. Pindahkan semua suku bervariabel ke ruas kiri dan angka ke ruas kanan."),
        {"persamaan": [False]})


def _cek_pengali(soal, layar, jawaban) -> HasilCek:
    var = variabel(soal)
    hilangkan = layar["kunci"]["hilangkan"]
    idx = var.index(hilangkan)
    kunci = [ke_persamaan(e) for e in layar["kunci"].get("persamaan", soal["model"])]
    pasangan = kunci
    # Gunakan persamaan versi siswa (urutan & bentuknya) bila setara dengan kunci.
    try:
        milik_siswa = _parse_persamaan_list(jawaban.get("persamaan"), 2)
        if all(cek_pasangan(milik_siswa, kunci)):
            pasangan = milik_siswa
    except (ParseError, ValueError):
        pass
    try:
        m1 = parse_angka(jawaban.get("m1", ""))
        m2 = parse_angka(jawaban.get("m2", ""))
    except ParseError:
        return HasilCek(False, PESAN_FORMAT, {"pengali": False, "operasi": False})
    operasi = jawaban.get("operasi")
    if operasi not in ("jumlah", "kurang"):
        return HasilCek(False, "Pilih dulu: dijumlahkan atau dikurangkan?", {"pengali": None, "operasi": False})
    pengali_ok, operasi_ok = cek_pengali(pasangan[0], pasangan[1], idx, m1, m2, operasi)
    detail = {"pengali": pengali_ok, "operasi": operasi_ok}
    if pengali_ok and operasi_ok:
        return HasilCek(True, layar.get("umpan_benar", f"Tepat! Variabel {hilangkan} hilang."), detail)
    if not pengali_ok:
        k1, k2 = pasangan[0][idx], pasangan[1][idx]
        return HasilCek(False,
                        f"Setelah dikalikan, koefisien {hilangkan} belum sama besar "
                        f"({format_angka(m1 * k1)} dan {format_angka(m2 * k2)}). "
                        f"Cari KPK dari {format_angka(abs(k1))} dan {format_angka(abs(k2))}.", detail)
    return HasilCek(False,
                    "Pengalinya sudah tepat. Sekarang lihat tandanya: "
                    "tanda sama → kurangkan, tanda beda → jumlahkan.", detail)


def _cek_substitusi(soal, layar, jawaban) -> HasilCek:
    var = variabel(soal)
    k = layar["kunci"]
    idx = var.index(k["var"])
    lain = 1 - idx
    nilai = parse_angka(k["nilai"])
    try:
        siswa = (parse_angka(jawaban.get("konst", "")),
                 parse_angka(jawaban.get("koef", "")),
                 parse_angka(jawaban.get("rhs", "")))
    except ParseError:
        return HasilCek(False, PESAN_FORMAT)
    if siswa[1] == 0:
        return HasilCek(False, f"Koefisien {var[lain]} tidak boleh 0.")
    kunci_list = [ke_persamaan(e) for e in k.get("persamaan", soal["model"])]
    for e in kunci_list:
        target = (e[idx] * nilai, e[lain], e[2])
        if setara(siswa, target):
            return HasilCek(True, layar.get("umpan_benar", "Tepat! Substitusinya benar."))
    return HasilCek(False, layar.get("umpan_salah", {}).get(
        "umum",
        f"Belum tepat. Pilih salah satu persamaan, lalu ganti {k['var']} dengan {format_angka(nilai)}. "
        f"Kalikan koefisien {k['var']} dengan {format_angka(nilai)} untuk mengisi kotak pertama."))


def _cek_tandai(soal, layar, jawaban) -> HasilCek:
    penting = {i for i, s in enumerate(soal["segmen"]) if s.get("peran")}
    dipilih = set(jawaban.get("segmen") or [])
    kurang = penting - dipilih
    if not kurang:
        return HasilCek(True, layar.get("umpan_benar", "Tepat! Semua informasi penting sudah ditandai."),
                        {"kurang": 0})
    return HasilCek(False, f"Masih ada {len(kurang)} informasi penting yang belum ditandai. "
                           f"Cari angka-angka dan kalimat yang ditanyakan.", {"kurang": len(kurang)})


PEMERIKSA = {
    "pilihan": _cek_pilihan,
    "angka": _cek_angka,
    "persamaan2": _cek_persamaan2,
    "persamaan1": _cek_persamaan1,
    "pengali": _cek_pengali,
    "substitusi": _cek_substitusi,
    "tandai": _cek_tandai,
}


def cek_layar(soal: dict, layar: dict, jawaban: dict) -> HasilCek:
    if not isinstance(jawaban, dict):
        return HasilCek(False, PESAN_FORMAT)
    fungsi = PEMERIKSA.get(layar["input"])
    if fungsi is None:
        raise ValueError(f"jenis input tidak dikenal: {layar['input']}")
    return fungsi(soal, layar, jawaban)
