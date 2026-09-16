import os

from google import genai
from google.genai import types
from ..domain.evaluation import CommunicationEvaluation
from .prompts import build_evaluation_prompt


class ProviderFailure(RuntimeError):
    pass


GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.0"))


def evaluate_communication(audio_bytes: bytes, mime_type: str, scenario: str) -> CommunicationEvaluation:
    prompt = build_evaluation_prompt(scenario)
    try:
        with genai.Client(http_options=types.HttpOptions(timeout=45000, retry_options=types.HttpRetryOptions(attempts=1))) as client:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[types.Part.from_bytes(data=audio_bytes, mime_type=mime_type), prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=CommunicationEvaluation,
                    temperature=GEMINI_TEMPERATURE,
                ),
            )
            if not response.text:
                raise ValueError("Empty provider response")
            return CommunicationEvaluation.model_validate_json(response.text)
    except Exception as exc:
        # SDK/config/network errors share a safe, recoverable boundary.
        raise ProviderFailure("Evaluation unavailable") from exc
