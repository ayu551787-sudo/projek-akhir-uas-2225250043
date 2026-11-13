# CLAUDE.md

Panduan untuk Claude Code (dan pengembang lain) saat menulis kode di repositori ini. Baca dokumen ini sebelum mengubah kode.

## Ringkasan proyek

Proyek ini adalah aplikasi web pembelajaran SPLDV untuk siswa SMP. Tujuannya mengurangi beban kognitif agar literasi matematika siswa meningkat. Backend ditulis dengan **Python (Flask)** dan frontend dengan **JavaScript vanilla**. Aplikasi harus nyaman dipakai di smartphone.

Rujukan wajib:
- Kebutuhan dan alasan setiap fitur: `docs/KEBUTUHAN.md`
- Aturan tampilan: `DESIGN.md`
- Isi soal dan kunci jawaban: `docs/BANK_SOAL.md` (sumber data: `backend/data/soal/*.json`)
- Aturan game dan penilaian: `docs/GAME.md`

## Perintah

```bash
pip install -r backend/requirements.txt   # pasang dependensi
python backend/app.py                     # jalankan server di http://localhost:5000
pytest backend/tests                      # semua tes Python
pytest backend/tests/test_solver.py -k eliminasi   # tes tertentu
node --test frontend/tests                # tes fungsi murni JS (format angka, parser input)
```

## Pembagian tanggung jawab Python dan JavaScript

| Python (`backend/`) | JavaScript (`frontend/`) |
|---|---|
| Menyimpan dan memuat bank soal | Menampilkan satu langkah per layar |
| **Memeriksa jawaban** dan menghitung skor rubrik | Keypad angka, input persamaan terstruktur |
| Menyelesaikan SPLDV (`spldv/solver.py`) | Penanda/highlight teks soal |
| Membuat petunjuk pengali eliminasi | Panel ringkasan langkah, kontrol tempo |
| Menyimpan sesi, jawaban, dan log ke SQLite | Mengirim log peristiwa ke API (berkelompok) |
| Ekspor CSV untuk guru/peneliti | Peta misi, bintang, lencana |

## Aturan wajib

1. **Kunci jawaban tidak boleh dikirim ke browser.** Endpoint `GET /api/soal/...` hanya mengirim teks soal, segmen, dan struktur langkah. Pemeriksaan jawaban selalu dilakukan di server melalui `POST /api/cek-langkah`. Pengecualian: konten Mode Belajar (contoh soal yang sudah dibahas) boleh berisi langkah lengkap.
2. **Gunakan `fractions.Fraction`, jangan `float`**, untuk semua perhitungan SPLDV di Python. Bandingkan nilai secara eksak.
3. **Persamaan setara harus diterima.** `50000x + 30000y = 8900000` dan `5x + 3y = 890` sama-sama benar. Periksa kesebandingan koefisien (lihat `docs/ARSITEKTUR.md` § Pemeriksa model). Urutan kedua persamaan bebas.
4. **Format angka Indonesia.** Titik adalah pemisah ribuan (`19.000` berarti 19000, bukan 19,0). Parser input harus menerima `19000`, `19.000`, `Rp19.000`, dan `Rp 19.000`, serta tanda minus `-`/`−`. Tampilkan uang sebagai `Rp19.000` dengan `Intl.NumberFormat('id-ID')`.
5. **Satu langkah satu layar.** Jangan menumpuk lebih dari satu tugas input dalam satu layar. Langkah yang sudah selesai dipindahkan ke Panel Ringkasan di atas.
6. **Tanpa animasi dekoratif.** Transisi hanya boleh untuk umpan balik fungsional (misalnya warna benar/salah, maksimal 150 ms) dan wajib menghormati `prefers-reduced-motion`.
7. **Tanpa batas waktu (timer) yang terlihat siswa.** Durasi tetap dicatat diam-diam untuk penelitian.
8. **Siswa tidak boleh mentok.** Setiap langkah punya Petunjuk tingkat 3 (menampilkan jawaban langkah) agar siswa tetap bisa lanjut, dengan konsekuensi skor tahap itu menjadi 0 (lihat `docs/GAME.md`).
9. **Warna variabel harus konsisten di seluruh aplikasi.** `x`/variabel pertama memakai token `--var-1`, `y`/variabel kedua memakai `--var-2`. Warna tidak boleh menjadi satu-satunya penanda, jadi selalu sertakan label teks.
10. **Privasi.** Siswa diidentifikasi dengan kode (misalnya `S01`). Jangan menyimpan nama lengkap, email, atau foto.

## Konvensi kode

- **Bahasa**: nama variabel, fungsi, dan file ditulis dalam bahasa Inggris pendek, kecuali istilah domain yang memang berbahasa Indonesia (`soal`, `tahap`, `petunjuk`). Teks yang dilihat siswa ditulis dalam Bahasa Indonesia yang sederhana dan menyapa langsung ("Kamu"). Komentar dan docstring boleh berbahasa Indonesia.
- **Python**: PEP 8, type hints, fungsi murni untuk logika matematika (tanpa akses DB). Logika dipisah dari route Flask.
- **JavaScript**: ES Modules (`import`/`export`), tanpa framework dan tanpa bundler. Satu file per layar atau komponen di `frontend/js/`. Hindari `innerHTML` untuk data dari pengguna; gunakan `textContent`.
- **CSS**: semua warna dan ukuran berupa token di `:root` (lihat `DESIGN.md`). Pendekatan mobile-first.
- **Teks UI**: semua string tampilan dikumpulkan di `frontend/js/teks.js` agar konsisten dan mudah direvisi.
- **Data soal**: hanya diubah di `backend/data/soal/*.json`, mengikuti skema di `docs/BANK_SOAL.md`. Setiap soal baru wajib punya tes yang memastikan kuncinya benar menurut solver.

## Pengujian

- Setiap fungsi di `backend/spldv/` wajib punya unit test.
- `test_bank_soal.py` memuat semua soal JSON, menyelesaikan SPLDV-nya dengan solver, lalu mencocokkan hasilnya dengan kunci. Tes ini mencegah salah ketik pada kunci jawaban.
- Uji tampilan secara manual pada lebar 360 px (HP) dan 1280 px (laptop) sebelum menyatakan fitur UI selesai.

## Checklist beban kognitif untuk setiap layar baru

- [ ] Hanya ada satu tugas dalam satu layar?
- [ ] Informasi langkah sebelumnya terlihat di Panel Ringkasan (tidak perlu diingat)?
- [ ] Istilah dan warna variabel sama dengan layar lain?
- [ ] Tidak ada animasi, gambar, atau hiasan yang tidak berfungsi?
- [ ] Ada tombol Petunjuk, dan petunjuk tingkat 1 tidak langsung memberi jawaban?
- [ ] Bisa dipakai dengan satu jempol di layar 360 px?
