# DESIGN.md: Desain Antarmuka

Dokumen ini menjelaskan bagaimana tampilan aplikasi dirancang untuk **menekan beban kognitif ekstraneus**, **mengelola beban intrinsik**, dan **mendorong beban germane**. Prinsipnya mengacu pada Cognitive Load Theory (Sweller) dan prinsip multimedia (Mayer).

## 1. Prinsip desain

| Prinsip | Penerapan di aplikasi | Dasar dari wawancara |
|---|---|---|
| **Segmentasi** | Satu langkah satu layar; contoh soal dibagi menjadi beberapa langkah | DS03, IL04 |
| **Pacing oleh siswa** | Tombol Ulang / Jeda / Lanjut, tanpa autoplay | EL04 |
| **Signaling (penandaan)** | Kata kunci dan angka penting diberi highlight; warna variabel konsisten | EL02, EL05 |
| **Koherensi** | Tanpa hiasan, maskot, atau animasi yang tidak berfungsi | DS03 |
| **Mengurangi beban memori kerja** | Panel Ringkasan Langkah menyimpan hasil langkah sebelumnya | Matriks: "lupa menghilangkan variabel" |
| **Worked example lalu fading** | Contoh lengkap, lalu soal yang sebagian langkahnya diisi, lalu soal mandiri | EL03, GL05 |
| **Scaffolding bertahap** | Petunjuk 3 tingkat | GL03, DS01 |
| **Konkret ke abstrak** | Simulasi belanja (benda) diubah menjadi simbol (x, y) | GL01 |

## 2. Token desain

```css
:root {
  /* Warna dasar: tenang, kontras tinggi */
  --bg: #FAFAF7;
  --surface: #FFFFFF;
  --text: #1F2328;
  --text-muted: #5B6470;
  --border: #D8DCE1;
  --accent: #2F6FEB;          /* tombol utama, satu-satunya warna aksen */

  /* Warna variabel: harus konsisten di semua layar */
  --var-1: #1D6FD8;           /* x atau variabel pertama (biru) */
  --var-1-bg: #E3EEFC;
  --var-2: #C2410C;           /* y atau variabel kedua (oranye tua) */
  --var-2-bg: #FCEBDD;

  /* Penanda soal cerita */
  --mark-data: #FFF3B0;       /* angka/data penting */
  --mark-tanya: #E6DDF9;      /* yang ditanyakan */

  /* Umpan balik */
  --ok: #1A7F37;   --ok-bg: #E6F4EA;
  --err: #B42318;  --err-bg: #FDECEA;

  /* Tipografi dan ukuran */
  --font: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --font-math: "Cambria Math", "STIX Two Math", serif;
  --fs-body: 18px;  --fs-soal: 19px;  --fs-h: 22px;
  --tap: 48px;                /* tinggi minimum target sentuh */
  --radius: 10px;
  --gutter: 16px;
}

@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #14171A; --surface: #1C2024; --text: #E8EAED; --text-muted: #9AA3AD;
    --border: #343A40; --var-1: #6EA8FE; --var-1-bg: #1B2B44;
    --var-2: #F59E63; --var-2-bg: #3A2416; --mark-data: #4A4220; --mark-tanya: #352C4D;
  }
}
```

Aturan warna:
- Hanya **satu warna aksen** untuk aksi utama.
- Warna variabel **tidak pernah dipakai untuk hal lain**, sehingga siswa belajar bahwa "biru berarti buku (x)".
- Warna selalu disertai label teks atau ikon, karena ada siswa yang buta warna.

## 3. Tata letak layar langkah (mobile, 360 px)

```
┌──────────────────────────────┐
│ ← Misi 3 · Tahap 2 dari 4     │  Header: posisi dan kembali
│ ●●○○  (indikator tahap)       │
├──────────────────────────────┤
│ ▸ Ringkasan (bisa dilipat)    │  Panel Ringkasan Langkah
│  (1) x + y = 250              │  hasil tahap sebelumnya
│  (2) 5x + 3y = 890            │
├──────────────────────────────┤
│ Soal (bisa dilipat)           │  teks soal + highlight
├──────────────────────────────┤
│ TUGAS SEKARANG:               │  satu instruksi singkat
│ Samakan koefisien y.          │
│ Kalikan pers. (1) dengan [ ]  │  input terstruktur
│                               │
├──────────────────────────────┤
│ [💡 Petunjuk]   [Periksa ✓]   │  aksi; tombol utama di kanan
│ ┌─ keypad 0–9  −  ⌫ ─┐        │  keypad muncul saat input aktif
└──────────────────────────────┘
```

