import sys
import json
from backend.mcp.tools.arxiv_tool import search_arxiv
from backend.mcp.tools.sandbox_tool import run_code_sandbox
from backend.mcp.tools.progress_tool import get_student_progress
from backend.mcp.tools.quiz_tool import generate_quiz
from backend.db.models import SessionLocal

def get_concept_graph(topic: str) -> dict:
    """
    Returns dependencies and related concepts for a study topic.
    Returns a node-link JSON structure.
    """
    topic_l = topic.lower().strip()
    
    # Defaults
    nodes = [
        {"id": "1", "label": "Fundamentals", "status": "mastered"},
        {"id": "2", "label": topic.title(), "status": "unlocked"},
        {"id": "3", "label": "Advanced Practice", "status": "locked"}
    ]
    links = [
        {"source": "1", "target": "2"},
        {"source": "2", "target": "3"}
    ]
    
    # Customise based on CS domains
    if "transformer" in topic_l or "nlp" in topic_l:
        nodes = [
            {"id": "linear_algebra", "label": "Linear Algebra", "status": "mastered"},
            {"id": "neural_networks", "label": "Neural Networks", "status": "mastered"},
            {"id": "sequence_models", "label": "Sequence Models (RNN/LSTM)", "status": "unlocked"},
            {"id": "attention_mechanisms", "label": "Attention Mechanisms", "status": "unlocked"},
            {"id": "transformers", "label": "Transformers (BERT/GPT)", "status": "locked"},
            {"id": "llms", "label": "Large Language Models", "status": "locked"}
        ]
        links = [
            {"source": "linear_algebra", "target": "neural_networks"},
            {"source": "neural_networks", "target": "sequence_models"},
            {"source": "sequence_models", "target": "attention_mechanisms"},
            {"source": "attention_mechanisms", "target": "transformers"},
            {"source": "transformers", "target": "llms"}
        ]
    elif "backpropagation" in topic_l or "neural" in topic_l or "deep learning" in topic_l:
        nodes = [
            {"id": "calculus", "label": "Calculus (Derivatives)", "status": "mastered"},
            {"id": "linear_regression", "label": "Linear Regression", "status": "mastered"},
            {"id": "perceptron", "label": "Perceptron", "status": "mastered"},
            {"id": "backpropagation", "label": "Backpropagation", "status": "unlocked"},
            {"id": "deep_nets", "label": "Multi-Layer Perceptrons", "status": "locked"}
        ]
        links = [
            {"source": "calculus", "target": "backpropagation"},
            {"source": "linear_regression", "target": "perceptron"},
            {"source": "perceptron", "target": "backpropagation"},
            {"source": "backpropagation", "target": "deep_nets"}
        ]
    elif "data structures" in topic_l or "algorithms" in topic_l:
        nodes = [
            {"id": "variables", "label": "Basic Programming", "status": "mastered"},
            {"id": "arrays", "label": "Arrays & Linked Lists", "status": "mastered"},
            {"id": "stacks", "label": "Stacks & Queues", "status": "unlocked"},
            {"id": "trees", "label": "Trees & Graphs", "status": "locked"},
            {"id": "sorting", "label": "Sorting Algorithms", "status": "unlocked"}
        ]
        links = [
            {"source": "variables", "target": "arrays"},
            {"source": "arrays", "target": "stacks"},
            {"source": "arrays", "target": "sorting"},
            {"source": "stacks", "target": "trees"}
        ]
        
    return {"nodes": nodes, "links": links}

# Map tool names to python execution definitions
TOOLS = {
    "search_arxiv": search_arxiv,
    "run_code_sandbox": run_code_sandbox,
    "get_student_progress": lambda uid: get_student_progress(uid, SessionLocal()),
    "generate_quiz": generate_quiz,
    "get_concept_graph": get_concept_graph
}

def handle_mcp_request(req_str: str) -> str:
    """
    Parses a standard JSON-RPC request for MCP tools.
    """
    try:
        req = json.loads(req_str)
        method = req.get("method")
        params = req.get("params", {})
        req_id = req.get("id")
        
        if method == "list_tools":
            return json.dumps({
                "jsonrpc": "2.0",
                "result": {
                    "tools": [
                        {"name": "search_arxiv", "description": "Fetch computer science papers from arXiv API"},
                        {"name": "run_code_sandbox", "description": "Execute python code safely in a subprocess"},
                        {"name": "get_student_progress", "description": "Retrieve study progress analytics from DB"},
                        {"name": "generate_quiz", "description": "Generate multiple choice questions"},
                        {"name": "get_concept_graph", "description": "Get concept dependency trees"}
                    ]
                },
                "id": req_id
            })
            
        elif method == "call_tool":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            
            if tool_name not in TOOLS:
                return json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"},
                    "id": req_id
                })
                
            # Invoke tool with args unpacked
            result = TOOLS[tool_name](**tool_args)
            return json.dumps({
                "jsonrpc": "2.0",
                "result": result,
                "id": req_id
            })
            
        else:
            return json.dumps({
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Method '{method}' not found"},
                "id": req_id
            })
    except Exception as e:
        return json.dumps({
            "jsonrpc": "2.0",
            "error": {"code": -32700, "message": f"Parse error: {str(e)}"},
            "id": None
        })

def run_stdio_server():
    """Main stdio server loop for Model Context Protocol."""
    for line in sys.stdin:
        if not line.strip():
            continue
        response = handle_mcp_request(line)
        sys.stdout.write(response + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    # If run directly, start standard MCP stdio loop
    run_stdio_server()
