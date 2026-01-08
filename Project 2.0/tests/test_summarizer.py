
from summarizer import summarize_text

def test_summary_short_text():
    text = "Short text."
    result = summarize_text(text)
    assert "Short text" in result
    assert "AI Generated Summary" in result

def test_summary_long_text():
    text = "Sentence one. Sentence two. Sentence three."
    result = summarize_text(text)
    # Check if logic picks the first sentence
    assert "Sentence one." in result
    assert "AI Generated Summary" in result
