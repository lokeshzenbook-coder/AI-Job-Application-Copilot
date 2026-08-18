from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import get_settings
from app.database import Base, get_db
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def _setup_env():
    os.environ["DATABASE_URL"] = "sqlite:///./test_jobs.db"
    os.environ["ANTHROPIC_API_KEY"] = ""
    os.environ["APIFY_API_TOKEN"] = ""


@pytest.fixture(scope="session")
def engine():
    eng = create_engine("sqlite:///./test_jobs.db", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=eng)
    yield eng
    Base.metadata.drop_all(bind=eng)
    db_path = Path("test_jobs.db")
    if db_path.exists():
        db_path.unlink()


@pytest.fixture()
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
