import sys
from pathlib import Path

# Ensure project root is on path *before* any app imports
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router

#import audio transcription scripts
from app.services.audio import record_microphone_to_file
from app.services.transcription import transcribe_audio_with_segments
from app.services.analysis import count_filler_words, get_section_analysis

app = FastAPI(
    title="SpeakClear",
    description="Audio file or voice recording → transcription",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health():
    """
    Health check endpoint for the API server.
    Args:
        None
    Returns:
        (dict): A dictionary with status key indicating the server is ok.
    """
    return {"status": "ok"}


def run_record_and_transcribe() -> None:
    """
    Records from the default microphone until the user presses Enter, then transcribes the audio and prints the result.
    Args:
        None
    Returns:
        (None): Nothing is returned; transcription is printed to the console.
    """
    print("Using default microphone. When ready, recording will start.")
    try:
        audio_path = record_microphone_to_file()
    except KeyboardInterrupt:
        print("\nCancelled.")
        return
    except Exception as e:
        print(f"Recording failed: {e}")
        return
    try:
        print("Transcribing...")
        text, segments = transcribe_audio_with_segments(audio_path)
        filler_word_count = count_filler_words(text)
        sections = get_section_analysis(segments, words_per_section=50)
        print("\n--- Transcription ---")
        print(text or "(no speech detected)")
        print("---------------------")
        print("\nFiller word count: ")
        for i in filler_word_count:
            print(f"{i}: {filler_word_count[i]}")
        print("\nSections (every ~50 words): high/low understanding by WPM: ")
        for s in sections:
            print(f"  Section {s['section_index']}: words {s['word_start']}-{s['word_end']}, "
                  f"WPM={s['wpm']}, understanding={s['understanding']}")
        print("---------------------")
    finally:
        audio_path.unlink(missing_ok=True)


if __name__ == "__main__":
    print("SpeakClear")
    print("  1. Start API server")
    print("  2. Record from microphone")
    choice = input("Choice (1 or 2): ").strip() or "1"

    if choice == "2":
        run_record_and_transcribe()
    else:
        print("Starting server at http://127.0.0.1:8000")
        print("API docs: http://127.0.0.1:8000/docs")
        uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
