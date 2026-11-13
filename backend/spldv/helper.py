"""Alat bantu belajar: Penyelaras Koefisien, Tips Metode, Cek Jawaban."""
from __future__ import annotations

from fractions import Fraction
from math import gcd

from .parse import format_angka
from .solver import Persamaan, evaluasi


def _kpk(a: int, b: int) -> int:
    return a * b // gcd(a, b)


def teks_persamaan(e: Persamaan, var: tuple[str, str]) -> str:
    """(2, -1, 30) -> '2x − y = 30'."""
    kiri = ""
    for k, v in zip(e[:2], var):
        if k == 0:
            continue
        angka = "" if abs(k) == 1 else format_angka(abs(k))
        if not kiri:
            kiri = ("−" if k < 0 else "") + angka + v
        else:
            kiri += (" − " if k < 0 else " + ") + angka + v
    return f"{kiri or '0'} = {format_angka(e[2])}"


def operasi_tepat(k1: Fraction, k2: Fraction) -> str:
    """Setelah koefisien disamakan: tanda sama -> kurang, tanda beda -> jumlah."""
    return "kurang" if (k1 > 0) == (k2 > 0) else "jumlah"


def bantu_eliminasi(e1: Persamaan, e2: Persamaan, idx: int, var: tuple[str, str]) -> dict:
    """Saran pengali (berbasis KPK) dan operasi untuk menghilangkan variabel ke-idx."""
    nama = var[idx]
    k1, k2 = e1[idx], e2[idx]
    if k1 == 0 or k2 == 0:
        return {
            "bisa": False,
            "alasan": f"Variabel {nama} sudah tidak ada di salah satu persamaan. "
                      f"Langsung hitung variabel lainnya.",
        }
    if k1.denominator == 1 and k2.denominator == 1:
        a, b = abs(k1.numerator), abs(k2.numerator)
        kpk = _kpk(a, b)
        m1, m2 = Fraction(kpk, a), Fraction(kpk, b)
    else:
        kpk = None
        m1, m2 = abs(k2), abs(k1)
    operasi = operasi_tepat(k1, k2)
    b1 = tuple(m1 * v for v in e1)
    b2 = tuple(m2 * v for v in e2)
    if operasi == "kurang":
        hasil = tuple(p - q for p, q in zip(b1, b2))
    else:
        hasil = tuple(p + q for p, q in zip(b1, b2))
    sama = (k1 > 0) == (k2 > 0)
    alasan = (
        f"Koefisien {nama}: {format_angka(k1)} dan {format_angka(k2)}. "
        + (f"KPK dari {format_angka(abs(k1))} dan {format_angka(abs(k2))} adalah {format_angka(kpk)}. "
           if kpk is not None else "")
        + f"Kalikan persamaan (1) dengan {format_angka(m1)} dan persamaan (2) dengan {format_angka(m2)}. "
        + ("Tandanya sama, jadi kedua persamaan dikurangkan."
           if sama else "Tandanya berbeda, jadi kedua persamaan dijumlahkan.")
    )
    return {
        "bisa": True,
        "hilangkan": nama,
        "kpk": format_angka(kpk) if kpk is not None else None,
        "pengali": [format_angka(m1), format_angka(m2)],
        "operasi": operasi,
        "aturan": "Tanda sama → kurangkan. Tanda beda → jumlahkan.",
        "langkah": [
            f"(1) × {format_angka(m1)}:  {teks_persamaan(b1, var)}",
            f"(2) × {format_angka(m2)}:  {teks_persamaan(b2, var)}",
            f"{'Dikurangkan' if operasi == 'kurang' else 'Dijumlahkan'}:  {teks_persamaan(hasil, var)}",
        ],
        "alasan": alasan,
    }


def cek_pengali(e1: Persamaan, e2: Persamaan, idx: int,
                m1: Fraction, m2: Fraction, operasi: str) -> tuple[bool, bool]:
    """Periksa jawaban siswa pada layar pengali. Kembalikan (pengali_ok, operasi_ok).

    Pengali apa pun diterima selama koefisien variabel ke-idx menjadi sama besar
    (mis. ×3 dan ×1, atau ×6 dan ×2).
    """
    if m1 == 0 or m2 == 0:
        return False, False
    a, b = m1 * e1[idx], m2 * e2[idx]
    if a == b and a != 0:
        return True, operasi == "kurang"
    if a == -b and a != 0:
        return True, operasi == "jumlah"
    return False, operasi == operasi_tepat(e1[idx], e2[idx])


def tips_metode(e1: Persamaan, e2: Persamaan, var: tuple[str, str]) -> dict:
    """Saran metode berdasarkan bentuk koefisien."""
    for i in (0, 1):
        k1, k2 = e1[i], e2[i]
        if k1 != 0 and (k1 == k2 or k1 == -k2):
            jenis = "sama" if k1 == k2 else "berlawanan"
            return {
                "metode": "eliminasi",
                "alasan": f"Koefisien {var[i]} di kedua persamaan {jenis} "
                          f"({format_angka(k1)} dan {format_angka(k2)}). "
                          f"Eliminasi {var[i]} bisa langsung tanpa mengalikan.",
            }
    for no, e in ((1, e1), (2, e2)):
        for i in (0, 1):
            if abs(e[i]) == 1:
                lain = var[1 - i]
                return {
                    "metode": "substitusi",
                    "alasan": f"Di persamaan ({no}) koefisien {var[i]} adalah {format_angka(e[i])}. "
                              f"Nyatakan {var[i]} dalam {lain}, lalu substitusikan ke persamaan lainnya. "
                              f"Eliminasi juga tetap bisa dipakai.",
                }
    return {
        "metode": "gabungan",
        "alasan": "Tidak ada koefisien yang sama atau bernilai 1. Pakai metode gabungan: "
                  "eliminasi satu variabel (samakan koefisiennya dengan KPK), "
                  "lalu substitusikan hasilnya.",
    }


def cek_jawaban(persamaan: list[Persamaan], v1: Fraction, v2: Fraction,
                var: tuple[str, str]) -> dict:
    """Substitusi balik nilai ke setiap persamaan."""
    baris = []
    for no, e in enumerate(persamaan, start=1):
        kiri, kanan = evaluasi(e, v1, v2)
        substitusi = ""
        for k, v in zip(e[:2], (v1, v2)):
            if k == 0:
                continue
            suku = f"{format_angka(abs(k))}×({format_angka(v)})"
            if not substitusi:
                substitusi = ("−" if k < 0 else "") + suku
            else:
                substitusi += (" − " if k < 0 else " + ") + suku
        baris.append({
            "no": no,
            "persamaan": teks_persamaan(e, var),
            "substitusi": substitusi or "0",
            "kiri": format_angka(kiri),
            "kanan": format_angka(kanan),
            "cocok": kiri == kanan,
        })
    semua = all(b["cocok"] for b in baris)
    return {
        "baris": baris,
        "semua_cocok": semua,
        "pesan": ("Nilai ini memenuhi semua persamaan. Jawabanmu konsisten!" if semua
                  else "Ada persamaan yang tidak terpenuhi. Periksa lagi hitunganmu."),
    }
