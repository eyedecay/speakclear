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
        (dict): Keys are filler words/phrases and "total"; values are counts.
    """
    text_lower = text.lower()
    counts: dict[str, Any] = {}
    total = 0
    for phrase in FILLER_PATTERNS:
        # Word-boundary style: avoid matching inside words
        pattern = r"\b" + re.escape(phrase) + r"\b"
        n = len(re.findall(pattern, text_lower))
        counts[phrase] = n
        total += n
    counts["total"] = total
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
        (list[dict]): Each item has section_index, word_start, word_end, word_count, duration_sec, wpm, understanding ("high"|"low").
    """
    if not segments:
        return []

    sections: list[dict[str, Any]] = []
    acc_words: list[str] = []
    acc_start: float | None = None
    acc_end: float | None = None
    section_index = 0

    for seg in segments:
        start = float(seg.get("start", 0))
        end = float(seg.get("end", 0))
        text = (seg.get("text") or "").strip()
        words = text.split()
        if not words:
            continue
        if acc_start is None:
            acc_start = start
        acc_end = end
        acc_words.extend(words)

        while len(acc_words) >= words_per_section:
            take = acc_words[:words_per_section]
            acc_words = acc_words[words_per_section:]
            total_duration = (acc_end or end) - (acc_start or start)
            if total_duration <= 0:
                total_duration = 0.1
            total_words_in_span = len(take) + len(acc_words)
            if total_words_in_span > 0:
                duration_sec = (len(take) / total_words_in_span) * total_duration
            else:
                duration_sec = total_duration
            if duration_sec <= 0:
                duration_sec = 0.1
            wpm = len(take) / (duration_sec / 60.0)
            understanding = "high" if wpm_high_min <= wpm <= wpm_high_max else "low"
            word_start = section_index * words_per_section
            word_end = word_start + len(take)
            sections.append({
                "section_index": section_index,
                "word_start": word_start,
                "word_end": word_end,
                "word_count": len(take),
                "duration_sec": round(duration_sec, 2),
                "wpm": round(wpm, 1),
                "understanding": understanding,
            })
            section_index += 1
            # Time for remainder so next section gets correct duration
            if acc_words and total_words_in_span > 0:
                remainder_frac = len(acc_words) / total_words_in_span
                acc_start = (acc_end or end) - remainder_frac * total_duration
            else:
                acc_start = acc_end

    # Remainder
    if acc_words and acc_start is not None and acc_end is not None:
        duration_sec = acc_end - acc_start
        if duration_sec <= 0:
            duration_sec = 0.1
        wpm = len(acc_words) / (duration_sec / 60.0)
        understanding = "high" if wpm_high_min <= wpm <= wpm_high_max else "low"
        word_start = section_index * words_per_section
        sections.append({
            "section_index": section_index,
            "word_start": word_start,
            "word_end": word_start + len(acc_words),
            "word_count": len(acc_words),
            "duration_sec": round(duration_sec, 2),
            "wpm": round(wpm, 1),
            "understanding": understanding,
        })

    return sections
