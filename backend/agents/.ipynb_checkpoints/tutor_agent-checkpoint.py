import urllib.request
import json
import os
from typing import Dict, Any

# Local fallback explanations for common topics
OFFLINE_TUTORIALS = {
    "transformers": (
        "### 💡 Intuition\n"
        "Transformers are deep learning architectures that use self-attention to process entire sequences of data in parallel, rather than step-by-step. "
        "This allows models to capture long-range relationships between words or tokens far more efficiently than older recurrent networks.\n\n"
        "### 🔑 Key Concepts\n"
        "* **Self-Attention:** Dynamically weights the relevance of each word in a sequence relative to all other words.\n"
        "* **Positional Encoding:** Adds spatial information to input word vectors to track their order without recurrence.\n"
        "* **Multi-Head Attention:** Calculates attention multiple times in parallel to focus on different aspects of relationships.\n\n"
        "### 💻 Pseudocode / Example\n"
        "```python\n"
        "# High-level representation of scaled dot-product attention\n"
        "import numpy as np\n\n"
        "def attention(Q, K, V):\n"
        "    d_k = Q.shape[-1]\n"
        "    scores = np.matmul(Q, K.T) / np.sqrt(d_k)\n"
        "    weights = softmax(scores)\n"
        "    return np.matmul(weights, V)\n"
        "```\n\n"
        "### 🌍 Real-world Application\n"
        "Powering state-of-the-art language translators, chatbots like ChatGPT, and search engines like Google Search."
    ),
    "backpropagation": (
        "### 💡 Intuition\n"
        "Backpropagation is the mathematical engine that trains neural networks by computing the gradient of the loss function with respect to the weights. "
        "It applies the calculus chain rule to trace errors backward from the output layer to the inputs, adjusting weights to reduce overall error.\n\n"
        "### 🔑 Key Concepts\n"
        "* **Loss Function:** Measures how far the model's predictions are from actual target labels.\n"
        "* **Chain Rule:** Calculus rule used to calculate the derivative of composite functions layer-by-layer.\n"
        "* **Gradient Descent:** Optimization step that updates weights in the opposite direction of the calculated gradient.\n\n"
        "### 💻 Worked Example\n"
        "```python\n"
        "# Single node backward pass example\n"
        "# Forward: y = w * x + b\n"
        "# Loss: L = (y - target)^2\n\n"
        "dy = 2 * (y - target)       # derivative of loss w.r.t prediction\n"
        "dw = dy * x                # chain rule for weight derivative (dy/dw = dy/dy_pred * dy_pred/dw)\n"
        "db = dy * 1                # chain rule for bias derivative\n"
        "```\n\n"
        "### 🌍 Real-world Application\n"
        "Training all deep learning structures, from image classifiers (CNNs) to autonomous vehicle navigation systems."
    )
}

GENERIC_TUTORIAL = (
    "### 💡 Intuition\n"
    "This concept is a cornerstone of modern software engineering and computational science. "
    "Understanding its underlying mechanics allows you to build more optimized, scalable architectures.\n\n"
    "### 🔑 Key Concepts\n"
    "* **Modular Design:** Breaking complex logic down into manageable components.\n"
    "* **Efficiency Constraints:** Keeping computational overhead low.\n"
    "* **Scalability:** Ensuring components perform under load.\n\n"
    "### 💻 Pseudocode / Example\n"
    "```python\n"
    "# Basic loop demonstrating concept flow\n"
    "def process_concept(data):\n"
    "    for item in data:\n"
    "        if validate(item):\n"
    "            yield item\n"
    "```\n\n"
    "### 🌍 Real-world Application\n"
    "Optimizing software execution runtimes and memory allocations in high-volume production deployments."
)

def explain_concept(topic: str, track: str = "CSE", difficulty: str = "Intermediate") -> str:
    """
    Tries to explain a concept using Gemma 3 on local Ollama instance.
    Falls back to high-quality local mock explanations if Ollama is offline.
    """
    ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    url = f"{ollama_host}/api/chat"
    
    system_prompt = (
        "You are an expert CS tutor. Explain the given topic clearly with:\n"
        "1. A simple intuition in 2 sentences\n"
        "2. Key concepts as bullet points\n"
        "3. A worked example or pseudocode\n"
        "4. One real-world application\n"
        f"Adapt depth to the student's track ({track}) and level ({difficulty})."
    )
    
    req_body = {
        "model": "gemma3",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Please explain the topic: {topic}"}
        ],
        "stream": False
    }
    
    try:
        data = json.dumps(req_body).encode("utf-8")
        req = urllib.request.Request(
            url, 
            data=data, 
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=3) as response:
            resp_data = json.loads(response.read().decode("utf-8"))
            explanation = resp_data.get("message", {}).get("content", "")
            if explanation:
                return explanation
    except Exception:
        pass
        
    # Check offline fallback repository
    topic_clean = topic.lower().strip()
    for key, text in OFFLINE_TUTORIALS.items():
        if key in topic_clean or topic_clean in key:
            return f"### {topic.title()} (Offline Mode)\n\n" + text
            
    return f"### {topic.title()} (Offline Mode)\n\n" + GENERIC_TUTORIAL
