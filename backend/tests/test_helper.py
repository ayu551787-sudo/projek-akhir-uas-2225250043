from spldv.helper import bantu_eliminasi, cek_jawaban, cek_pengali, teks_persamaan, tips_metode
from spldv.solver import ke_persamaan

V = ("x", "y")


def P(a, b, c):
    return ke_persamaan([a, b, c])


def test_teks_persamaan():
    assert teks_persamaan(P(2, -1, 30), V) == "2x − y = 30"
    assert teks_persamaan(P(-1, 1, 70), V) == "−x + y = 70"
    assert teks_persamaan(P(1, -6, -10), V) == "x − 6y = −10"
    assert teks_persamaan(P(0, 3, 9), V) == "3y = 9"


def test_bantu_eliminasi_kpk():
    h = bantu_eliminasi(P(3, 2, 130000), P(2, 5, 160000), 0, V)
    assert h["kpk"] == "6" and h["pengali"] == ["2", "3"] and h["operasi"] == "kurang"
    assert h["langkah"][2].endswith("−11y = −220.000")


def test_bantu_eliminasi_tanda_beda():
    h = bantu_eliminasi(P(-1, 1, 70), P(2, -1, 30), 1, V)
    assert h["pengali"] == ["1", "1"] and h["operasi"] == "jumlah"
    assert h["langkah"][2].endswith("x = 100")


def test_bantu_eliminasi_variabel_sudah_hilang():
    assert bantu_eliminasi(P(0, 1, 5), P(1, 1, 7), 0, V)["bisa"] is False


def test_cek_pengali():
    e1, e2 = P(1, 1, 250), P(5, 3, 890)
    assert cek_pengali(e1, e2, 1, 3, 1, "kurang") == (True, True)
    assert cek_pengali(e1, e2, 1, 3, -1, "jumlah") == (True, True)
    assert cek_pengali(e1, e2, 1, 2, 1, "kurang") == (False, True)


def test_tips_metode():
    assert tips_metode(P(-1, 1, 70), P(2, -1, 30), V)["metode"] == "eliminasi"
    assert tips_metode(P(4, 1, 5600), P(5, 3, 8400), V)["metode"] == "substitusi"
    assert tips_metode(P(3, 2, 130000), P(2, 5, 160000), V)["metode"] == "gabungan"


def test_cek_jawaban():
    h = cek_jawaban([P(2, 3, 19000), P(4, 1, 23000)], 5000, 3000, V)
    assert h["semua_cocok"]
    h2 = cek_jawaban([P(2, 3, 19000), P(4, 1, 23000)], 3000, 5000, V)
    assert not h2["semua_cocok"] and h2["baris"][0]["kiri"] == "21.000"
    h3 = cek_jawaban([P(2, -1, 30)], 100, 170, V)
    assert h3["baris"][0]["substitusi"] == "2×(100) − 1×(170)"
