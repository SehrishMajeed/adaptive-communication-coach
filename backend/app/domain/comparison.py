from typing import Dict, Any, Optional

def generate_comparison_feedback(current_metrics: Dict[str, Any], previous_metrics: Optional[Dict[str, Any]]) -> str:
    if not previous_metrics:
        return "This was your first attempt. Good baseline established."
        
    wpm_delta = current_metrics.get("wpm", 0) - previous_metrics.get("wpm", 0)
    filler_delta = current_metrics.get("total_fillers", 0) - previous_metrics.get("total_fillers", 0)
    
    feedback = []
    
    if wpm_delta > 10:
        feedback.append(f"You spoke {wpm_delta} WPM faster than your last attempt.")
    elif wpm_delta < -10:
        feedback.append(f"You slowed down your pace by {abs(wpm_delta)} WPM compared to your last attempt.")
    else:
        feedback.append("Your speaking pace remained consistent.")
        
    if filler_delta > 0:
        feedback.append(f"You used {filler_delta} more filler words this time. Focus on pausing instead.")
    elif filler_delta < 0:
        feedback.append(f"Great job! You reduced your filler words by {abs(filler_delta)}.")
    else:
        feedback.append("Your filler word usage was the same as your last attempt.")
        
    return " ".join(feedback)
