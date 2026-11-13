// Pembantu DOM kecil. Semua teks dimasukkan sebagai textNode (aman dari XSS).
import { sukuPersamaan } from './format.js';

export function h(tag, attrs = {}, ...anak) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k === 'class') el.className = v;
    else if (k.startsWith('on') && typeof v === 'function') el.addEventListener(k.slice(2), v);
    else if (k === 'dataset') Object.assign(el.dataset, v);
    else if (v === true) el.setAttribute(k, '');
    else el.setAttribute(k, v);
  }
  tambah(el, anak);
  return el;
}

export function tambah(el, anak) {
  for (const c of [anak].flat(Infinity)) {
    if (c === null || c === undefined || c === false) continue;
    el.append(c instanceof Node ? c : document.createTextNode(String(c)));
  }
  return el;
}

/** Elemen variabel berwarna konsisten: indeks 0 -> --var-1, indeks 1 -> --var-2. */
export function varEl(simbol, vars) {
  const i = vars.indexOf(simbol);
  return h('var', { class: `v v${i + 1}`, title: `variabel ${simbol}` }, simbol);
}

/**
 * Teks dengan penanda variabel: "{x} + 2{y}" -> x dan y berwarna.
 * Baris baru (\n) menjadi <br>. Kurung kurawal lain dibiarkan apa adanya.
 */
export function rich(teks, vars = []) {
  const frag = document.createDocumentFragment();
  String(teks ?? '').split('\n').forEach((baris, i) => {
    if (i > 0) frag.append(h('br'));
    baris.split(/(\{[a-z]\})/).forEach((bag) => {
      const m = bag.match(/^\{([a-z])\}$/);
      if (m && vars.includes(m[1])) frag.append(varEl(m[1], vars));
      else if (bag) frag.append(document.createTextNode(bag));
    });
  });
  return frag;
}

/** Persamaan sebagai elemen: [2, -1, 30] -> 2x − y = 30 dengan variabel berwarna. */
export function persamaanEl(e, vars) {
  const { suku, konstanta } = sukuPersamaan(e, vars);
  const el = h('span', { class: 'persamaan' });
  if (!suku.length) el.append('0');
  suku.forEach((s) => el.append(`${s.tanda}${s.angka}`, varEl(s.v, vars)));
  el.append(` = ${konstanta}`);
  return el;
}

export function pindah(hash) {
  if (location.hash === hash) window.dispatchEvent(new HashChangeEvent('hashchange'));
  else location.hash = hash;
}

export function acak(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}
