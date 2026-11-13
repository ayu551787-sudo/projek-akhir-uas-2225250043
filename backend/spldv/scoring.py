"""Penilaian rubrik per layar dan bintang per misi (lihat docs/GAME.md §4)."""
from __future__ import annotations

from typing import Mapping


def skor_layar(skor_maks: float, benar: bool, petunjuk_maks: int, percobaan: int,
               penalti: Mapping[int, float], hanya_percobaan_pertama: bool = False) -> float:
    if not benar or skor_maks <= 0:
        return 0.0
    if hanya_percobaan_pertama and percobaan > 1:
        return 0.0
    potong = penalti.get(petunjuk_maks, 0.0)
    return round(max(0.0, skor_maks * (1 - potong)), 2)


def bintang(skor: float, skor_maks: float, petunjuk_maks: int) -> int:
    """★★★ skor penuh & petunjuk ≤ tingkat 1; ★★ skor ≥ 2/3 maks; ★ selesai."""
    if skor_maks <= 0:
        return 3 if petunjuk_maks <= 1 else (2 if petunjuk_maks == 2 else 1)
    if skor >= skor_maks and petunjuk_maks <= 1:
        return 3
    if skor * 3 >= skor_maks * 2:
        return 2
    return 1
