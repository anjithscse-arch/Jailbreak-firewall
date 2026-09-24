"""Preprocessing service executing input validation, Unicode sanitization, and obfuscation extraction."""

from typing import Dict, Any
from app.config import settings
from app.core.exceptions import ValidationException
from app.rule_engine.normalizer import (
    normalize_unicode,
    remove_zero_width_characters,
    normalize_whitespace,
    detect_repeated_delimiters,
    detect_excessive_punctuation,
)
from app.rule_engine.obfuscation import (
    extract_obfuscation_indicators,
    detect_mixed_scripts,
    detect_encoding_indicators,
)


class PreprocessingService:
    """Orchestrates comprehensive text normalization and feature extraction for inspection."""

    def __init__(self, max_length: int = settings.MAX_PROMPT_LENGTH):
        self.max_length = max_length

    def preprocess(self, text: str) -> Dict[str, Any]:
        """Validate input and extract normalization representations."""
        if not text or not isinstance(text, str):
            raise ValidationException("Prompt must be a non-empty string.")

        raw_trimmed = text.strip()
        if len(raw_trimmed) == 0:
            raise ValidationException("Prompt cannot be empty or contain only whitespace.")

        if len(text) > self.max_length:
            raise ValidationException(
                f"Prompt exceeds maximum allowed length of {self.max_length} characters (received {len(text)})."
            )

        # 1. Unicode NFKC normalization
        unicode_normalized = normalize_unicode(text)

        # 2. Zero-width character inspection and removal
        clean_text, zero_width_count = remove_zero_width_characters(unicode_normalized)

        # 3. Whitespace normalization
        ws_normalized = normalize_whitespace(clean_text)

        # 4. Obfuscation & structural inspection
        mixed_script = detect_mixed_scripts(clean_text)
        encoding_indicators = detect_encoding_indicators(clean_text)
        obfuscation_indicators, defragmented_text = extract_obfuscation_indicators(ws_normalized)
        delimiters = detect_repeated_delimiters(clean_text)
        excessive_punct = detect_excessive_punctuation(clean_text)

        structural_indicators = []
        if delimiters:
            structural_indicators.append(f"REPEATED_DELIMITERS_{','.join(delimiters[:3])}")
        if excessive_punct:
            structural_indicators.append("HIGH_PUNCTUATION_DENSITY")

        # Lowercase normalized view for deterministic rule matching
        normalized_for_rules = defragmented_text.lower()

        return {
            "original_text": text,
            "normalized_text": normalized_for_rules,
            "clean_text": ws_normalized,
            "removed_zero_width_count": zero_width_count,
            "mixed_script_detected": mixed_script,
            "encoding_indicators": encoding_indicators,
            "obfuscation_indicators": obfuscation_indicators,
            "structural_indicators": structural_indicators,
        }


preprocessing_service = PreprocessingService()
