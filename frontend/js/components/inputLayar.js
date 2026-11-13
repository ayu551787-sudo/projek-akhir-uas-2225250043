// Input terstruktur untuk setiap jenis layar (lihat docs/BANK_SOAL.md §1).
// Setiap pembuat mengembalikan { el, ambil(), lengkap(), tandai(detail, benar), isi(jawaban) }.
import { acak, h, persamaanEl, rich, varEl } from '../dom.js';
import { catat } from '../logger.js';
import { buatSlot, fokus, slotAktif, slotBerikut } from './keypad.js';

function tandaiSlot(slot, ok) {
  slot.classList.toggle('salah', ok === false);
  slot.classList.toggle('benar', ok === true);
}

// ---------- pilihan ----------
function inputPilihan(layar, ctx) {
  const urutan = layar.opsi.length >= 4 ? (ctx.urutanOpsi ||= acak(layar.opsi.map((o) => o.id))) : layar.opsi.map((o) => o.id);
  let dipilih = null;
  const tombol = {};
  const daftar = h('div', { class: 'opsi', role: 'radiogroup', 'aria-label': 'Pilihan jawaban' });
  urutan.forEach((id) => {
    const o = layar.opsi.find((x) => x.id === id);
    const b = h('button', { type: 'button', class: 'opsi-item', role: 'radio', 'aria-checked': 'false' }, rich(o.teks, ctx.vars));
    b.addEventListener('click', () => {
      dipilih = id;
      Object.entries(tombol).forEach(([k, el]) => {
        el.setAttribute('aria-checked', k === id ? 'true' : 'false');
        el.classList.remove('salah');
      });
    });
    tombol[id] = b;
    daftar.append(b);
  });
  let area = null;
  const el = h('div', {}, daftar);
  if (layar.teks_opsional) {
    area = h('textarea', { class: 'teks-alasan', rows: '3', maxlength: '1000',
      placeholder: 'Tulis alasanmu dengan kata-katamu sendiri (boleh dikosongkan)…', 'aria-label': 'Alasan (opsional)' });
    el.append(h('label', { class: 'label-alasan' }, 'Alasan dengan kata-katamu (opsional)'), area);
  }
  return {
    el,
    ambil: () => ({ pilihan: dipilih, ...(area && area.value.trim() ? { teks: area.value.trim() } : {}) }),
    lengkap: () => dipilih !== null,
    tandai: (_d, benar) => { if (dipilih) tombol[dipilih].classList.toggle('salah', !benar); },
    isi: () => {},
  };
}

// ---------- angka (template "Teks [id] teks {x}") ----------
function inputAngka(layar, ctx) {
  const slot = {};
  const el = h('div', { class: 'template' });
  layar.template.split('\n').forEach((baris) => {
    const row = h('div', { class: 'baris-isian' });
    baris.split(/(\[\w+\])/).forEach((bag) => {
      const m = bag.match(/^\[(\w+)\]$/);
      if (m) {
        slot[m[1]] = buatSlot({ label: `isian ${m[1]}`, lebar: 'lebar' });
        row.append(slot[m[1]]);
      } else if (bag) {
        row.append(rich(bag, ctx.vars));
      }
    });
    el.append(row);
  });
  return {
    el,
    ambil: () => ({ nilai: Object.fromEntries(Object.entries(slot).map(([k, s]) => [k, s.nilai()])) }),
    lengkap: () => Object.values(slot).every((s) => s.nilai() && s.nilai() !== '-'),
    tandai: (d, benar) => Object.entries(slot).forEach(([k, s]) => tandaiSlot(s, benar ? true : d?.isian?.[k])),
    isi: () => {},
  };
}

