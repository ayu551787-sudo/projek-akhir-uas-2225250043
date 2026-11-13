"""Memuat bank soal dan contoh soal dari file JSON."""
from __future__ import annotations

import copy
import json
from pathlib import Path

# Bidang yang HANYA boleh ada di server (kunci jawaban & petunjuk).
RAHASIA_SOAL = {"model"}
RAHASIA_LAYAR = {"kunci", "petunjuk", "umpan_salah", "umpan_khusus", "umpan_benar", "ringkasan"}


class BankSoal:
    def __init__(self, soal_dir: Path, contoh_dir: Path):
        self.soal: dict[str, dict] = {}
        self.contoh: dict[str, dict] = {}
        for f in sorted(Path(soal_dir).glob("*.json")):
            data = json.loads(f.read_text(encoding="utf-8"))
            self._validasi(data, f.name)
            self.soal[data["id"]] = data
        for f in sorted(Path(contoh_dir).glob("*.json")):
            data = json.loads(f.read_text(encoding="utf-8"))
            self.contoh[data["id"]] = data

    @staticmethod
    def _validasi(soal: dict, nama: str) -> None:
        for kunci in ("id", "mode", "judul", "variabel", "model", "tahap", "urutan"):
            if kunci not in soal:
                raise ValueError(f"{nama}: bidang '{kunci}' tidak ada")
        ids = [l["id"] for t in soal["tahap"] for l in t["layar"]]
        if len(ids) != len(set(ids)):
            raise ValueError(f"{nama}: id layar ganda")
        for t in soal["tahap"]:
            for l in t["layar"]:
                if len(l.get("petunjuk", [])) != 3:
                    raise ValueError(f"{nama} layar {l['id']}: harus ada tepat 3 petunjuk")

    # ----- akses -----
    def daftar(self, mode: str | None = None) -> list[dict]:
        hasil = [s for s in self.soal.values() if mode is None or s["mode"] == mode]
        return sorted(hasil, key=lambda s: (s["mode"], s["urutan"]))

    def get(self, soal_id: str) -> dict | None:
        return self.soal.get(soal_id)

    @staticmethod
    def semua_layar(soal: dict) -> list[dict]:
        hasil = []
        for t in soal["tahap"]:
            for l in t["layar"]:
                hasil.append({**l, "tahap": t["no"]})
        return hasil

    def layar(self, soal: dict, layar_id: str) -> dict | None:
        for l in self.semua_layar(soal):
            if l["id"] == layar_id:
                return l
        return None

    @staticmethod
    def skor_maks(soal: dict) -> float:
        return float(sum(l.get("skor", 0) for t in soal["tahap"] for l in t["layar"]))

    @staticmethod
    def publik(soal: dict) -> dict:
        """Salinan soal tanpa kunci jawaban, untuk dikirim ke browser."""
        s = copy.deepcopy(soal)
        for k in RAHASIA_SOAL:
            s.pop(k, None)
        if s["mode"] == "misi":
            # Di misi siswa menandai sendiri, jadi penanda bagian penting tidak dikirim.
            for seg in s["segmen"]:
                seg.pop("peran", None)
                seg.pop("var", None)
        for t in s["tahap"]:
            for l in t["layar"]:
                if l["input"] == "substitusi":
                    # Variabel yang disubstitusi sudah tertulis di instruksi, jadi aman dibuka.
                    l["var_sub"] = l["kunci"]["var"]
                for k in RAHASIA_LAYAR:
                    l.pop(k, None)
        s["skor_maks"] = BankSoal.skor_maks(soal)
        return s

    @staticmethod
    def ringkas(soal: dict) -> dict:
        return {
            "id": soal["id"], "mode": soal["mode"], "judul": soal["judul"],
            "indikator": soal.get("indikator"), "urutan": soal["urutan"],
            "skor_maks": BankSoal.skor_maks(soal),
        }
