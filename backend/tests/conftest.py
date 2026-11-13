import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app import create_app  # noqa: E402
from config import Config  # noqa: E402
from soal_repo import BankSoal  # noqa: E402


@pytest.fixture(scope="session")
def bank_soal() -> BankSoal:
    return BankSoal(Config.SOAL_DIR, Config.CONTOH_DIR)


@pytest.fixture()
def app(tmp_path):
    return create_app({"DB_PATH": str(tmp_path / "test.db"), "GURU_PIN": "9999", "TESTING": True})


@pytest.fixture()
def client(app):
    return app.test_client()
