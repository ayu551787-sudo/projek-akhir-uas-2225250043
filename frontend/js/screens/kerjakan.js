// Layar pengerjaan generik untuk Latihan dan Misi: satu langkah satu layar,
// panel ringkasan, petunjuk 3 tingkat, alat bantu, dan pemeriksaan di server.
import { api } from '../api.js';
import { h, persamaanEl, pindah, rich } from '../dom.js';
import { catat } from '../logger.js';
import { state } from '../state.js';
import { bukaAlat, NAMA_ALAT } from '../components/alat.js';
import { buatInput } from '../components/inputLayar.js';
import { resetKeypad } from '../components/keypad.js';
import { halaman, memuat, pesanGalat } from '../components/layout.js';
import { konfirmasi } from '../components/sheet.js';
import { legendaTanda, teksSoal } from '../components/teksSoal.js';

const IKON_ALAT = { tips: '🧭', penyelaras: '⚖️', cek: '✔️' };

export async function kerjakan(root, [soalId]) {
  const sesi = state.sesi();
  root.replaceChildren(...halaman({ judul: 'Memuat…', kembali: '#/beranda' }, memuat()));

  let soal;
  let simpanan = state.main(soalId);
  const dilanjutkan = Boolean(simpanan);
  try {
    soal = await api.soal(soalId);
    if (!simpanan) {
      const r = await api.mulai(sesi.sesi_id, soalId);
      simpanan = { mainId: r.main_id, idx: 0, ringkasan: [], persamaan: [null, null], tanda: [], petunjuk: {},
        ringkasanTerbuka: true, soalTerbuka: true };
      state.setMain(soalId, simpanan);
    }
  } catch (err) {
    root.replaceChildren(...halaman({ judul: 'Gagal memuat', kembali: '#/beranda' },
      pesanGalat(err, () => kerjakan(root, [soalId]))));
    return;
  }

  const st = { ...simpanan, tanda: new Set(simpanan.tanda) };
  const misi = soal.mode === 'misi';
  const kembali = misi ? '#/misi' : '#/belajar';
  const vars = soal.variabel.map((v) => v.simbol);
  const daftarLayar = soal.tahap.flatMap((t) => t.layar.map((l) => ({ ...l, tahap: t.no, judulTahap: t.judul })));
  let mulai = performance.now();
  let bannerSudah = false;

  const simpan = () => state.setMain(soalId, { ...st, tanda: [...st.tanda] });
  const persamaanSiswa = () => {
    if (st.persamaan.every(Boolean)) return st.persamaan;
    if (soal.persamaan_tampil) return soal.persamaan_tampil.map((e) => e.map(String));
    return null;
  };

  async function akhiri() {
    root.replaceChildren(...halaman({ judul: soal.judul }, memuat()));
    try {
      await api.selesai(st.mainId);
      state.setMain(soalId, null);
      pindah(`#/hasil/${st.mainId}`);
    } catch (err) {
      root.replaceChildren(...halaman({ judul: soal.judul, kembali }, pesanGalat(err, akhiri)));
    }
  }

  function panelRingkasan() {
    const isi = st.ringkasan.length
      ? h('ol', { class: 'ringkasan-daftar' }, st.ringkasan.map((r) => h('li', {},
        r.pers
          ? r.pers.map((e, i) => h('div', {}, h('span', { class: 'no-pers' }, `(${(r.no ?? i + 1)})`), persamaanEl(e, vars)))
          : rich(r.teks, vars))))
      : h('p', { class: 'catatan' }, 'Hasil setiap langkah yang benar akan muncul di sini, jadi kamu tidak perlu mengingatnya.');
    const d = h('details', { class: 'panel ringkasan', open: st.ringkasanTerbuka },
      h('summary', {}, `Ringkasan langkah (${st.ringkasan.length})`), isi);
    d.addEventListener('toggle', () => {
      st.ringkasanTerbuka = d.open;
      simpan();
      catat('ringkasan_toggle', { soal_id: soalId, main_id: st.mainId, terbuka: d.open });
    });
    return d;
  }

  function panelSoal(L, ctx) {
    const tandaiLayar = L.input === 'tandai';
    const d = h('details', { class: 'panel soal', open: tandaiLayar || st.soalTerbuka },
      h('summary', {}, 'Soal'),
      teksSoal(soal, {
        otomatis: !misi,
        tanda: st.tanda,
        info: { soal_id: soalId, main_id: st.mainId, layar_id: L.id },
        onUbah: () => { simpan(); ctx.onTanda?.(); },
      }),
      tandaiLayar ? null : legendaTanda(!misi));
    d.addEventListener('toggle', () => {
      st.soalTerbuka = d.open;
      simpan();
      catat('soal_toggle', { soal_id: soalId, main_id: st.mainId, terbuka: d.open });
    });
    return d;
  }

  function render() {
    resetKeypad();
    if (st.idx >= daftarLayar.length) {
      akhiri();
      return;
    }
    const L = daftarLayar[st.idx];
    const info = { soal_id: soalId, main_id: st.mainId, layar_id: L.id };
    const ctx = { soal, vars, tanda: st.tanda, persamaan: persamaanSiswa(), otomatis: !misi, info };
    const input = buatInput(L, ctx);
    let tingkat = (st.petunjuk[L.id] || []).length;
    let selesaiLayar = false;
    catat('layar_buka', info);

    const umpan = h('div', { class: 'umpan-wadah', 'aria-live': 'polite' });
    const tampilUmpan = (teks, jenis) => umpan.replaceChildren(h('p', { class: `umpan ${jenis}` }, teks));

    // Petunjuk
    const kotakPetunjuk = h('div', { class: 'petunjuk-daftar' });
    const tombolLewati = h('button', { type: 'button', class: 'tombol teks' }, 'Lanjut tanpa menjawab langkah ini');
    const renderPetunjuk = () => {
      kotakPetunjuk.replaceChildren(...(st.petunjuk[L.id] || []).map((t, i) =>
        h('p', { class: `petunjuk p${i + 1}` }, h('strong', {}, `Petunjuk ${i + 1}: `), rich(t, vars))));
      if (tingkat >= 3 && !selesaiLayar) kotakPetunjuk.append(tombolLewati);
      tombolPetunjuk.textContent = tingkat >= 3 ? '💡 Petunjuk habis' : `💡 Petunjuk ${tingkat + 1}/3`;
      tombolPetunjuk.disabled = tingkat >= 3 || selesaiLayar;
    };

    const tombolPetunjuk = h('button', { type: 'button', class: 'tombol sekunder' });
    tombolPetunjuk.addEventListener('click', async () => {
      const berikut = tingkat + 1;
      if (berikut === 3) {
        const ok = await konfirmasi('Lihat jawaban langkah ini?',
          misi
            ? 'Petunjuk terakhir berisi jawaban langkah ini. Skor langkah ini menjadi 0, tetapi kamu tetap bisa melanjutkan.'
            : 'Petunjuk terakhir berisi jawaban langkah ini. Coba dulu dengan petunjuk sebelumnya, ya.',
          { ya: 'Lihat jawaban', tidak: 'Coba lagi dulu' });
        if (!ok) return;
      }
      tombolPetunjuk.disabled = true;
      try {
        const r = await api.petunjuk(st.mainId, L.id, berikut);
        tingkat = berikut;
        (st.petunjuk[L.id] ||= []).push(r.teks);
        simpan();
        catat('petunjuk', { ...info, tingkat: berikut });
      } catch (err) {
        tampilUmpan(err.message, 'salah');
      }
      renderPetunjuk();
    });

    // Lanjut / Periksa
    const tombolUtama = h('button', { type: 'button', class: 'tombol utama' }, 'Periksa ✓');
    const tandaiSelesai = (catatanRingkasan) => {
      selesaiLayar = true;
      if (catatanRingkasan) st.ringkasan.push(catatanRingkasan);
      st.idx += 1;
      simpan();
      tombolUtama.textContent = st.idx >= daftarLayar.length ? 'Lihat hasil ▸' : 'Lanjut ▸';
      renderPetunjuk();
      tombolUtama.focus();
    };
    const catatanDari = (sumber, ringkasanServer) => {
      if (L.input === 'persamaan2' && sumber?.persamaan) {
        st.persamaan = sumber.persamaan.map((e) => e.map(String));
        return { pers: st.persamaan };
      }
      if (L.input === 'persamaan1' && sumber?.persamaan) {
        const k = L.simpan_persamaan ?? 0;
        st.persamaan[k] = sumber.persamaan[0].map(String);
        return { pers: [st.persamaan[k]], no: k + 1 };
      }
      return ringkasanServer ? { teks: ringkasanServer } : null;
    };

    tombolLewati.addEventListener('click', async () => {
      tombolLewati.disabled = true;
      try {
        const r = await api.lewati(st.mainId, L.id);
        catat('lewati', info);
        if (r.jawaban) input.isi(r.jawaban);
        tampilUmpan(r.pesan, 'info');
        tandaiSelesai(catatanDari(r.jawaban, r.ringkasan));
      } catch (err) {
        if (err.status === 409) tandaiSelesai(null);
        else tampilUmpan(err.message, 'salah');
      }
    });

    tombolUtama.addEventListener('click', async () => {
      if (selesaiLayar) {
        catat('layar_tutup', { ...info, durasi_ms: Math.round(performance.now() - mulai) });
        mulai = performance.now();
        render();
        window.scrollTo({ top: 0 });
        return;
      }
      if (!input.lengkap()) {
        tampilUmpan(L.input === 'tandai' ? 'Tandai dulu informasi penting di soal.' : 'Lengkapi dulu semua isian/pilihan.', 'info');
        return;
      }
      resetKeypad();
      tombolUtama.disabled = true;
      const jawaban = input.ambil();
      try {
        const r = await api.cek(st.mainId, L.id, jawaban, Math.round(performance.now() - mulai));
        catat('periksa', { ...info, benar: r.benar, percobaan: r.percobaan });
        input.tandai(r.detail, r.benar);
        if (r.benar) {
          tampilUmpan(r.pesan, 'benar');
          tandaiSelesai(catatanDari(jawaban, r.ringkasan));
        } else {
          tampilUmpan(r.pesan, 'salah');
          if (r.percobaan >= 3 && tingkat < 3) tombolPetunjuk.classList.add('ingatkan');
        }
      } catch (err) {
        if (err.status === 409) {
          tampilUmpan('Langkah ini sudah tersimpan sebelumnya.', 'info');
          tandaiSelesai(null);
        } else {
          tampilUmpan(err.message, 'salah');
        }
      } finally {
        tombolUtama.disabled = false;
      }
    });

    // Alat bantu
    const alat = (L.alat || []).filter((a) => NAMA_ALAT[a]);
    const barAlat = alat.length
      ? h('div', { class: 'bar-alat' }, h('span', { class: 'label-kecil' }, 'Alat bantu:'),
        alat.map((a) => h('button', {
          type: 'button',
          class: 'tombol alat-btn',
          onclick: () => bukaAlat(a, { soal, persamaan: persamaanSiswa(), info }),
        }, `${IKON_ALAT[a]} ${NAMA_ALAT[a]}`)))
      : null;

    const jumlahTahap = soal.tahap.length;
    const isi = [
      dilanjutkan && st.idx > 0 && !bannerSudah ? bannerLanjut() : null,
      h('div', { class: 'progres', role: 'progressbar', 'aria-valuemin': '1', 'aria-valuemax': String(jumlahTahap),
        'aria-valuenow': String(L.tahap), 'aria-label': `Tahap ${L.tahap} dari ${jumlahTahap}` },
      soal.tahap.map((t) => h('span', { class: t.no < L.tahap ? 'selesai' : t.no === L.tahap ? 'kini' : '' }))),
      h('div', { class: 'tata-kerja' },
        h('div', { class: 'kolom-konteks' }, panelRingkasan(), panelSoal(L, ctx)),
        h('section', { class: 'kartu tugas', 'aria-labelledby': 'instruksi' },
          h('p', { class: 'label-kecil' }, `Tahap ${L.tahap} · ${L.judulTahap}`),
          h('h2', { id: 'instruksi', class: 'instruksi' }, rich(L.instruksi, vars)),
          input.el,
          barAlat,
          kotakPetunjuk,
          umpan)),
      h('div', { class: 'aksi' }, tombolPetunjuk, tombolUtama),
    ];
    root.replaceChildren(...halaman({
      judul: soal.judul,
      sub: `${misi ? 'Misi' : 'Latihan'} · Tahap ${L.tahap} dari ${jumlahTahap}`,
      kembali,
    }, ...isi));
    renderPetunjuk();
  }

  function bannerLanjut() {
    bannerSudah = true;
    return h('div', { class: 'banner' },
      h('span', {}, 'Melanjutkan pengerjaanmu sebelumnya.'),
      h('button', {
        type: 'button',
        class: 'tombol teks',
        onclick: async () => {
          const ok = await konfirmasi('Mulai dari awal?', 'Pengerjaan ini akan dimulai ulang dari langkah pertama.', { ya: 'Mulai ulang' });
          if (!ok) return;
          state.setMain(soalId, null);
          kerjakan(root, [soalId]);
        },
      }, 'Mulai ulang'));
  }

  render();
}
