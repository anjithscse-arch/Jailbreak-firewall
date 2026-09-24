"""Seed database with default detection rules."""

import logging
from sqlalchemy.orm import Session
from app.models.rule import DetectionRule
from app.rule_engine.default_rules import DEFAULT_RULES

logger = logging.getLogger(__name__)


def seed_rules(db: Session) -> int:
    """Insert default Layer 1 detection rules into database."""
    inserted = 0
    for r in DEFAULT_RULES:
        existing = db.query(DetectionRule).filter(DetectionRule.rule_code == r["rule_code"]).first()
        if not existing:
            rule = DetectionRule(
                rule_code=r["rule_code"],
                name=r["name"],
                description=r["description"],
                category=r["category"],
                pattern_type=r["pattern_type"],
                pattern=r["pattern"],
                severity=r["severity"],
                weight=r["weight"],
                enabled=r["enabled"],
                case_sensitive=r["case_sensitive"],
                created_by="system_seed",
            )
            db.add(rule)
            inserted += 1

    if inserted > 0:
        db.commit()
        logger.info(f"Seeded {inserted} new detection rules.")
    return inserted
