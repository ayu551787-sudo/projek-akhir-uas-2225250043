// Halaman guru/peneliti: rekap skor dan ekspor CSV. Dilindungi PIN (diatur di server).
import { api } from '../api.js';
import { h } from '../dom.js';
import { halaman, pesanGalat } from '../components/layout.js';

const KUNCI_PIN = 'spldv:pin';

function bacaPin() {
  try { return sessionStorage.getItem(KUNCI_PIN) || ''; } catch { return ''; }
}
function tulisPin(v) {
  try { if (v) sessionStorage.setItem(KUNCI_PIN, v); else sessionStorage.removeItem(KUNCI_PIN); } catch { /* abaikan */ }
}

export async function guru(root) {
  const pin = bacaPin();
  if (!pin) {
    formPin(root);
    return;
  }
  let data;
  try {
    data = await api.guruRekap(pin);
  } catch (err) {
    if (err.status === 401) {
      tulisPin('');
      formPin(root, 'PIN salah.');
      return;
    }
    root.replaceChildren(...halaman({ judul: 'Halaman Guru', kembali: '#/beranda' }, pesanGalat(err, () => guru(root))));
    return;
  }

  const kolom = data.rekap.length ? Object.keys(data.rekap[0]) : [];
  const unduh = async (tabel) => {
    const blob = await api.guruEkspor(pin, tabel);
    const url = URL.createObjectURL(blob);
    const a = h('a', { href: url, download: `spldv-${tabel}.csv` });
    document.body.append(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };

  root.replaceChildren(...halaman({
    judul: 'Halaman Guru',
    sub: `${data.rekap.length} siswa`,
    kembali: '#/beranda',
    kanan: h('button', { type: 'button', class: 'tombol teks', onclick: () => { tulisPin(''); guru(root); } }, 'Kunci'),
  },
  h('p', { class: 'catatan' }, 'Skor misi diambil dari pengerjaan pertama yang selesai. Pengulangan tidak menimpa skor pertama.'),
  data.rekap.length
    ? h('div', { class: 'tabel-wadah' }, h('table', { class: 'tabel' },
      h('thead', {}, h('tr', {}, kolom.map((k) => h('th', { scope: 'col' }, k.replaceAll('_', ' '))))),
      h('tbody', {}, data.rekap.map((r) => h('tr', {}, kolom.map((k) => h('td', {}, r[k] ?? '–')))))))
    : h('p', {}, 'Belum ada data siswa.'),
  h('section', { class: 'kartu' },
    h('h2', {}, 'Ekspor CSV (untuk Excel/SPSS)'),
    h('div', { class: 'baris-tombol wrap' },
      [['rekap', 'Rekap per siswa'], ['jawaban', 'Semua jawaban'], ['peristiwa', 'Log peristiwa'],
        ['alasan', 'Alasan tertulis'], ['main', 'Pengerjaan']].map(([t, label]) =>
        h('button', { type: 'button', class: 'tombol sekunder', onclick: () => unduh(t) }, label))))));
}

function formPin(root, galat = '') {
  const input = h('input', { id: 'pin', class: 'input-teks', type: 'password', inputmode: 'numeric', autocomplete: 'off' });
  const form = h('form', { class: 'kartu form-masuk' },
    h('label', { for: 'pin' }, 'PIN guru'), input,
    galat ? h('p', { class: 'umpan salah' }, galat) : null,
    h('button', { type: 'submit', class: 'tombol utama lebar' }, 'Buka'));
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    tulisPin(input.value.trim());
    guru(root);
  });
  root.replaceChildren(...halaman({ judul: 'Halaman Guru', kembali: '#/beranda' }, form));
  input.focus();
}
