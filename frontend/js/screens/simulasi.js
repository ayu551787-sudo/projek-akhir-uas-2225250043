// Simulasi belanja: konkret (barang di keranjang) -> simbol (persamaan).
// Harga dipilih acak di browser karena ini latihan bebas, bukan penilaian.
import { h, persamaanEl, varEl } from '../dom.js';
import { formatAngka, parseAngka } from '../format.js';
import { catat } from '../logger.js';
import { buatSlot } from '../components/keypad.js';
import { halaman } from '../components/layout.js';

const PASANGAN = [
  { a: { nama: 'buku', ikon: '📘' }, b: { nama: 'pensil', ikon: '✏️' }, ha: [3000, 3500, 4000, 4500, 5000], hb: [1000, 1500, 2000, 2500] },
  { a: { nama: 'apel', ikon: '🍎' }, b: { nama: 'jeruk', ikon: '🍊' }, ha: [2000, 2500, 3000], hb: [1000, 1500, 2000] },
  { a: { nama: 'roti', ikon: '🍞' }, b: { nama: 'susu', ikon: '🥛' }, ha: [4000, 5000, 6000], hb: [3000, 3500, 4500] },
];
const VARS = ['x', 'y'];
const pilih = (arr) => arr[Math.floor(Math.random() * arr.length)];

export function simulasi(root) {
  let p;
  let harga;
  let keranjang;

  function baru() {
    p = pilih(PASANGAN);
    harga = { x: pilih(p.ha), y: pilih(p.hb) };
    keranjang = [{ a: 2, b: 1 }, { a: 1, b: 3 }];
    render();
  }

  const total = (k) => k.a * harga.x + k.b * harga.y;
  const det = () => keranjang[0].a * keranjang[1].b - keranjang[1].a * keranjang[0].b;
  const kosong = (k) => k.a === 0 && k.b === 0;

  function pengatur(k, sisi, barang) {
    const nilai = h('span', { class: 'jumlah', 'aria-live': 'polite' }, String(k[sisi]));
    const ubah = (d) => {
      k[sisi] = Math.max(0, Math.min(9, k[sisi] + d));
      catat('simulasi_keranjang', { keranjang });
      render();
    };
    return h('div', { class: 'pengatur' },
      h('span', { class: 'barang' }, `${barang.ikon} ${barang.nama}`),
      h('button', { type: 'button', class: 'tombol-ikon', 'aria-label': `kurangi ${barang.nama}`, onclick: () => ubah(-1) }, '−'),
      nilai,
      h('button', { type: 'button', class: 'tombol-ikon', 'aria-label': `tambah ${barang.nama}`, onclick: () => ubah(1) }, '+'));
  }

  function kartuKeranjang(k, i) {
    const isiIkon = `${p.a.ikon.repeat(k.a)}${p.b.ikon.repeat(k.b)}` || '(kosong)';
    return h('div', { class: 'kartu keranjang' },
      h('h3', {}, `Keranjang ${i + 1}`),
      pengatur(k, 'a', p.a), pengatur(k, 'b', p.b),
      h('p', { class: 'ikon-barang', 'aria-hidden': 'true' }, isiIkon),
      h('p', { class: 'sorot' }, `Total bayar: Rp${formatAngka(total(k))}`),
      h('div', { class: 'terjemah' },
        h('p', {}, `${k.a} ${p.a.nama} + ${k.b} ${p.b.nama} = Rp${formatAngka(total(k))}`),
        h('p', { class: 'panah', 'aria-hidden': 'true' }, '↓'),
        h('p', {}, h('span', { class: 'no-pers' }, `(${i + 1})`), persamaanEl([k.a, k.b, total(k)], VARS))));
  }

  function render() {
    const slotX = buatSlot({ label: `harga 1 ${p.a.nama}`, lebar: 'lebar' });
    const slotY = buatSlot({ label: `harga 1 ${p.b.nama}`, lebar: 'lebar' });
    const umpan = h('div', { 'aria-live': 'polite' });
    let peringatan = null;
    if (keranjang.some(kosong)) {
      peringatan = 'Setiap keranjang harus berisi minimal satu barang.';
    } else if (det() === 0) {
      peringatan = 'Keranjang 2 punya pola yang sama dengan keranjang 1 (sebanding). Harga tidak bisa ditemukan. Coba komposisi lain.';
    }

    const tebak = () => {
      const x = parseAngka(slotX.nilai());
      const y = parseAngka(slotY.nilai());
      if (x === null || y === null) {
        umpan.replaceChildren(h('p', { class: 'umpan info' }, 'Isi kedua harga dulu.'));
        return;
      }
      const cocok = keranjang.map((k) => k.a * x + k.b * y === total(k));
      catat('simulasi_tebak', { harga, tebakan: { x, y }, cocok });
      const baris = keranjang.map((k, i) => h('li', { class: cocok[i] ? 'benar' : 'salah' },
        h('span', { class: 'no-pers' }, `(${i + 1})`),
        `${k.a}×${formatAngka(x)} + ${k.b}×${formatAngka(y)} = ${formatAngka(k.a * x + k.b * y)}`,
        cocok[i] ? ' ✓' : ` ≠ ${formatAngka(total(k))} ✗`));
      const benar = cocok.every(Boolean);
      umpan.replaceChildren(
        h('ul', { class: 'cek-baris' }, baris),
        h('p', { class: `umpan ${benar ? 'benar' : 'salah'}` }, benar
          ? `Tepat! ${p.a.nama} Rp${formatAngka(x)} dan ${p.b.nama} Rp${formatAngka(y)} memenuhi kedua keranjang.`
          : 'Belum cocok dengan semua keranjang. Coba susun dan selesaikan SPLDV-nya.'));
    };

    root.replaceChildren(...halaman({ judul: 'Simulasi Belanja', sub: 'Dari keranjang ke persamaan', kembali: '#/belajar' },
      h('div', { class: 'kartu label-sim' },
        h('p', {}, 'Misalkan ', varEl('x', VARS), ` = harga 1 ${p.a.nama} dan `, varEl('y', VARS), ` = harga 1 ${p.b.nama}.`),
        h('ul', { class: 'catatan' },
          h('li', {}, h('strong', {}, 'koefisien'), ' = banyak barang'),
          h('li', {}, h('strong', {}, 'variabel'), ' = harga satu barang (belum diketahui)'),
          h('li', {}, h('strong', {}, 'konstanta'), ' = total bayar'))),
      h('div', { class: 'grid-keranjang' }, keranjang.map(kartuKeranjang)),
      peringatan
        ? h('p', { class: 'umpan info' }, peringatan)
        : h('section', { class: 'kartu tugas' },
          h('h2', { class: 'instruksi' }, 'Berapa harga satu barang? Selesaikan SPLDV di atas, lalu periksa.'),
          h('div', { class: 'template' },
            h('div', { class: 'baris-isian' }, varEl('x', VARS), ` (1 ${p.a.nama}) = Rp`, slotX),
            h('div', { class: 'baris-isian' }, varEl('y', VARS), ` (1 ${p.b.nama}) = Rp`, slotY)),
          h('button', { type: 'button', class: 'tombol utama', onclick: tebak }, 'Periksa ✓'),
          umpan),
      h('div', { class: 'baris-tombol' },
        h('button', { type: 'button', class: 'tombol sekunder', onclick: baru }, '🔄 Barang & harga baru'))));
  }

  baru();
}
