"""
Transcription API: upload an audio file or send recorded audio → get back text.
"""
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.transcription import TranscriptionResponse
from app.services.transcription import transcribe_audio

router = APIRouter(prefix="/transcription", tags=["transcription"])


# Allowed MIME types / extensions for audio upload (file or voice recording)
ALLOWED_SUFFIXES = {".wav", ".mp3", ".webm", ".m4a", ".ogg", ".flac", ".mp4", ".mpeg"}


def _suffix_for_filename(filename: str) -> str:
    """Return file suffix, defaulting to .webm for unknown (e.g. blob from recorder)."""
    s = Path(filename).suffix.lower()
    return s if s in ALLOWED_SUFFIXES else ".webm"


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(
    file: UploadFile = File(..., description="Audio file or recorded voice (e.g. .wav, .mp3, .webm)"),
    language: Optional[str] = None,
) -> TranscriptionResponse:
    """
    Upload an audio file or recorded audio; returns transcription.

    Use for:
    - Uploading a saved audio file (e.g. .mp3, .wav).
    - Sending recorded audio from the client (e.g. browser MediaRecorder as .webm).
    """
    suffix = _suffix_for_filename(file.filename or "")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file")

    # Write to temp file (Whisper expects a path)
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(contents)
        path = Path(tmp.name)
    try:
        text = transcribe_audio(path, language=language or None)
        return TranscriptionResponse(text=text)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Transcription failed: {str(e)}")
    finally:
        path.unlink(missing_ok=True)
