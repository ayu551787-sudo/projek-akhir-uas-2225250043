"""Memastikan setiap kunci jawaban di bank soal benar menurut solver."""
import re

import pytest

from spldv.checker import cek_layar, setara, variabel
from spldv.helper import bantu_eliminasi
from spldv.parse import parse_angka
from spldv.solver import ke_persamaan, solve


def semua_soal(bank_soal):
    return list(bank_soal.soal.values())


def test_ada_soal(bank_soal):
    ids = set(bank_soal.soal)
    assert {"L1", "L2", "L3", "M1", "M2", "M3", "M4"} <= ids
    assert {"C1", "C2"} <= set(bank_soal.contoh)


@pytest.fixture(params=["L1", "L2", "L3", "M1", "M2", "M3", "M4"])
def soal(request, bank_soal):
    return bank_soal.get(request.param)


def test_model_punya_solusi_tunggal(soal):
    e1, e2 = (ke_persamaan(e) for e in soal["model"])
    assert solve(e1, e2) is not None


def test_skor_misi_enam(soal, bank_soal):
    if soal["mode"] == "misi":
        assert bank_soal.skor_maks(soal) == 6


def jawaban_benar(soal, layar):
    """Bangun jawaban yang benar dari kunci, lalu pastikan checker menerimanya."""
    var = variabel(soal)
    model = [ke_persamaan(e) for e in soal["model"]]
    k = layar.get("kunci", {})
    jenis = layar["input"]
    if jenis == "pilihan":
        p = k["pilihan"]
        return {"pilihan": p[0] if isinstance(p, list) else p}
    if jenis == "angka":
        return {"nilai": {n: str(v) for n, v in k["nilai"].items()}}
    if jenis == "persamaan2":
        return {"persamaan": [[str(v) for v in e] for e in k.get("persamaan", soal["model"])]}
    if jenis == "persamaan1":
        return {"persamaan": [[str(v) for v in k["persamaan"]]]}
    if jenis == "pengali":
        h = bantu_eliminasi(model[0], model[1], var.index(k["hilangkan"]), var)
        return {"m1": h["pengali"][0], "m2": h["pengali"][1], "operasi": h["operasi"]}
    if jenis == "substitusi":
        idx = var.index(k["var"])
        e = model[0]
        return {"konst": str(e[idx] * parse_angka(k["nilai"])), "koef": str(e[1 - idx]), "rhs": str(e[2])}
    if jenis == "tandai":
        return {"segmen": [i for i, s in enumerate(soal["segmen"]) if s.get("peran")]}
    raise AssertionError(jenis)


def test_setiap_layar_bisa_dijawab_benar(soal, bank_soal):
    for layar in bank_soal.semua_layar(soal):
        hasil = cek_layar(soal, layar, jawaban_benar(soal, layar))
        assert hasil.benar, f"{soal['id']} layar {layar['id']}: {hasil.pesan}"


def test_kunci_konsisten_dengan_solusi(soal, bank_soal):
    var = variabel(soal)
    solusi = dict(zip(var, solve(*(ke_persamaan(e) for e in soal["model"]))))
    model = [ke_persamaan(e) for e in soal["model"]]
    for layar in bank_soal.semua_layar(soal):
        k = layar.get("kunci", {})
        if layar["input"] == "angka":
            for nama, nilai in k["nilai"].items():
                if nama in solusi:  # isian yang bernama variabel harus sama dengan solusi
                    assert parse_angka(nilai) == solusi[nama], f"{soal['id']} {layar['id']} {nama}"
        if layar["input"] == "substitusi":
            assert parse_angka(k["nilai"]) == solusi[k["var"]]
        if layar["input"] == "persamaan1":
            assert any(setara(ke_persamaan(k["persamaan"]), e) for e in model)


def test_template_dan_opsi_cocok_dengan_kunci(soal, bank_soal):
    for layar in bank_soal.semua_layar(soal):
        if layar["input"] == "angka":
            slot = set(re.findall(r"\[(\w+)\]", layar["template"]))
            assert slot == set(layar["kunci"]["nilai"]), f"{soal['id']} {layar['id']}"
        if layar["input"] == "pilihan":
            ids = {o["id"] for o in layar["opsi"]}
            kunci = layar["kunci"]["pilihan"]
            assert set(kunci if isinstance(kunci, list) else [kunci]) <= ids
            assert set(layar.get("umpan_salah", {})) <= ids


def semua_kunci_dict(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from semua_kunci_dict(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from semua_kunci_dict(v)


def test_publik_tidak_membocorkan_kunci(soal, bank_soal):
    nama = set(semua_kunci_dict(bank_soal.publik(soal)))
    assert not nama & {"kunci", "model", "petunjuk", "umpan_salah", "umpan_khusus", "ringkasan"}
