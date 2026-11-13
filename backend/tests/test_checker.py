from spldv.checker import cek_layar, cek_pasangan, setara
from spldv.solver import ke_persamaan


def P(a, b, c):
    return ke_persamaan([a, b, c])


K = [P(1, 1, 250), P(50000, 30000, 8900000)]


def test_setara_sebanding():
    assert setara(P(5, 3, 890), P(50000, 30000, 8900000))
    assert setara(P(-1, -1, -250), P(1, 1, 250))
    assert not setara(P(1, 1, 251), P(1, 1, 250))
    assert not setara(P(0, 0, 0), P(1, 1, 250))


def test_pasangan_urutan_bebas():
    assert cek_pasangan([P(5, 3, 890), P(1, 1, 250)], K) == [True, True]


def test_pasangan_satu_salah():
    assert cek_pasangan([P(1, 1, 250), P(5, 3, 900)], K) == [True, False]


def test_pasangan_dua_kali_persamaan_sama():
    assert cek_pasangan([P(1, 1, 250), P(2, 2, 500)], K) == [True, False]


SOAL = {
    "variabel": [{"simbol": "x"}, {"simbol": "y"}],
    "model": [[1, 1, 250], [50000, 30000, 8900000]],
    "segmen": [{"t": "a", "peran": "data"}, {"t": " "}, {"t": "b?", "peran": "tanya"}],
}


def test_persamaan2():
    layar = {"input": "persamaan2", "kunci": {}, "umpan_salah": {"kunci2": "Cek uang."}}
    assert cek_layar(SOAL, layar, {"persamaan": [["1", "1", "250"], ["5", "3", "890"]]}).benar
    salah = cek_layar(SOAL, layar, {"persamaan": [["1", "1", "250"], ["5", "3", "900"]]})
    assert not salah.benar and "Persamaan (2)" in salah.pesan and "Cek uang." in salah.pesan
    assert not cek_layar(SOAL, layar, {"persamaan": [["", "1", "250"], ["5", "3", "890"]]}).benar


def test_pengali_berbagai_pengali_diterima():
    layar = {"input": "pengali", "kunci": {"hilangkan": "y"}}
    pers = [["1", "1", "250"], ["5", "3", "890"]]
    assert cek_layar(SOAL, layar, {"m1": "3", "m2": "1", "operasi": "kurang", "persamaan": pers}).benar
    assert cek_layar(SOAL, layar, {"m1": "6", "m2": "2", "operasi": "kurang", "persamaan": pers}).benar
    salah_op = cek_layar(SOAL, layar, {"m1": "3", "m2": "1", "operasi": "jumlah", "persamaan": pers})
    assert not salah_op.benar and salah_op.detail == {"pengali": True, "operasi": False}
    salah_m = cek_layar(SOAL, layar, {"m1": "2", "m2": "1", "operasi": "kurang", "persamaan": pers})
    assert salah_m.detail["pengali"] is False


def test_pengali_tanpa_persamaan_siswa_memakai_model():
    layar = {"input": "pengali", "kunci": {"hilangkan": "y"}}
    assert cek_layar(SOAL, layar, {"m1": "30000", "m2": "1", "operasi": "kurang"}).benar


def test_pengali_dengan_urutan_persamaan_siswa_tertukar():
    layar = {"input": "pengali", "kunci": {"hilangkan": "y"}}
    pers = [["5", "3", "890"], ["1", "1", "250"]]
    assert cek_layar(SOAL, layar, {"m1": "1", "m2": "3", "operasi": "kurang", "persamaan": pers}).benar


def test_substitusi():
    layar = {"input": "substitusi", "kunci": {"var": "x", "nilai": 70}}
    assert cek_layar(SOAL, layar, {"konst": "70", "koef": "1", "rhs": "250"}).benar
    assert cek_layar(SOAL, layar, {"konst": "3.500.000", "koef": "30.000", "rhs": "8.900.000"}).benar
    assert not cek_layar(SOAL, layar, {"konst": "0", "koef": "1", "rhs": "180"}).benar
    assert not cek_layar(SOAL, layar, {"konst": "70", "koef": "0", "rhs": "250"}).benar


def test_angka_dan_umpan_khusus():
    layar = {"input": "angka", "kunci": {"nilai": {"y": 170}},
             "umpan_khusus": [{"jika": {"y": -30}, "pesan": "terbalik"}]}
    assert cek_layar(SOAL, layar, {"nilai": {"y": "170"}}).benar
    assert cek_layar(SOAL, layar, {"nilai": {"y": "-30"}}).pesan == "terbalik"
    assert not cek_layar(SOAL, layar, {"nilai": {"y": "abc"}}).benar


def test_pilihan():
    layar = {"input": "pilihan", "kunci": {"pilihan": "B"}, "umpan_salah": {"A": "bukan A"}}
    assert cek_layar(SOAL, layar, {"pilihan": "B"}).benar
    assert cek_layar(SOAL, layar, {"pilihan": "A"}).pesan == "bukan A"


def test_tandai():
    layar = {"input": "tandai", "kunci": {}}
    assert cek_layar(SOAL, layar, {"segmen": [0, 2]}).benar
    hasil = cek_layar(SOAL, layar, {"segmen": [0, 1]})
    assert not hasil.benar and hasil.detail["kurang"] == 1
