def masuk(client, kode="S01"):
    r = client.post("/api/sesi", json={"kode_siswa": kode, "kelas": "IX"})
    assert r.status_code == 200
    return r.get_json()["sesi_id"]


def mulai(client, sesi_id, soal_id):
    r = client.post("/api/main", json={"sesi_id": sesi_id, "soal_id": soal_id})
    assert r.status_code == 200
    return r.get_json()["main_id"]


def cek(client, main_id, layar_id, jawaban):
    return client.post("/api/cek-langkah", json={"main_id": main_id, "layar_id": layar_id,
                                                 "jawaban": jawaban, "durasi_ms": 1000}).get_json()


def test_index_dan_404(client):
    assert client.get("/").status_code == 200
    assert client.get("/api/tidak-ada").status_code == 404


def test_sesi_kelas_opsional_boleh_kosong(client):
    r = client.post("/api/sesi", json={"kode_siswa": "S09", "kelas": ""})
    assert r.status_code == 200 and r.get_json()["kode_siswa"] == "S09"


def test_sesi_kode_tidak_valid(client):
    assert client.post("/api/sesi", json={"kode_siswa": "S 01; DROP"}).status_code == 400
    assert client.post("/api/sesi", json={}).status_code == 400


def test_detail_soal_tanpa_kunci(client):
    data = client.get("/api/soal/M3").get_data(as_text=True)
    for nama in ("kunci", "model", "petunjuk", "ringkasan", "umpan_salah"):
        assert f'"{nama}":' not in data
    assert "8.900.000" in data  # teks soal tetap ada


def test_alur_misi_lengkap_m3(client):
    sesi = masuk(client)
    main = mulai(client, sesi, "M3")
    pers = [["1", "1", "250"], ["5", "3", "890"]]

    salah = cek(client, main, "1a", {"persamaan": [["1", "1", "250"], ["5", "3", "900"]]})
    assert salah["benar"] is False and salah["detail"]["persamaan"] == [True, False]
    benar = cek(client, main, "1a", {"persamaan": pers})
    assert benar["benar"] and benar["skor"] == 1 and benar["percobaan"] == 2

    # Petunjuk harus berurutan
    assert client.post("/api/petunjuk", json={"main_id": main, "layar_id": "2a", "tingkat": 2}).status_code == 400
    p1 = client.post("/api/petunjuk", json={"main_id": main, "layar_id": "2a", "tingkat": 1}).get_json()
    assert p1["ada_lagi"] is True
    assert cek(client, main, "2a", {"m1": "3", "m2": "1", "operasi": "kurang", "persamaan": pers})["skor"] == 1

    # Petunjuk tingkat 3 → skor 0 walau jawaban benar
    for t in (1, 2, 3):
        client.post("/api/petunjuk", json={"main_id": main, "layar_id": "2b", "tingkat": t})
    r = cek(client, main, "2b", {"nilai": {"x": "70"}})
    assert r["benar"] and r["skor"] == 0

    assert cek(client, main, "3a", {"konst": "70", "koef": "1", "rhs": "250"})["benar"]
    # Lewati 3b
    lw = client.post("/api/lewati", json={"main_id": main, "layar_id": "3b"}).get_json()
    assert lw["ringkasan"]
    # Tidak bisa dijawab lagi setelah dilewati
    assert client.post("/api/cek-langkah", json={"main_id": main, "layar_id": "3b",
                                                 "jawaban": {"nilai": {"y": "180"}}}).status_code == 409

    # Belum lengkap → 409
    assert client.post(f"/api/main/{main}/selesai").status_code == 409
    assert cek(client, main, "4a", {"nilai": {"vip": "70", "reg": "180"}})["benar"]

    hasil = client.post(f"/api/main/{main}/selesai").get_json()
    assert hasil["skor"] == 4 and hasil["skor_maks"] == 6
    assert hasil["bintang"] == 2
    status = {l["id"]: l["status"] for l in hasil["layar"]}
    assert status == {"1a": "mandiri", "2a": "petunjuk", "2b": "petunjuk", "3a": "mandiri",
                      "3b": "dilihat", "4a": "mandiri"}


def test_progres_dan_kunci_misi(client):
    sesi = masuk(client, "S02")
    prog = client.get(f"/api/progres?sesi_id={sesi}").get_json()
    terbuka = {s["id"]: s["terbuka"] for s in prog["latihan"] + prog["misi"]}
    assert terbuka["L1"] and not terbuka["L2"] and not terbuka["M1"]
    assert len(prog["lencana"]) == 4 and len(prog["contoh"]) == 2


def test_alat_bantu(client):
    pers = [["3", "2", "130.000"], ["2", "5", "160.000"]]
    r = client.post("/api/alat/bantu-eliminasi", json={"soal_id": "M4", "persamaan": pers, "hilangkan": "x"})
    assert r.get_json()["pengali"] == ["2", "3"]
    r = client.post("/api/alat/cek-jawaban", json={"soal_id": "M4", "persamaan": pers,
                                                   "nilai": {"x": "30000", "y": "20000"}})
    assert r.get_json()["semua_cocok"] is True
    r = client.post("/api/alat/tips-metode", json={"persamaan": pers})
    assert r.get_json()["metode"] == "gabungan"
    assert client.post("/api/alat/tips-metode", json={"persamaan": [pers[0]]}).status_code == 400


def test_log_dan_guru(client):
    sesi = masuk(client)
    r = client.post("/api/log", json={"sesi_id": sesi, "peristiwa": [
        {"tipe": "cek_jawaban", "soal_id": "M1", "data": {"x": 1}},
        {"tipe": "tipe_aneh"},
    ]})
    assert r.get_json()["disimpan"] == 1
    assert client.get("/api/guru/rekap").status_code == 401
    assert client.get("/api/guru/rekap", headers={"X-PIN": "salah"}).status_code == 401
    rekap = client.get("/api/guru/rekap", headers={"X-PIN": "9999"}).get_json()["rekap"]
    assert rekap[0]["kode_siswa"] == "S01" and rekap[0]["pakai_cek_jawaban"] == 1
    csv = client.get("/api/guru/ekspor.csv?tabel=peristiwa", headers={"X-PIN": "9999"})
    assert csv.status_code == 200 and "cek_jawaban" in csv.get_data(as_text=True)


def test_alasan_teks_disimpan(client):
    sesi = masuk(client)
    main = mulai(client, sesi, "M1")
    r = cek(client, main, "5a", {"pilihan": "B", "teks": "Harganya sama di kedua toko."})
    assert r["benar"]
    csv = client.get("/api/guru/ekspor.csv?tabel=alasan", headers={"X-PIN": "9999"}).get_data(as_text=True)
    assert "Harganya sama" in csv
