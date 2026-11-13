// Kotak isian angka + keypad layar. Keyboard bawaan HP sering tidak punya tombol minus
// untuk input angka, jadi kita pakai keypad sendiri (0–9, −, ⌫, 000).
// Di laptop, keyboard fisik tetap bisa dipakai.
import { h } from '../dom.js';
import { formatMentah } from '../format.js';

const MAKS_DIGIT = 12;
let aktif = null;
let keypadEl = null;

/** Buat kotak isian. Nilai disimpan "mentah": digit dengan tanda minus opsional, mis. "-19000". */
export function buatSlot({ nilai = '', label = 'isian', lebar = '', onUbah } = {}) {
  const el = h('button', { type: 'button', class: `slot ${lebar}`, 'aria-label': label });
  el._nilai = String(nilai ?? '');
  el.nilai = () => el._nilai;
  el.setNilai = (v) => {
    el._nilai = v;
    tampilkan();
    el.classList.remove('salah', 'benar');
    onUbah?.(v);
  };
  function tampilkan() {
    el.textContent = formatMentah(el._nilai);
    el.classList.toggle('kosong', !el._nilai);
  }
  tampilkan();
  el.addEventListener('click', () => fokus(el));
  return el;
}

export function fokus(slot) {
  if (aktif) aktif.classList.remove('aktif');
  aktif = slot;
  if (!slot) {
    tutup();
    return;
  }
  slot.classList.add('aktif');
  buka();
  slot.scrollIntoView({ block: 'nearest', behavior: 'auto' });
}

export function slotAktif() {
  return aktif && document.body.contains(aktif) ? aktif : null;
}

function semuaSlot() {
  // Urutan kotak dalam wadah yang sama (halaman utama atau lembar alat bantu)
  const wadah = aktif?.closest('.sheet') || document.getElementById('app');
  return [...wadah.querySelectorAll('.slot')];
}

export function slotBerikut() {
  const daftar = semuaSlot();
  const i = daftar.indexOf(aktif);
  fokus(i >= 0 && i < daftar.length - 1 ? daftar[i + 1] : null);
}

function ketik(tombol) {
  const s = slotAktif();
  if (!s) return;
  let v = s.nilai();
  if (tombol === 'hapus') v = v.slice(0, -1);
  else if (tombol === 'minus') v = v.startsWith('-') ? v.slice(1) : `-${v}`;
  else {
    const digit = v.replace('-', '');
    if ((digit + tombol).length > MAKS_DIGIT) return;
    if (digit === '0') v = v.replace('0', '');
    v += tombol;
  }
  s.setNilai(v);
}

function buatKeypad() {
  const tombol = (label, aksi, kelas = '', aria = label) =>
    h('button', { type: 'button', class: `kp ${kelas}`, 'aria-label': aria, onclick: aksi }, label);
  const digit = (d) => tombol(d, () => ketik(d));
  keypadEl = h('div', { class: 'keypad', role: 'group', 'aria-label': 'Keypad angka' },
    h('div', { class: 'keypad-grid' },
      digit('1'), digit('2'), digit('3'), tombol('⌫', () => ketik('hapus'), 'kp-fungsi', 'hapus'),
      digit('4'), digit('5'), digit('6'), tombol('−', () => ketik('minus'), 'kp-fungsi', 'tanda minus'),
      digit('7'), digit('8'), digit('9'), tombol('→', slotBerikut, 'kp-fungsi', 'kotak berikutnya'),
      tombol('000', () => ketik('000')), digit('0'),
      tombol('Selesai', () => fokus(null), 'kp-selesai', 'tutup keypad')));
  // Mencegah tombol keypad mencuri fokus/menggulir halaman
  keypadEl.addEventListener('mousedown', (e) => e.preventDefault());
  document.getElementById('keypad-host').append(keypadEl);
}

function buka() {
  if (!keypadEl) buatKeypad();
  keypadEl.classList.add('terbuka');
  document.body.classList.add('keypad-terbuka');
}

function tutup() {
  keypadEl?.classList.remove('terbuka');
  document.body.classList.remove('keypad-terbuka');
}

export function resetKeypad() {
  aktif = null;
  tutup();
}

document.addEventListener('keydown', (e) => {
  const s = slotAktif();
  if (!s || e.ctrlKey || e.metaKey || e.altKey) return;
  if (/^[0-9]$/.test(e.key)) ketik(e.key);
  else if (e.key === '-' || e.key === '−') ketik('minus');
  else if (e.key === 'Backspace') ketik('hapus');
  else if (e.key === 'Enter' || e.key === 'Tab') slotBerikut();
  else if (e.key === 'Escape') fokus(null);
  else return;
  e.preventDefault();
});
