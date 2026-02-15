"""
Analysis: filler word count and section-level WPM (high/low understanding).
"""
import re
from typing import Any

# Hardcoded filler phrases/words (lowercase). Order matters for multi-word first.
FILLER_PATTERNS = [
    "you know",
    "i mean",
    "kind of",
    "sort of",
    "um",
    "uh",
    "like",
    "so",
    "actually",
    "basically",
    "well",
]

# Section size in words (hardcoded for now)
WORDS_PER_SECTION = 50

# WPM thresholds: within range = high understanding; outside = low
WPM_HIGH_MIN = 80
WPM_HIGH_MAX = 180


def count_filler_words(text: str) -> dict[str, Any]:
    """
    Counts filler words and phrases in the given text (case-insensitive, word boundaries).
    Args:
        text (str): The full transcription text.
    Returns:
        (dict): Keys are filler words/phrases; values are counts. Only includes non-zero counts.
    """
    text_lower = text.lower()
    counts: dict[str, Any] = {}
    
    print(f"DEBUG - Analyzing text: '{text_lower}'")  # Debug
    
    for phrase in FILLER_PATTERNS:
        # Word-boundary style: avoid matching inside words
        pattern = r"\b" + re.escape(phrase) + r"\b"
        matches = re.findall(pattern, text_lower)
        n = len(matches)
        print(f"DEBUG - Pattern '{phrase}': found {n} matches: {matches}")  # Debug
        if n > 0:
            counts[phrase] = n
    
    print(f"DEBUG - Final counts: {counts}")  # Debug
    return counts


def get_section_analysis(
    segments: list[dict],
    words_per_section: int = WORDS_PER_SECTION,
    wpm_high_min: float = WPM_HIGH_MIN,
    wpm_high_max: float = WPM_HIGH_MAX,
) -> list[dict[str, Any]]:
    """
    Splits segments into sections of roughly words_per_section words, computes WPM per section, and labels high or low understanding.
    Args:
        segments (list[dict]): List of {"start", "end", "text"} from Whisper.
        words_per_section (int): Target words per section (hardcoded 50 for now).
        wpm_high_min (float): Minimum WPM to count as high understanding.
        wpm_high_max (float): Maximum WPM to count as high understanding.
    Returns:
        (list[dict]): Each item has section_index, word_start, word_end, word_count, duration_sec, wpm, understanding ("high"|"low"), and text.
    """
    if not segments:
        return []

    # Flatten all words with their timestamps
    all_words = []
    for seg in segments:
        start = float(seg.get("start", 0))
        end = float(seg.get("end", 0))
        text = (seg.get("text") or "").strip()
        words = text.split()
        
        if not words:
            continue
            
        # Estimate timestamp for each word
        duration = end - start
        time_per_word = duration / len(words) if len(words) > 0 else 0
        
        for i, word in enumerate(words):
            word_start = start + (i * time_per_word)
            word_end = start + ((i + 1) * time_per_word)
            all_words.append({
                "word": word,
                "start": word_start,
                "end": word_end
            })
    
    if not all_words:
        return []
    
    # Create sections
    sections = []
    section_index = 0
    i = 0
    
    while i < len(all_words):
        # Take up to words_per_section words
        section_words = all_words[i:i + words_per_section]
        
        if not section_words:
            break
            
        section_start = section_words[0]["start"]
        section_end = section_words[-1]["end"]
        duration_sec = section_end - section_start
        
        if duration_sec <= 0:
            duration_sec = 0.1
        
        word_count = len(section_words)
        wpm = word_count / (duration_sec / 60.0)
        understanding = "high" if wpm_high_min <= wpm <= wpm_high_max else "low"
        
        section_text = " ".join([w["word"] for w in section_words])
        
        sections.append({
            "section_index": section_index,
            "word_start": i,
            "word_end": i + word_count,
            "word_count": word_count,
            "duration_sec": round(duration_sec, 2),
            "wpm": round(wpm, 1),
            "understanding": understanding,
            "text": section_text,
        })
        
        section_index += 1
        i += words_per_section
    
    return sections