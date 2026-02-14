import sys
from pathlib import Path

# Ensure project root is on path *before* any app imports
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import uvicorn
from fastapi import FastAPI

from app.api.v1 import api_router



app = FastAPI(
    title="SpeakClear",
    description="Audio file or voice recording → transcription",
    version="0.1.0",
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    
    print("Starting server at http://127.0.0.1:8000")
    print("API docs: http://127.0.0.1:8000/docs")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
