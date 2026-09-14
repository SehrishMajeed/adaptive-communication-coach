from dataclasses import dataclass
import io
import math
import wave

MAX_AUDIO_BYTES = 16 * 1024 * 1024


class InvalidMedia(ValueError):
    pass


@dataclass(frozen=True)
class ValidatedAudio:
    audio_bytes: bytes
    duration_seconds: float


def validate_audio(data: bytes, mime_type: str | None, capture_duration: float) -> ValidatedAudio:
    if not math.isfinite(capture_duration) or not 1 <= capture_duration <= 65:
        raise InvalidMedia("Invalid capture duration")
    if mime_type not in {"audio/wav", "audio/x-wav"} or not 44 <= len(data) <= MAX_AUDIO_BYTES:
        raise InvalidMedia("Expected bounded WAV audio")
    try:
        with wave.open(io.BytesIO(data), "rb") as reader:
            channels, width, rate, frames, compression, _ = reader.getparams()
            if channels != 1 or width != 2 or not 8000 <= rate <= 96000 or compression != "NONE":
                raise InvalidMedia("Expected mono PCM16")
            duration = frames / rate
            if not 1 <= duration <= 65 or abs(duration - capture_duration) > 1.5:
                raise InvalidMedia("Invalid or inconsistent duration")
            samples = reader.readframes(frames)
            if len(samples) != frames * channels * width:
                raise InvalidMedia("Truncated audio")
    except (wave.Error, EOFError, OverflowError) as exc:
        raise InvalidMedia("Malformed WAV") from exc
    # Only PCM reaches the provider; discard ancillary/trailing payloads.
    output = io.BytesIO()
    with wave.open(output, "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(rate)
        writer.writeframes(samples)
    return ValidatedAudio(output.getvalue(), duration)
