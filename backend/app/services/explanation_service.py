"""Explainability Service synthesizing rule evidence and ML feature attributions into human-readable insights."""

from typing import Dict, Any, List
from app.core.enums import AttackCategory, FirewallDecision
from app.core.constants import CATEGORY_DESCRIPTIONS, CATEGORY_REMEDIATIONS


class ExplanationService:
    """Builds transparent, interpretable security explanations for firewall decisions."""

    def generate(
        self,
        decision: str,
        attack_category: str,
        confidence: float,
        risk_score: float,
        rule_result: Dict[str, Any],
        ml_result: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synthesize Layer 1 and Layer 2 evidence into an interpretable audit explanation."""
        cat_enum = AttackCategory(attack_category) if attack_category in AttackCategory._value2member_map_ else AttackCategory.BENIGN

        reasons: List[str] = []
        evidence: List[Dict[str, Any]] = []

        matched_rules = rule_result.get("matches", [])
        ml_label = ml_result.get("label", AttackCategory.BENIGN.value)
        ml_conf = ml_result.get("confidence", 0.0)
        ml_features = ml_result.get("top_features", [])
        obf_indicators = metadata.get("obfuscation_indicators", [])

        # 1. Evidence Collection
        for r in matched_rules:
            evidence.append({
                "type": "rule",
                "label": r.get("name", "Deterministic Rule"),
                "severity": r.get("severity", "MEDIUM"),
                "score": r.get("score", 0.0),
                "matched_text": r.get("matched_text"),
            })

        for feat in ml_features:
            evidence.append({
                "type": "ml_feature",
                "text": feat.get("feature", ""),
                "weight": feat.get("weight", 0.0),
                "direction": feat.get("direction", "attack"),
            })

        # 2. Decision Logic Explanations
        if decision == FirewallDecision.BLOCK.value:
            if matched_rules:
                top_rule = matched_rules[0]
                reasons.append(
                    f"Layer 1 Rule Match: Triggered rule '{top_rule.get('name')}' ({top_rule.get('severity')} severity)."
                )

            if ml_label != AttackCategory.BENIGN.value and ml_conf >= 0.60:
                reasons.append(
                    f"Layer 2 ML Classification: Predicted '{ml_label}' attack pattern with {int(ml_conf * 100)}% confidence."
                )

            if obf_indicators:
                reasons.append(
                    f"Obfuscation Heuristics: Detected adversarial evasion markers ({', '.join(obf_indicators)})."
                )

            summary = (
                f"The prompt was blocked by the security firewall because it was classified as a "
                f"{attack_category.replace('_', ' ').title()} attempt (Risk Score: {int(risk_score * 100)}%)."
            )
            remediation = CATEGORY_REMEDIATIONS.get(
                cat_enum,
                "Please restructure your request using standard language without adversarial framing."
            )

        elif decision == FirewallDecision.REVIEW.value:
            summary = (
                f"The prompt was flagged for manual review due to ambiguous safety indicators "
                f"(Risk Score: {int(risk_score * 100)}%)."
            )
            reasons.append(
                f"Statistical uncertainty: ML confidence is moderate ({int(ml_conf * 100)}%), requiring manual inspection."
            )
            if matched_rules:
                reasons.append(f"Low-severity informational rule indicators were noted.")
            remediation = (
                "Review the prompt for contextual ambiguity before approving or resubmitting."
            )

        else:  # ALLOW
            summary = "The prompt passed all Layer 1 and Layer 2 security inspections."
            reasons.append("No high-risk prompt injection, jailbreak, or exfiltration indicators were identified.")
            reasons.append(f"ML Classifier predicted benign intent with {int(confidence * 100)}% confidence.")
            remediation = "No remediation needed. Prompt complies with security policy."

        return {
            "summary": summary,
            "reasons": reasons,
            "evidence": evidence,
            "recommended_action": remediation,
        }


explanation_service = ExplanationService()
