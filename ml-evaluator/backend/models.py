"""SQLAlchemy ORM models for ML Evaluator."""

from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# ── Database Setup ──
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./candidates.db")
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Candidate(Base):
    """Candidate evaluation result."""
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    raw_response = Column(Text)  # Full response text submitted
    total_score = Column(Float)  # 0-100
    decision = Column(String(50))  # SELECTED, BORDERLINE, REJECTED
    confidence = Column(Float)  # 0-100
    grade = Column(String(10))  # A+, A, B+, B, C+, C, D, F
    star_rating = Column(Integer)  # 1-5
    rank = Column(Integer)  # Overall rank among batch
    percentile = Column(Float)  # 0-100

    # Detailed breakdown (stored as JSON)
    breakdown = Column(JSON)  # Per-criterion scores and details
    point_scores = Column(JSON)  # Detailed point-by-point evaluation
    
    # Analysis fields
    coverage = Column(Float)  # % of rubric criteria covered
    keyword_match_rate = Column(Float)  # % of rubric keywords found
    consistency_score = Column(Float)  # Score consistency 0-100
    criteria_passed = Column(Integer)  # # of criteria passed
    criteria_total = Column(Integer)  # Total # of criteria
    technical_breadth = Column(Integer)  # # of matched keywords
    technical_depth_score = Column(Float)  # 0-100
    experience_level = Column(String(50))  # Senior, Mid-Level, Junior
    experience_confidence = Column(Float)  # 0-1
    must_have_pass_rate = Column(Float)  # % of must-have criteria passed
    response_depth = Column(Float)  # 0-100
    
    # Lists (stored as JSON)
    matched_keywords = Column(JSON)  # List of matched keywords
    missing_keywords = Column(JSON)  # List of missing keywords
    strengths = Column(JSON)  # List of strength descriptions
    weaknesses = Column(JSON)  # List of weakness descriptions
    gaps = Column(JSON)  # List of gap descriptions
    
    # Reasoning
    reason = Column(Text)  # Full reason explanation
    recommendation = Column(Text)  # Action recommendation
    response_snippet = Column(Text)  # Preview of response
    
    # Borderline analysis (if applicable)
    borderline_analysis = Column(JSON)  # {proximity_to_hire, gap_percentage, interview_questions, improvements, verdict}
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    rubric_hash = Column(String(64))  # SHA256 hash of rubric used for grouping results


class Rubric(Base):
    """Stored rubric templates."""
    __tablename__ = "rubrics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    content = Column(Text)  # Full rubric text
    role = Column(String(255))  # e.g., "Senior Backend Engineer"
    description = Column(Text)
    criteria_count = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EvaluationBatch(Base):
    """Group of candidates evaluated together."""
    __tablename__ = "evaluation_batches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    rubric_id = Column(Integer)
    rubric_hash = Column(String(64), index=True)
    total_candidates = Column(Integer)
    hired_count = Column(Integer)
    borderline_count = Column(Integer)
    rejected_count = Column(Integer)
    eval_time_seconds = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# ── Create tables ──
def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
