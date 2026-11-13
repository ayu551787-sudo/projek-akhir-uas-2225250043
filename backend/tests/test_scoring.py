from config import Config
from spldv.scoring import bintang, skor_layar

PEN = Config.PENALTI_PETUNJUK


def test_skor_layar_default():
    assert skor_layar(1, True, 0, 1, PEN) == 1
    assert skor_layar(1, True, 2, 4, PEN) == 1      # petunjuk 1–2 & banyak percobaan tidak mengurangi
    assert skor_layar(1, True, 3, 1, PEN) == 0      # petunjuk 3 = jawaban dilihat
    assert skor_layar(1, False, 0, 1, PEN) == 0
    assert skor_layar(0, True, 0, 1, PEN) == 0


def test_skor_layar_percobaan_pertama():
    assert skor_layar(1, True, 0, 2, PEN, hanya_percobaan_pertama=True) == 0


def test_bintang():
    assert bintang(6, 6, 1) == 3
    assert bintang(6, 6, 2) == 2
    assert bintang(4, 6, 0) == 2
    assert bintang(3, 6, 0) == 1
