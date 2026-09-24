"""ML feature preprocessing and text normalization pipeline."""

from typing import List
from app.rule_engine.normalizer import normalize_unicode, remove_zero_width_characters, normalize_whitespace
from app.rule_engine.obfuscation import normalize_leetspeak


def preprocess_for_ml(text: str) -> str:
    """Prepare raw prompt for TF-IDF vectorization and classification."""
    if not text:
        return ""
    # Unicode NFKC
    nfkc = normalize_unicode(text)
    # Remove zero-width
    no_zw, _ = remove_zero_width_characters(nfkc)
    # Normalize whitespace
    ws = normalize_whitespace(no_zw)
    # Normalize leet substitutions
    leet_norm = normalize_leetspeak(ws)
    return leet_norm.lower().strip()


def batch_preprocess_for_ml(texts: List[str]) -> List[str]:
    """Process a batch of prompt texts."""
    return [preprocess_for_ml(t) for t in texts]
