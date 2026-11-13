import { api } from '../api.js';
import { h, pindah } from '../dom.js';
import { halaman } from '../components/layout.js';
import { state } from '../state.js';

export function masuk(root) {
  const kode = h('input', { id: 'kode', class: 'input-teks', autocomplete: 'off', autocapitalize: 'characters',
    maxlength: '20', required: true, placeholder: 'contoh: S01', pattern: '[A-Za-z0-9_\\-]+' });
  const kelas = h('input', { id: 'kelas', class: 'input-teks', autocomplete: 'off', maxlength: '20', placeholder: 'contoh: IX A' });
  const pesan = h('p', { class: 'umpan-wadah', 'aria-live': 'polite' });
  const tombol = h('button', { type: 'submit', class: 'tombol utama lebar' }, 'Masuk');

  const form = h('form', { class: 'kartu form-masuk', novalidate: true },
    h('p', {}, 'Masukkan kode siswa dari gurumu. Kamu tidak perlu menulis nama.'),
    h('label', { for: 'kode' }, 'Kode siswa'), kode,
    h('label', { for: 'kelas' }, 'Kelas (opsional)'), kelas,
    tombol, pesan);

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const nilai = kode.value.trim();
    if (!/^[A-Za-z0-9_-]{1,20}$/.test(nilai)) {
      pesan.replaceChildren(h('p', { class: 'umpan salah' }, 'Kode hanya boleh berisi huruf, angka, - atau _.'));
      kode.focus();
      return;
    }
    tombol.disabled = true;
    try {
      const perangkat = window.matchMedia('(pointer: coarse)').matches ? 'mobile' : 'desktop';
      const r = await api.sesi(nilai, kelas.value.trim(), perangkat);
      state.setSesi(r);
      pindah('#/beranda');
    } catch (err) {
      pesan.replaceChildren(h('p', { class: 'umpan salah' }, err.message));
    } finally {
      tombol.disabled = false;
    }
  });

  root.replaceChildren(...halaman({ judul: 'Jelajah SPLDV', sub: 'Sistem Persamaan Linear Dua Variabel' }, form));
  kode.focus();
}
