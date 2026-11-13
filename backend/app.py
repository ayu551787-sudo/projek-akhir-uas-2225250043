"""Titik masuk aplikasi Flask: melayani API (/api) dan frontend statis."""
from __future__ import annotations

import mimetypes
import os
import socket

from flask import Flask, jsonify, request

import db
from config import Config
from routes import cek, guru, log, siswa
from soal_repo import BankSoal

# Di Windows, registry kadang memetakan .js ke text/plain sehingga browser menolak ES module.
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("text/css", ".css")


def create_app(overrides: dict | None = None) -> Flask:
    app = Flask(__name__, static_folder=str(Config.FRONTEND_DIR), static_url_path="")
    app.config.from_object(Config)
    if overrides:
        app.config.update(overrides)
    app.json.ensure_ascii = False

    app.extensions["bank"] = BankSoal(app.config["SOAL_DIR"], app.config["CONTOH_DIR"])
    db.init_app(app)

    for modul in (siswa, cek, log, guru):
        app.register_blueprint(modul.bp)

    @app.get("/")
    def index():
        return app.send_static_file("index.html")

    @app.errorhandler(404)
    def tidak_ada(_e):
        if request.path.startswith("/api/"):
            return jsonify(pesan="Alamat API tidak ditemukan."), 404
        return app.send_static_file("index.html")

    @app.errorhandler(405)
    def metode_salah(_e):
        return jsonify(pesan="Metode tidak diizinkan."), 405

    return app


def _ip_lokal() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("10.255.255.255", 1))
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    aplikasi = create_app()
    if aplikasi.config["GURU_PIN"] == "1234":
        print("PERINGATAN: PIN guru masih bawaan (1234). Set variabel lingkungan GURU_PIN.")
    print(f"Buka di laptop : http://localhost:{port}")
    print(f"Buka di HP     : http://{_ip_lokal()}:{port}  (HP dan laptop di Wi-Fi yang sama)")
    aplikasi.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
