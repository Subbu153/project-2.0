
import random

def summarize_text(text: str) -> str:
    """
    Mock function to simulate an external summarization API.
    In a real app, this would call OpenAI, HuggingFace, etc.
    """
    # Simple mock logic: take the first sentence or truncate.
    doc_len = len(text)
    if doc_len < 50:
        return f"Summary: {text} (Short text)"
    
    sentences = text.split('.')
    summary = sentences[0] + "." if sentences else text[:50] + "..."
    
    # Simulate some "AI" processing
    return f"AI Generated Summary: {summary} [Analyzed {doc_len} chars]"
