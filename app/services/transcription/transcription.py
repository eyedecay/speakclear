"""
Transcription service: audio file or bytes → text using Whisper.
"""
from pathlib import Path
from typing import Optional

# use openai whisper model for transcriptions
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
    Transcribes an audio file to text using the Whisper model.
    Args:
        audio_path (Path): Path to the audio file (e.g. .wav, .mp3, .webm, .m4a).
        model_name (str): Whisper model size: "tiny", "base", "small", "medium", "large".
        language (Optional[str]): Optional ISO language code (e.g. "en"); None for auto-detect.
    Returns:
        (str): The transcribed text.
    """
    model = whisper.load_model(model_name)
    kwargs = {"verbose": False}
    if language:
        kwargs["language"] = language
    result = model.transcribe(str(audio_path), **kwargs)
    return (result.get("text") or "").strip()


def transcribe_audio_with_segments(
    audio_path: Path,
    *,
    model_name: str = DEFAULT_MODEL,
    language: Optional[str] = None,
) -> tuple[str, list[dict]]:
    """
    Transcribes an audio file to text and returns segment timestamps for analysis.
    Args:
        audio_path (Path): Path to the audio file.
        model_name (str): Whisper model size.
        language (Optional[str]): Optional ISO language code; None for auto-detect.
    Returns:
        (tuple[str, list[dict]]): Full text and list of segments with "start", "end", "text".
    """
    model = whisper.load_model(model_name)
    kwargs = {"verbose": False}
    if language:
        kwargs["language"] = language
    result = model.transcribe(str(audio_path), **kwargs)
    text = (result.get("text") or "").strip()
    segments = result.get("segments") or []
    # Normalize to list of {start, end, text}
    seg_list = [
        {"start": s["start"], "end": s["end"], "text": (s.get("text") or "").strip()}
        for s in segments
    ]
    return text, seg_list


def transcribe_bytes(
    audio_bytes: bytes,*,suffix: str = ".webm",model_name: str = DEFAULT_MODEL,language: Optional[str] = None,) -> str:
    """
    Transcribes raw audio bytes to text (e.g. from browser MediaRecorder) by writing to a temporary file and running Whisper.
    Args:
        audio_bytes (bytes): Raw audio data.
        suffix (str): File extension so Whisper/ffmpeg can detect format (.webm, .wav, etc.).
        model_name (str): Whisper model size.
        language (Optional[str]): Optional language code; None for auto-detect.
    Returns:
        (str): The transcribed text.
    """

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(audio_bytes)
        path = Path(f.name)
    try:
        return transcribe_audio(path, model_name=model_name, language=language)
    finally:
        path.unlink(missing_ok=True)
