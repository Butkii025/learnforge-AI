from sqlalchemy.orm import Session
from backend.db.models import ProgressLog, QuizResult, Student
from typing import Dict, Any, List

def get_student_progress(student_id: int, db: Session) -> Dict[str, Any]:
    """
    Reads study logs and quiz performance from SQLite.
    Returns aggregated progress data and concept mastery stats.
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return {"error": f"Student with ID {student_id} not found."}
        
    logs = db.query(ProgressLog).filter(ProgressLog.student_id == student_id).all()
    quizzes = db.query(QuizResult).filter(QuizResult.student_id == student_id).all()
    
    # 1. Study Sessions Log
    mode_counts = {}
    for log in logs:
        mode_counts[log.mode] = mode_counts.get(log.mode, 0) + 1
        
    # 2. Quiz Performance Summary
    total_quizzes = len(quizzes)
    avg_score = 0.0
    quiz_history = []
    weak_topics = set()
    mastered_topics = set()
    
    if total_quizzes > 0:
        total_score_pct = 0.0
        for quiz in quizzes:
            pct = (quiz.score / quiz.total_questions) * 100
            total_score_pct += pct
            quiz_history.append({
                "topic": quiz.topic,
                "score_pct": pct,
                "difficulty": quiz.difficulty,
                "timestamp": quiz.timestamp.isoformat()
            })
            # Assess weak vs mastered topics
            if pct < 70:
                weak_topics.add(quiz.topic)
            else:
                mastered_topics.add(quiz.topic)
                
        avg_score = round(total_score_pct / total_quizzes, 2)
        
    # Exclude mastered topics from weak list
    weak_topics = list(weak_topics - mastered_topics)
    
    # 3. Compile timeline data
    recent_activities = []
    # Mix logs and quizzes, sort by timestamp
    for log in logs[-5:]:
        recent_activities.append({
            "type": "study",
            "topic": log.topic,
            "mode": log.mode,
            "timestamp": log.timestamp.isoformat(),
            "description": f"Studied {log.topic} using mode {log.mode}"
        })
        
    for quiz in quizzes[-5:]:
        recent_activities.append({
            "type": "quiz",
            "topic": quiz.topic,
            "score": f"{quiz.score}/{quiz.total_questions}",
            "timestamp": quiz.timestamp.isoformat(),
            "description": f"Completed {quiz.topic} Quiz: {quiz.score}/{quiz.total_questions}"
        })
        
    recent_activities = sorted(recent_activities, key=lambda x: x["timestamp"], reverse=True)[:5]
    
    return {
        "student_id": student_id,
        "username": student.username,
        "track": student.track,
        "total_sessions": len(logs),
        "total_quizzes": total_quizzes,
        "average_score": avg_score,
        "mode_distribution": mode_counts,
        "weak_topics": weak_topics,
        "mastered_topics": list(mastered_topics),
        "recent_activity": recent_activities,
        "quiz_history": quiz_history
    }
