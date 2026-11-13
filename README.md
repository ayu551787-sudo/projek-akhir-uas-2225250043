# Jelajah SPLDV

Aplikasi web pembelajaran **Sistem Persamaan Linear Dua Variabel (SPLDV)** untuk siswa SMP (kelas VIII–IX). Aplikasi ini dirancang untuk **mengurangi beban kognitif (cognitive load)** siswa sehingga kemampuan **literasi matematika (mathematical literacy)** mereka berkembang. Aplikasi dapat dibuka dari browser **smartphone** maupun **laptop/PC**.

> Nama "Jelajah SPLDV" masih nama kerja dan dapat diganti.

## Latar belakang

Perancangan aplikasi ini didasarkan pada wawancara analisis kebutuhan dengan siswa S01 (kelas IX, 6 November 2026). Temuan utamanya:

| Temuan wawancara | Jenis beban | Jawaban aplikasi |
|---|---|---|
| Sulit memodelkan soal cerita menjadi persamaan (IL01, IL03, EL05) | Intrinsik | Fitur **Penerjemah Soal** dan latihan berjenjang |
| Bingung harus menjumlah atau mengurangi saat eliminasi (IL04, IL05) | Intrinsik | **Penyelaras Koefisien**: petunjuk pengali dan aturan tanda |
| Kalimat soal membingungkan, waktu habis untuk memahami soal (EL02) | Ekstraneus | **Penanda informasi penting**, tanpa batas waktu |
| Penjelasan guru terlalu cepat (EL04) | Ekstraneus | **Kontrol tempo**: Ulang / Jeda / Lanjut |
| Animasi dan warna ramai mengganggu (DS03) | Ekstraneus | Tampilan sederhana, **satu langkah satu layar** |
| Terbantu oleh petunjuk bertahap (GL03, DS01) | Germane | **Petunjuk 3 tingkat**, tidak langsung memberi jawaban |
| Terbantu oleh simulasi kegiatan sehari-hari (GL01) | Germane | **Mode Simulasi Belanja** |
| Belum biasa memeriksa jawaban (GL02) | Germane | **Cek Jawaban** otomatis dengan substitusi balik |

Penjelasan lengkap ada di [docs/KEBUTUHAN.md](docs/KEBUTUHAN.md).

## Fitur utama

1. **Mode Belajar**: contoh soal yang ditampilkan langkah demi langkah (tempo diatur siswa), simulasi belanja, dan latihan berjenjang yang diambil dari soal pemicu wawancara.
2. **Mode Misi (game)**: 4 misi sesuai kisi-kisi soal literasi matematika (Reasoning, Formulating, Employing, Interpreting). Setiap misi dinilai per tahap mengikuti rubrik, dengan skor maksimum 6 per misi dan 24 secara keseluruhan.
3. **Alat bantu**: Penerjemah Soal, Tips Memilih Metode, Penyelaras Koefisien, Cek Jawaban, dan Panel Ringkasan Langkah.
4. **Halaman Guru/Peneliti**: rekap skor, penggunaan petunjuk, dan log aktivitas yang dapat diekspor ke CSV untuk analisis penelitian.

## Teknologi

| Bagian | Bahasa | Kerangka/pustaka |
|---|---|---|
| Backend: API, pemeriksa jawaban, penilaian rubrik, basis data | **Python 3.11+** | Flask 3, SQLite, `fractions` (standar), pytest |
| Frontend: tampilan, interaksi, game | **JavaScript** (ES Modules) | Vanilla JS tanpa build step, HTML5, CSS3 |

Detail arsitektur dibahas di [docs/ARSITEKTUR.md](docs/ARSITEKTUR.md).

## Menjalankan aplikasi

```bash
# 1. Buat virtual environment (sekali saja)
python -m venv .venv
.venv\Scripts\activate          # Windows (PowerShell/CMD)
# source .venv/bin/activate     # macOS/Linux

# 2. Pasang dependensi (sekali saja)
pip install -r backend/requirements.txt

# 3. Jalankan server
python backend/app.py
# Terminal akan menampilkan dua alamat:
#   laptop : http://localhost:5000
#   HP     : http://<IP-laptop>:5000   (HP dan laptop harus di Wi-Fi/hotspot yang sama)

# 4. Jalankan pengujian
pytest backend/tests             # Python (logika SPLDV, bank soal, API)
cd frontend && node --test tests/   # JavaScript (format angka)
```

**PIN halaman guru** bawaannya `1234`. Ganti sebelum uji coba kelas:
`$env:GURU_PIN="pinrahasia"; python backend/app.py` (PowerShell) atau `GURU_PIN=pinrahasia python backend/app.py` (bash).

Data tersimpan di `backend/app.db` (SQLite). Hapus file itu untuk mengosongkan data uji coba.

### Alur penggunaan
1. Siswa masuk dengan kode (misalnya `S01`), tanpa nama.
2. **Mode Belajar**: Contoh 1–2, Simulasi Belanja, lalu Latihan 1 → 2 → 3.
3. **Mode Misi** terbuka setelah Latihan 2 selesai: Misi 1 → 4.
4. Guru membuka tautan "Halaman guru/peneliti" di beranda, memasukkan PIN, lalu mengekspor CSV.

## Peta dokumen

| File | Isi |
|---|---|
| [CLAUDE.md](CLAUDE.md) | Aturan dan konvensi untuk asisten AI (Claude Code) saat menulis kode |
| [DESIGN.md](DESIGN.md) | Desain antarmuka dan prinsip beban kognitif |
| [docs/KEBUTUHAN.md](docs/KEBUTUHAN.md) | Kebutuhan aplikasi yang ditelusuri dari hasil wawancara |
| [docs/ARSITEKTUR.md](docs/ARSITEKTUR.md) | Struktur folder, pembagian Python/JS, API, dan basis data |
| [docs/GAME.md](docs/GAME.md) | Desain game Mode Misi dan aturan penilaian |
| [docs/BANK_SOAL.md](docs/BANK_SOAL.md) | Isi soal, langkah, kunci jawaban, dan petunjuk |
| [docs/EVALUASI.md](docs/EVALUASI.md) | Cara menguji setiap fitur dan data yang dicatat |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Tahapan pengerjaan |

## Penyusun

Ayu Syarifatu Zahra (NIM 2225250043), Pendidikan Matematika, kelas 3B. Mata kuliah Algoritma Pemrograman.
