"""Penyelesaian SPLDV secara eksak.

Persamaan direpresentasikan sebagai tuple (a, b, c) yang berarti a·v1 + b·v2 = c.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Sequence

from .parse import parse_angka

Persamaan = tuple[Fraction, Fraction, Fraction]


def ke_persamaan(data: Sequence) -> Persamaan:
    """Ubah list [a, b, c] (angka atau teks) menjadi tuple Fraction."""
    if not isinstance(data, (list, tuple)) or len(data) != 3:
        raise ValueError("persamaan harus berisi tepat 3 bilangan [a, b, c]")
    a, b, c = (parse_angka(v) for v in data)
    return (a, b, c)


def determinan(e1: Persamaan, e2: Persamaan) -> Fraction:
    return e1[0] * e2[1] - e2[0] * e1[1]


def solve(e1: Persamaan, e2: Persamaan) -> tuple[Fraction, Fraction] | None:
    """Kembalikan (v1, v2) atau None jika tidak punya solusi tunggal (Cramer)."""
    a1, b1, c1 = e1
    a2, b2, c2 = e2
    d = a1 * b2 - a2 * b1
    if d == 0:
        return None
    v1 = (c1 * b2 - c2 * b1) / d
    v2 = (a1 * c2 - a2 * c1) / d
    return v1, v2


def evaluasi(e: Persamaan, v1: Fraction, v2: Fraction) -> tuple[Fraction, Fraction]:
    """Kembalikan (ruas_kiri, ruas_kanan) setelah nilai disubstitusikan."""
    return e[0] * v1 + e[1] * v2, e[2]
