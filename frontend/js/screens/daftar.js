// Layar daftar: Mode Belajar dan Peta Misi.
import { api } from '../api.js';
import { h, pindah } from '../dom.js';
import { catat } from '../logger.js';
import { bintangEl, halaman, memuat, pesanGalat } from '../components/layout.js';
import { konfirmasi } from '../components/sheet.js';
import { state } from '../state.js';

async function ambilProgres(root, judul, ulang) {
  root.replaceChildren(...halaman({ judul, kembali: '#/beranda' }, memuat()));
  try {
    return await api.progres(state.sesi().sesi_id);
  } catch (err) {
    root.replaceChildren(...halaman({ judul, kembali: '#/beranda' }, pesanGalat(err, ulang)));
    return null;
  }
}

function kartuSoal(s, { syarat, mode }) {
  const status = s.selesai
    ? h('span', { class: 'status' }, mode === 'misi' ? [bintangEl(s.bintang), ` Skor ${s.skor_pertama}/${s.skor_maks}`] : '✓ Selesai')
    : s.terbuka
      ? h('span', { class: 'status' }, state.main(s.id) ? '▶ Lanjutkan' : 'Belum dikerjakan')
      : h('span', { class: 'status terkunci' }, `🔒 ${syarat}`);
  const kartu = h('button', { type: 'button', class: `kartu soal-item ${s.terbuka ? '' : 'terkunci'}` },
    h('span', { class: 'label-kecil' }, mode === 'misi' ? `Misi ${s.urutan} · ${s.indikator}` : s.indikator),
    h('strong', {}, s.judul),
    status);
  kartu.addEventListener('click', async () => {
    if (!s.terbuka) {
      const ok = await konfirmasi('Belum terbuka',
        `${syarat}. Disarankan menyelesaikannya dulu agar lebih siap. Tetap kerjakan sekarang?`,
        { ya: 'Tetap kerjakan', tidak: 'Kembali' });
      if (!ok) return;
      catat('buka_terkunci', { soal_id: s.id });
    }
    pindah(`#/kerjakan/${s.id}`);
  });
  return kartu;
}

export async function belajar(root) {
  const p = await ambilProgres(root, 'Mode Belajar', () => belajar(root));
  if (!p) return;
  root.replaceChildren(...halaman({ judul: 'Mode Belajar', kembali: '#/beranda' },
    h('section', {},
      h('h2', { class: 'judul-bagian' }, '1. Contoh soal'),
      h('p', { class: 'catatan' }, 'Pelajari penyelesaian lengkap. Kamu yang mengatur kecepatannya.'),
      h('div', { class: 'daftar-kartu' },
        p.contoh.map((c) => h('a', { class: 'kartu soal-item', href: `#/contoh/${c.id}` },
          h('strong', {}, c.judul), h('span', { class: 'catatan' }, c.deskripsi))))),
    h('section', {},
      h('h2', { class: 'judul-bagian' }, '2. Simulasi belanja'),
      h('div', { class: 'daftar-kartu' },
        h('a', { class: 'kartu soal-item', href: '#/simulasi' },
          h('strong', {}, 'Dari keranjang belanja ke persamaan'),
          h('span', { class: 'catatan' }, 'Isi keranjang, lihat persamaannya terbentuk, lalu tebak harganya.')))),
    h('section', {},
      h('h2', { class: 'judul-bagian' }, '3. Latihan berjenjang'),
      h('p', { class: 'catatan' }, 'Dari soal simbolik, ke soal cerita sederhana, lalu soal cerita yang lebih sulit.'),
      h('div', { class: 'daftar-kartu' },
        p.latihan.map((s, i) => kartuSoal(s, {
          mode: 'latihan',
          syarat: i > 0 ? `Selesaikan ${p.latihan[i - 1].judul.split(' · ')[0]} dulu` : '',
        }))))));
}

export async function petaMisi(root) {
  const p = await ambilProgres(root, 'Mode Misi', () => petaMisi(root));
  if (!p) return;
  const total = p.misi.reduce((n, s) => n + (s.skor_pertama ?? 0), 0);
  const maks = p.misi.reduce((n, s) => n + s.skor_maks, 0);
  root.replaceChildren(...halaman({ judul: 'Mode Misi', kembali: '#/beranda' },
    h('p', { class: 'catatan' },
      'Kerjakan misi berurutan. Tidak ada batas waktu. Petunjuk 1 dan 2 tidak mengurangi skor; petunjuk 3 (jawaban) membuat skor langkah itu 0.'),
    h('p', { class: 'sorot' }, `Skor total: ${total} dari ${maks}`),
    h('div', { class: 'daftar-kartu peta' },
      p.misi.map((s, i) => kartuSoal(s, {
        mode: 'misi',
        syarat: i === 0 ? 'Selesaikan Latihan 2 dulu' : `Selesaikan Misi ${i} dulu`,
      })))));
}
