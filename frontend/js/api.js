// Pembungkus fetch ke API Python.

export class ApiError extends Error {
  constructor(pesan, status) {
    super(pesan);
    this.status = status;
  }
}

async function minta(metode, url, body, headers = {}) {
  let res;
  try {
    res = await fetch(url, {
      method: metode,
      headers: { 'Content-Type': 'application/json', ...headers },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError('Tidak dapat terhubung ke server. Periksa koneksi internet/Wi-Fi.', 0);
  }
  let data = null;
  try { data = await res.json(); } catch { /* bukan JSON */ }
  if (!res.ok) throw new ApiError(data?.pesan || `Terjadi kesalahan (${res.status}).`, res.status);
  return data;
}

export const api = {
  sesi: (kode_siswa, kelas, perangkat) => minta('POST', '/api/sesi', { kode_siswa, kelas, perangkat }),
  progres: (sesi_id) => minta('GET', `/api/progres?sesi_id=${encodeURIComponent(sesi_id)}`),
  soal: (id) => minta('GET', `/api/soal/${encodeURIComponent(id)}`),
  contoh: (id) => minta('GET', `/api/contoh/${encodeURIComponent(id)}`),
  mulai: (sesi_id, soal_id) => minta('POST', '/api/main', { sesi_id, soal_id }),
  cek: (main_id, layar_id, jawaban, durasi_ms) =>
    minta('POST', '/api/cek-langkah', { main_id, layar_id, jawaban, durasi_ms }),
  petunjuk: (main_id, layar_id, tingkat) => minta('POST', '/api/petunjuk', { main_id, layar_id, tingkat }),
  lewati: (main_id, layar_id) => minta('POST', '/api/lewati', { main_id, layar_id }),
  selesai: (main_id) => minta('POST', `/api/main/${main_id}/selesai`),
  hasil: (main_id) => minta('GET', `/api/main/${main_id}/hasil`),
  alat: (nama, body) => minta('POST', `/api/alat/${nama}`, body),
  guruRekap: (pin) => minta('GET', '/api/guru/rekap', undefined, { 'X-PIN': pin }),
  async guruEkspor(pin, tabel) {
    const res = await fetch(`/api/guru/ekspor.csv?tabel=${encodeURIComponent(tabel)}`, { headers: { 'X-PIN': pin } });
    if (!res.ok) throw new ApiError('Gagal mengekspor data.', res.status);
    return res.blob();
  },
};
