from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import datetime
import os

Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    track = Column(String, default="CSE") # CSE, IT, AI/ML, Data Science
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    logs = relationship("ProgressLog", back_populates="student", cascade="all, delete-orphan")
    quiz_results = relationship("QuizResult", back_populates="student", cascade="all, delete-orphan")

class ProgressLog(Base):
    __tablename__ = 'progress_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    topic = Column(String, nullable=False)
    mode = Column(String, nullable=False) # explain, quiz, plan, review
    details = Column(String, nullable=True) # JSON or descriptive text of what was studied
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    student = relationship("Student", back_populates="logs")

class QuizResult(Base):
    __tablename__ = 'quiz_results'
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    topic = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    total_questions = Column(Integer, nullable=False)
    difficulty = Column(String, nullable=False) # beginner, intermediate, advanced
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    student = relationship("Student", back_populates="quiz_results")

# Database session helpers
DB_URL = os.environ.get("DATABASE_URL", "sqlite:///./progress.db")

# Ensure db directory exists if SQLite
if DB_URL.startswith("sqlite:///"):
    db_file = DB_URL.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_file)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
