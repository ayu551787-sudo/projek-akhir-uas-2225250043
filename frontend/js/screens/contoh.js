// Contoh soal (worked example) dengan kontrol tempo oleh siswa:
// ⟲ Ulang · ◀ Kembali · ▶ Putar/⏸ Jeda · Lanjut ▸  (tidak ada putar otomatis saat dibuka).
import { api } from '../api.js';
import { h, rich } from '../dom.js';
import { catat } from '../logger.js';
import { halaman, memuat, pesanGalat } from '../components/layout.js';

const JEDA_PUTAR_MS = 3500;

export async function contoh(root, [id]) {
  root.replaceChildren(...halaman({ judul: 'Contoh soal', kembali: '#/belajar' }, memuat()));
  let c;
  try {
    c = await api.contoh(id);
  } catch (err) {
    root.replaceChildren(...halaman({ judul: 'Contoh soal', kembali: '#/belajar' }, pesanGalat(err, () => contoh(root, [id]))));
    return;
  }
  const vars = c.variabel;
  let langkah = 0;
  let baris = 1; // banyak baris yang sudah ditampilkan pada langkah ini
  let timer = null;

  const kartu = h('section', { class: 'kartu tugas', 'aria-live': 'polite' });
  const info = h('p', { class: 'label-kecil' });
  const tPutar = h('button', { type: 'button', class: 'tombol sekunder' });
  const tLanjut = h('button', { type: 'button', class: 'tombol utama' }, 'Lanjut ▸');
  const tKembali = h('button', { type: 'button', class: 'tombol sekunder' }, '◀ Kembali');
  const tUlang = h('button', { type: 'button', class: 'tombol sekunder' }, '⟲ Ulang');
  const log = (tipe) => catat(tipe, { soal_id: c.id, langkah, baris });

  const L = () => c.langkah[langkah];
  const diAkhir = () => langkah === c.langkah.length - 1 && baris >= L().baris.length;

  function maju() {
    if (baris < L().baris.length) baris += 1;
    else if (langkah < c.langkah.length - 1) {
      langkah += 1;
      baris = 1;
    }
    if (diAkhir()) berhenti();
    tampil();
  }

  function berhenti() {
    clearInterval(timer);
    timer = null;
  }

  function tampil() {
    info.textContent = `Langkah ${langkah + 1} dari ${c.langkah.length}`;
    kartu.replaceChildren(
      h('h2', { class: 'instruksi' }, rich(L().judul, vars)),
      h('ul', { class: 'baris-contoh' }, L().baris.slice(0, baris).map((b) => h('li', {}, rich(b, vars)))));
    tPutar.textContent = timer ? '⏸ Jeda' : '▶ Putar';
    tKembali.disabled = langkah === 0 && baris <= 1;
    tLanjut.textContent = diAkhir() ? 'Selesai ✓' : 'Lanjut ▸';
  }

  tLanjut.addEventListener('click', () => {
    if (diAkhir()) {
      log('tempo_lanjut');
      location.hash = '#/belajar';
      return;
    }
    berhenti();
    maju();
    log('tempo_lanjut');
  });
  tKembali.addEventListener('click', () => {
    berhenti();
    if (langkah > 0) {
      langkah -= 1;
      baris = L().baris.length;
    } else baris = 1;
    log('tempo_kembali');
    tampil();
  });
  tUlang.addEventListener('click', () => {
    berhenti();
    baris = 1;
    log('tempo_ulang');
    tampil();
  });
  tPutar.addEventListener('click', () => {
    if (timer) {
      berhenti();
      log('tempo_jeda');
    } else if (!diAkhir()) {
      timer = setInterval(maju, JEDA_PUTAR_MS);
      log('tempo_putar');
    }
    tampil();
  });

  root.replaceChildren(...halaman({ judul: c.judul, sub: c.deskripsi, kembali: '#/belajar' },
    h('details', { class: 'panel soal', open: true }, h('summary', {}, 'Soal'), h('p', { class: 'teks-soal' }, c.soal)),
    info,
    kartu,
    h('div', { class: 'aksi aksi-tempo' }, tUlang, tKembali, tPutar, tLanjut)));
  tampil();

  // Hentikan timer bila pindah halaman
  return () => berhenti();
}
