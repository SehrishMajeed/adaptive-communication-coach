from sqlalchemy.orm import Session
from ..models.database import UserProfile
from .evaluation import CommunicationEvaluation

def update_user_profile(db: Session, user_id: str, eval: CommunicationEvaluation, focus_area: str):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
        
    # Update rolling averages
    N = profile.total_sessions
    profile.avg_clarity = (profile.avg_clarity * N + eval.clarity) / (N + 1)
    profile.avg_structure = (profile.avg_structure * N + eval.structure) / (N + 1)
    profile.avg_conciseness = (profile.avg_conciseness * N + eval.conciseness) / (N + 1)
    profile.avg_audience_awareness = (profile.avg_audience_awareness * N + eval.audience_awareness) / (N + 1)
    
    # Store latest strengths/weaknesses (simplified list append for MVP)
    profile.recurring_strengths = list(set(profile.recurring_strengths + eval.strengths))[-5:] # Keep top 5
    profile.recurring_weaknesses = list(set(profile.recurring_weaknesses + eval.weaknesses))[-5:]
    
    profile.current_focus_area = focus_area
    profile.total_sessions += 1
    
    db.commit()
    db.refresh(profile)
    return profile
