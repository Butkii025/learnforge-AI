from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from backend.db.models import get_db, Student, QuizResult, ProgressLog
from backend.security.auth import get_current_student, create_access_token, get_password_hash, verify_password
from backend.security.rate_limiter import limiter
from backend.security.sanitizer import check_prompt_injection
from backend.agents.orchestrator import orchestrate_study_task
from backend.mcp.tools.arxiv_tool import search_arxiv
from backend.mcp.tools.sandbox_tool import run_code_sandbox
from backend.mcp.server import get_concept_graph
from backend.mcp.tools.progress_tool import get_student_progress
import json

router = APIRouter()

# --- Auth Pydantic Schemas ---
class StudentRegister(BaseModel):
    username: str
    password: str
    track: str = "CSE"

class StudentLogin(BaseModel):
    username: str
    password: str

class TrackUpdate(BaseModel):
    track: str

# --- Agent Schemas ---
class AgentQuery(BaseModel):
    mode: str # explain, quiz, plan, review
    query: str
    meta: Optional[Dict[str, Any]] = {}

# --- Quiz Log Schema ---
class QuizLogSchema(BaseModel):
    topic: str
    score: float
    total_questions: int
    difficulty: str

# --- Auth Routes ---
@router.post("/auth/register")
@limiter.limit("10/minute")
def register(request: Request, data: StudentRegister, db: Session = Depends(get_db)):
    # Sanitize input
    username = check_prompt_injection(data.username).strip()
    if not username or len(data.password) < 4:
        raise HTTPException(status_code=400, detail="Invalid username or password (min 4 chars).")
        
    db_student = db.query(Student).filter(Student.username == username).first()
    if db_student:
        raise HTTPException(status_code=400, detail="Username is already registered.")
        
    hashed_pwd = get_password_hash(data.password)
    student = Student(
        username=username,
        password_hash=hashed_pwd,
        track=data.track
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    
    token = create_access_token(data={"sub": student.username})
    return {"access_token": token, "token_type": "bearer", "username": student.username, "track": student.track}

@router.post("/auth/login")
@limiter.limit("20/minute")
def login(request: Request, data: StudentLogin, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.username == data.username).first()
    if not student or not verify_password(data.password, student.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(data={"sub": student.username})
    return {"access_token": token, "token_type": "bearer", "username": student.username, "track": student.track}

@router.get("/auth/me")
def get_me(current_student: Student = Depends(get_current_student)):
    return {"id": current_student.id, "username": current_student.username, "track": current_student.track}

@router.put("/auth/track")
def update_track(data: TrackUpdate, current_student: Student = Depends(get_current_student), db: Session = Depends(get_db)):
    track = data.track.upper().strip()
    if track not in ["CSE", "IT", "AI/ML", "DATA SCIENCE"]:
        raise HTTPException(status_code=400, detail="Invalid study track selection.")
    current_student.track = track
    db.commit()
    return {"success": True, "track": current_student.track}

# --- Multi-Agent Core Route ---
@router.post("/agent/query")
@limiter.limit("15/minute")
def query_agent(
    request: Request,
    data: AgentQuery,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    try:
        result = orchestrate_study_task(
            student_id=current_student.id,
            mode=data.mode,
            query=data.query,
            meta=data.meta,
            db=db
        )
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Progress Analytics Route ---
@router.get("/student/progress")
def get_progress(current_student: Student = Depends(get_current_student), db: Session = Depends(get_db)):
    return get_student_progress(current_student.id, db)

@router.post("/student/quiz-result")
def log_quiz(
    data: QuizLogSchema,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    result = QuizResult(
        student_id=current_student.id,
        topic=check_prompt_injection(data.topic),
        score=data.score,
        total_questions=data.total_questions,
        difficulty=data.difficulty
    )
    db.add(result)
    
    # Also log this as a progress session
    log_detail = {"score": data.score, "total": data.total_questions, "difficulty": data.difficulty}
    log = ProgressLog(
        student_id=current_student.id,
        topic=data.topic,
        mode="quiz",
        details=json.dumps(log_detail)
    )
    db.add(log)
    
    db.commit()
    return {"success": True}

# --- MCP Tool Proxies ---
class ArxivQuery(BaseModel):
    query: str

class CodeSandboxQuery(BaseModel):
    code: str

class ConceptGraphQuery(BaseModel):
    topic: str

@router.post("/mcp/arxiv")
@limiter.limit("10/minute")
def proxy_arxiv(request: Request, data: ArxivQuery, current_student: Student = Depends(get_current_student)):
    sanitized = check_prompt_injection(data.query)
    return search_arxiv(sanitized)

@router.post("/mcp/sandbox")
@limiter.limit("10/minute")
def proxy_sandbox(request: Request, data: CodeSandboxQuery, current_student: Student = Depends(get_current_student)):
    # Do not check prompt injection here since students write actual programming code
    return run_code_sandbox(data.code)

@router.post("/mcp/concept-graph")
def proxy_concept_graph(data: ConceptGraphQuery, current_student: Student = Depends(get_current_student)):
    sanitized = check_prompt_injection(data.topic)
    return get_concept_graph(sanitized)
