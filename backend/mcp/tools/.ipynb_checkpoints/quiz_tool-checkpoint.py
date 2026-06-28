import json
import urllib.request
import urllib.error
import os
from typing import List, Dict, Any

# Local fallback MCQ repository covering major tracks
MOCK_QUIZZES = {
    "data structures": [
        {
            "question": "What is the worst-case search complexity in a balanced Binary Search Tree (BST)?",
            "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
            "correct_idx": 1,
            "explanation": "A balanced BST (e.g., AVL or Red-Black Tree) limits height to log(n), guaranteeing logarithmic search time."
        },
        {
            "question": "Which data structure operates on a First-In-First-Out (FIFO) principle?",
            "options": ["Stack", "Queue", "Heap", "Hash Table"],
            "correct_idx": 1,
            "explanation": "Queues insert elements at the back and remove from the front, forming a FIFO structure."
        }
    ],
    "algorithms": [
        {
            "question": "What is the average-case time complexity of Merge Sort?",
            "options": ["O(n)", "O(n log n)", "O(n^2)", "O(log n)"],
            "correct_idx": 1,
            "explanation": "Merge Sort splits lists in halves (log n depth) and merges them in linear time (n), yielding O(n log n) complexity."
        }
    ],
    "cybersecurity": [
        {
            "question": "Which cryptographic algorithm is classified as asymmetric?",
            "options": ["AES", "DES", "RSA", "Blowfish"],
            "correct_idx": 2,
            "explanation": "RSA uses a public key for encryption and a private key for decryption, making it asymmetric."
        }
    ],
    "ml algorithms": [
        {
            "question": "In a Support Vector Machine (SVM), what is the objective of the optimization problem?",
            "options": ["Minimize the margin size", "Maximize the margin between classes", "Calculate centroid distance", "Construct a decision tree"],
            "correct_idx": 1,
            "explanation": "SVMs search for a hyperplane that maximizes the margin (distance) between closest data points of opposing classes."
        }
    ],
    "statistics": [
        {
            "question": "What does a p-value less than 0.05 typically indicate in hypothesis testing?",
            "options": ["Accept the null hypothesis", "Reject the null hypothesis", "Prove the alternative hypothesis is false", "Data is corrupted"],
            "correct_idx": 1,
            "explanation": "A p-value below 0.05 indicates strong evidence against the null hypothesis, leading to its rejection."
        }
    ]
}

# Generic fallbacks if topic doesn't match
GENERIC_QUIZZES = [
    {
        "question": "What is the main role of a cache memory in a computer architecture?",
        "options": ["Increase permanent storage", "Store execution logs", "Provide high-speed, temporary access to CPU instructions", "Manage network routing"],
        "correct_idx": 2,
        "explanation": "Cache sits between CPU registers and RAM, storing frequently accessed data to minimize memory latency."
    },
    {
        "question": "What is the default port used by HTTP requests?",
        "options": ["Port 22", "Port 80", "Port 443", "Port 8080"],
        "correct_idx": 1,
        "explanation": "HTTP defaults to port 80, whereas HTTPS uses port 443."
    }
]

def generate_quiz(topic: str, level: str) -> List[Dict[str, Any]]:
    """
    Tries to generate an MCQ quiz using local Ollama model (Gemma 3).
    If Ollama is not running, falls back to structured pre-written local repositories.
    """
    ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    url = f"{ollama_host}/api/chat"
    
    # Prompt instructing model to return JSON
    prompt = (
        f"Generate a quiz of 3 multiple-choice questions about '{topic}' with difficulty '{level}'. "
        "Each question must have exactly 4 options, a 0-indexed correct_idx representing the correct answer, "
        "and a brief explanation. Return ONLY a valid JSON array matching this structure:\n"
        "[\n"
        "  {\n"
        "    \"question\": \"Question text\",\n"
        "    \"options\": [\"Opt1\", \"Opt2\", \"Opt3\", \"Opt4\"],\n"
        "    \"correct_idx\": 0,\n"
        "    \"explanation\": \"Why it is correct\"\n"
        "  }\n"
        "]\n"
        "Do not include markdown blocks or HTML."
    )
    
    req_body = {
        "model": "gemma3",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "format": "json" # Force Ollama JSON mode
    }
    
    try:
        data = json.dumps(req_body).encode("utf-8")
        req = urllib.request.Request(
            url, 
            data=data, 
            headers={'Content-Type': 'application/json'}
        )
        # Timeout quickly if Ollama isn't active
        with urllib.request.urlopen(req, timeout=3) as response:
            resp_data = json.loads(response.read().decode("utf-8"))
            content = resp_data.get("message", {}).get("content", "")
            
            # Parse json returned by the LLM
            quiz_list = json.loads(content)
            if isinstance(quiz_list, list) and len(quiz_list) > 0:
                return quiz_list
    except Exception:
        # Fallback to local structured data if Ollama is offline/erroring
        pass

    # Search local repository
    topic_clean = topic.lower().strip()
    for key, questions in MOCK_QUIZZES.items():
        if key in topic_clean or topic_clean in key:
            return questions
            
    # Return generic technical questions if no match
    return GENERIC_QUIZZES
