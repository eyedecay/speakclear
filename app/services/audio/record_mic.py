"""
Record from the default microphone until the user presses Enter; save to a WAV file.
"""
import tempfile
from pathlib import Path
from threading import Thread

import sounddevice as sd
import soundfile as sf
import numpy as np

SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = "int16"
BLOCK_MS = 500


def record_until_enter(output_path: Path) -> None:
    """
    Records from the default microphone until the user presses Enter, then saves the audio to a WAV file.
    Args:
        output_path (Path): Path where the recorded WAV file (16 kHz, mono) will be saved.
    Returns:
        (None): Nothing is returned; audio is written to output_path.
    """
    stop_flag = False
    chunks = []

    def record_loop():
        nonlocal stop_flag, chunks
        block_size = int(SAMPLE_RATE * BLOCK_MS / 1000)
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=DTYPE,
            blocksize=block_size,
        ) as stream:
            while not stop_flag:
                chunk, _ = stream.read(block_size)
                chunks.append(chunk)

    print("Recording... Press Enter to stop.")
    rec_thread = Thread(target=record_loop, daemon=True)
    rec_thread.start()
    input()
    stop_flag = True
    rec_thread.join(timeout=1.0)

    if not chunks:
        raise RuntimeError("No audio recorded.")

    audio = np.concatenate(chunks, axis=0)
    sf.write(str(output_path), audio, SAMPLE_RATE, subtype="PCM_16")
    print(f"Saved {len(audio) / SAMPLE_RATE:.1f} seconds to {output_path}")


def record_microphone_to_file() -> Path:
    """
    Records from the default microphone until the user presses Enter and saves the audio to a temporary WAV file.
    Args:
        None
    Returns:
        (Path): Path to the temporary WAV file containing the recorded audio.
    """
    out = Path(tempfile.mktemp(suffix=".wav"))
    record_until_enter(out)
    return out
