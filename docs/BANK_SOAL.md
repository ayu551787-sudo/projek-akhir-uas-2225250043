# Bank Soal

Semua soal disimpan sebagai JSON di `backend/data/soal/`. Dokumen ini adalah **sumber isi**: teks soal, langkah, kunci jawaban, dan petunjuk. Seluruh kunci di bawah sudah diverifikasi dengan substitusi balik. `test_bank_soal.py` wajib memverifikasinya ulang secara otomatis.

## 1. Skema JSON

```jsonc
{
  "id": "M3",
  "mode": "misi",                       // "misi" | "latihan" | "contoh"
  "judul": "Tiket Pentas Seni",
  "indikator": "Employing Mathematical Concepts, Facts, and Procedures",
  "skor_maks": 6,
  "variabel": {
    "x": { "simbol": "x", "arti": "banyak tiket VIP", "satuan": "lembar" },
    "y": { "simbol": "y", "arti": "banyak tiket Reguler", "satuan": "lembar" }
  },
  "segmen": [                           // teks soal dipotong untuk penanda
    { "t": "Panitia pentas seni sekolah menjual dua jenis tiket: tiket kelas VIP dan tiket kelas Reguler. " },
    { "t": "Total tiket yang terjual seluruhnya adalah 250 lembar", "peran": "data", "var": ["x","y"] },
    { "t": ". " },
    { "t": "Harga tiket VIP adalah Rp50.000", "peran": "data", "var": ["x"] },
    { "t": " per lembar dan " },
    { "t": "tiket Reguler adalah Rp30.000", "peran": "data", "var": ["y"] },
    { "t": " per lembar. " },
    { "t": "Total pendapatan … adalah Rp8.900.000", "peran": "data", "var": ["x","y"] },
    { "t": ". " },
    { "t": "Berapa banyak tiket VIP dan tiket Reguler yang masing-masing berhasil terjual?", "peran": "tanya" }
  ],
  "tahap": [
    {
      "no": 1, "skor": 1,
      "layar": [
        {
          "id": "model", "skor": 1,
          "instruksi": "Susun dua persamaan dari soal.",
          "input": "persamaan2",
          "alat": ["penerjemah"],
          "kunci": { "persamaan": [[1,1,250],[50000,30000,8900000]] },   // HANYA di server
          "petunjuk": [
            "Ada dua informasi 'total': total tiket dan total pendapatan.",
            "Total tiket: banyak VIP + banyak Reguler = 250. Total uang: harga × banyak tiket, dijumlahkan.",
            "(1) x + y = 250   (2) 50.000x + 30.000y = 8.900.000"
          ],
          "umpan_salah": {
            "pers1": "Cek persamaan tentang total tiket: berapa jumlah semua tiket?",
            "pers2": "Cek persamaan tentang uang: harga VIP dikali banyak tiket VIP, ditambah …"
          }
        }
      ]
    }
    // … tahap berikutnya
  ]
}
```

**Tipe `input` yang tersedia:** `persamaan2` (dua template `[ ]x + [ ]y = [ ]`), `persamaan1`, `angka` (satu atau beberapa isian bernama), `pilihan` (opsi + indeks kunci), `pengali` (dua pengali + operasi `jumlah`/`kurang`), `tandai` (ketuk segmen + pasangkan variabel), `formula` (`Y = [ ] + [ ]x`), `teks` (bebas, tidak dinilai otomatis).

**Aturan kunci:**
- `persamaan`: diterima jika setara (sebanding) dalam urutan apa pun.
- `angka`: dibandingkan secara eksak setelah parsing format Indonesia.
- `pilihan`: urutan opsi diacak di klien, tetapi kunci tetap disimpan di server berdasarkan id opsi.

---

## 2. Mode Misi (dari kisi-kisi)

### M1: Toko Mana yang Hemat? · Mathematical Reasoning · maksimum 6

**Soal.** Toko A menawarkan paket promo: **Paket 1** (2 buku tulis + 3 pensil) seharga Rp19.000, dan **Paket 2** (4 buku tulis + 1 pensil) seharga Rp23.000. Toko B menawarkan harga eceran tetap: Rp5.000 per buku tulis dan Rp3.000 per pensil. Rini ingin membeli **3 buku tulis dan 3 pensil**. Ia ingin mengeluarkan uang sesedikit mungkin. Di toko mana Rini sebaiknya membeli alat tulis tersebut? Jelaskan alasan matematismu!

Variabel: x = harga 1 buku tulis di Toko A, y = harga 1 pensil di Toko A.

