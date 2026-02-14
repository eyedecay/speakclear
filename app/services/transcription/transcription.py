"""
Transcription service: audio file or bytes → text using Whisper.
"""
from pathlib import Path
from typing import Optional

import whisper
import tempfile

# Default model: 
DEFAULT_MODEL = "base"


def transcribe_audio(
    audio_path: Path,
    *,
    model_name: str = DEFAULT_MODEL,
    language: Optional[str] = None,
) -> str:
    """
    Transcribe an audio file to text.

    Args:
        audio_path: Path to the audio file (e.g. .wav, .mp3, .webm, .m4a).
        model_name: Whisper model size: "tiny", "base", "small", "medium", "large".
        language: Optional ISO language code (e.g. "en"); None for auto-detect.

    Returns:
        Transcribed text.
    """
    model = whisper.load_model(model_name)
    kwargs = {"verbose": False}
    if language:
        kwargs["language"] = language
    result = model.transcribe(str(audio_path), **kwargs)
    return (result.get("text") or "").strip()


def transcribe_bytes(
    audio_bytes: bytes,*,suffix: str = ".webm",model_name: str = DEFAULT_MODEL,language: Optional[str] = None,) -> str:
    """
    Transcribe raw audio bytes to text (e.g. from browser MediaRecorder).

    Writes bytes to a temporary file and runs Whisper, then returns the text.

    Args:
        audio_bytes: Raw audio data.
        suffix: File extension so Whisper/ffmpeg can detect format (.webm, .wav, etc.).
        model_name: Whisper model size.
        language: Optional language code.

    Returns:
        Transcribed text.
    """

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(audio_bytes)
        path = Path(f.name)
    try:
        return transcribe_audio(path, model_name=model_name, language=language)
    finally:
        path.unlink(missing_ok=True)
