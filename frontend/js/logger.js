// Antrean log peristiwa untuk penelitian (lihat docs/EVALUASI.md §3).
// Dikirim berkelompok setiap 10 detik, dan saat tab disembunyikan/ditutup.
import { state } from './state.js';

let antrean = [];

export function catat(tipe, info = {}) {
  const { soal_id, layar_id, main_id, ...data } = info;
  antrean.push({ tipe, soal_id, layar_id, main_id, data, waktu: new Date().toISOString() });
  if (antrean.length >= 50) kirim();
}

export function kirim(pakaiBeacon = false) {
  const sesi = state.sesi();
  if (!sesi || !antrean.length) return;
  const paket = { sesi_id: sesi.sesi_id, peristiwa: antrean.splice(0, 100) };
  const body = JSON.stringify(paket);
  if (pakaiBeacon && navigator.sendBeacon) {
    navigator.sendBeacon('/api/log', new Blob([body], { type: 'application/json' }));
    return;
  }
  fetch('/api/log', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body, keepalive: true })
    .catch(() => { antrean = paket.peristiwa.concat(antrean).slice(0, 500); });
}

setInterval(() => kirim(), 10000);
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'hidden') {
    catat('aplikasi_sembunyi');
    kirim(true);
  } else {
    catat('aplikasi_tampil');
  }
});
