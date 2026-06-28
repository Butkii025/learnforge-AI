import subprocess
import sys
import re
from typing import Dict, Any

# Safety filters to prevent arbitrary command execution or system access
DANGEROUS_KEYWORDS = [
    r"\bos\b", r"\bsubprocess\b", r"\bshutil\b", r"\bsys\b", r"\bsocket\b",
    r"\beval\b", r"\bexec\b", r"\bopen\b", r"\bimportlib\b", r"\bbuiltins\b",
    r"__import__", r"\brequests\b", r"\burllib\b"
]

def run_code_sandbox(code: str) -> Dict[str, Any]:
    """
    Runs Python code in a sandboxed subprocess.
    Includes time limit and restricted keyword search.
    """
    if not code:
        return {"success": False, "output": "Error: No code provided."}
        
    # Check for dangerous modules or functions
    for pattern in DANGEROUS_KEYWORDS:
        if re.search(pattern, code):
             clean_pattern = pattern.replace(r'\\b', '')
        
        return {
            "success": False,
            "output": f"Security Error: Execution blocked due to disallowed keyword pattern: '{clean_pattern}'."
        }
            
    try:
        # Run code in a separate Python process
        # Limit CPU time using timeout
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=2.0 # Enforce strict 2-second timeout
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "output": result.stdout if result.stdout else "Code executed successfully with no console output."
            }
        else:
            return {
                "success": False,
                "output": result.stderr if result.stderr else f"Execution failed with return code {result.returncode}."
            }
            
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "Execution Error: Execution timed out (limit: 2 seconds). Infinite loop suspected."
        }
    except Exception as e:
        return {
            "success": False,
            "output": f"Execution Error: {str(e)}"
        }
