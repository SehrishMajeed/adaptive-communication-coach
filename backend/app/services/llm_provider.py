import os
from google import genai
from google.genai import types
from ..domain.evaluation import CommunicationEvaluation

def evaluate_communication(transcript: str, scenario: str) -> CommunicationEvaluation:
    # Ensure GEMINI_API_KEY is set in the environment
    client = genai.Client() 
    
    prompt = f"""
    You are an expert communication coach. Evaluate the following transcript based on this scenario: {scenario}
    
    <transcript>
    {transcript}
    </transcript>
    
    Provide scores from 0-10 for clarity, structure, conciseness, and audience_awareness.
    Provide strengths, weaknesses, and a recommended focus area.
    Do NOT evaluate pace, filler words, or word counts. Focus purely on qualitative communication skills.
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=CommunicationEvaluation,
            temperature=0.2,
        ),
    )
    
    if not response.text:
        raise ValueError("Failed to generate evaluation")
        
    return CommunicationEvaluation.model_validate_json(response.text)
