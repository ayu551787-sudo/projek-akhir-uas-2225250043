# Desain Game: Mode Misi

Mode Misi mengubah **4 soal kisi-kisi literasi matematika** menjadi game bertahap. Game ini berfungsi ganda: sebagai **latihan** (ada petunjuk dan umpan balik) dan sebagai **instrumen penilaian** (skor dihitung mengikuti rubrik per tahap di kisi-kisi).

## 1. Prinsip: gamifikasi yang tidak menambah beban

| Dipakai | Alasan |
|---|---|
| Peta misi (4 kartu berurutan) | Siswa tahu posisi dan tujuannya |
| Bintang 0–3 per misi | Umpan balik ringkas atas pencapaian |
| Lencana berbentuk teks | Menghargai kebiasaan baik (mandiri, memeriksa) |
| Cerita konteks sehari-hari | Mendukung pemodelan (GL01) |

| Tidak dipakai | Alasan |
|---|---|
| Timer atau hitung mundur | EL02: waktu habis karena memahami soal; timer menambah kecemasan |
| Nyawa atau game over | Bertentangan dengan IL03 (siswa harus tetap bisa lanjut) |
| Papan peringkat antarsiswa | Memicu perbandingan sosial; tidak relevan dengan tujuan |
| Animasi dan efek besar | DS03 |

## 2. Struktur

```
Beranda
 ├─ Mode Belajar
 │   ├─ Contoh Soal (worked example, kontrol tempo)    C1–C3
 │   ├─ Simulasi Belanja                                SIM
 │   └─ Latihan Berjenjang (dari soal pemicu wawancara) L1 → L2 → L3
 └─ Mode Misi (game)
     ├─ Misi 1 · Toko Mana yang Hemat?    (Reasoning)       maks 6
     ├─ Misi 2 · Tarif Sewa Futsal        (Formulating)     maks 6
     ├─ Misi 3 · Tiket Pentas Seni        (Employing)       maks 6
     └─ Misi 4 · Cek Hitungan Candra      (Interpreting)    maks 6
                                                    Total maks 24
```

**Urutan buka kunci:**
- L1 selalu terbuka.
- L(n+1) terbuka setelah L(n) selesai.
- **Mode Misi terbuka setelah L2 selesai.** Siswa juga boleh langsung masuk Mode Misi dengan konfirmasi; data ini dicatat untuk penelitian.
- Misi dikerjakan berurutan dari M1 ke M4. Peneliti bisa mengatur urutan acak lewat konfigurasi untuk mengontrol efek urutan.

## 3. Alur satu misi

```
Baca soal (penanda informasi aktif)
   │
   ▼
Tahap 1 ─▶ Tahap 2 ─▶ … ─▶ Tahap n ─▶ Layar Hasil
   │ setiap tahap bisa terdiri dari 1–3 layar (satu tugas per layar)
   │ di setiap layar: [Petunjuk] [Periksa]; alat bantu muncul sesuai tahap
   ▼
Panel Ringkasan bertambah setiap kali layar dijawab benar
```

## 4. Aturan penilaian

### 4.1 Skor rubrik (untuk penelitian, mengikuti kisi-kisi)

Setiap tahap punya skor maksimum sesuai kisi-kisi. Tahap yang bernilai 2 dibagi menjadi 2 layar yang masing-masing bernilai 1.

| Kejadian di sebuah layar | Skor layar |
|---|---|
| Benar tanpa petunjuk, atau dengan petunjuk tingkat 1–2 | **penuh** |
| Siswa membuka petunjuk tingkat 3 (jawaban langkah ditampilkan) | **0** |
| Siswa menekan "Lewati" | **0** |

- **Percobaan tidak dibatasi** dan **tidak mengurangi skor rubrik**, tetapi jumlah percobaan dicatat. Setelah 3 kali salah, tombol Petunjuk berkedip lembut sekali sebagai pengingat (bukan animasi berulang).
- Petunjuk tingkat 1–2 tidak mengurangi skor rubrik karena fungsinya scaffolding yang diminta siswa (GL03). Penggunaannya tetap dicatat dan memengaruhi bintang.

