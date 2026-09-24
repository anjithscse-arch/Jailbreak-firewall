"""Explainability module utilizing LIME (Local Interpretable Model-Agnostic Explanations).

Implements Section IV.F and Figure 9 of the base paper:
'JailbreakTracer: Explainable Detection of Jailbreaking Prompts in LLMs Using Synthetic Data Generation'
(IEEE Access, 2025).
"""

import logging
from typing import List, Dict, Any, Callable
import numpy as np
from lime.lime_text import LimeTextExplainer
from app.core.enums import AttackCategory

logger = logging.getLogger(__name__)


class FeatureExplainer:
    """Computes transparent, token-level feature attribution using LIME."""

    _explainer: LimeTextExplainer = None

    @classmethod
    def get_lime_explainer(cls, class_names: List[str]) -> LimeTextExplainer:
        if cls._explainer is None:
            cls._explainer = LimeTextExplainer(
                class_names=class_names,
                random_state=42
            )
        return cls._explainer

    @classmethod
    def explain_prediction(
        cls,
        text: str,
        predicted_label: str,
        vectorizer: Any,
        classifier: Any,
        label_encoder: Any,
        top_k: int = 6,
        num_samples: int = 100
    ) -> List[Dict[str, Any]]:
        """Run LIME text perturbation to generate exact token importance weights."""
        if not hasattr(classifier, "predict_proba"):
            return []

        classes = list(label_encoder.classes_)
        if predicted_label not in classes:
            return []

        target_class_idx = classes.index(predicted_label)

        def predict_proba_fn(texts: List[str]) -> np.ndarray:
            X = vectorizer.transform(texts)
            return classifier.predict_proba(X)

        try:
            explainer = cls.get_lime_explainer(classes)
            # LIME local perturbation
            exp = explainer.explain_instance(
                text_instance=text,
                classifier_fn=predict_proba_fn,
                labels=[target_class_idx],
                num_features=top_k,
                num_samples=num_samples,
            )

            weights_list = exp.as_list(label=target_class_idx)

            features = []
            for word, weight in weights_list:
                clean_word = word.strip()
                if not clean_word:
                    continue

                # Positive weight pushes toward predicted class, negative pushes away
                if predicted_label != AttackCategory.BENIGN.value:
                    direction = "attack" if weight > 0 else "benign"
                else:
                    direction = "benign" if weight > 0 else "attack"

                features.append({
                    "feature": clean_word,
                    "weight": round(abs(weight), 4),
                    "raw_weight": round(weight, 4),
                    "direction": direction,
                })

            return features

        except Exception as e:
            logger.warning(f"LIME explanation generation failed, falling back to TF-IDF weights: {e}")
            return cls._fallback_tfidf_explain(text, predicted_label, vectorizer, classifier, label_encoder, top_k)

    @classmethod
    def _fallback_tfidf_explain(
        cls,
        text: str,
        predicted_label: str,
        vectorizer: Any,
        classifier: Any,
        label_encoder: Any,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Fast fallback using direct TF-IDF feature weight alignment."""
        try:
            classes = list(label_encoder.classes_)
            class_idx = classes.index(predicted_label)
            X = vectorizer.transform([text])
            if X.nnz == 0:
                return []

            feature_names = []
            for name, trans in vectorizer.transformer_list:
                feature_names.extend(trans.get_feature_names_out())

            non_zero_indices = X.indices
            non_zero_values = X.data
            class_coefs = classifier.coef_[class_idx]

            contributions = []
            for idx, val in zip(non_zero_indices, non_zero_values):
                weight = float(val * class_coefs[idx])
                feat_name = feature_names[idx].strip()
                if len(feat_name) < 2:
                    continue

                direction = "attack" if predicted_label != AttackCategory.BENIGN.value else "benign"
                if weight < 0:
                    direction = "benign" if direction == "attack" else "attack"

                contributions.append({
                    "feature": feat_name,
                    "weight": round(abs(weight), 4),
                    "raw_weight": round(weight, 4),
                    "direction": direction,
                })

            contributions.sort(key=lambda x: x["raw_weight"], reverse=True)
            return [
                {"feature": it["feature"], "weight": it["weight"], "direction": it["direction"]}
                for it in contributions[:top_k]
            ]
        except Exception:
            return []
