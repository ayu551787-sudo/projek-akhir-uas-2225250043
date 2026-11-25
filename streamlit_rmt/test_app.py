"""Tes aplikasi Streamlit: fungsi matematika + simulasi antarmuka dengan AppTest."""
from fractions import Fraction
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import app

APP = str(Path(__file__).with_name("app.py"))


# ---------- matematika ----------
def test_selesaikan_jenis():
    assert app.selesaikan(1, 1, 5, 2, -1, 4).jenis == "tunggal"
    h = app.selesaikan(1, 1, 1, 1, -1, 0)
    assert (h.x, h.y) == (Fraction(1, 2), Fraction(1, 2))
    assert app.selesaikan(1, 2, 4, 2, 4, 10).jenis == "sejajar"
    assert app.selesaikan(2, 3, 6, 4, 6, 12).jenis == "berimpit"
    assert app.selesaikan(0, 0, 1, 1, 1, 1).jenis == "tidak_valid"


@pytest.mark.parametrize("soal", [s for s in app.LATIHAN if s["tipe"] == "isian"], ids=lambda s: s["id"])
def test_kunci_latihan_isian_benar(soal):
    (a1, b1, c1), (a2, b2, c2) = soal["sistem"]
    h = app.selesaikan(a1, b1, c1, a2, b2, c2)
    assert (h.x, h.y) == (soal["kunci"]["x"], soal["kunci"]["y"])


def test_kunci_kuis_terverifikasi():
    # Soal hitungan kuis diverifikasi dengan solver
    assert app.selesaikan(1, 1, 8, 1, -1, 2).x == 5                       # K2
    h = app.selesaikan(2, 1, 7, 1, -1, -1); assert h.x + h.y == 5         # K3
    assert app.selesaikan(3, -1, 4, 6, -2, 10).jenis == "sejajar"         # K4
    assert app.selesaikan(2, 3, 13000, 1, 2, 8000).y == 3000              # K6
    assert app.selesaikan(2, 4, 6, 1, 2, 3).jenis == "berimpit"           # K9 (k = 2)
    assert app.selesaikan(1, 1, 250, 50000, 30000, 8900000).x == 70       # K10
    for q in app.KUIS:
        assert 0 <= q["kunci"] < len(q["opsi"]) and q["fungsi"] in app.FUNGSI_KOGNITIF


@pytest.mark.parametrize("contoh", app.CONTOH_SOAL, ids=lambda c: c["id"])
def test_contoh_soal_konsisten(contoh):
    h = app.selesaikan(*contoh["sistem"][0], *contoh["sistem"][1])
    assert h.jenis == "tunggal"
    # Kesimpulan harus memuat nilai x dan y yang benar menurut solver
    assert app.fteks(h.x) in contoh["kesimpulan"] and app.fteks(h.y) in contoh["kesimpulan"]


def test_contoh_soal_tampil_bertahap():
    at = jalankan()
    buka(at, "materi")
    at.button(key="lanjut_C1").click().run()
    assert at.session_state.tahap_C1 == 1
    at.button(key="semua_C1").click().run()
    assert not at.exception, at.exception
    assert any("Kesimpulan" in s.value for s in at.success)
    at.number_input(key="coba_C1_x").set_value(1)
    at.number_input(key="coba_C1_y").set_value(2)
    at.button(key="coba_C1_cek").click().run()
    assert any("Tepat" in s.value for s in at.success)


def test_sely_pisah_status():
    assert app.pisah_status("STATUS: BENAR\nBagus sekali.") == ("BENAR", "Bagus sekali.")
    assert app.pisah_status("**STATUS: SALAH**\n\nLangkah 2 keliru.")[0] == "SALAH"
    assert app.pisah_status("status: tidak_terbaca\nFoto buram")[0] == "TIDAK_TERBACA"
    assert app.pisah_status("Tanpa status") == (None, "Tanpa status")


def test_sely_siapkan_gambar_dan_pesan():
    import base64
    import io
    from PIL import Image

    buf = io.BytesIO()
    Image.new("RGB", (4000, 3000), "white").save(buf, format="PNG")
    jpeg = app.siapkan_gambar(buf.getvalue())
    hasil = Image.open(io.BytesIO(jpeg))
    assert hasil.format == "JPEG" and max(hasil.size) == app.SISI_GAMBAR_MAKS

    pesan = app.bangun_pesan_foto(jpeg, "Soal A", "x = 1, y = 2")
    gambar, teks = pesan[0].parts
    assert pesan[0].role == "user"
    assert gambar.inline_data.data == jpeg and gambar.inline_data.mime_type == "image/jpeg"
    assert "Soal A" in teks.text and "x = 1, y = 2" in teks.text
    assert "Tidak ada kunci" in app.bangun_pesan_foto(jpeg, "Soal B", None)[0].parts[1].text
    with pytest.raises(Exception):
        app.siapkan_gambar(b"bukan gambar")