> **Keputusan yang bisa diubah peneliti** (`backend/config.py`): `PENALTI_PETUNJUK = {1: 0, 2: 0, 3: 1.0}` (proporsi skor yang hilang) dan `HITUNG_PERCOBAAN_PERTAMA = False`. Jika ingin skor "murni tanpa bantuan", aktifkan `HITUNG_PERCOBAAN_PERTAMA` sehingga hanya jawaban benar pada percobaan pertama yang mendapat skor.

### 4.2 Bintang (untuk motivasi siswa)

| Bintang | Syarat |
|---|---|
| ★★★ | Skor 6/6 dan petunjuk maksimal tingkat 1 |
| ★★☆ | Skor ≥ 4/6 |
| ★☆☆ | Misi diselesaikan |

### 4.3 Lencana

| Lencana | Syarat | Kebiasaan yang didorong |
|---|---|---|
| **Mandiri** | Menyelesaikan satu misi tanpa petunjuk | Kemandirian |
| **Pemeriksa Teliti** | Memakai Cek Jawaban sebelum menekan Periksa di 3 misi | Verifikasi (GL02) |
| **Penerjemah Andal** | Model persamaan benar pada percobaan pertama di 3 misi | Pemodelan (IL01) |
| **Penjelas Hebat** | Mengisi alasan teks bebas di Misi 1 dan 4 | Menjelaskan (GL04) |

## 5. Rancangan layar per misi

Keterangan alat bantu: **PS** = Penerjemah Soal, **PK** = Penyelaras Koefisien, **TM** = Tips Metode, **CJ** = Cek Jawaban.
Isi soal, kunci, dan teks petunjuk lengkap ada di `BANK_SOAL.md`.

### Misi 1: Toko Mana yang Hemat? (Mathematical Reasoning), maksimum 6

| Tahap (skor) | Layar | Tugas siswa | Jenis input | Alat |
|---|---|---|---|---|
| 1 (1) | 1a | Pilih rencana penyelesaian yang tepat | Pilihan ganda (4) | — |
| 2 (2) | 2a (1) | Susun model SPLDV harga di Toko A | InputPersamaan ×2 | PS |
| | 2b (1) | Tentukan harga 1 buku (x) dan 1 pensil (y), lalu total 3 buku + 3 pensil di Toko A dan Toko B | Isian angka ×4 (bisa di 2 sub-layar) | TM, PK, CJ |
| 3 (1) | 3a | Bandingkan total: A < B, A = B, atau A > B | Pilihan (3) | — |
| 4 (1) | 4a | Keputusan: Toko A / Toko B / Boleh di mana saja | Pilihan (3) | — |
| 5 (1) | 5a | Pilih alasan matematis yang tepat (+ teks bebas opsional) | Pilihan ganda (4) + teks | — |

### Misi 2: Tarif Sewa Futsal (Formulating Situations Mathematically), maksimum 6

| Tahap (skor) | Layar | Tugas siswa | Jenis input | Alat |
|---|---|---|---|---|
| 1 (1) | 1a | Tandai data diketahui dan ditanya, lalu tetapkan variabel a = biaya admin dan b = biaya per jam | Ketuk segmen + pasangkan variabel | PS |
| 2 (1) | 2a | Susun dua persamaan (dalam a dan b) | InputPersamaan ×2 | PS |
| 3 (1) | 3a | Eliminasi a, lalu tentukan b | Pilih operasi + isian | PK |
| 4 (1) | 4a | Substitusi b dan tentukan a | Isian | CJ |
| 5 (1) | 5a | Lengkapi formula `Y = [ ] + [ ]x` | Isian ×2 | — |
| 6 (1) | 6a | Pilih kalimat kesimpulan yang tepat (arti 30.000 dan 50.000) | Pilihan ganda | — |

### Misi 3: Tiket Pentas Seni (Employing Concepts, Facts & Procedures), maksimum 6

