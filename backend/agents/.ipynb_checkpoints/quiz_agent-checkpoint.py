from backend.mcp.tools.quiz_tool import generate_quiz
from typing import List, Dict, Any

def generate_assessment(topic: str, difficulty: str = "intermediate") -> List[Dict[str, Any]]:
    """
    Exposes an interface to generate multiple choice questions about a topic.
    Delegates task execution to the generate_quiz tool.
    """
    return generate_quiz(topic, difficulty)
