import pytest
from backend.app.agent.graph import build_coaching_graph
from backend.app.services.llm_provider import ProviderFailure


def test_compiled_graph(evaluator):
    result = build_coaching_graph().invoke({
        "scenario": "test", "audio_bytes": b"audio", "mime_type": "audio/wav", "duration_seconds": 5,
    })
    assert result["deterministic_metrics"]["word_count"] == 6
    assert result["deterministic_metrics"]["total_fillers"] == 2
    assert result["deterministic_metrics"]["wpm"] == 72
    assert "comparison_delta" not in result
    evaluator.assert_called_once()


def test_compiled_graph_stops_on_evaluation_failure(evaluator, monkeypatch):
    evaluator.side_effect = ProviderFailure("failed")
    calls = []
    monkeypatch.setattr("backend.app.agent.nodes.calculate_deterministic_metrics", lambda *args: calls.append(args))
    with pytest.raises(ProviderFailure):
        build_coaching_graph().invoke({"scenario": "test", "audio_bytes": b"x", "mime_type": "audio/wav", "duration_seconds": 5})
    assert calls == []
