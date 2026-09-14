import io
import wave
from unittest.mock import patch
import pytest
from sqlalchemy.exc import SQLAlchemyError
from backend.app.models.database import CoachingAttempt, CoachingSession, UserProfile
from backend.app.services.llm_provider import ProviderFailure
from backend.app.services.media import validate_audio, InvalidMedia, MAX_AUDIO_BYTES

URL = "/api/sessions/latest/attempts"


def wav(seconds=5, rate=8000, channels=1, width=2):
    output = io.BytesIO()
    with wave.open(output, "wb") as writer:
        writer.setnchannels(channels)
        writer.setsampwidth(width)
        writer.setframerate(rate)
        writer.writeframes(b"\x01" * int(seconds * rate * channels * width))
    return output.getvalue()


def submit(client, data=None, duration="5", mime="audio/wav"):
    return client.post(URL, files={"audio": ("recording.wav", wav() if data is None else data, mime)}, data={"duration_seconds": duration})


def test_http_contract_and_persistence(client, database, evaluator, contract):
    response = submit(client)
    assert response.status_code == 200
    assert response.json() == contract
    database.expire_all()
    saved = database.query(CoachingAttempt).one()
    assert saved.filler_words_count == response.json()["measurements"]["total_fillers"] == 2
    assert saved.duration_seconds == 5
    assert saved.wpm == 72
    assert database.query(UserProfile).count() == 0
    audio, mime, scenario = evaluator.call_args.args
    assert mime == "audio/wav"
    assert audio == wav()
    assert "non-technical" in scenario


def test_repeat_uploads_never_read_or_update_shared_profile(client, database, evaluator):
    profile = UserProfile(user_id="demo_user", avg_clarity=9, total_sessions=10)
    database.add(profile)
    database.commit()
    first, second = submit(client).json(), submit(client).json()
    assert "comparison" not in first and "comparison" not in second
    sessions = database.query(CoachingSession).all()
    assert len({x.session_id for x in sessions}) == 2
    assert all(x.user_id is None for x in sessions)
    database.refresh(profile)
    assert profile.avg_clarity == 9 and profile.total_sessions == 10
    assert [a.attempt_number for a in database.query(CoachingAttempt).all()] == [1, 1]


@pytest.mark.parametrize("duration", ["0", "-1", "66", "nan", "inf", "not-a-number", "1"])
def test_invalid_duration_before_provider(client, evaluator, database, duration):
    assert submit(client, duration=duration).status_code == 422
    evaluator.assert_not_called()
    assert database.query(CoachingAttempt).count() == 0


@pytest.mark.parametrize("data,mime", [
    (b"", "audio/wav"), (b"fake media" * 10, "audio/wav"),
    (wav(), "video/webm"), (wav()[:-10], "audio/wav"),
    (wav(channels=2), "audio/wav"), (wav(width=1), "audio/wav"),
    (wav(seconds=0.5), "audio/wav"), (b"x" * (MAX_AUDIO_BYTES + 1), "audio/wav"),
], ids=["empty", "garbage", "video", "truncated", "stereo", "pcm8", "short", "oversized"])
def test_invalid_media_before_provider(client, evaluator, database, data, mime):
    assert submit(client, data, mime=mime).status_code == 422
    evaluator.assert_not_called()
    assert database.query(CoachingSession).count() == 0


def test_missing_fields_are_safe(client, evaluator):
    result = client.post(URL, data={"duration_seconds": "private-invalid-input"})
    assert result.status_code == 422
    assert "private-invalid-input" not in result.text
    evaluator.assert_not_called()


def test_provider_failure_does_not_persist(client, database, evaluator):
    evaluator.side_effect = ProviderFailure("secret-provider-detail")
    result = submit(client)
    assert result.status_code == 502
    assert "secret-provider-detail" not in result.text
    assert database.query(CoachingAttempt).count() == 0
    assert database.query(CoachingSession).count() == 0
    assert database.query(UserProfile).count() == 0


def test_commit_failure_rolls_back(client, database, evaluator):
    with patch.object(database, "commit", side_effect=SQLAlchemyError("private-db-detail")):
        result = submit(client)
    assert result.status_code == 503
    assert "private-db-detail" not in result.text
    assert database.query(CoachingAttempt).count() == 0
    assert database.query(CoachingSession).count() == 0


def test_duration_is_sample_based_not_compressed_byte_guess():
    small = validate_audio(wav(rate=8000), "audio/wav", 5)
    large = validate_audio(wav(rate=48000), "audio/wav", 5)
    assert len(small.audio_bytes) != len(large.audio_bytes)
    assert small.duration_seconds == large.duration_seconds == 5


def test_ancillary_payload_does_not_reach_provider():
    data = wav()
    assert validate_audio(data + b"private-trailing-payload", "audio/wav", 5).audio_bytes == data


@pytest.mark.parametrize("duration", [float("nan"), float("inf"), -1, 0, 66])
def test_direct_media_validation_bounds(duration):
    with pytest.raises(InvalidMedia):
        validate_audio(wav(), "audio/wav", duration)

def test_invalid_provider_json_through_http(client, database, monkeypatch):
    from unittest.mock import MagicMock
    sdk = MagicMock()
    sdk.__enter__.return_value = sdk
    sdk.models.generate_content.return_value.text = '{"transcript":"hello","clarity":999}'
    monkeypatch.setattr("backend.app.services.llm_provider.genai.Client", lambda **kwargs: sdk)
    result = submit(client)
    assert result.status_code == 502
    assert database.query(CoachingAttempt).count() == 0
    assert database.query(UserProfile).count() == 0


def test_invalid_provider_score_through_http(client, database, monkeypatch, contract):
    import json
    from unittest.mock import MagicMock
    contract["evaluation"]["clarity"] = 11
    sdk = MagicMock()
    sdk.__enter__.return_value = sdk
    sdk.models.generate_content.return_value.text = json.dumps(contract["evaluation"])
    monkeypatch.setattr("backend.app.services.llm_provider.genai.Client", lambda **kwargs: sdk)
    assert submit(client).status_code == 502
    assert database.query(CoachingAttempt).count() == 0


def test_openapi_documents_success_and_error_contracts(client):
    operation = client.get("/openapi.json").json()["paths"][URL]["post"]
    responses = operation["responses"]
    assert responses["200"]["content"]["application/json"]["schema"]["$ref"].endswith("AttemptResponse")
    for status in ("422", "502", "503"):
        assert responses[status]["content"]["application/json"]["schema"]["$ref"].endswith("ErrorResponse")
