// Router berbasis hash: #/beranda, #/kerjakan/M1, dst.
import { resetKeypad } from './components/keypad.js';
import { tutupSheet } from './components/sheet.js';
import { kirim } from './logger.js';
import { beranda } from './screens/beranda.js';
import { contoh } from './screens/contoh.js';
import { belajar, petaMisi } from './screens/daftar.js';
import { guru } from './screens/guru.js';
import { hasil } from './screens/hasil.js';
import { kerjakan } from './screens/kerjakan.js';
import { masuk } from './screens/masuk.js';
import { simulasi } from './screens/simulasi.js';
import { state } from './state.js';

const RUTE = [
  [/^#\/masuk$/, masuk, false],
  [/^#\/beranda$/, beranda, true],
  [/^#\/belajar$/, belajar, true],
  [/^#\/misi$/, petaMisi, true],
  [/^#\/contoh\/(\w+)$/, contoh, true],
  [/^#\/simulasi$/, simulasi, true],
  [/^#\/kerjakan\/(\w+)$/, kerjakan, true],
  [/^#\/hasil\/(\d+)$/, hasil, true],
  [/^#\/guru$/, guru, false],
];

let bersihkan = null;

async function tampilkan() {
  // Setiap navigasi memakai wadah baru, sehingga layar lama yang masih menunggu
  // data dari server tidak bisa menimpa layar yang baru.
  const root = document.createElement('div');
  root.className = 'layar';
  document.getElementById('app').replaceChildren(root);
  if (typeof bersihkan === 'function') bersihkan();
  bersihkan = null;
  tutupSheet();
  resetKeypad();
  kirim();

  const hash = location.hash || '#/beranda';
  const cocok = RUTE.map(([pola, fn, perluSesi]) => [hash.match(pola), fn, perluSesi]).find(([m]) => m);
  if (!cocok) {
    location.replace('#/beranda');
    return;
  }
  const [m, fn, perluSesi] = cocok;
  if (perluSesi && !state.sesi()) {
    location.replace('#/masuk');
    return;
  }
  if (hash === '#/masuk' && state.sesi()) {
    location.replace('#/beranda');
    return;
  }
  window.scrollTo({ top: 0 });
  const hasilFn = await fn(root, m.slice(1));
  if (typeof hasilFn === 'function') bersihkan = hasilFn;
  document.querySelector('#app h1')?.setAttribute('tabindex', '-1');
}

window.addEventListener('hashchange', tampilkan);
tampilkan();