| Tahap | Layar | Kunci | Petunjuk 1 → 2 → 3 |
|---|---|---|---|
| 1 (1) | Rencana | **B** (lihat opsi) | Apa yang perlu diketahui agar bisa membandingkan harga 3 buku + 3 pensil? → Harga satuan di Toko A belum diketahui; harga itu bisa dicari dari dua paket. → Jawaban B |
| 2 (2) | 2a Model (1) | `2x + 3y = 19000`, `4x + y = 23000` | Satu paket menghasilkan satu persamaan. → Paket 1: 2 buku dan 3 pensil, jadi 2x + 3y = … → Kedua persamaan |
| | 2b Nilai & total (1) | x = 5000, y = 3000; total A = 24000; total B = 24000 | Koefisien y di pers. (2) adalah 1, jadi substitusi bisa dipakai. → y = 23000 − 4x, substitusi ke (1). → x = 5000, y = 3000, total = 3(5000) + 3(3000) |
| 3 (1) | Bandingkan | A = B | Lihat Panel Ringkasan: total A dan B. → Keduanya Rp24.000. → "A = B" |
| 4 (1) | Keputusan | Boleh di mana saja | Jika totalnya sama, apakah ada toko yang lebih hemat? → Tidak ada. → "Boleh di Toko A maupun Toko B" |
| 5 (1) | Alasan | **B** (lihat opsi) | Alasan yang baik memakai hasil hitungan. → Bandingkan harga satuan A dan B. → Jawaban B |

Opsi tahap 1:
- A. Jumlahkan harga Paket 1 dan Paket 2, lalu bandingkan dengan Toko B.
- **B. Cari harga satuan buku dan pensil di Toko A dengan SPLDV, hitung total 3 buku + 3 pensil di kedua toko, lalu bandingkan.** ✓
- C. Pilih Toko A karena promo pasti lebih murah.
- D. Bagi harga tiap paket dengan banyak barangnya.

Opsi tahap 5:
- A. Karena Toko A memberikan promo paket.
- **B. Karena harga satuan hasil SPLDV di Toko A (buku Rp5.000, pensil Rp3.000) sama dengan harga eceran Toko B, sehingga total di kedua toko sama-sama Rp24.000.** ✓
- C. Karena Toko B tidak menjual paket.
- D. Karena Rp19.000 + Rp23.000 lebih dari Rp24.000.

> **Catatan validitas untuk peneliti:** Toko A hanya menjual paket. Kombinasi paket tidak bisa tepat menghasilkan 3 buku + 3 pensil, sehingga kisi-kisi mengasumsikan harga satuan Toko A berlaku untuk pembelian eceran. Pertimbangkan menambah kalimat "Toko A juga menjual eceran dengan harga satuan yang sama seperti di dalam paket" agar soal tidak ambigu. Typo "oko A" di kisi-kisi sudah diperbaiki menjadi "Toko A".

---

### M2: Tarif Sewa Futsal · Formulating Situations Mathematically · maksimum 6

**Soal.** Dua tim futsal menyewa lapangan di tempat yang sama dengan skema tarif yang terdiri atas biaya admin tetap dan biaya per jam. Tim A bermain selama 2 jam dan membayar total Rp130.000. Tim B bermain selama 4 jam dan membayar total Rp230.000. Pengelola ingin membuat formula umum untuk menghitung total biaya sewa (Y) berdasarkan lama sewa (x jam). Ubahlah situasi tersebut menjadi model matematika (SPLDV), tentukan besar biaya admin dan biaya per jam, lalu selesaikan untuk membentuk persamaan Y!

Variabel: a = biaya admin (tetap), b = biaya per jam. Koefisien input ditampilkan sebagai `[ ]a + [ ]b = [ ]`.

| Tahap | Kunci | Petunjuk 1 → 2 → 3 |
|---|---|---|
| 1 (1) Diketahui/ditanya | Data: (2 jam, 130.000), (4 jam, 230.000). Ditanya: a, b, dan Y. Variabel: a = admin, b = per jam | Ada dua tim, jadi ada dua data. → Biaya admin dibayar sekali, biaya per jam dikali lama bermain. → Penanda lengkap ditampilkan |
| 2 (1) Model | `a + 2b = 130000`, `a + 4b = 230000` | Total = admin + (lama × biaya per jam). → Tim A: a + 2b = … → Kedua persamaan |
| 3 (1) Eliminasi a | Kurangkan, sehingga 2b = 100000 dan **b = 50000** | Koefisien a di kedua persamaan sama-sama 1. → Tanda sama, jadi dikurangkan: (2) − (1). → 2b = 100.000, b = 50.000 |
| 4 (1) Nilai a | **a = 30000** | Masukkan b ke persamaan yang paling sederhana. → a + 2(50.000) = 130.000 → a = 30.000 |
| 5 (1) Formula | `Y = 30000 + 50000x` | Formula: admin + biaya per jam × lama. → Y = a + b·x → Y = 30.000 + 50.000x |
| 6 (1) Kesimpulan | Opsi: "Biaya admin tetap Rp30.000 dan tarif Rp50.000 per jam, jadi Y = 30.000 + 50.000x" | — → — → jawaban |

