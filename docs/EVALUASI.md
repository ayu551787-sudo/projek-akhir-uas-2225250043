# Rencana Evaluasi dan Pengujian Fitur

Dokumen ini menurunkan kolom **"Cara menguji fitur"** dari matriks wawancara menjadi data yang benar-benar dicatat aplikasi. Isinya mencakup dua jenis pengujian: (A) pengujian perangkat lunak (apakah aplikasi berjalan benar) dan (B) pengujian kependidikan (apakah fitur mengurangi beban kognitif dan meningkatkan literasi).

## A. Pengujian perangkat lunak

| Jenis | Alat | Cakupan minimum |
|---|---|---|
| Unit test Python | pytest | `solver`, `checker` (persamaan setara, urutan bebas, kasus nol), `helper` (KPK, aturan tanda), `parse` (format angka Indonesia), `scoring` |
| Validasi bank soal | pytest `test_bank_soal.py` | Setiap soal: model kunci diselesaikan solver harus sama dengan kunci nilai; determinan ≠ 0; skor tahap berjumlah `skor_maks` |
| Tes API | Flask test client | Setiap endpoint: input valid, input rusak, kunci tidak bocor di `GET /soal/<id>` |
| Tes fungsi JS | `node --test` | `format.js` (parse dan format id-ID) |
| Uji manual perangkat | HP Android (Chrome), iPhone (Safari) jika ada, laptop | Checklist di bawah |

**Kasus uji penting untuk `checker`:**

| Input siswa | Kunci | Hasil yang diharapkan |
|---|---|---|
| `5x + 3y = 890` | `50000x + 30000y = 8900000` | benar (sebanding) |
| pers. (1) dan (2) tertukar | — | benar |
| `-x - y = -250` | `x + y = 250` | benar (dikali −1) |
| `x + y = 250` dua kali | `x + y = 250`, `5x + 3y = 890` | salah pada pers. (2) |
| `0x + 0y = 0` | apa pun | salah |
| `19.000` | 19000 | sama |

**Checklist uji manual (per rilis):**
- [ ] Lebar 360 px: tidak ada scroll horizontal; tombol utama terjangkau jempol.
- [ ] Keypad bisa memasukkan angka negatif.
- [ ] Muat ulang halaman di tengah misi mengembalikan siswa ke layar terakhir.
- [ ] Mode gelap terbaca dan warna variabel tetap bisa dibedakan.
- [ ] View-source atau DevTools Network tidak memperlihatkan kunci jawaban misi.

## B. Pengujian kependidikan

### 1. Desain uji coba (usulan)

1. **Pra-uji**: siswa mengerjakan 4 soal kisi-kisi di kertas (skor rubrik 0–24) dan mengisi kuesioner beban kognitif singkat.
2. **Perlakuan**: siswa memakai Mode Belajar (L1–L3, simulasi) selama 1–2 pertemuan.
3. **Pasca-uji**: siswa mengerjakan Mode Misi di aplikasi (skor otomatis 0–24) dan mengisi kuesioner beban kognitif lagi.
4. **Wawancara pasca**: memakai pertanyaan kejelasan tampilan dan meminta siswa menjelaskan ulang hubungan x dan y.

> Agar perbandingan pra dan pasca adil, gunakan **soal paralel** (konteks dan angka berbeda, struktur sama) untuk pra-uji. Soal paralel dapat ditambahkan ke bank soal sebagai M1b–M4b.

**Instrumen beban kognitif (usulan):** skala mental effort Paas (1 item, skala 1–9), atau kuesioner 10 item Leppink et al. (2013) yang memisahkan IL, EL, dan GL. Versi bahasa Indonesianya perlu divalidasi atau mengutip adaptasi yang sudah ada.

### 2. Indikator per fitur

| Fitur | Pertanyaan evaluasi (dari matriks) | Data dari aplikasi | Data di luar aplikasi |
|---|---|---|---|
| F01 Penerjemah Soal, F02 Latihan berjenjang | Apakah siswa bisa menjelaskan hubungan x dan y? | Ketepatan layar "model" pada percobaan pertama; jumlah percobaan; tingkat petunjuk | Siswa menjelaskan secara lisan (wawancara) |
| F03 Satu langkah + Ringkasan | Apakah langkah eliminasi/substitusi yang terlewat berkurang? | Jumlah jawaban salah tipe "variabel belum hilang"; frekuensi membuka/melipat ringkasan | — |
| F04 Penanda informasi | Apakah siswa menemukan data relevan lebih cepat? | Durasi layar `tandai`; jumlah salah tandai | — |
| F05 Tampilan sederhana | Apakah tampilan dianggap jelas? | — | Wawancara kejelasan tampilan |
| F06 Kontrol tempo | Seberapa sering siswa mengulang? | Jumlah `tempo_ulang` dan `tempo_jeda` per contoh soal | — |
| F07 Simulasi | Apakah penjelasan siswa membaik setelah simulasi? | Waktu di simulasi; jumlah keranjang dicoba | Penjelasan sebelum dan sesudah |
| F08 Tips Metode | Apakah keraguan memilih metode berkurang? | Metode yang dipilih dan kecocokannya dengan saran | — |
| F09 Cek Jawaban | Apakah siswa membiasakan verifikasi mandiri? | Proporsi layar akhir yang didahului `cek_jawaban` (tanpa disuruh) | — |
| F10 Penyelaras Koefisien | Apakah kesalahan pengali berkurang? | Salah pengali/operasi di L1 → L2 → L3 → misi (tren) | — |
| F11 Petunjuk | Apakah petunjuk bertahap cukup tanpa jawaban? | Distribusi tingkat petunjuk tertinggi per layar | — |
| F12 Mode Misi | Bagaimana kemampuan literasi per indikator? | Skor per misi (Reasoning, Formulating, Employing, Interpreting) | Pra-uji kertas |

### 3. Jenis peristiwa log (`peristiwa.tipe`)

| Tipe | Data (`data_json`) |
|---|---|
| `layar_buka`, `layar_tutup` | `{layar, durasi_ms}` |
| `periksa` | `{layar, benar, percobaan}` |
| `petunjuk` | `{layar, tingkat}` |
| `lewati` | `{layar}` |
| `tempo_ulang`, `tempo_jeda`, `tempo_lanjut` | `{contoh_id, langkah}` |
| `tandai_segmen` | `{indeks_segmen, benar}` |
| `cek_jawaban` | `{x, y, cocok:[bool,bool]}` |
| `bantu_eliminasi` | `{hilangkan, pengali_saran}` |
| `tips_metode` | `{saran, dipilih}` |
| `ringkasan_toggle` | `{terbuka}` |
| `simulasi_keranjang` | `{keranjang1, keranjang2, valid}` |
| `aplikasi_sembunyi` | `{}` (tab ditinggal; untuk membersihkan data durasi) |

### 4. Ekspor untuk analisis

`/api/guru/ekspor.csv?tabel=jawaban_tahap|peristiwa|rekap`. Kolom `rekap` berisi satu baris per siswa:
`kode_siswa, kelas, skor_M1..M4, total, petunjuk_t1, petunjuk_t2, petunjuk_t3, pakai_cek_jawaban, durasi_total_menit`.

### 5. Etika

- Mintalah persetujuan dari sekolah, orang tua/wali, dan siswa sebelum uji coba.
- Siswa hanya dikenali dengan kode; tabel pemetaan kode ke nama disimpan terpisah oleh peneliti, di luar aplikasi.
- Foto dokumentasi disamarkan wajahnya, seperti pada laporan wawancara.
