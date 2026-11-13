// Alat bantu: Tips Metode, Penyelaras Koefisien, Cek Jawaban (dihitung oleh server Python).
import { api } from '../api.js';
import { h, persamaanEl, varEl } from '../dom.js';
import { catat } from '../logger.js';
import { buatSlot } from './keypad.js';
import { bukaSheet } from './sheet.js';

export const NAMA_ALAT = {
  tips: 'Tips Metode',
  penyelaras: 'Penyelaras Koefisien',
  cek: 'Cek Jawaban',
};

function belumAdaModel() {
  return h('p', { class: 'umpan info' },
    'Susun dulu model matematikanya (dua persamaan) di langkah sebelumnya. Setelah itu alat ini bisa dipakai.');
}

function daftarPersamaan(persamaan, vars) {
  return h('div', { class: 'daftar-persamaan' },
    persamaan.map((e, i) => h('div', {}, h('span', { class: 'no-pers' }, `(${i + 1})`), persamaanEl(e, vars))));
}

function galat(err) {
  return h('p', { class: 'umpan salah' }, err.message);
}

/**
 * @param {string} nama   'tips' | 'penyelaras' | 'cek'
 * @param {object} ctx    { soal, persamaan: [[a,b,c],[a,b,c]] | null, info: {soal_id, main_id, layar_id} }
 */
export function bukaAlat(nama, { soal, persamaan, info = {} }) {
  const vars = soal.variabel.map((v) => v.simbol);
  const isi = h('div', { class: 'alat' });
  bukaSheet(NAMA_ALAT[nama], isi);
  if (!persamaan) {
    isi.append(belumAdaModel());
    return;
  }
  isi.append(daftarPersamaan(persamaan, vars));
  if (nama === 'tips') alatTips(isi, soal, persamaan, info);
  if (nama === 'penyelaras') alatPenyelaras(isi, soal, persamaan, vars, info);
  if (nama === 'cek') alatCek(isi, soal, persamaan, vars, info);
}

async function alatTips(isi, soal, persamaan, info) {
  catat('tips_metode', info);
  try {
    const r = await api.alat('tips-metode', { soal_id: soal.id, persamaan });
    isi.append(
      h('p', { class: 'sorot' }, 'Saran: metode ', h('strong', {}, r.metode)),
      h('p', {}, r.alasan));
  } catch (err) {
    isi.append(galat(err));
  }
}

function alatPenyelaras(isi, soal, persamaan, vars, info) {
  const hasil = h('div', { 'aria-live': 'polite' });
  const pilih = async (v) => {
    catat('bantu_eliminasi', { ...info, hilangkan: v });
    hasil.replaceChildren();
    try {
      const r = await api.alat('bantu-eliminasi', { soal_id: soal.id, persamaan, hilangkan: v });
      if (!r.bisa) {
        hasil.append(h('p', {}, r.alasan));
        return;
      }
      hasil.append(
        h('p', {}, r.alasan),
        h('ol', { class: 'langkah-alat' }, r.langkah.map((l) => h('li', {}, l))),
        h('p', { class: 'sorot' }, r.aturan));
    } catch (err) {
      hasil.append(galat(err));
    }
  };
  isi.append(
    h('p', {}, 'Variabel mana yang ingin kamu hilangkan?'),
    h('div', { class: 'baris-tombol' },
      vars.map((v) => h('button', { type: 'button', class: 'tombol sekunder', onclick: () => pilih(v) },
        'Hilangkan ', varEl(v, vars)))),
    hasil);
}

function alatCek(isi, soal, persamaan, vars, info) {
  const slot = vars.map((v) => buatSlot({ label: `nilai ${v}`, lebar: 'lebar' }));
  const hasil = h('div', { 'aria-live': 'polite' });
  const periksa = async () => {
    hasil.replaceChildren();
    const nilai = Object.fromEntries(vars.map((v, i) => [v, slot[i].nilai()]));
    try {
      const r = await api.alat('cek-jawaban', { soal_id: soal.id, persamaan, nilai });
      catat('cek_jawaban', { ...info, nilai, cocok: r.baris.map((b) => b.cocok) });
      hasil.append(
        h('ul', { class: 'cek-baris' }, r.baris.map((b) => h('li', { class: b.cocok ? 'benar' : 'salah' },
          h('span', { class: 'no-pers' }, `(${b.no})`),
          `${b.substitusi} = ${b.kiri}`,
          b.cocok ? ` = ${b.kanan} ✓` : ` ≠ ${b.kanan} ✗`))),
        h('p', { class: `umpan ${r.semua_cocok ? 'benar' : 'salah'}` }, r.pesan));
    } catch (err) {
      hasil.append(galat(err));
    }
  };
  isi.append(
    h('p', {}, 'Masukkan nilai yang kamu temukan. Nilai itu akan disubstitusikan ke kedua persamaan.'),
    h('div', { class: 'isian-alat' },
      vars.map((v, i) => h('label', { class: 'baris-isian' }, varEl(v, vars), ' = ', slot[i]))),
    h('button', { type: 'button', class: 'tombol utama', onclick: periksa }, 'Masukkan ke persamaan'),
    hasil);
}
