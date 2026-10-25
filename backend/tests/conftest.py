import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))
os.environ["DATABASE_URL"] = "sqlite://"

from app.core.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def job_data():
    return {
        "title": "Senior Platform Engineer",
        "department": "Engineering",
        "description": "Build reliable systems for the hiring platform.",
        "location": "remote",
        "salary_min": 90000,
        "salary_max": 140000,
        "required_skills": ["Python", "FastAPI"],
        "max_applicants": None,
        "deadline": "2099-12-31",
    }


@pytest.fixture()
def application_data():
    return {
        "applicant_name": "Ada Lovelace",
        "email": "ada@example.com",
        "years_experience": 5,
        "cv_summary": "Backend engineer focused on dependable APIs.",
        "linkedin_url": "https://www.linkedin.com/in/ada",
    }