Pengecoh tahap 6: "Biaya admin Rp50.000 dan tarif Rp30.000 per jam", "Tarif Rp65.000 per jam tanpa admin" (130.000 : 2), "Y = 130.000 + 230.000x".

---

### M3: Tiket Pentas Seni · Employing Concepts, Facts & Procedures · maksimum 6

**Soal.** Panitia pentas seni sekolah menjual dua jenis tiket: tiket kelas VIP dan tiket kelas Reguler. Total tiket yang terjual seluruhnya adalah 250 lembar. Harga tiket VIP adalah Rp50.000 per lembar dan tiket Reguler Rp30.000 per lembar. Total pendapatan dari penjualan seluruh tiket tersebut adalah Rp8.900.000. Berapa banyak tiket VIP dan tiket Reguler yang masing-masing berhasil terjual? Tunjukkan langkah perhitunganmu!

Variabel: x = banyak tiket VIP, y = banyak tiket Reguler.

| Tahap | Layar | Kunci | Petunjuk 1 → 2 → 3 |
|---|---|---|---|
| 1 (1) | Model | `x + y = 250`, `50000x + 30000y = 8900000` (setara dengan `5x + 3y = 890`) | Lihat skema JSON di atas |
| 2 (2) | 2a Pengali (1) | Pers. (1) × 3, (2) × 1, **kurang** | Lihat koefisien y: 1 dan 3. Bagaimana cara menyamakannya? → Kalikan (1) dengan 3; tanda sama, jadi dikurangkan. → 3x + 3y = 750; (5x + 3y) − (3x + 3y) = 890 − 750 |
| | 2b Nilai x (1) | **x = 70** | Sisa persamaannya hanya memuat x. → 2x = 140 → x = 70 |
| 3 (2) | 3a Substitusi (1) | `70 + y = 250` (persamaan lain yang setara juga diterima) | Pilih persamaan yang paling sederhana. → Pers. (1): x + y = 250, ganti x dengan 70. → 70 + y = 250 |
| | 3b Nilai y + cek (1) | **y = 180** | → y = 250 − 70 → y = 180. Cek: 50.000(70) + 30.000(180) = 8.900.000 ✓ |
| 4 (1) | Kesimpulan | VIP = 70 lembar, Reguler = 180 lembar | Jawab pertanyaan soal lengkap dengan satuan. → … → 70 VIP, 180 Reguler |

Pilihan metode alternatif: jika siswa memilih substitusi di layar Tips Metode, tahap 2 berubah menjadi `y = 250 − x`, lalu `5x + 3(250 − x) = 890`, sehingga x = 70. Skor tetap sama dan kedua jalur diterima.

---

### M4: Cek Hitungan Candra · Interpreting, Applying & Evaluating · maksimum 6

**Soal.** Budi membeli 3 kg apel dan 2 kg jeruk dengan harga Rp130.000. Di kios yang sama, Ani membeli 2 kg apel dan 5 kg jeruk dengan harga Rp160.000. Pembeli lain, Candra, menghitung bahwa harga 1 kg apel adalah Rp30.000 dan 1 kg jeruk Rp20.000. Ia menyimpulkan bahwa dengan uang Rp100.000, ia bisa membeli 2 kg apel dan 2 kg jeruk. Apakah kamu setuju dengan analisis dan kesimpulan Candra? Jelaskan alasanmu berdasarkan perhitungan matematis yang benar!

Variabel: x = harga 1 kg apel, y = harga 1 kg jeruk.

| Tahap | Kunci | Petunjuk 1 → 2 → 3 |
|---|---|---|
| 1 (1) Model | `3x + 2y = 130000`, `2x + 5y = 160000` | Jangan langsung percaya angka Candra; susun dari data Budi dan Ani. → Budi: 3x + 2y = … → Kedua persamaan |
| 2 (1) Eliminasi x | Pengali (1)×2, (2)×3, **kurang**; 11y = 220000, **y = 20000** | Koefisien x: 3 dan 2. KPK-nya? → KPK 6: (1)×2, (2)×3; tanda sama, jadi dikurangkan. → 6x + 4y = 260.000; 6x + 15y = 480.000; 11y = 220.000 |
| 3 (1) Nilai x + evaluasi | **x = 30000**; harga Candra **benar** | Substitusi y ke pers. (1). → 3x + 40.000 = 130.000 → x = 30.000, sama dengan hitungan Candra |
| 4 (1) Biaya | **100000** | 2 kg apel + 2 kg jeruk = 2x + 2y. → 2(30.000) + 2(20.000) → Rp100.000 |
| 5 (1) Bandingkan | **Pas/cukup** (100.000 ≤ 100.000) | Bandingkan biaya dengan uang Candra. → Keduanya sama besar. → "Uangnya pas (cukup)" |
| 6 (1) Kesimpulan | **Setuju**, dengan alasan: harga satuan Candra tepat dan total 2 kg apel + 2 kg jeruk tepat Rp100.000 | — → — → jawaban |

