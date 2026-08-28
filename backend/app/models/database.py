import os
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON
from sqlalchemy.orm import declarative_base, sessionmaker

raw_db_url = os.environ.get("DATABASE_URL", "").strip()

if not raw_db_url:
    # Fallback to local SQLite if no DATABASE_URL is provided
    SQLALCHEMY_DATABASE_URL = "sqlite:///./adaptive_coach.db"
else:
    # Normalize legacy Render/Heroku postgres:// to postgresql://
    if raw_db_url.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URL = raw_db_url.replace("postgres://", "postgresql://", 1)
    else:
        SQLALCHEMY_DATABASE_URL = raw_db_url

    # Fail fast on obviously invalid configurations
    if not SQLALCHEMY_DATABASE_URL.startswith(("postgresql://", "sqlite:///")):
        raise ValueError("Invalid DATABASE_URL. Must start with postgres://, postgresql://, or sqlite:///")

# Configure engine arguments based on dialect
engine_kwargs = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite:///"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # For robust hosted connections
    engine_kwargs["pool_pre_ping"] = True

engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    
    # Rolling averages
    avg_clarity = Column(Float, default=0.0)
    avg_structure = Column(Float, default=0.0)
    avg_conciseness = Column(Float, default=0.0)
    avg_audience_awareness = Column(Float, default=0.0)
    
    # JSON lists of strings
    recurring_strengths = Column(JSON, default=list)
    recurring_weaknesses = Column(JSON, default=list)
    current_focus_area = Column(String, nullable=True)
    
    total_sessions = Column(Integer, default=0)
    
class CoachingSession(Base):
    __tablename__ = "coaching_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    scenario = Column(String)

class CoachingAttempt(Base):
    __tablename__ = "coaching_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    attempt_number = Column(Integer)
    transcript = Column(String)
    duration_seconds = Column(Float)
    
    # Metrics
    wpm = Column(Float, nullable=True)
    filler_words_count = Column(Integer, default=0)
    
    # Evaluation
    clarity = Column(Float, nullable=True)
    structure = Column(Float, nullable=True)
    conciseness = Column(Float, nullable=True)
    audience_awareness = Column(Float, nullable=True)
    
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)
    focus_area = Column(String, nullable=True)

# Create tables safely
Base.metadata.create_all(bind=engine)
