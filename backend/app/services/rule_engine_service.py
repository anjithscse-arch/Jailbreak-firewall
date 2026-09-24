"""Rule Engine Service managing rule storage, in-memory caching, and Layer 1 inspection."""

import time
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import logging

from app.database import SessionLocal
from app.models.rule import DetectionRule
from app.rule_engine.default_rules import DEFAULT_RULES
from app.rule_engine.matcher import RuleMatcher
from app.rule_engine.scorer import RuleScorer

logger = logging.getLogger(__name__)


class RuleEngineService:
    """Singleton service for high-performance Layer 1 deterministic inspection."""

    def __init__(self):
        self.matcher = RuleMatcher()
        self.scorer = RuleScorer()
        self._cached_rules: List[Dict[str, Any]] = []
        self._last_loaded: float = 0

    def get_rules(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Retrieve active detection rules from cache or database."""
        now = time.time()
        # Refresh cache if empty or forced or older than 60 seconds
        if not self._cached_rules or force_refresh or (now - self._last_loaded > 60):
            try:
                db: Session = SessionLocal()
                try:
                    db_rules = db.query(DetectionRule).filter(DetectionRule.enabled == True).all()
                    if db_rules:
                        self._cached_rules = [
                            {
                                "rule_code": r.rule_code,
                                "name": r.name,
                                "description": r.description,
                                "category": r.category,
                                "pattern_type": r.pattern_type,
                                "pattern": r.pattern,
                                "severity": r.severity,
                                "weight": r.weight,
                                "enabled": r.enabled,
                                "case_sensitive": r.case_sensitive,
                            }
                            for r in db_rules
                        ]
                    else:
                        # Fallback to default in-memory rules if database not yet seeded
                        self._cached_rules = DEFAULT_RULES
                    self._last_loaded = now
                finally:
                    db.close()
            except Exception as e:
                logger.warning(f"Could not load rules from database, using built-in defaults: {e}")
                self._cached_rules = DEFAULT_RULES

        return self._cached_rules

    def reload_rules(self):
        """Force cache invalidation and reload."""
        self.get_rules(force_refresh=True)

    def detect(
        self,
        original_text: str,
        normalized_text: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute Layer 1 deterministic inspection on incoming prompt."""
        start_time = time.perf_counter()
        rules = self.get_rules()
        raw_matches = self.matcher.match_all(rules, original_text, normalized_text, metadata)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return self.scorer.aggregate(raw_matches, elapsed_ms)

    def test_pattern(
        self,
        prompt: str,
        pattern_type: str,
        pattern: str,
        case_sensitive: bool = False
    ) -> Dict[str, Any]:
        """Test a candidate rule pattern against a sample prompt without persisting."""
        start_time = time.perf_counter()
        dummy_rule = {
            "rule_code": "TEST_RULE",
            "name": "Test Pattern",
            "description": "Ad-hoc pattern evaluation",
            "category": "DIRECT_PROMPT_INJECTION",
            "pattern_type": pattern_type,
            "pattern": pattern,
            "severity": "HIGH",
            "weight": 1.0,
            "enabled": True,
            "case_sensitive": case_sensitive,
        }
        from app.services.preprocessing_service import preprocessing_service
        preprocessed = preprocessing_service.preprocess(prompt)
        res = self.matcher.match_rule(
            dummy_rule,
            original_text=prompt,
            normalized_text=preprocessed["normalized_text"],
            metadata=preprocessed
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "matched": res is not None,
            "matched_text": res.get("matched_text") if res else None,
            "score": res.get("score") if res else 0.0,
            "latency_ms": round(elapsed_ms, 2),
        }


rule_engine_service = RuleEngineService()
