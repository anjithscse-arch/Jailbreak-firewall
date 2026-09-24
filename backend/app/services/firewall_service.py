"""Central Firewall Pipeline coordinating Preprocessing, Rule Engine, ML Classifier, and LLM Gateway."""

import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.config import settings
from app.core.enums import AttackCategory, FirewallDecision, DetectionLayer
from app.core.constants import (
    CATEGORY_CONSISTENCY_BONUS,
    OBFUSCATION_BONUS,
    DEFAULT_BLOCKED_MESSAGE,
    DEFAULT_REVIEW_MESSAGE,
)
from app.services.preprocessing_service import preprocessing_service
from app.services.rule_engine_service import rule_engine_service
from app.services.ml_classifier_service import ml_classifier_service
from app.services.explanation_service import explanation_service
from app.services.llm_gateway_service import llm_gateway_service
from app.services.logging_service import logging_service
from app.services.knowledge_service import knowledge_service
from app.schemas.firewall import (
    AnalyzePromptRequest,
    AnalyzePromptResponse,
    MatchedRuleSchema,
    MLResultSchema,
    ExplanationSchema,
    LLMResponseDetail,
)


class FirewallService:
    """Orchestrates two-layer defense and strictly enforces LLM boundary security."""

    def __init__(
        self,
        block_threshold: float = settings.DEFAULT_ML_THRESHOLD,
        review_threshold: float = settings.REVIEW_THRESHOLD,
        secure_mode: bool = settings.SECURE_MODE,
    ):
        self.block_threshold = block_threshold
        self.review_threshold = review_threshold
        self.secure_mode = secure_mode

    async def analyze_prompt(
        self,
        request: AnalyzePromptRequest,
        db: Optional[Session] = None,
    ) -> AnalyzePromptResponse:
        """Inspect prompt through the hybrid two-layer security gateway."""
        start_time = time.perf_counter()
        request_id = str(uuid.uuid4())
        created_at_iso = datetime.now(timezone.utc).isoformat()

        # Step 1: Preprocessing & Normalization
        prep_result = preprocessing_service.preprocess(request.prompt)
        normalized_text = prep_result["normalized_text"]

        # Step 2: Layer 1 - Deterministic Rule Engine
        rule_result = rule_engine_service.detect(
            original_text=request.prompt,
            normalized_text=normalized_text,
            metadata=prep_result
        )

        # Early exit check: High-severity deterministic rule match
        if rule_result["is_blocking"]:
            decision = FirewallDecision.BLOCK.value
            attack_category = rule_result["top_category"]
            confidence = rule_result["max_score"]
            risk_score = rule_result["max_score"]
            detected_by = DetectionLayer.RULE_ENGINE.value

            # Compute Layer 2 ML and LIME features for complete explainability visualization
            ml_result = ml_classifier_service.predict(normalized_text)

            explanation = explanation_service.generate(
                decision=decision,
                attack_category=attack_category,
                confidence=confidence,
                risk_score=risk_score,
                rule_result=rule_result,
                ml_result=ml_result,
                metadata=prep_result,
            )

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            # Audit record
            if db:
                logging_service.record_prompt_transaction(
                    db=db,
                    request_id=request_id,
                    prompt=request.prompt,
                    decision=decision,
                    attack_category=attack_category,
                    confidence=confidence,
                    risk_score=risk_score,
                    detected_by=detected_by,
                    processing_time_ms=elapsed_ms,
                    rule_result=rule_result,
                    ml_result=ml_result,
                    conversation_id=request.conversation_id,
                    user_id=request.user_id,
                    llm_provider=request.llm_provider or settings.LLM_PROVIDER,
                    llm_called=False,
                )

            return AnalyzePromptResponse(
                request_id=request_id,
                decision=decision,
                is_attack=True,
                attack_category=attack_category,
                confidence=confidence,
                risk_score=risk_score,
                processing_time_ms=round(elapsed_ms, 2),
                detected_by=detected_by,
                normalized_prompt=normalized_text if settings.DEBUG else None,
                matched_rules=[MatchedRuleSchema(**r) for r in rule_result["matches"]],
                ml_result=MLResultSchema(**ml_result),
                explanation=ExplanationSchema(**explanation),
                llm_response=None,
                blocked_message=DEFAULT_BLOCKED_MESSAGE,
                created_at=created_at_iso,
            )

        # Step 3: Layer 2 - Machine Learning Classifier
        ml_result = ml_classifier_service.predict(normalized_text)

        # Step 4: Hybrid Risk Aggregation Formula
        rule_score = rule_result["max_score"]
        ml_label = ml_result["label"]
        ml_conf = ml_result["confidence"]

        probs = ml_result.get("probabilities") or {}
        benign_prob = probs.get(AttackCategory.BENIGN.value, 0.0) if probs else (1.0 - ml_conf if ml_label != AttackCategory.BENIGN.value else ml_conf)
        total_attack_prob = 1.0 - benign_prob

        # If ML label is an attack, attack contribution incorporates the total attack mass (1 - P(benign))
        if ml_label != AttackCategory.BENIGN.value:
            ml_attack_score = max(ml_conf, total_attack_prob * 0.90)
        else:
            attack_probs = [p for c, p in probs.items() if c != AttackCategory.BENIGN.value]
            ml_attack_score = max(attack_probs) if attack_probs else (1.0 - ml_conf) * 0.25

        # Consensus bonus if both layers flagged non-benign threat
        consistency_bonus = 0.0
        if (
            rule_result["top_category"] == ml_label
            and rule_result["top_category"] != AttackCategory.BENIGN.value
        ):
            consistency_bonus = CATEGORY_CONSISTENCY_BONUS

        # Obfuscation bonus
        obfuscation_bonus = (
            OBFUSCATION_BONUS if len(prep_result.get("obfuscation_indicators", [])) > 0 else 0.0
        )

        composite_risk = min(1.0, max(rule_score, ml_attack_score) + consistency_bonus + obfuscation_bonus)

        # Determine top threat category & detection layer attribution
        if rule_score >= ml_attack_score and rule_score > 0.3:
            attack_category = rule_result["top_category"]
        else:
            attack_category = ml_label

        # Determine detection layer
        has_rule = len(rule_result["matches"]) > 0
        has_ml = ml_label != AttackCategory.BENIGN.value and ml_conf >= 0.50

        if has_rule and has_ml:
            detected_by = DetectionLayer.BOTH.value
        elif has_rule:
            detected_by = DetectionLayer.RULE_ENGINE.value
        elif has_ml:
            detected_by = DetectionLayer.ML_CLASSIFIER.value
        else:
            detected_by = DetectionLayer.NONE.value

        # Step 5: Verdict Threshold Evaluation
        if composite_risk >= self.block_threshold or rule_result["is_blocking"]:
            decision = FirewallDecision.BLOCK.value
            is_attack = True
            blocked_msg = DEFAULT_BLOCKED_MESSAGE
            confidence = composite_risk
        elif composite_risk >= self.review_threshold:
            decision = (
                FirewallDecision.BLOCK.value if self.secure_mode else FirewallDecision.REVIEW.value
            )
            is_attack = True if self.secure_mode else False
            blocked_msg = DEFAULT_REVIEW_MESSAGE if decision == FirewallDecision.REVIEW.value else DEFAULT_BLOCKED_MESSAGE
            confidence = composite_risk
        else:
            decision = FirewallDecision.ALLOW.value
            is_attack = False
            blocked_msg = None
            attack_category = AttackCategory.BENIGN.value
            confidence = ml_conf if ml_label == AttackCategory.BENIGN.value else (1.0 - composite_risk)

        # Step 6: Upstream LLM Dispatch (Strict Barrier Guarantee)
        llm_content = None
        llm_detail = None
        llm_called = False

        if decision == FirewallDecision.ALLOW.value and request.forward_to_llm:
            target_provider = request.llm_provider or settings.LLM_PROVIDER
            target_model = request.llm_model

            # Query Knowledge Database for grounded context
            knowledge_docs = knowledge_service.retrieve_context(request.prompt)
            prompt_for_llm = request.prompt
            if knowledge_docs:
                context_str = "\n".join([f"[{d['title']}]: {d['content']}" for d in knowledge_docs])
                prompt_for_llm = f"Knowledge Base Reference:\n{context_str}\n\nUser Question:\n{request.prompt}"

            llm_res = await llm_gateway_service.call_llm(
                prompt=prompt_for_llm,
                provider=target_provider,
                model=target_model,
            )
            llm_called = True
            llm_content = llm_res.get("content", "")
            llm_detail = LLMResponseDetail(
                provider=llm_res.get("provider", "mock"),
                model=llm_res.get("model", "default"),
                content=llm_content,
                latency_ms=llm_res.get("latency_ms", 0.0),
                usage=llm_res.get("usage", {}),
                knowledge_context=knowledge_docs,
            )

        # Step 7: Explainability Synthesis
        explanation = explanation_service.generate(
            decision=decision,
            attack_category=attack_category,
            confidence=round(confidence, 3),
            risk_score=round(composite_risk, 3),
            rule_result=rule_result,
            ml_result=ml_result,
            metadata=prep_result,
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        # Step 8: Database Audit Log
        if db:
            logging_service.record_prompt_transaction(
                db=db,
                request_id=request_id,
                prompt=request.prompt,
                decision=decision,
                attack_category=attack_category,
                confidence=round(confidence, 3),
                risk_score=round(composite_risk, 3),
                detected_by=detected_by,
                processing_time_ms=elapsed_ms,
                rule_result=rule_result,
                ml_result=ml_result,
                conversation_id=request.conversation_id,
                user_id=request.user_id,
                llm_provider=request.llm_provider or settings.LLM_PROVIDER,
                llm_model=request.llm_model,
                llm_called=llm_called,
                llm_response=llm_content,
            )

        return AnalyzePromptResponse(
            request_id=request_id,
            decision=decision,
            is_attack=is_attack,
            attack_category=attack_category,
            confidence=round(confidence, 4),
            risk_score=round(composite_risk, 4),
            processing_time_ms=round(elapsed_ms, 2),
            detected_by=detected_by,
            normalized_prompt=normalized_text if settings.DEBUG else None,
            matched_rules=[MatchedRuleSchema(**r) for r in rule_result["matches"]],
            ml_result=MLResultSchema(**ml_result),
            explanation=ExplanationSchema(**explanation),
            llm_response=llm_content,
            llm_metadata=llm_detail,
            blocked_message=blocked_msg,
            created_at=created_at_iso,
        )


firewall_service = FirewallService()
