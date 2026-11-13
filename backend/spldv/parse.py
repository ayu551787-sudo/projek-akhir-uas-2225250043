"""Parsing angka dalam format Indonesia.

Titik adalah pemisah ribuan ("19.000" = 19000) dan koma adalah pemisah desimal ("1,5" = 3/2).
"""
from __future__ import annotations

import re
from fractions import Fraction

_BULAT = re.compile(r"^\d+$")
_RIBUAN = re.compile(r"^\d{1,3}(\.\d{3})+$")
_DESIMAL = re.compile(r"^\d+,\d+$")
_RIBUAN_DESIMAL = re.compile(r"^\d{1,3}(\.\d{3})+,\d+$")


class ParseError(ValueError):
    """Teks tidak dapat dibaca sebagai angka."""


def parse_angka(nilai) -> Fraction:
    """Ubah input siswa (str/int/Fraction) menjadi Fraction secara eksak."""
    if isinstance(nilai, bool):
        raise ParseError("bukan angka")
    if isinstance(nilai, Fraction):
        return nilai
    if isinstance(nilai, int):
        return Fraction(nilai)
    if isinstance(nilai, float):
        return Fraction(str(nilai))
    if not isinstance(nilai, str):
        raise ParseError("bukan angka")

    s = nilai.strip().replace("−", "-").replace(" ", "").replace(" ", "")
    if s.count("-") > 1:
        raise ParseError(f"format angka tidak dikenali: {nilai!r}")
    negatif = False
    # Boleh: "-Rp5.000", "Rp-5.000", "-5.000"
    if s.startswith("-"):
        negatif, s = True, s[1:]
    if s[:2].lower() == "rp":
        s = s[2:]
    if s.startswith("-"):
        negatif, s = True, s[1:]

    if _BULAT.match(s):
        hasil = Fraction(int(s))
    elif _RIBUAN.match(s):
        hasil = Fraction(int(s.replace(".", "")))
    elif _DESIMAL.match(s):
        hasil = Fraction(s.replace(",", "."))
    elif _RIBUAN_DESIMAL.match(s):
        hasil = Fraction(s.replace(".", "").replace(",", "."))
    else:
        raise ParseError(f"format angka tidak dikenali: {nilai!r}")
    return -hasil if negatif else hasil


def format_angka(nilai: Fraction | int) -> str:
    """Format angka bulat dengan pemisah ribuan titik: 8900000 -> '8.900.000'."""
    f = Fraction(nilai)
    if f.denominator != 1:
        return f"{f.numerator}/{f.denominator}"
    n = f.numerator
    teks = f"{abs(n):,}".replace(",", ".")
    return f"−{teks}" if n < 0 else teks
