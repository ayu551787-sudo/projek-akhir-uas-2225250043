import { api } from '../api.js';
import { h, pindah } from '../dom.js';
import { halaman, memuat, pesanGalat } from '../components/layout.js';
import { konfirmasi } from '../components/sheet.js';
import { state } from '../state.js';

export async function beranda(root) {
  const sesi = state.sesi();
  const keluar = h('button', {
    type: 'button',
    class: 'tombol teks',
    onclick: async () => {
      if (await konfirmasi('Ganti siswa?', 'Kamu akan keluar dari kode ini di perangkat ini.', { ya: 'Keluar' })) {
        state.keluar();
        pindah('#/masuk');
      }
    },
  }, 'Ganti siswa');
  root.replaceChildren(...halaman({ judul: 'Jelajah SPLDV', sub: `Kode: ${sesi.kode_siswa}`, kanan: keluar }, memuat()));

  let p;
  try {
    p = await api.progres(sesi.sesi_id);
  } catch (err) {
    if (err.status === 404) {
      state.keluar();
      pindah('#/masuk');
      return;
    }
    root.replaceChildren(...halaman({ judul: 'Jelajah SPLDV', kanan: keluar }, pesanGalat(err, () => beranda(root))));
    return;
  }

  const latihanSelesai = p.latihan.filter((s) => s.selesai).length;
  const misiSelesai = p.misi.filter((s) => s.selesai).length;
  const misiTerbuka = p.misi.some((s) => s.terbuka);

  const kartuMenu = (judul, desk, status, hash) => h('a', { class: 'kartu menu', href: hash },
    h('h2', {}, judul), h('p', {}, desk), h('p', { class: 'status' }, status));

  root.replaceChildren(...halaman({ judul: 'Jelajah SPLDV', sub: `Kode: ${sesi.kode_siswa}`, kanan: keluar },
    h('p', { class: 'sapa' }, 'Pilih apa yang ingin kamu lakukan hari ini.'),
    h('div', { class: 'grid-menu' },
      kartuMenu('📘 Mode Belajar',
        'Contoh soal langkah demi langkah, simulasi belanja, dan latihan berjenjang.',
        `Latihan selesai: ${latihanSelesai} dari ${p.latihan.length}`, '#/belajar'),
      kartuMenu('🎯 Mode Misi',
        'Empat misi soal cerita untuk menguji kemampuan literasi matematikamu.',
        misiTerbuka ? `Misi selesai: ${misiSelesai} dari ${p.misi.length}` : '🔒 Terbuka setelah Latihan 2 selesai',
        '#/misi')),
    h('section', { class: 'kartu' },
      h('h2', {}, 'Lencana'),
      h('ul', { class: 'lencana' }, p.lencana.map((l) => h('li', { class: l.dapat ? 'dapat' : '' },
        h('span', { class: 'lencana-ikon', 'aria-hidden': 'true' }, l.dapat ? '🏅' : '○'),
        h('span', {}, h('strong', {}, l.nama), h('br'), h('span', { class: 'catatan' }, l.syarat)))))),
    h('p', { class: 'kaki' }, h('a', { href: '#/guru' }, 'Halaman guru/peneliti'))));
}
