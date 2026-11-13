// Format & parsing angka Indonesia (titik = ribuan, koma = desimal).
// Hanya untuk TAMPILAN dan validasi ringan; penilaian tetap dilakukan di server (Python).

const BULAT = /^\d+$/;
const RIBUAN = /^\d{1,3}(\.\d{3})+$/;
const DESIMAL = /^\d+,\d+$/;

/** "Rp19.000" -> 19000 ; mengembalikan null jika format tidak dikenali. */
export function parseAngka(teks) {
  if (typeof teks === 'number') return Number.isFinite(teks) ? teks : null;
  if (typeof teks !== 'string') return null;
  let s = teks.trim().replace(/−/g, '-').replace(/[\s ]/g, '');
  if ((s.match(/-/g) || []).length > 1) return null;
  let negatif = false;
  if (s.startsWith('-')) { negatif = true; s = s.slice(1); }
  if (s.slice(0, 2).toLowerCase() === 'rp') s = s.slice(2);
  if (s.startsWith('-')) { negatif = true; s = s.slice(1); }
  let n;
  if (BULAT.test(s)) n = Number(s);
  else if (RIBUAN.test(s)) n = Number(s.replace(/\./g, ''));
  else if (DESIMAL.test(s)) n = Number(s.replace(',', '.'));
  else return null;
  return negatif ? -n : n;
}

const nf = new Intl.NumberFormat('id-ID', { maximumFractionDigits: 4 });

/** 8900000 -> "8.900.000" ; -10 -> "−10" (minus matematika). */
export function formatAngka(n) {
  const teks = nf.format(Math.abs(n));
  return n < 0 ? `−${teks}` : teks;
}

/** Nilai mentah isian ("-19000", "-", "") -> teks tampilan ("−19.000", "−", ""). */
export function formatMentah(raw) {
  if (!raw) return '';
  const neg = raw.startsWith('-');
  const digit = raw.replace('-', '');
  if (!digit) return neg ? '−' : '';
  return (neg ? '−' : '') + nf.format(Number(digit));
}

/** Daftar suku persamaan untuk ditampilkan: [{tanda, angka, v}] dan konstanta. */
export function sukuPersamaan(e, vars) {
  const [a, b, c] = e.map((v) => (typeof v === 'number' ? v : parseAngka(String(v))));
  const suku = [];
  [[a, vars[0]], [b, vars[1]]].forEach(([k, v]) => {
    if (k === null || k === 0) return;
    const pertama = suku.length === 0;
    let tanda = '';
    if (pertama) tanda = k < 0 ? '−' : '';
    else tanda = k < 0 ? ' − ' : ' + ';
    const angka = Math.abs(k) === 1 ? '' : formatAngka(Math.abs(k));
    suku.push({ tanda, angka, v });
  });
  return { suku, konstanta: c === null ? '?' : formatAngka(c) };
}

/** [2, -1, 30] -> "2x − y = 30" */
export function teksPersamaan(e, vars) {
  const { suku, konstanta } = sukuPersamaan(e, vars);
  const kiri = suku.map((s) => `${s.tanda}${s.angka}${s.v}`).join('') || '0';
  return `${kiri} = ${konstanta}`;
}
