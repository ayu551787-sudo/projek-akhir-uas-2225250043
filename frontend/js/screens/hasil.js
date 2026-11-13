import { api } from '../api.js';
import { h, pindah } from '../dom.js';
import { bintangEl, halaman, memuat, pesanGalat } from '../components/layout.js';
import { state } from '../state.js';

const LABEL = {
  mandiri: ['✓', 'mandiri'],
  petunjuk: ['💡', 'dengan petunjuk'],
  dilihat: ['👁', 'jawaban dilihat'],
  belum: ['–', 'belum'],
};

export async function hasil(root, [mainId]) {
  root.replaceChildren(...halaman({ judul: 'Hasil' }, memuat()));
  let r;
  let progres;
  try {
    [r, progres] = await Promise.all([api.hasil(Number(mainId)), api.progres(state.sesi().sesi_id)]);
  } catch (err) {
    root.replaceChildren(...halaman({ judul: 'Hasil', kembali: '#/beranda' }, pesanGalat(err, () => hasil(root, [mainId]))));
    return;
  }
  const misi = r.mode === 'misi';
  const daftar = misi ? progres.misi : progres.latihan;
  const i = daftar.findIndex((s) => s.id === r.soal_id);
  const berikut = daftar[i + 1];
  const kembali = misi ? '#/misi' : '#/belajar';

  const perTahap = new Map();
  r.layar.forEach((l) => {
    if (!perTahap.has(l.tahap)) perTahap.set(l.tahap, []);
    perTahap.get(l.tahap).push(l);
  });

  root.replaceChildren(...halaman({ judul: r.judul, sub: misi ? 'Hasil misi' : 'Hasil latihan', kembali },
    h('section', { class: 'kartu hasil' },
      h('p', { class: 'bintang-besar' }, bintangEl(r.bintang)),
      misi
        ? h('p', { class: 'skor' }, `Skor ${r.skor} dari ${r.skor_maks}`)
        : h('p', { class: 'skor' }, `${r.mandiri} dari ${r.jumlah_layar} langkah dikerjakan mandiri`),
      r.refleksi ? h('p', { class: 'refleksi' }, r.refleksi) : null),
    h('section', { class: 'kartu' },
      h('h2', {}, 'Rincian langkah'),
      h('ul', { class: 'rincian' }, [...perTahap.entries()].map(([t, ls]) => h('li', {},
        h('strong', {}, `Tahap ${t}`),
        h('span', { class: 'rincian-status' }, ls.map((l) => h('span', { class: `st st-${l.status}`, title: LABEL[l.status][1] },
          `${LABEL[l.status][0]} ${LABEL[l.status][1]}${misi && l.skor_maks ? ` (${l.skor}/${l.skor_maks})` : ''}`)))))),
      h('p', { class: 'catatan' }, '✓ mandiri · 💡 dengan petunjuk · 👁 jawaban dilihat')),
    h('div', { class: 'baris-tombol' },
      h('button', { type: 'button', class: 'tombol sekunder', onclick: () => pindah(`#/kerjakan/${r.soal_id}`) }, 'Ulangi'),
      berikut
        ? h('button', { type: 'button', class: 'tombol utama', onclick: () => pindah(`#/kerjakan/${berikut.id}`) },
          `${misi ? 'Misi' : 'Latihan'} berikutnya ▸`)
        : h('button', { type: 'button', class: 'tombol utama', onclick: () => pindah(misi ? '#/beranda' : '#/misi') },
          misi ? 'Kembali ke beranda' : 'Ke Mode Misi ▸'))));
}
