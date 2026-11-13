# Kebutuhan Aplikasi (Requirements)

Sumber: *Laporan Hasil Wawancara Analisis Kebutuhan, Materi SPLDV*. Siswa S01, kelas IX, 6 November 2026, durasi 40 menit, pewawancara Ayu Syarifatu Zahra.

## 1. Profil pengguna

**Pengguna utama**: siswa SMP kelas VIII–IX yang sudah atau sedang mempelajari SPLDV.
- Sudah mengenal variabel, konstanta, dan soal SPLDV simbolik sederhana (K01).
- Terbiasa dengan pola belajar penjelasan guru, mencatat, lalu latihan di depan kelas (K02).
- Mampu mengerjakan soal simbolik, tetapi **kesulitan pada soal cerita** (K03).
- Memakai HP untuk belajar. Wawancara pun dilakukan lewat video call di HP.

**Pengguna kedua**: guru atau peneliti yang melihat rekap skor dan log penggunaan fitur.

## 2. Ringkasan temuan berdasarkan kode

| Kode | Inti temuan | Implikasi |
|---|---|---|
| K01–K03 | Soal dasar dikenali; soal cerita membingungkan | Mulai dari soal simbolik, lalu naik ke soal cerita |
| IL01, IL03 | Tidak bisa memodelkan cerita menjadi persamaan, sehingga tidak bisa lanjut | Penerjemah Soal dan petunjuk yang menjamin siswa bisa lanjut |
| IL02, EL01, EL03 | Contoh di kelas sederhana, soal ujian lebih sulit | Latihan berjenjang dari mudah ke sulit (fading) |
| IL04, IL05 | Salah tanda dan bingung menjumlah atau mengurangi saat eliminasi | Penyelaras Koefisien dan aturan tanda |
| EL02 | Kalimat soal memusingkan, waktu habis untuk memahami | Penanda informasi dan tanpa timer |
| EL04 | Penjelasan terlalu cepat | Kontrol tempo |
| EL05 | Mencari angka tanpa memahami soal | Tahap "Diketahui/Ditanya" wajib sebelum menghitung |
| GL01 | Paham setelah ada model; simulasi jual-beli membantu | Mode Simulasi Belanja |
| GL02 | Memastikan ada nilai x dan y di akhir | Cek Jawaban dengan substitusi balik |
| GL03 | Petunjuk sedikit demi sedikit membantu | Petunjuk 3 tingkat |
| GL04 | Menjelaskan ulang membuat paham | Tahap "jelaskan alasan" di Misi |
| GL05 | Langkah mudah, pola soal membingungkan | Tips Metode dan pengenalan pola |
| DS01 | Usulan: simulasi sehari-hari, petunjuk bertahap | — |
| DS02 | Usulan: pola soal dijelaskan, bukan hanya rumus | Penjelasan "mengapa" di setiap petunjuk tingkat 2 |
| DS03 | Usulan: tanpa animasi atau warna ramai, satu langkah satu layar | Prinsip dasar desain |

## 3. Kebutuhan fungsional

Prioritas: **W** = wajib (MVP), **P** = penting, **O** = opsional.

