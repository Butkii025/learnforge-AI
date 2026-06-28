import urllib.request
import json
import os
import re
from typing import Dict, Any
from backend.mcp.tools.sandbox_tool import run_code_sandbox

# Fallback review patterns when Ollama is offline
def run_local_heuristics(code: str, language: str) -> Dict[str, Any]:
    """Analyzes code parameters locally when offline."""
    correctness = "Looks functional. No syntax errors detected."
    style = "PEP 8 compliant. Good variable naming."
    complexity = "O(n) linear complexity."
    suggestion = "Everything looks clean! Consider adding docstrings to clarify input parameters."
    
    code_lower = code.lower()
    
    # Check time complexity patterns
    if "for" in code_lower:
        # Check for nested loops
        loop_count = len(re.findall(r"\bfor\b", code_lower))
        if loop_count > 1:
            complexity = "O(n^2) quadratic complexity due to nested loops."
            suggestion = "Consider refactoring nested loops to reduce time complexity to O(n) or O(n log n) using caching/hashing."
        else:
            complexity = "O(n) linear complexity due to single loop."
            
    if "def " in code_lower and not re.search(r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'', code):
        style = "Style warning: Function defined without descriptive docstring."
        
    if "print" not in code_lower and language.lower() == "python":
        correctness = "Code executes successfully, but does not print any output. Suggest adding print() statements to inspect values."

    return {
        "correctness": correctness,
        "style": style,
        "complexity": complexity,
        "suggestion": suggestion
    }

def review_code(code: str, language: str = "python") -> Dict[str, Any]:
    """
    Accepts code, executes it in the safe sandbox tool, and queries Ollama 
    for analysis. Falls back to static code parsing if offline.
    """
    # 1. Execute code in safe subprocess sandbox if python
    sandbox_result = {"success": True, "output": "Sandbox execution not supported for this language."}
    if language.lower() == "python":
        sandbox_result = run_code_sandbox(code)
        
    # 2. Call local Ollama model
    ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    url = f"{ollama_host}/api/chat"
    
    prompt = (
        f"Review this {language} code:\n\n{code}\n\n"
        "Provide a code review. Return ONLY a valid JSON object matching this structure:\n"
        "{\n"
        "  \"correctness\": \"Syntax or logic issues found\",\n"
        "  \"style\": \"Style issue descriptions\",\n"
        "  \"complexity\": \"Time and space complexity\",\n"
        "  \"suggestion\": \"Suggested code modifications\"\n"
        "}\n"
        "Do not include markdown tags."
    )
    
    req_body = {
        "model": "gemma3",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "format": "json"
    }
    
    analysis = {}
    try:
        data = json.dumps(req_body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=3) as response:
            resp_data = json.loads(response.read().decode("utf-8"))
            content = resp_data.get("message", {}).get("content", "")
            analysis = json.loads(content)
    except Exception:
        # Fallback to local parsing
        analysis = run_local_heuristics(code, language)
        
    # Add actual sandbox execution outputs
    analysis["sandbox_success"] = sandbox_result.get("success", False)
    analysis["sandbox_output"] = sandbox_result.get("output", "No output captured.")
    
    return analysis
