# Algorika (aplikasi Streamlit)

Aplikasi web interaktif untuk materi Sistem Persamaan Linear Dua Variabel (SPLDV) dengan pendekatan **Rigorous Mathematical Thinking (RMT)** (Kinard & Kozulin, 2008). Seluruh aplikasi ada di satu file: `app.py`.

Aplikasi ini terpisah dari aplikasi Flask di folder `backend/` dan `frontend/`.

## Menjalankan

```bash
# dari folder proyek
python -m venv .venv                      # sekali saja (lewati jika .venv sudah ada)
.venv\Scripts\activate                    # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r streamlit_rmt/requirements.txt
streamlit run streamlit_rmt/app.py
```

Browser akan terbuka di `http://localhost:8501`. Untuk membukanya di HP pada Wi-Fi yang sama, gunakan alamat "Network URL" yang tampil di terminal.

Tes: `pytest streamlit_rmt/test_app.py`

## Isi aplikasi dan penerapan RMT

| Menu | Isi | Penerapan RMT |
|---|---|---|
| 1. Materi Pembelajaran | Bentuk umum, 3 jenis penyelesaian, 4 metode (grafik, substitusi, eliminasi, campuran) dengan `st.latex` | Fase 1–2: alat psikologis (tabel, simbol, grafik), pertanyaan mediasi, label fungsi kognitif di setiap langkah, satu contoh yang sama untuk membandingkan keempat metode |
| 2. Eksplorasi Grafik & Kalkulator | Atur a₁, b₁, c₁, a₂, b₂, c₂; grafik Plotly real-time; status penyelesaian dan titik potong | Fase 2: tabel perbandingan koefisien, lalu **hipotesis** (grafik disembunyikan sampai siswa menebak), uji dengan grafik, dan verifikasi substitusi |
| 3. Latihan Soal Mandiri | 7 soal (konsep, prosedur, soal cerita), Periksa Jawaban, Lihat Pembahasan | Fase 3: orientasi bermediasi, petunjuk 3 tingkat, umpan balik berbasis verifikasi ("memenuhi persamaan (1) tetapi tidak (2)"), refleksi dan checklist berpikir teliti |
| 4. Kuis Evaluasi | Nama siswa, 10 soal pilihan ganda, timer hitung mundur, Selesai Kuis, rapor dan pembahasan, unduh rapor | Rapor menampilkan penguasaan per **fungsi kognitif** |

| 5. Tanya Kak Sely | Asisten AI (Google Gemini, paket gratis) untuk tanya jawab SPLDV, dan **cek jawaban dari foto** (unggah atau kamera) | Kak Sely menuntun dengan pertanyaan dan petunjuk, tidak langsung memberi jawaban akhir |

## Mengatur API key untuk Kak Sely (gratis)

1. Buka https://aistudio.google.com/apikey, masuk dengan akun Google, lalu klik **Create API key**. Tidak perlu kartu kredit.
2. Salin `.streamlit/secrets.toml.example` menjadi `.streamlit/secrets.toml` (di folder proyek, tempat perintah `streamlit run` dijalankan), lalu isi `GEMINI_API_KEY = "AIza..."`. File ini sudah masuk `.gitignore`.
   - Alternatif: variabel lingkungan `$env:GEMINI_API_KEY="AIza..."` (PowerShell), atau isi sementara di **Tanya Kak Sely → ⚙️ Pengaturan untuk guru**.

Model yang dipakai: `gemini-3.6-flash` (gratis di paket gratis Gemini API dan bisa membaca foto). Bisa diganti lewat konstanta `MODEL_AI` di `app.py`.

Batasan paket gratis:
- Ada batas jumlah permintaan per menit dan per hari (lihat di https://aistudio.google.com/rate-limit). Jika terlampaui, Kak Sely menampilkan pesan "batas pemakaian gratis tercapai".
- Pada paket gratis, Google dapat memakai isi pertanyaan dan foto untuk meningkatkan produknya. Karena itu aplikasi mengingatkan siswa agar tidak mengirim wajah, nama lengkap, atau data pribadi. Foto tidak disimpan oleh aplikasi.

Catatan desain:
- Timer bisa dimatikan sebelum kuis dimulai. Wawancara (EL02) menunjukkan siswa merasa waktunya habis untuk memahami soal, jadi guru bisa memilih kuis tanpa tekanan waktu.
- Nama siswa hanya tampil di rapor dan tidak disimpan di server.
- Semua perhitungan memakai `fractions.Fraction` (eksak), sehingga titik potong pecahan ditampilkan tepat, misalnya ½.
