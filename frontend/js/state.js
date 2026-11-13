// Penyimpanan lokal (per perangkat). Semua akses dibungkus try/catch karena
// localStorage bisa diblokir (mode privat). Data utama tetap di server.

function baca(kunci) {
  try {
    const v = localStorage.getItem(kunci);
    return v ? JSON.parse(v) : null;
  } catch {
    return null;
  }
}

function tulis(kunci, nilai) {
  try {
    if (nilai === null) localStorage.removeItem(kunci);
    else localStorage.setItem(kunci, JSON.stringify(nilai));
  } catch { /* abaikan */ }
}

let sesiMemori = null;

export const state = {
  sesi() {
    return sesiMemori || (sesiMemori = baca('spldv:sesi'));
  },
  setSesi(s) {
    sesiMemori = s;
    tulis('spldv:sesi', s);
  },
  keluar() {
    sesiMemori = null;
    tulis('spldv:sesi', null);
  },
  // Progres pengerjaan yang sedang berjalan, agar bisa dilanjutkan setelah browser ditutup.
  main(soalId) {
    const s = this.sesi();
    const data = baca(`spldv:main:${soalId}`);
    return data && s && data.sesiKode === s.kode_siswa ? data : null;
  },
  setMain(soalId, data) {
    const s = this.sesi();
    tulis(`spldv:main:${soalId}`, data ? { ...data, sesiKode: s?.kode_siswa } : null);
  },
};
