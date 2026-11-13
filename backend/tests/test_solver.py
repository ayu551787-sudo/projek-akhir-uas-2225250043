from fractions import Fraction

from spldv.solver import evaluasi, ke_persamaan, solve


def P(a, b, c):
    return ke_persamaan([a, b, c])


def test_solve_soal_pemicu_1():
    assert solve(P(-1, 1, 70), P(2, -1, 30)) == (100, 170)


def test_solve_buku_pensil():
    assert solve(P(4, 1, 5600), P(5, 3, 8400)) == (1200, 800)


def test_solve_umur():
    assert solve(P(1, -6, -10), P(1, -2, 18)) == (32, 7)


def test_solve_hasil_pecahan_eksak():
    assert solve(P(1, 1, 1), P(1, -1, 0)) == (Fraction(1, 2), Fraction(1, 2))


def test_solve_tidak_tunggal():
    assert solve(P(1, 2, 3), P(2, 4, 6)) is None   # berimpit
    assert solve(P(1, 2, 3), P(2, 4, 7)) is None   # sejajar


def test_evaluasi():
    assert evaluasi(P(2, 3, 19000), 5000, 3000) == (19000, 19000)


def test_ke_persamaan_menerima_teks():
    assert ke_persamaan(["50.000", "30.000", "Rp8.900.000"]) == (50000, 30000, 8900000)
