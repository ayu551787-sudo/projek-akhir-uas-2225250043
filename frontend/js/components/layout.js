// Kerangka halaman: header (kembali + judul) dan isi.
import { h, pindah } from '../dom.js';

export function halaman({ judul, sub = null, kembali = null, kanan = null }, ...isi) {
  return [
    h('header', { class: 'kepala' },
      kembali
        ? h('button', { type: 'button', class: 'tombol-ikon', 'aria-label': 'Kembali', onclick: () => pindah(kembali) }, '←')
        : h('span', { class: 'logo', 'aria-hidden': 'true' }, 'x,y'),
      h('div', { class: 'kepala-judul' }, h('h1', {}, judul), sub ? h('p', { class: 'kepala-sub' }, sub) : null),
      kanan),
    h('main', { class: 'isi' }, ...isi),
  ];
}

export function pesanGalat(err, ulangi) {
  return h('div', { class: 'kartu galat', role: 'alert' },
    h('p', {}, err?.message || 'Terjadi kesalahan.'),
    ulangi ? h('button', { type: 'button', class: 'tombol sekunder', onclick: ulangi }, 'Coba lagi') : null);
}

export function memuat() {
  return h('p', { class: 'memuat', role: 'status' }, 'Memuat…');
}

export function bintangEl(n, maks = 3) {
  return h('span', { class: 'bintang', 'aria-label': `${n} dari ${maks} bintang` },
    '★'.repeat(n), h('span', { class: 'bintang-kosong' }, '☆'.repeat(maks - n)));
}
