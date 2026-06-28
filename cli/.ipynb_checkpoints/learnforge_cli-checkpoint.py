#!/usr/bin/env python
import argparse
import json
import os
import sys
import urllib.request
import urllib.error

CONFIG_FILE = os.path.expanduser("~/.learnforge_cli_config.json")
DEFAULT_API_URL = "http://localhost:8000"

def load_auth_token(api_url: str) -> str:
    """
    Loads token from config file.
    If not found, automatically logs in as default demo user for easy evaluation.
    """
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                if config.get("token"):
                    return config.get("token")
        except Exception:
            pass
            
    # Auto-register and login demo credentials
    print("[CLI] Initializing automatic demo credentials for evaluation...")
    reg_url = f"{api_url}/api/auth/register"
    login_url = f"{api_url}/api/auth/login"
    
    demo_user = {"username": "cli_student_judge", "password": "demo_password_123", "track": "CSE"}
    
    # 1. Register
    try:
        data = json.dumps(demo_user).encode("utf-8")
        req = urllib.request.Request(reg_url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=3) as r:
            pass
    except Exception:
        # User might already be registered
        pass
        
    # 2. Login
    try:
        login_payload = {"username": "cli_student_judge", "password": "demo_password_123"}
        data = json.dumps(login_payload).encode("utf-8")
        req = urllib.request.Request(login_url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=3) as r:
            resp = json.loads(r.read().decode("utf-8"))
            token = resp.get("access_token")
            # Save token
            with open(CONFIG_FILE, "w") as f:
                json.dump({"token": token}, f)
            print("[CLI] Automatic authentication successful.\n")
            return token
    except Exception as e:
        print(f"[Error] Automatic login failed: {str(e)}")
        print("Please ensure the FastAPI backend is running locally at http://localhost:8000")
        sys.exit(1)

def query_agent_api(mode: str, query: str, meta: dict, api_url: str):
    """Sends requests directly to the study agent API endpoint."""
    token = load_auth_token(api_url)
    url = f"{api_url}/api/agent/query"
    
    payload = {
        "mode": mode,
        "query": query,
        "meta": meta
    }
    
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, 
            data=data, 
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )
        with urllib.request.urlopen(req) as response:
            resp_data = json.loads(response.read().decode("utf-8"))
            return resp_data
    except urllib.error.HTTPError as e:
        try:
            err_detail = json.loads(e.read().decode("utf-8")).get("detail", str(e))
        except Exception:
            err_detail = str(e)
        print(f"Error querying study agent: {err_detail}")
        sys.exit(1)
    except Exception as e:
        print(f"Connection Error: {str(e)}")
        print(f"Is the server running at {api_url}?")
        sys.exit(1)

def handle_study(args):
    print(f"=== Consult Study Agent (Concept: {args.topic}) ===")
    res = query_agent_api("explain", args.topic, {"difficulty": "Intermediate"}, args.api_url)
    print(res.get("output", "No response received."))

def handle_quiz(args):
    print(f"=== Adaptive MCQ Assessment (Topic: {args.topic}) ===")
    res = query_agent_api("quiz", args.topic, {"difficulty": args.difficulty}, args.api_url)
    questions = res.get("output", [])
    
    if not questions or not isinstance(questions, list):
        print("Failed to generate quiz questions.")
        return
        
    for idx, q in enumerate(questions):
        print(f"\nQuestion {idx + 1}: {q.get('question')}")
        for oIdx, opt in enumerate(q.get("options", [])):
            marker = " [Correct]" if oIdx == q.get("correct_idx") else ""
            print(f"  {oIdx}) {opt}{marker}")
        print(f"Explanation: {q.get('explanation')}")

def handle_plan(args):
    print(f"=== Study Timeline Roadmapper (Goal: {args.goal}) ===")
    res = query_agent_api("plan", args.goal, {}, args.api_url)
    plan = res.get("output", [])
    
    if not plan or not isinstance(plan, list):
        print("Failed to compile study roadmap.")
        return
        
    for day in plan:
        print(f"\nDAY {day.get('day')} ({day.get('time')})")
        print(f"  Concept: {day.get('topic')}")
        print(f"  Materials: {day.get('resource')}")

def handle_review(args):
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found.")
        sys.exit(1)
        
    with open(args.file, "r") as f:
        code_content = f.read()
        
    language = "python"
    if args.file.endswith(".js"):
        language = "javascript"
    elif args.file.endswith(".sql"):
        language = "sql"
        
    print(f"=== Code Review Terminal ({args.file} - {language}) ===")
    res = query_agent_api("review", code_content, {"language": language}, args.api_url)
    output = res.get("output", {})
    
    print("\n[Correctness]")
    print(output.get("correctness"))
    print("\n[Time Complexity]")
    print(output.get("complexity"))
    print("\n[Style Check]")
    print(output.get("style"))
    print("\n[Recommendation]")
    print(output.get("suggestion"))
    print("\n[Subprocess Sandbox Output]")
    print(output.get("sandbox_output"))

def main():
    parser = argparse.ArgumentParser(description="LearnForge Study Console Terminal Client")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="FastAPI backend host URL")
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # study command
    p_study = subparsers.add_parser("study", help="Study conceptual topics")
    p_study.add_argument("--topic", required=True, help="CS / AI / ML topic name")
    p_study.add_argument("--mode", default="explain", choices=["explain"], help="Tutoring option")
    
    # quiz command
    p_quiz = subparsers.add_parser("quiz", help="Test concept understanding")
    p_quiz.add_argument("--topic", required=True, help="Assessment topic")
    p_quiz.add_argument("--difficulty", default="intermediate", choices=["beginner", "intermediate", "advanced"], help="Complexity level")
    
    # plan command
    p_plan = subparsers.add_parser("plan", help="Synthesize weekly timelines")
    p_plan.add_argument("--goal", required=True, help="Target study milestone")
    
    # review command
    p_review = subparsers.add_parser("review", help="Review code styling & time complexity")
    p_review.add_argument("--file", required=True, help="Source code file path")
    
    args = parser.parse_args()
    
    if args.command == "study":
        handle_study(args)
    elif args.command == "quiz":
        handle_quiz(args)
    elif args.command == "plan":
        handle_plan(args)
    elif args.command == "review":
        handle_review(args)

if __name__ == "__main__":
    main()
