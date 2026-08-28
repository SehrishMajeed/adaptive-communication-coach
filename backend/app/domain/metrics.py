import re
from typing import Dict, Any, List

FILLER_WORDS = {"um", "uh", "ah", "like", "you know", "so", "actually", "basically"}

def calculate_deterministic_metrics(transcript: str, duration_seconds: float) -> Dict[str, Any]:
    """
    Calculates deterministic speech metrics from a transcript.
    The LLM is NOT responsible for these counts.
    """
    # Clean transcript for counting
    words = re.findall(r'\b\w+\b', transcript.lower())
    word_count = len(words)
    
    # WPM
    wpm = 0
    if duration_seconds > 0:
        wpm = round((word_count / duration_seconds) * 60)
        
    # Filler words
    filler_counts = {}
    total_fillers = 0
    
    # A bit naive for "you know" since it's a phrase, but works for MVP
    for word in words:
        if word in FILLER_WORDS:
            filler_counts[word] = filler_counts.get(word, 0) + 1
            total_fillers += 1
            
    # Handle multi-word fillers like "you know"
    you_know_count = len(re.findall(r'\byou know\b', transcript.lower()))
    if you_know_count > 0:
        filler_counts["you know"] = you_know_count
        total_fillers += you_know_count
        # Adjust single word counts if 'you' and 'know' were counted separately? 
        # (They aren't in FILLER_WORDS individually so it's fine).

    # Format filler words output as required by the frontend AIFeedback interface
    filler_words_list = [{"word": k, "count": v} for k, v in filler_counts.items()]

    return {
        "duration_seconds": duration_seconds,
        "word_count": word_count,
        "wpm": wpm,
        "total_fillers": total_fillers,
        "filler_words_list": filler_words_list
    }