// ---------- persamaan ----------
function barisPersamaan(no, vars) {
  const s = [0, 1, 2].map((i) => buatSlot({ label: `persamaan ${no} ${['koefisien ' + vars[0], 'koefisien ' + vars[1], 'konstanta'][i]}` }));
  const row = h('div', { class: 'baris-pers' },
    h('span', { class: 'no-pers' }, `(${no})`),
    s[0], varEl(vars[0], vars), h('span', { class: 'op' }, '+'), s[1], varEl(vars[1], vars),
    h('span', { class: 'op' }, '='), s[2]);
  return {
    row,
    slot: s,
    nilai: () => s.map((x) => x.nilai()),
    lengkap: () => s.every((x) => x.nilai() && x.nilai() !== '-'),
    isi: (e) => s.forEach((x, i) => x.setNilai(String(e[i]).replace('−', '-'))),
  };
}

function chipPenerjemah(ctx) {
  const chips = ctx.soal.segmen
    .map((seg, i) => ({ ...seg, i }))
    .filter((seg) => typeof seg.angka === 'number');
  if (!chips.length) return null;
  const pesan = h('p', { class: 'catatan', 'aria-live': 'polite' },
    'Penerjemah soal: ketuk sebuah kotak, lalu ketuk potongan kalimat soal yang sesuai. Angkanya akan masuk ke kotak.');
  const wadah = h('div', { class: 'chips' });
  chips.forEach((c) => {
    const warna = ctx.otomatis && c.var ? ` chip-v${ctx.vars.indexOf(c.var) + 1}` : '';
    wadah.append(h('button', {
      type: 'button',
      class: `chip${warna}`,
      onmousedown: (e) => e.preventDefault(),
      onclick: () => {
        const s = slotAktif();
        if (!s) {
          pesan.textContent = 'Ketuk dulu kotak yang ingin diisi, lalu ketuk potongan kalimatnya.';
          return;
        }
        s.setNilai(String(c.angka));
        catat('penerjemah', { ...ctx.info, segmen: c.i });
        slotBerikut();
      },
    }, c.t));
  });
  return h('div', { class: 'penerjemah' }, pesan, wadah);
}

function inputPersamaan(layar, ctx, jumlah) {
  const baris = [];
  const el = h('div', { class: 'input-persamaan' });
  if ((layar.alat || []).includes('penerjemah')) {
    const chip = chipPenerjemah(ctx);
    if (chip) el.append(chip);
  }
  for (let i = 0; i < jumlah; i++) {
    const no = jumlah === 1 ? (layar.simpan_persamaan ?? 0) + 1 : i + 1;
    const b = barisPersamaan(no, ctx.vars);
    baris.push(b);
    el.append(b.row);
  }
  el.append(h('p', { class: 'catatan' },
    'Isi koefisien di depan ', varEl(ctx.vars[0], ctx.vars), ' dan ', varEl(ctx.vars[1], ctx.vars),
    ', lalu konstanta di ruas kanan. Koefisien 1 tetap ditulis 1; koefisien negatif pakai tombol −.'));
  return {
    el,
    ambil: () => ({ persamaan: baris.map((b) => b.nilai()) }),
    lengkap: () => baris.every((b) => b.lengkap()),
    tandai: (d, benar) => baris.forEach((b, i) => {
      const ok = benar ? true : d?.persamaan?.[i];
      b.row.classList.toggle('salah', ok === false);
      b.row.classList.toggle('benar', ok === true);
    }),
    isi: (j) => j?.persamaan?.forEach((e, i) => baris[i]?.isi(e)),
    fokusPertama: () => fokus(baris[0].slot[0]),
  };
}

