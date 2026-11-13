"""Utilitas bersama untuk route API."""
from __future__ import annotations

from flask import abort, current_app, jsonify, make_response, request

from soal_repo import BankSoal


def bank() -> BankSoal:
    return current_app.extensions["bank"]


def body() -> dict:
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        gagal("Data harus berupa JSON.")
    return data


def gagal(pesan: str, kode: int = 400):
    abort(make_response(jsonify(pesan=pesan), kode))


def ambil_int(data: dict, nama: str) -> int:
    nilai = data.get(nama)
    if isinstance(nilai, bool) or not isinstance(nilai, int):
        gagal(f"'{nama}' harus berupa bilangan bulat.")
    return nilai


def ambil_str(data: dict, nama: str, maks: int = 100, wajib: bool = True) -> str | None:
    nilai = data.get(nama)
    if not wajib and (nilai is None or (isinstance(nilai, str) and not nilai.strip())):
        return None
    if not isinstance(nilai, str) or not nilai.strip():
        gagal(f"'{nama}' wajib diisi.")
    if len(nilai) > maks:
        gagal(f"'{nama}' terlalu panjang.")
    return nilai.strip()
