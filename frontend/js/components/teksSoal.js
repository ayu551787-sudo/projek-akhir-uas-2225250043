// Teks soal yang dipecah per segmen.
// - Mode latihan: informasi penting diberi penanda otomatis (signaling).
// - Mode misi: siswa menandai sendiri dengan mengetuk (dan di layar "tandai" menjadi jawaban).
import { h, persamaanEl } from '../dom.js';
import { catat } from '../logger.js';

/**
 * @param {object} soal  data soal publik
 * @param {object} opsi  { otomatis: bool, tanda: Set<number>, bisaTandai: bool, info: {soal_id, main_id} }
 */
export function teksSoal(soal, { otomatis = false, tanda = new Set(), bisaTandai = true, info = {}, onUbah } = {}) {
  const vars = soal.variabel.map((v) => v.simbol);
  const p = h('p', { class: 'teks-soal' });
  soal.segmen.forEach((seg, i) => {
    const kelas = ['seg'];
    if (otomatis && seg.peran) kelas.push(`seg-${seg.peran}`);
    if (tanda.has(i)) kelas.push('ditandai');
    if (!bisaTandai) {
      p.append(h('span', { class: kelas.join(' ') }, seg.t));
      return;
    }
    const el = h('span', {
      class: `${kelas.join(' ')} bisa-tandai`,
      role: 'button',
      tabindex: '0',
      'aria-pressed': tanda.has(i) ? 'true' : 'false',
    }, seg.t);
    const toggle = () => {
      if (tanda.has(i)) tanda.delete(i);
      else tanda.add(i);
      el.classList.toggle('ditandai', tanda.has(i));
      el.setAttribute('aria-pressed', tanda.has(i) ? 'true' : 'false');
      catat('tandai_segmen', { ...info, indeks: i, aktif: tanda.has(i) });
      onUbah?.();
    };
    el.addEventListener('click', toggle);
    el.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        toggle();
      }
    });
    p.append(el);
  });
  const isi = [p];
  if (soal.persamaan_tampil) {
    isi.push(h('div', { class: 'daftar-persamaan' },
      soal.persamaan_tampil.map((e, i) => h('div', {}, h('span', { class: 'no-pers' }, `(${i + 1})`), persamaanEl(e, vars)))));
  }
  return isi;
}

export function legendaTanda(otomatis) {
  if (!otomatis) {
    return h('p', { class: 'catatan' }, 'Ketuk bagian soal untuk menandai informasi yang menurutmu penting.');
  }
  return h('p', { class: 'catatan legenda' },
    h('span', { class: 'seg-data' }, 'data penting'), ' ',
    h('span', { class: 'seg-tanya' }, 'yang ditanyakan'));
}
