# Roadmap Pengerjaan

Tahapan ini disusun agar setiap fase menghasilkan sesuatu yang **bisa dicoba**. Perkiraan durasi mengasumsikan 1 orang bekerja paruh waktu.

## Fase 0: Persiapan (1–2 hari)
- [ ] Pasang Python 3.11+, VS Code, dan Git. Jalankan `git init`.
- [ ] Buat struktur folder sesuai `docs/ARSITEKTUR.md`.
- [ ] Buat `backend/requirements.txt` (`flask`, `pytest`) dan `app.py` "Hello" yang melayani `frontend/index.html`.
- [ ] Buat `style.css` berisi token dari `DESIGN.md`.

**Hasil:** halaman kosong bergaya dasar terbuka di HP lewat Wi-Fi yang sama.

## Fase 1: Inti matematika di Python (3–4 hari)
- [ ] `spldv/parse.py` dengan tes format angka Indonesia.
- [ ] `spldv/solver.py` dengan tes.
- [ ] `spldv/checker.py` (persamaan setara, urutan bebas, angka, pilihan) dengan tes.
- [ ] `spldv/helper.py` (KPK, pengali, aturan tanda, tips metode) dengan tes.
- [ ] Tulis JSON L1, L2, L3, M1–M4 dari `BANK_SOAL.md`, lalu `test_bank_soal.py`.

**Hasil:** `pytest` lulus dan semua kunci soal terverifikasi otomatis.

## Fase 2: API dan basis data (2–3 hari)
- [ ] `db.py` beserta tabel dari `ARSITEKTUR.md` §5.
- [ ] Endpoint `sesi`, `soal`, `cek-langkah`, `petunjuk`, `cek-jawaban`, `bantu-eliminasi`, `tips-metode`, `log`.
- [ ] `scoring.py` sesuai `GAME.md` §4.
- [ ] `test_api.py`, termasuk tes "kunci tidak bocor".

**Hasil:** seluruh alur misi bisa diuji lewat pytest atau Thunder Client tanpa tampilan.

## Fase 3: Frontend inti (5–7 hari) → **MVP**
- [ ] Router hash, layar Masuk (kode siswa), Beranda, dan Peta Misi.
- [ ] Komponen: `keypad`, `inputPersamaan`, `teksSoal` (penanda), `panelRingkasan`, `petunjuk`, `umpanBalik`.
- [ ] Layar generik `langkah.js` yang membaca struktur tahap/layar dari API.
- [ ] Alat bantu: `penyelaras`, `cekJawaban`, `tipsMetode`.
- [ ] Layar Hasil dengan bintang.
- [ ] `logger.js` dan progres tersimpan.

**Hasil (MVP):** L1–L3 dan M1–M4 bisa dimainkan penuh di HP; skor dan log tersimpan.

## Fase 4: Fitur pendukung belajar (3–4 hari)
- [ ] Penerjemah Soal interaktif (frasa menjadi suku persamaan), termasuk tabel "dulu/sekarang/nanti" untuk L3.
- [ ] Contoh soal C1–C3 dengan kontrol tempo.
- [ ] Simulasi Belanja.
- [ ] Lencana.

## Fase 5: Halaman guru dan rapikan (2 hari)
- [ ] `/guru`: PIN, tabel rekap, dan tombol ekspor CSV.
- [ ] Mode gelap dan cek kontras.
- [ ] Uji manual dengan checklist di `EVALUASI.md` §A.

## Fase 6: Uji coba terbatas (1 minggu)
- [ ] Uji keterbacaan dengan 1–3 siswa (termasuk S01 jika bersedia) dan wawancara kejelasan tampilan.
- [ ] Revisi teks petunjuk dan umpan balik berdasarkan temuan.
- [ ] Uji coba kelas kecil sesuai desain di `EVALUASI.md` §B.
- [ ] Deploy (PythonAnywhere/Render) jika diperlukan akses dari rumah.

## Opsional (setelah UAS)
- PWA agar aplikasi bisa dipasang di layar utama dan dimuat offline.
- Soal paralel M1b–M4b untuk pra-uji.
- Pembangkit soal acak untuk latihan (angka dibuat agar solusinya bulat).

## Keputusan yang masih perlu dikonfirmasi peneliti

| Keputusan | Default di rencana | Lokasi |
|---|---|---|
| Petunjuk tingkat 1–2 mengurangi skor rubrik? | Tidak | `GAME.md` §4.1 |
| Skor hanya dari percobaan pertama? | Tidak | `GAME.md` §4.1 |
| Mode Misi wajib menyelesaikan L2 dulu? | Ya, tetapi boleh dilewati dengan konfirmasi | `GAME.md` §2 |
| Revisi kalimat soal M1 (eceran di Toko A) | Disarankan | `BANK_SOAL.md` M1 |
| Nama aplikasi | "Jelajah SPLDV" | `README.md` |
