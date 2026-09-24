"""ML Classifier Service providing Layer 2 inspection and model lifecycle management."""

from typing import Dict, Any
from app.ml.predict import ml_predictor


class MLClassifierService:
    """Service wrapper for ML inference and explainability."""

    def predict(self, text: str) -> Dict[str, Any]:
        """Classify prompt text using the active ML model."""
        return ml_predictor.predict(text)

    def reload(self):
        """Reload serialized model weights."""
        ml_predictor.load_artifacts(force_reload=True)

    def get_metadata(self) -> Dict[str, Any]:
        """Return active model version and evaluation metrics."""
        return ml_predictor.metadata


ml_classifier_service = MLClassifierService()