// ---------- pengali ----------
function inputPengali(layar, ctx) {
  const pers = ctx.persamaan;
  const slot = [0, 1].map((i) => buatSlot({ label: `pengali persamaan ${i + 1}` }));
  let operasi = null;
  const tombolOp = {};
  const opsiOp = h('div', { class: 'baris-tombol', role: 'radiogroup', 'aria-label': 'Operasi' });
  [['jumlah', 'Jumlahkan (+)'], ['kurang', 'Kurangkan (−)']].forEach(([id, label]) => {
    const b = h('button', { type: 'button', class: 'tombol pilih', role: 'radio', 'aria-checked': 'false' }, label);
    b.addEventListener('click', () => {
      operasi = id;
      Object.entries(tombolOp).forEach(([k, el]) => {
        el.setAttribute('aria-checked', k === id ? 'true' : 'false');
        el.classList.remove('salah');
      });
    });
    tombolOp[id] = b;
    opsiOp.append(b);
  });
  const el = h('div', { class: 'template' },
    [0, 1].map((i) => h('div', { class: 'baris-isian' },
      h('span', { class: 'no-pers' }, `(${i + 1})`),
      pers ? persamaanEl(pers[i], ctx.vars) : `Persamaan (${i + 1})`,
      h('span', { class: 'op' }, '×'), slot[i])),
    h('p', { class: 'label-kecil' }, 'Setelah dikalikan, kedua persamaan…'),
    opsiOp);
  return {
    el,
    ambil: () => ({ m1: slot[0].nilai(), m2: slot[1].nilai(), operasi, ...(pers ? { persamaan: pers } : {}) }),
    lengkap: () => slot.every((s) => s.nilai() && s.nilai() !== '-') && operasi !== null,
    tandai: (d, benar) => {
      slot.forEach((s) => tandaiSlot(s, benar ? true : d?.pengali));
      if (operasi) tombolOp[operasi].classList.toggle('salah', !benar && d?.operasi === false);
    },
    isi: () => {},
  };
}

// ---------- substitusi ----------
function inputSubstitusi(layar, ctx) {
  const lain = ctx.vars.find((v) => v !== layar.var_sub) || ctx.vars[1];
  const s = ['konst', 'koef', 'rhs'].map((k) => buatSlot({ label: k, lebar: 'lebar' }));
  const el = h('div', { class: 'template' },
    h('div', { class: 'baris-isian' },
      s[0], h('span', { class: 'op' }, '+'), s[1], varEl(lain, ctx.vars), h('span', { class: 'op' }, '='), s[2]),
    h('p', { class: 'catatan' },
      'Kotak pertama: hasil koefisien ', varEl(layar.var_sub, ctx.vars), ' dikali nilainya (boleh negatif).'));
  return {
    el,
    ambil: () => ({ konst: s[0].nilai(), koef: s[1].nilai(), rhs: s[2].nilai() }),
    lengkap: () => s.every((x) => x.nilai() && x.nilai() !== '-'),
    tandai: (_d, benar) => s.forEach((x) => tandaiSlot(x, benar)),
    isi: () => {},
  };
}

// ---------- tandai ----------
function inputTandai(layar, ctx) {
  const info = h('p', { class: 'catatan sorot', 'aria-live': 'polite' });
  const perbarui = () => { info.textContent = `Ketuk bagian soal di atas. Sudah ditandai: ${ctx.tanda.size} bagian.`; };
  perbarui();
  ctx.onTanda = perbarui;
  return {
    el: info,
    ambil: () => ({ segmen: [...ctx.tanda] }),
    lengkap: () => ctx.tanda.size > 0,
    tandai: () => {},
    isi: () => {},
  };
}

export function buatInput(layar, ctx) {
  switch (layar.input) {
    case 'pilihan': return inputPilihan(layar, ctx);
    case 'angka': return inputAngka(layar, ctx);
    case 'persamaan2': return inputPersamaan(layar, ctx, 2);
    case 'persamaan1': return inputPersamaan(layar, ctx, 1);
    case 'pengali': return inputPengali(layar, ctx);
    case 'substitusi': return inputSubstitusi(layar, ctx);
    case 'tandai': return inputTandai(layar, ctx);
    default: return { el: h('p', {}, `Jenis input tidak dikenal: ${layar.input}`), ambil: () => ({}), lengkap: () => false, tandai() {}, isi() {} };
  }
}
