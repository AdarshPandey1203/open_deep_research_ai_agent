import os
import sys
# Ensure directory of current file is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import re
from genai_client import ask_gemini

def summarize_text(text: str, chat_history: list = None) -> str:
    """
    Summarizes content clearly with structured format:
    Title, Executive Summary, Key Findings, and Actionable Takeaways.
    """
    if not text or not text.strip():
        return "No text provided to summarize."

    prompt = f"""You are an expert research analyst. Summarize the following content comprehensively:

{text[:10000]}

Format your response in GitHub-flavored markdown:
### Executive Summary
<A concise overview of the central thesis or concept.>

### Key Highlights & Findings
- **Point 1**: <Details>
- **Point 2**: <Details>
- **Point 3**: <Details>

### Implications & Significance
<Why this matters and future impact.>
"""
    return ask_gemini(prompt, chat_history=chat_history)

def summarize_text_short(text: str, chat_history: list = None) -> str:
    """
    Generates a concise 1-2 sentence executive summary of the response.
    """
    if not text or not text.strip():
        return ""

    # Clean markdown headers for quick summary
    clean_text = re.sub(r'#+\s*', '', text)
    clean_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', clean_text)
    
    prompt = f"Provide a concise, 1-2 sentence high-level summary of the following content: {clean_text[:4000]}"
    res = ask_gemini(prompt, chat_history=chat_history)
    
    # If returned multiple lines, pick first 2 sentences
    lines = [l.strip() for l in res.splitlines() if l.strip() and not l.startswith("#")]
    if lines:
        return " ".join(lines[:2])
    return res.strip()