Di layar lebar (≥ 900 px): soal dan ringkasan pindah ke kolom kiri, sedangkan tugas sekarang ada di kolom kanan. Lebar maksimum isi 1100 px.

## 4. Komponen

| Komponen | Fungsi | Catatan |
|---|---|---|
| **TeksSoal** | Menampilkan soal cerita per segmen | Mode Belajar: highlight otomatis. Misi: siswa mengetuk segmen penting, lalu sistem mengonfirmasi |
| **PenerjemahSoal** | Kartu "kalimat ke simbol": `4 buku` menjadi `4x`, ditempatkan ke slot persamaan | Fitur kunci untuk IL01/IL03 |
| **InputPersamaan** | Template `[ ]x + [ ]y = [ ]` | Siswa tidak mengetik bebas sehingga beban sintaks berkurang; koefisien negatif diisi dengan tombol − |
| **KeypadAngka** | Keypad 0–9, −, ⌫, 000 | Keyboard bawaan HP sering tidak menyediakan tombol minus untuk input numerik |
| **PanelRingkasan** | Daftar hasil langkah yang sudah benar | Selalu terlihat (dilipat menjadi 1 baris di HP) |
| **TombolPetunjuk** | Petunjuk tingkat 1 lalu 2 lalu 3 | Tingkat 3 meminta konfirmasi: "Lihat jawaban langkah ini? Skor tahap ini jadi 0." |
| **PenyelarasKoefisien** | Menampilkan KPK koefisien, pengali, dan aturan tanda | "Tanda sama: kurangkan. Tanda beda: jumlahkan." |
| **TipsMetode** | Saran metode berdasarkan bentuk koefisien | Contoh: "Ada koefisien 1 pada y di pers. (2). Substitusi akan cepat." |
| **CekJawaban** | Memasukkan x dan y ke kedua persamaan dan menampilkan ruas kiri = ruas kanan | Membiasakan verifikasi (GL02) |
| **KontrolTempo** | ⟲ Ulang · ⏸ Jeda · Lanjut ▸ | Hanya di contoh soal (worked example) |
| **UmpanBalik** | Pesan benar/salah | Pesan salah menunjuk letak kesalahan, bukan hanya "Salah" |

## 5. Gaya umpan balik

- **Benar**: latar hijau muda dan teks "Tepat! [penjelasan 1 kalimat]". Tidak ada konfeti atau animasi besar.
- **Salah**: latar merah muda dan pesan yang spesifik, misalnya:
  - "Persamaan (1) sudah benar. Cek lagi persamaan (2): berapa banyak pensil yang dibeli Ali?"
  - "Koefisien y sudah sama dan tandanya sama. Sebaiknya dijumlah atau dikurang?"
- Hindari kata yang menghakimi ("kamu salah lagi"). Gunakan "Belum tepat, coba lihat …".

## 6. Bahasa dan istilah

Gunakan istilah yang sama di semua layar. Daftar istilah baku:

| Pakai | Jangan campur dengan |
|---|---|
| variabel | peubah, huruf |
| koefisien | angka di depan |
| konstanta | angka sendiri |
| persamaan (1), persamaan (2) | rumus 1, baris atas |
| eliminasi, substitusi, gabungan | hilangkan, masukkan |
| model matematika | rumus, kalimat matematika |

Instruksi ditulis maksimal 2 kalimat dan diawali kata kerja ("Tentukan…", "Pilih…", "Isi…").

## 7. Elemen game (dibatasi agar tidak menambah beban)

- Peta misi sederhana berupa 4 kartu dengan status terkunci / tersedia / selesai dan bintang.
- Bintang (0–3) dan lencana teks seperti "Mandiri" dan "Pemeriksa Teliti".
- **Tidak ada**: nyawa, hitung mundur, papan peringkat antarsiswa, efek suara otomatis, maupun maskot animasi.

## 8. Aksesibilitas dan perangkat

- Target sentuh minimal 48 × 48 px; tombol utama dapat dijangkau jempol (bagian bawah).
- Kontras teks minimal 4.5:1 (WCAG AA).
- Matematika ditulis dengan HTML dan CSS biasa (`<var>`, `<sup>`), tanpa pustaka berat, agar cepat dimuat di HP murah.
- Ukuran halaman awal di bawah 300 KB dan tetap bisa dipakai di jaringan 3G.
- Mendukung `prefers-reduced-motion` dan `prefers-color-scheme`.
