from backend.security.sanitizer import check_prompt_injection
from backend.agents.tutor_agent import explain_concept
from backend.agents.quiz_agent import generate_assessment
from backend.agents.planner_agent import generate_study_plan
from backend.agents.code_review_agent import review_code
from backend.db.models import ProgressLog, Student
from sqlalchemy.orm import Session
import json
from typing import Dict, Any

def orchestrate_study_task(
    student_id: int, 
    mode: str, 
    query: str, 
    meta: Dict[str, Any], 
    db: Session
) -> Dict[str, Any]:
    """
    Main ADK Orchestrator Root Agent.
    1. Sanitizes user input against prompt injection.
    2. Logs the activity to SQLite DB.
    3. Delegates requests to the correct specialist agent.
    """
    # 1. Input Sanitization
    sanitized_query = check_prompt_injection(query)
    
    # Fetch student track
    student = db.query(Student).filter(Student.id == student_id).first()
    track = student.track if student else "CSE"
    
    # 2. Database Log
    log = ProgressLog(
        student_id=student_id,
        topic=sanitized_query[:100] if mode != "review" else "Submitted Code Review",
        mode=mode,
        details=json.dumps(meta)
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    
    # 3. Delegate to Specialist Agents
    result = {}
    if mode == "explain":
        difficulty = meta.get("difficulty", "Intermediate")
        result = {
            "mode": mode,
            "topic": sanitized_query,
            "output": explain_concept(sanitized_query, track, difficulty)
        }
        
    elif mode == "quiz":
        difficulty = meta.get("difficulty", "intermediate")
        result = {
            "mode": mode,
            "topic": sanitized_query,
            "output": generate_assessment(sanitized_query, difficulty)
        }
        
    elif mode == "plan":
        goal = sanitized_query
        result = {
            "mode": mode,
            "goal": goal,
            "output": generate_study_plan(student_id, goal, track, db)
        }
        
    elif mode == "review":
        language = meta.get("language", "python")
        result = {
            "mode": mode,
            "language": language,
            "output": review_code(sanitized_query, language)
        }
        
    else:
        result = {"error": f"Unsupported agent mode: {mode}"}
        
    return result
