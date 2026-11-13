from fractions import Fraction

import pytest

from spldv.parse import ParseError, format_angka, parse_angka


@pytest.mark.parametrize("teks, hasil", [
    ("19000", 19000),
    ("19.000", 19000),
    ("Rp19.000", 19000),
    ("Rp 19.000", 19000),
    ("rp8.900.000", 8900000),
    ("-10", -10),
    ("−10", -10),
    ("-Rp5.000", -5000),
    ("1,5", Fraction(3, 2)),
    ("1.234,5", Fraction(24690, 20)),
    (" 70 ", 70),
    (250, 250),
])
def test_parse_valid(teks, hasil):
    assert parse_angka(teks) == hasil


@pytest.mark.parametrize("teks", ["", "abc", "19.00", "1.2.3", "Rp", "--5", "1e3", None, True])
def test_parse_tidak_valid(teks):
    with pytest.raises(ParseError):
        parse_angka(teks)


def test_format_angka():
    assert format_angka(8900000) == "8.900.000"
    assert format_angka(-10) == "−10"
    assert format_angka(0) == "0"
    assert format_angka(Fraction(1, 2)) == "1/2"
