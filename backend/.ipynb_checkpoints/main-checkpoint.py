from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
import os
import uvicorn

from backend.db.models import init_database
from backend.api.routes import router
from backend.security.rate_limiter import limiter

# 1. Initialize DB tables
init_database()

# Seed demo data for student Vijay
from backend.db.models import SessionLocal, Student, ProgressLog, QuizResult
from backend.security.auth import get_password_hash
import datetime
import json

db = SessionLocal()
try:
    vijay = db.query(Student).filter(Student.username == "Vijay").first()
    hashed_pwd = get_password_hash("Hello#1234")
    if not vijay:
        new_student = Student(
            username="Vijay",
            password_hash=hashed_pwd,
            track="AI/ML"
        )
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        
        # Add study progress logs
        logs = [
            ProgressLog(
                student_id=new_student.id,
                topic="Linear Algebra",
                mode="explain",
                details=json.dumps({"difficulty": "Beginner"}),
                timestamp=datetime.datetime.utcnow() - datetime.timedelta(days=3)
            ),
            ProgressLog(
                student_id=new_student.id,
                topic="ML Algorithms",
                mode="explain",
                details=json.dumps({"difficulty": "Intermediate"}),
                timestamp=datetime.datetime.utcnow() - datetime.timedelta(days=2)
            ),
            ProgressLog(
                student_id=new_student.id,
                topic="Deep Learning",
                mode="explain",
                details=json.dumps({"difficulty": "Intermediate"}),
                timestamp=datetime.datetime.utcnow() - datetime.timedelta(days=1)
            )
        ]
        db.add_all(logs)
        
        # Add quiz results (representing mastered and weak areas)
        quizzes = [
            QuizResult(
                student_id=new_student.id,
                topic="Linear Algebra",
                score=4,
                total_questions=4,
                difficulty="beginner",
                timestamp=datetime.datetime.utcnow() - datetime.timedelta(days=3)
            ),
            QuizResult(
                student_id=new_student.id,
                topic="ML Algorithms",
                score=1,
                total_questions=4,
                difficulty="intermediate",
                timestamp=datetime.datetime.utcnow() - datetime.timedelta(days=2)
            ),
            QuizResult(
                student_id=new_student.id,
                topic="Deep Learning",
                score=3,
                total_questions=4,
                difficulty="intermediate",
                timestamp=datetime.datetime.utcnow() - datetime.timedelta(days=1)
            )
        ]
        db.add_all(quizzes)
        db.commit()
        print("[DATABASE] Demo student 'Vijay' seeded successfully.")
    else:
        # Force password hash update to match current direct bcrypt format
        vijay.password_hash = hashed_pwd
        db.commit()
        print("[DATABASE] Demo student 'Vijay' credentials synchronized.")
finally:
    db.close()

# 2. Setup FastAPI App
app = FastAPI(
    title="LearnForge API",
    description="Backend AI study orchestration & MCP tools service for software engineering students",
    version="1.0.0"
)

# 3. Register Slowapi state & handler
app.state.limiter = limiter
@app.exception_handler(RateLimitExceeded)
def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Rate limit exceeded."}
    )

# 4. CORS Configurations
origins_str = os.environ.get("CORS_ORIGINS", "http://localhost:3000")
origins = [origin.strip() for origin in origins_str.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. API Router mounting
app.include_router(router, prefix="/api")

# 6. Health check for Railway deployment
@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/")
def read_root():
    return {"message": "Welcome to LearnForge AI Study API. Query /health for status."}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
