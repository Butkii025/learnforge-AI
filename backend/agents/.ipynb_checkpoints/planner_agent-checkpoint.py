import json
import os
import urllib.request
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.db.models import QuizResult

# Default plans based on track
TRACK_ROADMAPS = {
    "CSE": [
        {"day": 1, "topic": "Data Structures - Array & List Complexity", "time": "2 hours", "resource": "GeeksforGeeks, CLRS Chapter 10"},
        {"day": 2, "topic": "Algorithms - Binary Search & Quick Sort", "time": "2.5 hours", "resource": "MIT OpenCourseWare Lecture 3"},
        {"day": 3, "topic": "Operating Systems - Process Scheduling", "time": "2 hours", "resource": "Silberschatz Chapter 5"},
        {"day": 4, "topic": "DBMS - Indexing & B-Trees", "time": "2.5 hours", "resource": "Database System Concepts Chapter 11"},
        {"day": 5, "topic": "Computer Networks - TCP/IP Flow Control", "time": "2 hours", "resource": "Tanenbaum Chapter 6"},
        {"day": 6, "topic": "System Design - Load Balancers & Caching", "time": "3 hours", "resource": "System Design Primer GitHub"},
        {"day": 7, "topic": "Weekly Assessment & Code Practice", "time": "2 hours", "resource": "LeetCode Easy-Medium problems"}
    ],
    "IT": [
        {"day": 1, "topic": "Networking - DNS Protocols", "time": "2 hours", "resource": "Cisco Academy Modules"},
        {"day": 2, "topic": "Cybersecurity - Cryptographic Handshakes", "time": "2.5 hours", "resource": "OWASP top 10 guides"},
        {"day": 3, "topic": "Cloud Computing - AWS S3 & EC2 Security", "time": "2 hours", "resource": "AWS Practitioner tutorials"},
        {"day": 4, "topic": "DevOps - Docker Containers & Volumes", "time": "2.5 hours", "resource": "Docker documentation guides"},
        {"day": 5, "topic": "Linux - Shell Scripting & Grep/Sed", "time": "2 hours", "resource": "Linux Command Line book"},
        {"day": 6, "topic": "DevOps - GitHub Actions & CI/CD Pipelines", "time": "3 hours", "resource": "GitHub docs"},
        {"day": 7, "topic": "Self-Assessment & Camp lab exercise", "time": "2 hours", "resource": "Local Sandboxed script lab"}
    ],
    "AI/ML": [
        {"day": 1, "topic": "Linear Algebra - Matrix Inversion & SVD", "time": "2.5 hours", "resource": "Gilbert Strang MIT Lectures"},
        {"day": 2, "topic": "ML Algorithms - Gradient Descent Mechanics", "time": "2 hours", "resource": "Andrew Ng Coursera Lectures"},
        {"day": 3, "topic": "Deep Learning - Activation Functions & MLP", "time": "2.5 hours", "resource": "Deep Learning Book Chapter 6"},
        {"day": 4, "topic": "Deep Learning - Backpropagation chain rule", "time": "3 hours", "resource": "3Blue1Brown Backprop video"},
        {"day": 5, "topic": "NLP - Tokenization & Word Embeddings", "time": "2 hours", "resource": "Stanford CS224n Lecture notes"},
        {"day": 6, "topic": "MLOps - Model Registry & Feature Store", "time": "2.5 hours", "resource": "MLflow documentation docs"},
        {"day": 7, "topic": "Weekly Project - Training MNIST from scratch", "time": "3 hours", "resource": "PyTorch Getting Started guide"}
    ],
    "Data Science": [
        {"day": 1, "topic": "Statistics - Hypothesis Testing & Central Limit Theorem", "time": "2 hours", "resource": "Khan Academy Stats course"},
        {"day": 2, "topic": "Pandas - Data Wrangling & Merge/Concat", "time": "2 hours", "resource": "Python for Data Analysis book"},
        {"day": 3, "topic": "SQL - Joins, GroupBy, and Window Functions", "time": "2.5 hours", "resource": "LeetCode SQL problems"},
        {"day": 4, "topic": "Data Visualization - Matplotlib & Seaborn", "time": "2 hours", "resource": "PyViz tutorials"},
        {"day": 5, "topic": "Feature Engineering - Scaling & One-hot encoding", "time": "2 hours", "resource": "Scikit-Learn documentation"},
        {"day": 6, "topic": "Exploratory Data Analysis (EDA) project", "time": "3 hours", "resource": "Kaggle introductory datasets"},
        {"day": 7, "topic": "Track Assessment - SQL & Pandas exercises", "time": "2 hours", "resource": "Kaggle learning hub"}
    ]
}

def generate_study_plan(student_id: int, goal: str, track: str, db: Session) -> List[Dict[str, Any]]:
    """
    Builds a weekly study plan.
    Scans SQLite DB for weak topics from QuizResult (score < 70%) and injects 
    custom study slots prioritizing those topics.
    """
    # 1. Fetch student's recent low scores
    quizzes = db.query(QuizResult).filter(QuizResult.student_id == student_id).all()
    weak_topics = []
    for q in quizzes:
        pct = (q.score / q.total_questions) * 100
        if pct < 70 and q.topic not in weak_topics:
            weak_topics.append(q.topic)
            
    # 2. Get default roadmap for track
    roadmap = TRACK_ROADMAPS.get(track, TRACK_ROADMAPS["CSE"]).copy()
    
    # 3. Inject weak topics into Days 3 and 5 if available to prioritize them
    if weak_topics:
        for idx, day_idx in enumerate([2, 4]): # Day 3 (index 2) and Day 5 (index 4)
            if idx < len(weak_topics):
                roadmap[day_idx] = {
                    "day": day_idx + 1,
                    "topic": f"🔥 RE-STUDY (Weak Area): {weak_topics[idx].title()}",
                    "time": "3 hours",
                    "resource": f"Review previous quiz answers & check online explanations on {weak_topics[idx]}"
                }
                
    # 4. Attempt to customize with local LLM if running
    ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    url = f"{ollama_host}/api/chat"
    
    prompt = (
        f"Generate a 7-day study plan to achieve this goal: '{goal}'. "
        f"The student is in the '{track}' track and has low scores in these concepts: {weak_topics}. "
        "Return ONLY a valid JSON list of 7 items, where each item has this structure:\n"
        "{\n"
        "  \"day\": 1,\n"
        "  \"topic\": \"Topic name\",\n"
        "  \"time\": \"Duration\",\n"
        "  \"resource\": \"Reference materials\"\n"
        "}\n"
        "Do not output markdown."
    )
    
    req_body = {
        "model": "gemma3",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "format": "json"
    }
    
    try:
        data = json.dumps(req_body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=3) as response:
            resp_data = json.loads(response.read().decode("utf-8"))
            content = resp_data.get("message", {}).get("content", "")
            custom_plan = json.loads(content)
            if isinstance(custom_plan, list) and len(custom_plan) > 0:
                return custom_plan
    except Exception:
        pass
        
    return roadmap
