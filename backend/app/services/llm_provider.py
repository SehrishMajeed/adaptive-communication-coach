import os
from google import genai
from google.genai import types
from ..domain.evaluation import CommunicationEvaluation

def evaluate_communication(audio_bytes: bytes, mime_type: str, scenario: str) -> CommunicationEvaluation:
    # Ensure GEMINI_API_KEY is set in the environment
    client = genai.Client() 
    
    prompt = f"""
    You are an expert communication coach. Listen to the provided audio recording.
    The speaker is practicing the following scenario: {scenario}
    
    First, accurately transcribe the spoken audio.
    Then, provide scores from 0-10 for clarity, structure, conciseness, and audience_awareness.
    Provide strengths, weaknesses, and a recommended focus area.
    
    STRICT RULES:
    1. Do NOT evaluate pace, filler words, or word counts. Focus purely on qualitative communication skills.
    2. Do NOT fabricate visual feedback (e.g. eye contact, body language, posture) since this is an audio-only analysis.
    """
    
    audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[audio_part, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=CommunicationEvaluation,
            temperature=0.2,
        ),
    )
    
    if not response.text:
        raise ValueError("Failed to generate evaluation")
        
    return CommunicationEvaluation.model_validate_json(response.text)
