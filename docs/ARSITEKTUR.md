# Arsitektur Aplikasi

## 1. Gambaran umum

```
 Browser (HP / laptop)                        Server (Python)
┌──────────────────────────┐   HTTP/JSON   ┌───────────────────────────────┐
│ JavaScript (ES Modules)  │ ────────────▶ │ Flask (app.py)                │
│ - layar & komponen       │               │  ├─ routes/  (API)            │
│ - keypad, highlight      │ ◀──────────── │  ├─ spldv/   (logika mat.)    │
│ - state progres (lokal)  │               │  │   solver, checker,          │
│ - antrean log            │               │  │   helper, scoring           │
└──────────────────────────┘               │  ├─ data/soal/*.json          │
                                           │  └─ SQLite (app.db)           │
                                           └───────────────────────────────┘
```

Satu proses Flask melayani **file statis frontend** sekaligus **API**, sehingga deploy cukup satu server tanpa CORS.

**Alasan memilih Python + JavaScript:**
- **Python** cocok untuk logika matematika yang harus tepat dan mudah diuji (modul `fractions`, pytest). Python juga menyimpan kunci jawaban di server.
- **JavaScript** dibutuhkan untuk interaksi cepat di browser (ketuk, keypad, highlight) tanpa memuat ulang halaman.
- Tanpa framework atau bundler JS, kode lebih mudah dipahami untuk tugas mata kuliah Algoritma Pemrograman dan halaman tetap ringan di HP.

## 2. Struktur folder

```
projek uas ayu/
├── README.md, CLAUDE.md, DESIGN.md
├── docs/                         # dokumen perencanaan
├── backend/
│   ├── app.py                    # membuat app Flask, mendaftarkan route, melayani frontend/
│   ├── config.py                 # path DB, PIN guru (dari variabel lingkungan)
│   ├── requirements.txt          # flask, pytest
│   ├── db.py                     # koneksi SQLite & pembuatan tabel
│   ├── routes/
│   │   ├── soal.py               # GET daftar & detail soal (tanpa kunci)
│   │   ├── sesi.py               # POST sesi, GET progres
│   │   ├── cek.py                # POST cek-langkah, petunjuk, cek-jawaban, bantu-eliminasi
│   │   ├── log.py                # POST log peristiwa
│   │   └── guru.py               # rekap & ekspor CSV
│   ├── spldv/
│   │   ├── solver.py             # menyelesaikan SPLDV (Cramer, Fraction)
│   │   ├── checker.py            # memeriksa persamaan setara, nilai, pilihan
│   │   ├── helper.py             # pengali KPK, aturan tanda, tips metode
│   │   ├── scoring.py            # skor rubrik per tahap
│   │   └── parse.py              # parsing angka format Indonesia
│   ├── data/soal/
│   │   ├── latihan_L1.json … L3.json
│   │   ├── contoh_C1.json …      # worked example
│   │   └── misi_M1.json … M4.json
│   └── tests/
│       ├── test_solver.py, test_checker.py, test_helper.py
│       ├── test_parse.py, test_scoring.py
│       ├── test_bank_soal.py     # memvalidasi semua kunci soal
│       └── test_api.py           # tes route dengan Flask test client
└── frontend/
    ├── index.html                # satu halaman (SPA sederhana, routing pakai hash)
    ├── css/style.css             # token + komponen (lihat DESIGN.md)
    ├── js/
    │   ├── main.js               # router hash: #/beranda, #/misi/M1, …
    │   ├── api.js                # fetch wrapper ke /api
    │   ├── state.js              # sesi & progres (localStorage sebagai cadangan)
    │   ├── logger.js             # antrean log, kirim setiap 10 dtk / saat pindah layar
    │   ├── teks.js               # semua string UI
    │   ├── format.js             # format & parse angka id-ID
    │   ├── screens/
    │   │   ├── beranda.js, masuk.js, petaMisi.js
    │   │   ├── langkah.js        # layar generik "satu langkah"
    │   │   ├── contohSoal.js     # worked example + kontrol tempo
    │   │   ├── simulasi.js       # simulasi belanja
    │   │   └── hasil.js          # skor & bintang akhir misi
    │   └── components/
    │       ├── teksSoal.js, penerjemah.js, inputPersamaan.js
    │       ├── keypad.js, panelRingkasan.js, petunjuk.js
    │       ├── penyelaras.js, tipsMetode.js, cekJawaban.js
    │       └── umpanBalik.js
    └── tests/format.test.js      # node --test
```

### Catatan implementasi (versi 1)