Pengecoh alasan tahap 6: "Tidak setuju, karena uang harus lebih dari harga", "Setuju, karena Candra pembeli", "Tidak setuju, karena 130.000 + 160.000 > 100.000".

---

## 3. Mode Belajar: Latihan berjenjang (dari soal pemicu wawancara)

Latihan tidak masuk skor penelitian, tetapi percobaan dan petunjuk tetap dicatat.

### L1: Soal simbolik (soal pemicu 1)
`−x + y = 70` dan `2x − y = 30`

| Langkah | Kunci | Catatan |
|---|---|---|
| Pilih variabel yang dihilangkan | y (koefisien +1 dan −1, berlawanan) | Tips Metode: "Koefisien y berlawanan, jadi eliminasi langsung" |
| Operasi | **jumlah** | Pada wawancara siswa sering salah memilih tambah/kurang (IL05), jadi Penyelaras Koefisien menekankan aturan tanda |
| Nilai x | x = 100 | |
| Substitusi | −100 + y = 70, sehingga **y = 170** | Siswa S01 mengalami "perhitungan terbalik" di tahap ini; umpan balik khusus untuk y = −30 atau y = 30: "Pindahkan −100 ke ruas kanan: tandanya berubah." |
| Cek Jawaban | −100 + 170 = 70 ✓; 200 − 170 = 30 ✓ | |

### L2: Buku dan pensil (soal pemicu 2)
Ajeng membeli 4 buku dan 1 pensil seharga Rp5.600. Di toko yang sama, Ali membeli 5 buku dan 3 pensil seharga Rp8.400. Berapa harga 1 buku dan 1 pensil?

- Model: `4x + y = 5600`, `5x + 3y = 8400`
- Tips Metode: koefisien y di pers. (1) adalah 1, sehingga substitusi `y = 5600 − 4x` cepat. Eliminasi ((1)×3 lalu dikurangkan) juga diterima.
- Kunci: **x = 1200** (buku), **y = 800** (pensil). Cek: 4(1200) + 800 = 5600 ✓; 5(1200) + 3(800) = 8400 ✓

### L3: Umur ibu dan Sahi (soal pemicu 3)
Dua tahun lalu, umur ibu sama dengan 6 kali umur Sahi. 18 tahun yang akan datang, umur ibu menjadi 2 kali umur Sahi. Berapakah umur ibu dan Sahi sekarang?

Variabel: x = umur ibu sekarang, y = umur Sahi sekarang.

| Langkah | Kunci | Catatan |
|---|---|---|
| Terjemahkan "dua tahun lalu" | umur ibu = x − 2, umur Sahi = y − 2 | Penerjemah Soal menampilkan tabel "dulu / sekarang / nanti" |
| Persamaan mentah 1 | x − 2 = 6(y − 2) | |
| Bentuk baku 1 | `x − 6y = −10` | Layar khusus "rapikan ke bentuk ax + by = c". Inilah bagian yang sulit bagi S01 (EL01) |
| Persamaan mentah 2 | x + 18 = 2(y + 18) | |
| Bentuk baku 2 | `x − 2y = 18` | |
| Eliminasi x | (2) − (1): 4y = 28, sehingga **y = 7** | |
| Nilai x | x − 14 = 18, sehingga **x = 32** | |
| Cek kewajaran | 30 = 6 × 5 ✓; 50 = 2 × 25 ✓; umur positif dan masuk akal | Melatih "menilai kewajaran" (GL02) |

---

## 4. Mode Belajar: Simulasi Belanja (SIM)

- Rak berisi 2 jenis barang dengan ikon datar sederhana (misalnya buku = biru `--var-1`, pensil = oranye `--var-2`).
- Siswa mengisi **Keranjang 1** dan **Keranjang 2** dengan mengetuk + / −. Total harga setiap keranjang diberikan dari harga tersembunyi yang dipilih acak dari daftar harga bulat (kelipatan Rp500).
- Persamaan terbentuk langsung di bawah keranjang: `3 buku + 2 pensil = Rp13.000` lalu `3x + 2y = 13.000`, dengan label "koefisien = banyak barang", "variabel = harga satu barang", "konstanta = total bayar".
- Siswa menebak harga satuan, lalu Cek Jawaban memeriksanya.
- Validasi: kedua keranjang harus menghasilkan persamaan yang **tidak sebanding** (determinan ≠ 0). Jika sebanding, muncul pesan: "Keranjang 2 sama polanya dengan keranjang 1. Coba komposisi lain agar harga bisa ditemukan."
