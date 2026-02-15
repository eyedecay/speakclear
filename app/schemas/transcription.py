from typing import Any, Optional

from pydantic import BaseModel


class TranscriptionResponse(BaseModel):
    """Response body for transcription endpoints."""

    text: str
    fillers: Optional[dict[str, Any]] = None
    sections: Optional[list[dict[str, Any]]] = None
