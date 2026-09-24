"""Model prediction service with cached artifact loading and feature explanation."""

import json
import logging
import time
from typing import Dict, Any, Optional
import joblib
import numpy as np

from app.config import settings
from app.core.enums import AttackCategory
from app.ml.preprocessing import preprocess_for_ml
from app.ml.explain import FeatureExplainer

logger = logging.getLogger(__name__)


class MLPredictor:
    """High-speed CPU inference engine for Layer 2 prompt classification."""

    def __init__(self):
        self.vectorizer = None
        self.classifier = None
        self.label_encoder = None
        self.metadata = {}
        self._is_loaded = False
        self.load_artifacts()

    def load_artifacts(self, force_reload: bool = False):
        """Load serialized ML model artifacts from disk."""
        if self._is_loaded and not force_reload:
            return

        artifacts_dir = settings.ARTIFACTS_DIR
        vec_path = artifacts_dir / "vectorizer.joblib"
        clf_path = artifacts_dir / "classifier.joblib"
        le_path = artifacts_dir / "label_encoder.joblib"
        meta_path = artifacts_dir / "model_metadata.json"

        if not (vec_path.exists() and clf_path.exists() and le_path.exists()):
            logger.warning("ML artifacts not found. Training model now...")
            try:
                from app.ml.train import train_model
                train_model()
            except Exception as e:
                logger.error(f"Failed to auto-train model: {e}")
                return

        try:
            self.vectorizer = joblib.load(vec_path)
            self.classifier = joblib.load(clf_path)
            self.label_encoder = joblib.load(le_path)

            if meta_path.exists():
                with open(meta_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
            else:
                self.metadata = {"version": "tfidf-logreg-v1"}

            self._is_loaded = True
            logger.info(f"Loaded ML model version {self.metadata.get('version', 'v1')}")
        except Exception as e:
            logger.error(f"Error loading ML artifacts: {e}")
            self._is_loaded = False

    def predict(self, text: str) -> Dict[str, Any]:
        """Perform multiclass inference on a prompt."""
        start_time = time.perf_counter()

        if not self._is_loaded:
            self.load_artifacts()

        if not self._is_loaded or self.classifier is None:
            # Safe heuristic fallback if model could not be loaded
            return {
                "label": AttackCategory.BENIGN.value,
                "confidence": 0.50,
                "probabilities": {AttackCategory.BENIGN.value: 0.50},
                "top_features": [],
                "model_version": "fallback-unloaded",
                "latency_ms": 0.0,
            }

        processed_text = preprocess_for_ml(text)
        X = self.vectorizer.transform([processed_text])
        probas = self.classifier.predict_proba(X)[0]
        classes = self.label_encoder.classes_

        top_idx = int(np.argmax(probas))
        predicted_label = str(classes[top_idx])
        confidence = float(probas[top_idx])

        # Probability dictionary
        prob_dict = {
            str(cls_name): round(float(prob), 4)
            for cls_name, prob in zip(classes, probas)
        }

        # Explainability feature attribution
        top_features = FeatureExplainer.explain_prediction(
            text=processed_text,
            predicted_label=predicted_label,
            vectorizer=self.vectorizer,
            classifier=self.classifier,
            label_encoder=self.label_encoder,
            top_k=5
        )

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "label": predicted_label,
            "confidence": round(confidence, 4),
            "probabilities": prob_dict,
            "top_features": top_features,
            "model_version": self.metadata.get("version", "tfidf-logreg-v1"),
            "latency_ms": round(latency_ms, 2),
        }


ml_predictor = MLPredictor()
