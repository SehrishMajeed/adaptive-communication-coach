from sqlalchemy import create_engine, Column, Integer, String, Float, JSON
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./adaptive_coach.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
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

# Create tables
Base.metadata.create_all(bind=engine)
