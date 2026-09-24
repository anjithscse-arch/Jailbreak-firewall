"""Rule scoring and aggregation engine."""

from typing import List, Dict, Any
from app.config import settings
from app.core.enums import RuleSeverity, AttackCategory


class RuleScorer:
    """Aggregates rule matches, computes composite threat score, and determines early-exit blocking."""

    def __init__(self, block_threshold: float = settings.RULE_BLOCK_THRESHOLD):
        self.block_threshold = block_threshold

    def aggregate(
        self,
        matches: List[Dict[str, Any]],
        execution_time_ms: float
    ) -> Dict[str, Any]:
        """Aggregate individual rule matches into a consolidated Layer 1 verdict."""
        if not matches:
            return {
                "matches": [],
                "max_score": 0.0,
                "top_category": AttackCategory.BENIGN.value,
                "is_blocking": False,
                "matched_count": 0,
                "execution_time_ms": execution_time_ms,
            }

        # Determine highest severity match
        max_score = 0.0
        top_category = AttackCategory.BENIGN.value
        has_critical_or_high = False

        # Category frequency count for multi-match consensus
        category_scores: Dict[str, float] = {}

        for match in matches:
            score = match.get("score", 0.0)
            sev = match.get("severity", RuleSeverity.LOW.value)
            cat = match.get("category", AttackCategory.DIRECT_PROMPT_INJECTION.value)

            if score > max_score:
                max_score = score
                top_category = cat

            category_scores[cat] = category_scores.get(cat, 0.0) + score

            if sev in (RuleSeverity.CRITICAL.value, RuleSeverity.HIGH.value):
                has_critical_or_high = True

        # Sort matches by score descending
        sorted_matches = sorted(matches, key=lambda x: x["score"], reverse=True)

        # Early block determination: If max rule score exceeds threshold or critical/high hit
        is_blocking = (max_score >= self.block_threshold) or has_critical_or_high

        return {
            "matches": sorted_matches,
            "max_score": round(max_score, 3),
            "top_category": top_category,
            "is_blocking": is_blocking,
            "matched_count": len(matches),
            "execution_time_ms": round(execution_time_ms, 2),
        }
