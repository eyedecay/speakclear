from pydantic import BaseModel


class TranscriptionResponse(BaseModel):
    """Response body for transcription endpoints."""

    text: str
