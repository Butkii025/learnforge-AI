import re
from fastapi import HTTPException, status

# Prompt injection threat signatures
INJECTION_SIGNATURES = [
    r"ignore\s+previous\s+instructions",
    r"system\s+override",
    r"bypass\s+restrictions",
    r"you\s+are\s+now\s+a",
    r"dan\s+mode",
    r"jailbreak",
    r"act\s+as\s+a",
    r"forget\s+everything",
    r"new\s+system\s+prompt",
    r"ignore\s+above",
    r"translate\s+the\s+above\s+and\s+ignore",
    r"developer\s+mode"
]

def sanitize_text(text: str) -> str:
    """Strips HTML tags and normalizes whitespace."""
    if not text:
        return ""
    # Strip HTML tags
    clean = re.sub(r"<[^>]*>", "", text)
    # Normalize multiple spaces/newlines
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean

def check_prompt_injection(text: str) -> str:
    """
    Checks for prompt injection patterns.
    Raises HTTPException 400 if malicious pattern is detected, otherwise returns sanitized text.
    """
    sanitized = sanitize_text(text)
    lower_text = sanitized.lower()
    
    for pattern in INJECTION_SIGNATURES:
        if re.search(pattern, lower_text):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Malicious input pattern detected. Study request blocked for security."
            )
            
    return sanitized
