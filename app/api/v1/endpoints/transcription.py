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
    """
    Returns the file suffix for the given filename, or .webm if the suffix is not in the allowed list (e.g. blob from recorder).
    Args:
        filename (str): The filename to extract the suffix from.
    Returns:
        (str): The lowercase file extension (e.g. .wav, .webm).
    """
    s = Path(filename).suffix.lower()
    return s if s in ALLOWED_SUFFIXES else ".webm"


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(
    file: UploadFile = File(..., description="Audio file or recorded voice (e.g. .wav, .mp3, .webm)"),
    language: Optional[str] = None,
) -> TranscriptionResponse:
    """
    Accepts an uploaded audio file or recorded audio and returns the transcription as text.
    Args:
        file (UploadFile): The uploaded audio file (e.g. .wav, .mp3, .webm).
        language (Optional[str]): Optional ISO language code for the transcription; None for auto-detect.
    Returns:
        (TranscriptionResponse): Response model containing the transcribed text.
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
