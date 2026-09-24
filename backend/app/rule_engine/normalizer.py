"""Text normalization, Unicode NFKC, zero-width character detection, and whitespace sanitization."""

import unicodedata
import re
from typing import Tuple, List
from app.core.constants import ZERO_WIDTH_CHARS

# Regex for collapsing multiple whitespace characters
WHITESPACE_RE = re.compile(r"\s+")
# Common delimiter repetition (e.g. ===, ---, ***, ###, ___, ~~~, >>>)
DELIMITER_RE = re.compile(r"([=\-\*#_~><\\/|]){4,}")


def remove_zero_width_characters(text: str) -> Tuple[str, int]:
    """Identify and remove zero-width and invisible directional codepoints.
    
    Returns:
        (sanitized_text, count_removed)
    """
    removed_count = 0
    clean_chars = []
    for ch in text:
        if ch in ZERO_WIDTH_CHARS or unicodedata.category(ch) in ("Cf", "Cc") and ch not in ("\n", "\r", "\t"):
            removed_count += 1
        else:
            clean_chars.append(ch)
    return "".join(clean_chars), removed_count


def normalize_unicode(text: str) -> str:
    """Normalize text using Compatibility Decomposition followed by Canonical Composition (NFKC)."""
    return unicodedata.normalize("NFKC", text)


def normalize_whitespace(text: str) -> str:
    """Collapse consecutive spaces, tabs, and line-breaks into a single space."""
    return WHITESPACE_RE.sub(" ", text).strip()


def detect_repeated_delimiters(text: str) -> List[str]:
    """Detect unusual repetitions of structural delimiters often used to frame injected instructions."""
    matches = DELIMITER_RE.findall(text)
    return list(set(matches))


def detect_excessive_punctuation(text: str, threshold: float = 0.35) -> bool:
    """Check if punctuation density exceeds threshold, indicating possible obfuscation."""
    if len(text) < 15:
        return False
    punct_count = sum(1 for ch in text if unicodedata.category(ch).startswith("P"))
    ratio = punct_count / len(text)
    return ratio > threshold