| ID | Kebutuhan | Prioritas | Sumber | Jenis beban |
|---|---|---|---|---|
| F01 | **Penerjemah Soal**: siswa mengetuk frasa soal ("4 buku") lalu menempatkannya menjadi suku persamaan (`4x`) | W | IL01, IL03, Matriks 1 | Intrinsik |
| F02 | **Latihan berjenjang**: simbolik, lalu cerita sederhana, lalu cerita kompleks (umur) | W | IL02, EL01, EL03 | Intrinsik |
| F03 | **Satu langkah satu layar** dengan **Panel Ringkasan** langkah yang sudah selesai | W | DS03, Matriks 2 | Memori kerja |
| F04 | **Penanda informasi penting**: highlight data (kuning) dan pertanyaan (ungu) | W | EL02, Matriks 3 | Ekstraneus |
| F05 | **Tampilan sederhana** tanpa animasi atau hiasan | W | DS03, Matriks 4 | Ekstraneus |
| F06 | **Kontrol tempo** Ulang / Jeda / Lanjut pada contoh soal | W | EL04, Matriks 5 | Ekstraneus |
| F07 | **Mode Simulasi Belanja**: memilih barang ke keranjang, lalu persamaan terbentuk dengan label koefisien dan variabel | P | GL01, DS01, Matriks 6 | Germane |
| F08 | **Tips Memilih Metode** berdasarkan bentuk koefisien | P | Matriks 7 | Intrinsik |
| F09 | **Cek Jawaban**: substitusi balik otomatis ke kedua persamaan | W | GL02, Matriks 8 | Germane |
| F10 | **Penyelaras Koefisien**: petunjuk pengali (KPK) dan aturan operasi tanda | W | IL04, IL05, Matriks 9 | Intrinsik |
| F11 | **Petunjuk 3 tingkat**: (1) arahan, (2) pola/alasan, (3) jawaban langkah | W | GL03, DS01, DS02 | Germane |
| F12 | **Mode Misi (game)**: 4 misi sesuai kisi-kisi dan skor rubrik per tahap | W | Kisi-kisi | Asesmen |
| F13 | **Tahap "jelaskan alasan"** (pilihan alasan + teks bebas opsional) | P | GL04 | Germane |
| F14 | **Login dengan kode siswa** (tanpa kata sandi) dan sesi tersimpan | W | Penelitian | — |
| F15 | **Log peristiwa** (petunjuk, ulang, durasi, percobaan) | W | Matriks: kolom "cara menguji" | — |
| F16 | **Halaman Guru**: rekap dan ekspor CSV, dilindungi PIN | P | Penelitian | — |
| F17 | **Lanjutkan dari terakhir**: progres tidak hilang saat HP terkunci atau browser ditutup | P | Konteks HP | — |
| F18 | Mode gelap otomatis | O | — | — |
| F19 | Bisa dipasang ke layar utama HP (PWA) | O | — | — |

## 4. Kebutuhan non-fungsional

| ID | Kebutuhan |
|---|---|
| N01 | Responsif mulai lebar 360 px; nyaman dipakai dengan satu tangan |
| N02 | Halaman pertama di bawah 300 KB dan tampil dalam waktu kurang dari 3 detik di jaringan 3G |
| N03 | Berjalan di Chrome Android 90+, Safari iOS 14+, Chrome/Edge/Firefox desktop terbaru |
| N04 | Kunci jawaban tidak terlihat di kode sumber halaman (diperiksa di server) |
| N05 | Data siswa hanya berupa kode anonim; tidak ada nama asli atau foto |
| N06 | Perhitungan eksak (pecahan), tanpa galat pembulatan |
| N07 | Bahasa Indonesia sederhana, dengan instruksi maksimal 2 kalimat |

## 5. Ketertelusuran: matriks analisis wawancara ke fitur

| Baris matriks wawancara | Fitur | Cara menguji (lihat `EVALUASI.md`) |
|---|---|---|
| Sulit mencari pola/model matematika | F01, F02 | Siswa menjelaskan kembali hubungan x dan y |
| Lupa menghilangkan salah satu variabel | F03 | Frekuensi langkah yang terlewat |
| Soal membingungkan (bahasa) | F04 | Waktu dan ketepatan menemukan data relevan |
| Hiasan dan animasi mengganggu | F05 | Wawancara kejelasan tampilan |
| Penjelasan terlalu cepat | F06 | Frekuensi tombol Ulang |
| Memahami lewat simulasi sehari-hari | F07 | Kualitas penjelasan sebelum dan sesudah simulasi |
| Ragu memilih eliminasi atau substitusi | F08 | Ketepatan pilihan metode |
| Tidak tahu cara mengecek jawaban | F09 | Frekuensi Cek Jawaban dipakai secara mandiri |
| Bingung menentukan pengali | F10 | Kesalahan pengali di latihan bertahap |

## 6. Batasan ruang lingkup (tidak dikerjakan di versi 1)

- Input persamaan dalam bentuk teks bebas atau tulisan tangan. Versi 1 memakai template terstruktur.
- Metode grafik untuk SPLDV.
- Akun kelas dan multi-guru.
- Penilaian otomatis untuk jawaban esai bebas. Teks alasan bebas hanya disimpan agar dinilai guru.
