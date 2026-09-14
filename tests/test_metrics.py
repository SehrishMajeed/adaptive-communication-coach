import pytest
from backend.app.domain.metrics import calculate_deterministic_metrics


@pytest.mark.parametrize("text,count,fillers", [
    ("Um, hello. I am like, happy.", 6, 2),
    ("you know, you know", 4, 2),
    ("", 0, 0),
    ("Hello WORLD!", 2, 0),
    ("UM uh actually basically so", 5, 5),
])
def test_metric_fixtures(text, count, fillers):
    result = calculate_deterministic_metrics(text, 60)
    assert result["word_count"] == count
    assert result["wpm"] == count
    assert result["total_fillers"] == fillers
    assert sum(x["count"] for x in result["filler_words_list"]) == fillers


@pytest.mark.parametrize("duration", [0, -1, float("inf"), float("nan")])
def test_invalid_duration(duration):
    with pytest.raises(ValueError):
        calculate_deterministic_metrics("hello", duration)
