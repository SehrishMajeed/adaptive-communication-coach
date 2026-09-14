import json
from unittest.mock import MagicMock
import pytest
from pydantic import ValidationError
from backend.app.domain.evaluation import CommunicationEvaluation
from backend.app.services.llm_provider import evaluate_communication, ProviderFailure


@pytest.mark.parametrize("score", [-1, 11, float("inf"), float("nan"), "8"])
@pytest.mark.parametrize("dimension", ["clarity", "structure", "conciseness", "audience_awareness"])
def test_invalid_scores(contract, score, dimension):
    contract["evaluation"][dimension] = score
    with pytest.raises(ValidationError):
        CommunicationEvaluation(**contract["evaluation"])


@pytest.mark.parametrize("score", [0, 10])
def test_score_boundaries(contract, score):
    contract["evaluation"]["clarity"] = score
    assert CommunicationEvaluation(**contract["evaluation"]).clarity == score


@pytest.mark.parametrize("update", [{"transcript": " "}, {"recommended_focus": ["confidence"]}, {"confidence": 0.8}, {"strengths": [""]}])
def test_invalid_required_data(contract, update):
    contract["evaluation"].update(update)
    with pytest.raises(ValidationError):
        CommunicationEvaluation(**contract["evaluation"])


@pytest.mark.parametrize("output", [None, "{broken", '{"clarity":999}'])
def test_provider_invalid_output_fails_safely(monkeypatch, output):
    client = MagicMock()
    client.__enter__.return_value = client
    client.models.generate_content.return_value.text = output
    monkeypatch.setattr("backend.app.services.llm_provider.genai.Client", lambda **kwargs: client)
    with pytest.raises(ProviderFailure):
        evaluate_communication(b"audio", "audio/wav", "scenario")


def test_provider_schema_and_audio_boundary(monkeypatch, contract):
    client = MagicMock()
    client.__enter__.return_value = client
    client.models.generate_content.return_value.text = json.dumps(contract["evaluation"])
    monkeypatch.setattr("backend.app.services.llm_provider.genai.Client", lambda **kwargs: client)
    result = evaluate_communication(b"only-audio", "audio/wav", "scenario")
    assert result.clarity == 7
    args = client.models.generate_content.call_args.kwargs
    assert args["contents"][0].inline_data.data == b"only-audio"
    assert args["contents"][0].inline_data.mime_type == "audio/wav"
    assert args["config"].response_schema is CommunicationEvaluation
