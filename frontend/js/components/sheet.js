// Lembar bawah (bottom sheet) untuk alat bantu dan konfirmasi.
import { h } from '../dom.js';
import { resetKeypad } from './keypad.js';

let terbuka = null;

export function bukaSheet(judul, isi, { onTutup } = {}) {
  tutupSheet();
  resetKeypad();
  const host = document.getElementById('sheet-host');
  const tutup = () => {
    tutupSheet();
    onTutup?.();
  };
  const kembaliKe = document.activeElement;
  const panel = h('div', { class: 'sheet', role: 'dialog', 'aria-modal': 'true', 'aria-label': judul },
    h('div', { class: 'sheet-kepala' },
      h('h2', {}, judul),
      h('button', { type: 'button', class: 'tombol-ikon', 'aria-label': 'Tutup', onclick: tutup }, '✕')),
    h('div', { class: 'sheet-isi' }, isi));
  const latar = h('div', { class: 'sheet-latar', onclick: tutup });
  host.append(latar, panel);
  terbuka = { latar, panel, kembaliKe };
  panel.querySelector('button')?.focus();
  return tutup;
}

export function tutupSheet() {
  if (!terbuka) return;
  terbuka.latar.remove();
  terbuka.panel.remove();
  terbuka.kembaliKe?.focus?.();
  terbuka = null;
  resetKeypad();
}

/** Konfirmasi sederhana. Mengembalikan Promise<boolean>. */
export function konfirmasi(judul, pesan, { ya = 'Ya', tidak = 'Batal' } = {}) {
  return new Promise((selesai) => {
    let dijawab = false;
    const jawab = (v) => {
      dijawab = true;
      tutupSheet();
      selesai(v);
    };
    bukaSheet(judul, [
      h('p', {}, pesan),
      h('div', { class: 'baris-tombol' },
        h('button', { type: 'button', class: 'tombol sekunder', onclick: () => jawab(false) }, tidak),
        h('button', { type: 'button', class: 'tombol utama', onclick: () => jawab(true) }, ya)),
    ], { onTutup: () => { if (!dijawab) selesai(false); } });
  });
}

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && terbuka) tutupSheet();
});
