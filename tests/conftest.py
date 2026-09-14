import json
import os
from pathlib import Path
from unittest.mock import Mock

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["LANGSMITH_TRACING"] = "false"
os.environ.pop("GEMINI_API_KEY", None)
os.environ.pop("GOOGLE_API_KEY", None)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.app.main import app, get_db
from backend.app.models.database import Base
from backend.app.domain.evaluation import CommunicationEvaluation


@pytest.fixture
def contract():
    return json.loads((Path(__file__).parent / "fixtures/attempt-response.json").read_text())


@pytest.fixture(autouse=True)
def forbid_live_provider(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Live provider calls are forbidden in offline tests")
    monkeypatch.setattr("backend.app.services.llm_provider.genai.Client", forbidden)


@pytest.fixture
def evaluator(monkeypatch, contract):
    fake = Mock(return_value=CommunicationEvaluation(**contract["evaluation"]))
    monkeypatch.setattr("backend.app.agent.nodes.evaluate_communication", fake)
    return fake


@pytest.fixture
def database():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    with factory() as session:
        yield session
    engine.dispose()


@pytest.fixture
def client(database):
    app.dependency_overrides[get_db] = lambda: database
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