Struktur yang benar-benar dibuat sedikit berbeda dari rencana di atas:
- `backend/routes/` berisi `siswa.py` (sesi, progres, soal, contoh, main), `cek.py` (cek-langkah, petunjuk, lewati, alat), `log.py`, `guru.py`, dan `util.py`.
- `backend/layanan.py` memuat logika hasil misi, progres, dan lencana (memakai DB, terpisah dari route).
- `backend/soal_repo.py` memuat bank soal dan menghapus kunci jawaban sebelum soal dikirim ke browser.
- `backend/data/contoh/C1.json, C2.json` berisi contoh soal (worked example).
- Layar frontend: `screens/masuk.js, beranda.js, daftar.js` (Mode Belajar + Peta Misi), `kerjakan.js` (mesin langkah), `hasil.js, contoh.js, simulasi.js, guru.js`. Komponen: `keypad.js, inputLayar.js, teksSoal.js, alat.js, sheet.js, layout.js`.
- Satu "pengerjaan" disimpan di tabel `main` (bukan `sesi`), sehingga siswa bisa mengulang misi tanpa menimpa skor pertama. Tabel `jawaban` menggantikan `jawaban_tahap`, dan tabel `petunjuk` mencatat setiap petunjuk yang dibuka.
- Endpoint alat bantu berada di `/api/alat/cek-jawaban`, `/api/alat/bantu-eliminasi`, dan `/api/alat/tips-metode`.

## 3. Logika matematika (Python, `backend/spldv/`)

Persamaan direpresentasikan sebagai tuple `(a, b, c)` yang berarti `a·x + b·y = c`, dengan semua nilai bertipe `Fraction`.

### 3.1 Solver

```python
def solve(e1, e2) -> tuple[Fraction, Fraction] | None:
    a1, b1, c1 = e1; a2, b2, c2 = e2
    d = a1*b2 - a2*b1
    if d == 0:
        return None          # tidak punya solusi tunggal
    x = (c1*b2 - c2*b1) / d
    y = (a1*c2 - a2*c1) / d
    return x, y
```

### 3.2 Pemeriksa model (persamaan setara)

Persamaan siswa `(a, b, c)` **setara** dengan kunci `(p, q, r)` jika vektornya sebanding dan tidak nol:
`a*q == b*p` **dan** `a*r == c*p` **dan** `b*r == c*q`, serta `(a, b, c) != (0, 0, 0)`.

Sepasang persamaan siswa benar jika setara dengan pasangan kunci **dalam urutan apa pun**. Pemeriksa mengembalikan status per persamaan sehingga umpan balik bisa spesifik, misalnya "Persamaan (1) benar, (2) belum".

### 3.3 Penyelaras koefisien (eliminasi)

Untuk menghilangkan variabel dengan koefisien `k1` (pers. 1) dan `k2` (pers. 2):
- `L = kpk(|k1|, |k2|)`, maka pengali pers. 1 adalah `L/|k1|` dan pengali pers. 2 adalah `L/|k2|`.
- Setelah dikalikan, jika **tanda koefisien sama**, kedua persamaan **dikurangkan**; jika **tanda berbeda**, kedua persamaan **dijumlahkan**.

Contoh: `3x + 2y = 130000` dan `2x + 5y = 160000`, eliminasi x: KPK(3, 2) = 6, sehingga pers. (1) × 2 dan pers. (2) × 3. Tanda sama, jadi dikurangkan.

### 3.4 Tips metode

| Kondisi koefisien | Saran |
|---|---|
| Koefisien suatu variabel sama atau berlawanan | Eliminasi langsung |
| Ada koefisien 1 atau −1 | Substitusi (nyatakan variabel itu lebih dulu) |
| Lainnya | Gabungan: eliminasi satu variabel, lalu substitusi |

### 3.5 Parser angka Indonesia (`parse.py`)

| Input | Hasil |
|---|---|
| `19000`, `19.000`, `Rp19.000`, `Rp 19.000` | 19000 |
| `-10`, `−10` (minus Unicode) | −10 |
| `1,5` | 3/2 (koma sebagai desimal; jarang dipakai) |
| `19.00` (titik tidak berpola ribuan) | ditolak dengan pesan "format angka tidak dikenali" |

Fungsi yang sama dibuat ulang di `frontend/js/format.js` hanya untuk **validasi tampilan** (bukan penilaian).

## 4. API

Semua endpoint diawali `/api`, memakai format JSON, dan berbahasa Indonesia pada pesan umpan balik.

