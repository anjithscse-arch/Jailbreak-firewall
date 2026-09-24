"""Pattern matching engine with pre-compiled regex cache and structural evaluators."""

import re
import time
from typing import List, Dict, Any, Optional
from app.core.enums import PatternType, RuleSeverity
from app.core.security import redact_matched_text


class RuleMatcher:
    """Evaluates text against compiled detection rules with sub-millisecond efficiency."""

    def __init__(self):
        self._compiled_cache: Dict[str, re.Pattern] = {}

    def get_or_compile_regex(self, pattern: str, case_sensitive: bool = False) -> re.Pattern:
        """Cache compiled regular expressions to eliminate per-request compilation overhead."""
        key = f"{case_sensitive}:{pattern}"
        if key not in self._compiled_cache:
            flags = 0 if case_sensitive else re.IGNORECASE
            self._compiled_cache[key] = re.compile(pattern, flags)
        return self._compiled_cache[key]

    def match_rule(
        self,
        rule_dict: Dict[str, Any],
        original_text: str,
        normalized_text: str,
        metadata: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Evaluate a single rule definition against prompt content and metadata."""
        if not rule_dict.get("enabled", True):
            return None

        pattern_type = rule_dict.get("pattern_type", PatternType.REGEX.value)
        pattern = rule_dict.get("pattern", "")
        case_sensitive = rule_dict.get("case_sensitive", False)
        severity = rule_dict.get("severity", RuleSeverity.MEDIUM.value)
        weight = float(rule_dict.get("weight", 1.0))

        matched = False
        matched_span = ""

        try:
            # 1. Obfuscation heuristic checks
            if pattern_type == PatternType.OBFUSCATION.value:
                if pattern == "zero_width_count > 0":
                    if metadata.get("removed_zero_width_count", 0) > 0:
                        matched = True
                        matched_span = f"{metadata['removed_zero_width_count']} zero-width characters detected"
                elif pattern == "mixed_script_detected == True":
                    if metadata.get("mixed_script_detected", False):
                        matched = True
                        matched_span = "Mixed script homoglyphs detected"
                elif pattern == "has_encoded_blocks == True":
                    enc = metadata.get("encoding_indicators", [])
                    if len(enc) > 0:
                        matched = True
                        matched_span = f"Encoded blocks present ({enc[0].get('type', 'ENCODING')})"

            # 2. Keyword check
            elif pattern_type == PatternType.KEYWORD.value:
                target = original_text if case_sensitive else normalized_text
                kw = pattern if case_sensitive else pattern.lower()
                if kw in target:
                    matched = True
                    matched_span = kw

            # 3. Phrase check
            elif pattern_type == PatternType.PHRASE.value:
                target = original_text if case_sensitive else normalized_text
                phrase = pattern if case_sensitive else pattern.lower()
                if phrase in target:
                    matched = True
                    matched_span = phrase

            # 4. Regex / Structural / Unicode / Template check
            else:
                compiled = self.get_or_compile_regex(pattern, case_sensitive=case_sensitive)
                # Test against normalized text first
                m = compiled.search(normalized_text)
                if not m:
                    # Test against original text
                    m = compiled.search(original_text)

                if m:
                    matched = True
                    matched_span = m.group(0)

        except Exception:
            matched = False

        if matched:
            base_score = RuleSeverity(severity).default_score
            final_score = min(1.0, base_score * weight)
            return {
                "rule_id": rule_dict.get("rule_code", "CUSTOM_RULE"),
                "name": rule_dict.get("name", "Security Rule"),
                "category": rule_dict.get("category", "DIRECT_PROMPT_INJECTION"),
                "severity": severity,
                "score": round(final_score, 3),
                "description": rule_dict.get("description", ""),
                "matched_text": redact_matched_text(matched_span),
            }

        return None

    def match_all(
        self,
        rules: List[Dict[str, Any]],
        original_text: str,
        normalized_text: str,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Run all enabled rules against the prompt."""
        matches = []
        for r in rules:
            res = self.match_rule(r, original_text, normalized_text, metadata)
            if res:
                matches.append(res)
        return matches