def test_sely_riwayat_format_gemini():
    riwayat = [{"role": "user", "content": str(i)} if i % 2 == 0 else {"role": "assistant", "content": str(i)}
               for i in range(25)]
    hasil = app.riwayat_untuk_api(riwayat)
    assert hasil[0].role == "user" and len(hasil) <= app.MAKS_RIWAYAT
    assert {c.role for c in hasil} == {"user", "model"}   # Gemini menyebut giliran AI "model"
    assert hasil[0].parts[0].text == riwayat[len(riwayat) - len(hasil)]["content"]


def test_sely_soal_foto_punya_kunci():
    pilihan = app.daftar_soal_foto()
    assert pilihan["✏️ Soal lain (ketik sendiri)"] is None
    assert any(v and "x = 1.200" in v[1] for v in pilihan.values())


def test_menu_sely_tampil_tanpa_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    at = jalankan()
    buka(at, "sely")
    assert not at.exception, at.exception
    assert any("API key belum diatur" in i.value for i in at.info)
    assert at.button(key="foto_periksa").disabled   # belum ada foto


def test_periksa_isian_umpan_balik():
    soal = next(s for s in app.LATIHAN if s["id"] == "L3")
    assert app.periksa_isian(soal, (7, 3))[0]
    assert "tertukar" in app.periksa_isian(soal, (3, 7))[1]
    assert "persamaan (1)" in app.periksa_isian(soal, (6, 4))[1]   # 6+4=10 tetapi 6-4≠4


def test_format():
    assert app.ftex(Fraction(-3, 2)) == r"-\frac{3}{2}"
    assert app.fteks(8900000) == "8.900.000"
    assert app.pers_tex(2, -1, 30) == f"2{app.X} - {app.Y} = 30"


# ---------- antarmuka ----------
def jalankan():
    at = AppTest.from_file(APP, default_timeout=30)
    at.run()
    assert not at.exception, at.exception
    return at


def buka(at, kunci):
    """Buka menu lewat tombol di Beranda, seperti yang dilakukan siswa."""
    if kunci == "sely":                               # Kak Sely dibuka lewat tombol melayang
        at.button(key="fab_sely").click().run()
    else:
        if at.session_state.menu != "beranda":
            at.button(key="ke_beranda").click().run()
        at.button(key=f"buka_{kunci}").click().run()
    assert at.session_state.menu == kunci and not at.exception, at.exception


def test_beranda_dan_semua_menu_tanpa_error():
    at = jalankan()
    assert at.session_state.menu == "beranda"
    assert len(at.sidebar) == 0                      # tidak ada menu di samping
    for kunci in [*app.MENU, "sely"]:
        buka(at, kunci)
    at.button(key="ke_beranda").click().run()
    assert at.session_state.menu == "beranda"


def test_tombol_tanya_kak_sely_tersembunyi_saat_kuis():
    at = jalankan()
    assert any(b.key == "fab_sely" for b in at.button)
    buka(at, "kuis")
    at.text_input(key="input_nama").input("Siswa Uji").run()
    next(b for b in at.button if "Mulai Kuis" in b.label).click().run()
    assert at.session_state.kuis_tahap == "ujian"
    assert not any(b.key == "fab_sely" for b in at.button)   # tidak bisa bertanya ke AI saat ujian
    at.button(key="ke_beranda").click().run()
    assert any(b.key == "lanjut_kuis" for b in at.button)
    assert any("Halo, Siswa Uji" in m.value for m in at.markdown)


def test_kalkulator_hipotesis():
    at = jalankan()
    buka(at, "grafik")
    assert any("hipotesis" in i.value for i in at.info)
    at.radio(key="hipotesis").set_value("berpotongan (satu penyelesaian)").run()
    assert any("x = 3, y = 2" in s.value for s in at.success)


def test_latihan_periksa_dan_petunjuk():
    at = jalankan()
    buka(at, "latihan")
    at.selectbox(key="pilih_latihan").set_value(2).run()          # L3 substitusi
    at.number_input(key="lat_L3_x").set_value(7)
    at.number_input(key="lat_L3_y").set_value(3)
    at.button(key="periksa_L3").click().run()
    assert any("Tepat" in s.value for s in at.success)
    at.button(key="pet_L3").click().run()
    assert any("Petunjuk 1" in i.value for i in at.info)


def test_kuis_alur_lengkap():
    at = jalankan()
    buka(at, "kuis")
    mulai = lambda: next(b for b in at.button if "Mulai Kuis" in b.label)
    mulai().click().run()                                          # tanpa nama
    assert any("Isi nama" in w.value for w in at.warning)
    at.text_input(key="input_nama").input("Siswa Uji").run()
    at.toggle(key="toggle_timer").set_value(False).run()
    mulai().click().run()
    assert at.session_state.kuis_tahap == "ujian"
    for i, q in enumerate(app.KUIS):
        nilai = q["kunci"] if i < 8 else (q["kunci"] + 1) % len(q["opsi"])
        at.radio(key=f"kuis_q{i}").set_value(nilai)
    at.run()
    next(b for b in at.button if "Selesai" in b.label).click().run()
    assert not at.exception, at.exception
    assert at.session_state.kuis_hasil["skor"] == 80
    assert any(m.value == "80" for m in at.metric)