| Metode | Endpoint | Masukan | Keluaran |
|---|---|---|---|
| POST | `/sesi` | `{kode_siswa, kelas}` | `{sesi_id, progres}` |
| GET | `/soal?mode=belajar\|misi` | — | daftar ringkas soal + status terkunci/selesai |
| GET | `/soal/<id>` | — | teks, segmen, variabel, daftar tahap & layar (**tanpa kunci**) |
| POST | `/cek-langkah` | `{sesi_id, soal_id, tahap, layar, jawaban}` | `{benar, detail[], pesan, skor_tahap?, lanjut_ke}` |
| POST | `/petunjuk` | `{sesi_id, soal_id, tahap, layar, tingkat}` | `{teks, jawaban_langkah?}` (jawaban hanya untuk tingkat 3) |
| POST | `/cek-jawaban` | `{persamaan:[[a,b,c],[a,b,c]], x, y}` | per persamaan: ruas kiri, ruas kanan, cocok? |
| POST | `/bantu-eliminasi` | `{persamaan, hilangkan:"x"\|"y"}` | `{kpk, pengali:[m1,m2], operasi:"jumlah"\|"kurang", alasan}` |
| POST | `/tips-metode` | `{persamaan}` | `{metode, alasan}` |
| POST | `/log` | `{sesi_id, peristiwa:[…]}` | `{ok}` |
| GET | `/guru/rekap` | header `X-PIN` | JSON rekap |
| GET | `/guru/ekspor.csv?tabel=…` | header `X-PIN` | CSV |

Contoh `cek-langkah` (Misi 3, tahap 1, model):

```json
// request
{ "sesi_id": 12, "soal_id": "M3", "tahap": 1, "layar": "model",
  "jawaban": { "persamaan": [[1,1,250],[50000,30000,8900000]] } }
// response
{ "benar": true, "detail": [true, true],
  "pesan": "Tepat! Persamaan (2) juga boleh disederhanakan menjadi 5x + 3y = 890.",
  "skor_tahap": 1, "lanjut_ke": {"tahap": 2, "layar": "pengali"} }
```

## 5. Basis data (SQLite)

```sql
CREATE TABLE siswa (
  kode TEXT PRIMARY KEY,          -- contoh "S01"
  kelas TEXT,
  dibuat TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE sesi (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  kode_siswa TEXT REFERENCES siswa(kode),
  mulai TEXT DEFAULT CURRENT_TIMESTAMP,
  perangkat TEXT                  -- "mobile"/"desktop" (dari lebar layar)
);
CREATE TABLE jawaban_tahap (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sesi_id INTEGER REFERENCES sesi(id),
  soal_id TEXT, tahap INTEGER, layar TEXT,
  jawaban_json TEXT,
  benar INTEGER,                  -- 0/1
  percobaan INTEGER,              -- percobaan ke-
  petunjuk_maks INTEGER,          -- 0..3
  skor REAL,
  durasi_ms INTEGER,
  waktu TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE peristiwa (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sesi_id INTEGER REFERENCES sesi(id),
  tipe TEXT,                      -- lihat EVALUASI.md §3
  soal_id TEXT, tahap INTEGER,
  data_json TEXT,
  waktu_klien TEXT,
  waktu TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE alasan_teks (        -- jawaban esai bebas untuk dinilai guru
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sesi_id INTEGER, soal_id TEXT, tahap INTEGER,
  teks TEXT, skor_guru REAL
);
```

## 6. Alur data satu langkah

1. JS meminta `GET /api/soal/M3`, lalu menampilkan layar pertama.
2. Siswa mengisi input dan menekan **Periksa**, sehingga JS mengirim `POST /api/cek-langkah`.
3. Python memeriksa jawaban dengan `checker`, menghitung skor dengan `scoring`, lalu menyimpan ke `jawaban_tahap`.
4. JS menampilkan umpan balik. Jika benar, hasilnya masuk ke Panel Ringkasan dan aplikasi pindah ke layar berikut.
5. Setiap klik petunjuk, ulang, jeda, dan sebagainya masuk antrean `logger.js` lalu dikirim berkelompok ke `POST /api/log`.

## 7. Keamanan dan privasi (secukupnya untuk penelitian)

- PIN guru disimpan di variabel lingkungan `GURU_PIN`, tidak ditulis di kode.
- Validasi input di server: jumlah koefisien, panjang teks maksimal 1000 karakter, dan tipe angka.
- Semua query SQL memakai parameter (`?`), tanpa penggabungan string.
- Teks dari siswa ditampilkan dengan `textContent`, bukan `innerHTML`.

## 8. Deploy (rencana)

| Tahap | Pilihan |
|---|---|
| Uji coba di kelas | Laptop menjalankan Flask, siswa membuka `http://IP-laptop:5000` melalui Wi-Fi/hotspot yang sama |
| Daring | PythonAnywhere (gratis, mendukung Flask + SQLite) atau Render |
