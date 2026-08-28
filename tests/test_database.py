import os
import pytest
from unittest.mock import patch
import importlib

# We need to mock create_engine and create_all before importing database
@pytest.fixture(autouse=True)
def mock_db_connections():
    with patch("sqlalchemy.create_engine") as mock_engine, \
         patch("sqlalchemy.orm.declarative_base") as mock_base:
        # Prevent Base.metadata.create_all from connecting
        yield mock_engine, mock_base

def test_database_url_absent_defaults_to_sqlite(mock_db_connections):
    with patch.dict(os.environ, clear=True):
        import backend.app.models.database as db_module
        importlib.reload(db_module)
        assert db_module.SQLALCHEMY_DATABASE_URL == "sqlite:///./adaptive_coach.db"
        assert db_module.engine_kwargs.get("connect_args") == {"check_same_thread": False}
        assert "pool_pre_ping" not in db_module.engine_kwargs

def test_postgres_legacy_url_normalized(mock_db_connections):
    with patch.dict(os.environ, {"DATABASE_URL": "postgres://user:pass@host/db"}):
        import backend.app.models.database as db_module
        importlib.reload(db_module)
        assert db_module.SQLALCHEMY_DATABASE_URL == "postgresql://user:pass@host/db"
        assert db_module.engine_kwargs.get("pool_pre_ping") is True
        assert "connect_args" not in db_module.engine_kwargs

def test_postgresql_url_accepted(mock_db_connections):
    with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@host/db"}):
        import backend.app.models.database as db_module
        importlib.reload(db_module)
        assert db_module.SQLALCHEMY_DATABASE_URL == "postgresql://user:pass@host/db"
        assert db_module.engine_kwargs.get("pool_pre_ping") is True
        assert "connect_args" not in db_module.engine_kwargs

def test_invalid_database_url_fails_fast(mock_db_connections):
    with patch.dict(os.environ, {"DATABASE_URL": "mysql://user:pass@host/db"}):
        with pytest.raises(ValueError, match="Invalid DATABASE_URL. Must start with postgres://, postgresql://, or sqlite:///"):
            import backend.app.models.database as db_module
            importlib.reload(db_module)

def test_empty_database_url_falls_back(mock_db_connections):
    with patch.dict(os.environ, {"DATABASE_URL": "   "}):
        import backend.app.models.database as db_module
        importlib.reload(db_module)
        assert db_module.SQLALCHEMY_DATABASE_URL == "sqlite:///./adaptive_coach.db"