| Tahap (skor) | Layar | Tugas siswa | Jenis input | Alat |
|---|---|---|---|---|
| 1 (1) | 1a | Susun model (bentuk sederhana `5x + 3y = 890` juga diterima) | InputPersamaan ×2 | PS |
| 2 (2) | 2a (1) | Samakan koefisien y: pilih pengali dan operasi | Isian pengali + pilih jumlah/kurang | PK, TM |
| | 2b (1) | Hitung x | Isian | — |
| 3 (2) | 3a (1) | Pilih persamaan untuk substitusi dan tulis bentuknya `70 + y = 250` | Isian | — |
| | 3b (1) | Hitung y dan periksa dengan Cek Jawaban | Isian + CJ | CJ |
| 4 (1) | 4a | Kesimpulan: banyak tiket VIP dan Reguler | Isian dengan satuan "lembar" | — |

### Misi 4: Cek Hitungan Candra (Interpreting, Applying & Evaluating), maksimum 6

| Tahap (skor) | Layar | Tugas siswa | Jenis input | Alat |
|---|---|---|---|---|
| 1 (1) | 1a | Susun model harga apel (x) dan jeruk (y) | InputPersamaan ×2 | PS |
| 2 (1) | 2a | Eliminasi x (pengali ×2 dan ×3), lalu tentukan y | Pengali + isian | PK |
| 3 (1) | 3a | Tentukan x, lalu nilai: "Apakah harga hitungan Candra benar?" | Isian + Ya/Tidak | CJ |
| 4 (1) | 4a | Hitung biaya 2 kg apel + 2 kg jeruk | Isian | — |
| 5 (1) | 5a | Bandingkan dengan uang Rp100.000: kurang / pas / lebih | Pilihan (3) | — |
| 6 (1) | 6a | Setuju atau tidak dengan Candra, lalu pilih alasan (+ teks bebas) | Pilihan + pilihan alasan + teks | — |

### Catatan implementasi (versi 1)

Pembagian layar di kode (`backend/data/soal/M*.json`) sedikit lebih rinci daripada tabel di atas. Skor total tetap 6 per misi. Layar bernilai 0 adalah **langkah antara**: dicatat untuk penelitian, tetapi tidak dinilai.

| Misi | Layar bernilai 0 (langkah antara) |
|---|---|
| M1 | 2c: total harga di Toko A dan B (nilai x dan y di 2b bernilai 1) |
| M2 | 1a: menandai informasi (skor tahap 1 ada di 1b, memilih arti a dan b); 3a: pengali eliminasi (skor tahap 3 ada di 3b, nilai b) |
| M3 | tidak ada |
| M4 | 2a: pengali eliminasi; 3b: menilai apakah harga Candra benar |

Alat **Penyelaras Koefisien** tidak muncul di layar pengali pada Mode Misi karena alat itu akan langsung memberikan jawabannya. Di Mode Latihan alat ini tersedia.

## 6. Mode Belajar (bukan untuk skor penelitian)

| ID | Isi | Tujuan | Fitur |
|---|---|---|---|
| C1 | Contoh lengkap: soal buku-pensil, metode gabungan | Worked example | Kontrol tempo, highlight otomatis |
| C2 | Contoh lengkap: soal umur | Contoh pemodelan yang lebih sulit (EL03) | Kontrol tempo |
| C3 | Contoh dengan bagian kosong (fading) | Transisi ke mandiri | Kontrol tempo + isian |
| SIM | Simulasi belanja: pilih barang ke 2 keranjang, harga total diketahui, persamaan terbentuk otomatis | Konkret ke simbol (GL01) | Label koefisien dan variabel |
| L1 | `−x + y = 70`, `2x − y = 30` | Prosedur simbolik (soal pemicu 1) | PK, CJ |
| L2 | Buku dan pensil (soal pemicu 2) | Cerita sederhana | PS, PK, CJ |
| L3 | Umur ibu dan Sahi (soal pemicu 3) | Cerita kompleks, perlu menyusun ulang bentuk persamaan | PS, PK, CJ |

## 7. Layar Hasil Misi

- Skor rubrik (contoh: 5/6), bintang, dan lencana baru.
- Daftar tahap dengan tanda ✓ (mandiri), 💡 (dengan petunjuk), atau 👁 (jawaban dilihat).
- Satu kalimat refleksi: "Bagian yang perlu dilatih: *menyusun model*. Coba Latihan L3."
- Tombol: **Misi berikutnya** · **Ulangi misi** (ulangan dicatat sebagai percobaan kedua dan tidak menimpa skor pertama).
