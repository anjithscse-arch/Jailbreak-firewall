"""Heuristic obfuscation analysis: script mixing, base64/hex, leetspeak, and token fragmentation."""

import unicodedata
import re
from typing import List, Dict, Any, Tuple
from app.core.constants import LEET_MAPPINGS

# Regex patterns for encoded payload signatures
BASE64_PATTERN = re.compile(r"(?:[A-Za-z0-9+/]{4}){6,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?")
HEX_PATTERN = re.compile(r"(?:0x|\\x)?[0-9a-fA-F]{16,}")
# Token fragmentation: single letters separated by space or punctuation (e.g., "i g n o r e" or "d.e.v.e.l.o.p.e.r")
FRAGMENTED_WORDS_PATTERN = re.compile(r"\b([a-zA-Z][\s\.\-_]){4,}[a-zA-Z]\b")

# Known attack markers in reverse
REVERSED_ATTACK_WORDS = [
    "snoitcurtsni erongi",  # ignore instructions
    "edom repoleved",        # developer mode
    "edirpmevortp",          # system prompt
    "krowemarfdan",          # dan framework
]


def detect_mixed_scripts(text: str) -> bool:
    """Detect if tokens combine Latin letters with other scripts (e.g. Cyrillic homoglyphs)."""
    words = re.findall(r"\w+", text)
    for word in words:
        if len(word) < 3:
            continue
        scripts = set()
        for ch in word:
            try:
                name = unicodedata.name(ch, "")
                if "LATIN" in name:
                    scripts.add("LATIN")
                elif "CYRILLIC" in name:
                    scripts.add("CYRILLIC")
                elif "GREEK" in name:
                    scripts.add("GREEK")
            except Exception:
                pass
        if len(scripts) > 1:
            return True
    return False


def detect_encoding_indicators(text: str) -> List[Dict[str, str]]:
    """Scan for Base64 and Hexadecimal encoded segments."""
    indicators = []

    # Base64 segments
    for match in BASE64_PATTERN.finditer(text):
        span = match.group(0)
        # Avoid false-positive short tokens
        if len(span) >= 24 and ("=" in span or len(set(span)) > 10):
            indicators.append({
                "type": "BASE64",
                "sample": span[:20] + "...",
                "length": str(len(span))
            })

    # Hex strings
    for match in HEX_PATTERN.finditer(text):
        span = match.group(0)
        if len(span) >= 16:
            indicators.append({
                "type": "HEXADECIMAL",
                "sample": span[:20] + "...",
                "length": str(len(span))
            })

    return indicators


def detect_token_fragmentation(text: str) -> List[str]:
    """Identify artificially fragmented words intended to defeat exact keyword matchers."""
    matches = FRAGMENTED_WORDS_PATTERN.findall(text)
    return [m.strip() for m in matches]


def normalize_leetspeak(text: str) -> str:
    """Normalize simple leetspeak digits and symbols into alphabetic equivalents."""
    chars = []
    for ch in text:
        chars.append(LEET_MAPPINGS.get(ch, ch))
    return "".join(chars)


def detect_reversed_text(text: str) -> bool:
    """Check if reversed text matches common prompt injection signatures."""
    lowered = text.lower()
    for rev in REVERSED_ATTACK_WORDS:
        if rev in lowered:
            return True
    return False


def extract_obfuscation_indicators(text: str) -> Tuple[List[str], str]:
    """Synthesize obfuscation checks and return indicators plus an un-obfuscated normalized view."""
    indicators = []

    if detect_mixed_scripts(text):
        indicators.append("MIXED_SCRIPTS_HOMOGLYPH")

    encodings = detect_encoding_indicators(text)
    if encodings:
        indicators.append(f"ENCODED_BLOCKS_{len(encodings)}")

    fragmented = detect_token_fragmentation(text)
    if fragmented:
        indicators.append("TOKEN_FRAGMENTATION")

    if detect_reversed_text(text):
        indicators.append("REVERSED_TEXT_SIGNATURE")

    # Generate a leet-normalized lowercase string for rule matching
    leet_norm = normalize_leetspeak(text)

    # De-fragment words if tokens like "i g n o r e" exist
    defragmented = re.sub(r"(?<=\b[a-zA-Z])[\s\.\-_](?=[a-zA-Z]\b)", "", leet_norm)

    return indicators, defragmented
