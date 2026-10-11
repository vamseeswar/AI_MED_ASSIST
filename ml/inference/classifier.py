import os
import time
import joblib
from typing import Dict, Any, Optional
from ml.preprocessing.text_normalizer import normalize_text_for_ml
from backend.app.core.logging import app_logger

MODEL_PATH = "ml/saved_models/doc_classifier.joblib"
_LOADED_MODEL = None


class MLDocumentClassifier:
    def __init__(self, model_path: str = MODEL_PATH):
        global _LOADED_MODEL
        self.model_path = model_path
        if _LOADED_MODEL is None and os.path.exists(model_path):
            try:
                _LOADED_MODEL = joblib.load(model_path)
                app_logger.info("Loaded persisted Scikit-learn document classifier.")
            except Exception as exc:
                app_logger.warning(f"Could not load ML model: {exc}")
        self.model = _LOADED_MODEL

    def classify(self, text: str) -> Dict[str, Any]:
        start_time = time.time()
        norm_text = normalize_text_for_ml(text)

        if not self.model:
            # Fallback heuristic
            inference_ms = (time.time() - start_time) * 1000
            t_lower = text.lower()
            if "lab" in t_lower or "cholesterol" in t_lower or "hemoglobin" in t_lower:
                cat = "laboratory_report"
            elif "insurance" in t_lower or "claim" in t_lower or "copay" in t_lower:
                cat = "insurance_document"
            elif "abstract" in t_lower or "methodology" in t_lower or "trial" in t_lower:
                cat = "medical_research"
            elif "patient" in t_lower or "physician" in t_lower or "vital signs" in t_lower:
                cat = "clinical_report"
            else:
                cat = "general_health_information"

            return {
                "category": cat,
                "confidence": 0.85,
                "model_version": "1.0.0-heuristic",
                "inference_time_ms": round(inference_ms, 2)
            }

        try:
            probs = self.model.predict_proba([norm_text])[0]
            pred_idx = probs.argmax()
            pred_class = self.model.classes_[pred_idx]
            confidence = float(probs[pred_idx])
            inference_ms = (time.time() - start_time) * 1000

            return {
                "category": str(pred_class),
                "confidence": round(confidence, 4),
                "model_version": "1.0.0-sklearn",
                "inference_time_ms": round(inference_ms, 2)
            }
        except Exception as exc:
            app_logger.error(f"ML classification inference error: {exc}")
            inference_ms = (time.time() - start_time) * 1000
            return {
                "category": "other",
                "confidence": 0.50,
                "model_version": "1.0.0-error",
                "inference_time_ms": round(inference_ms, 2)
            }


_GLOBAL_ML_CLASSIFIER = None


def get_ml_classifier() -> MLDocumentClassifier:
    global _GLOBAL_ML_CLASSIFIER
    if _GLOBAL_ML_CLASSIFIER is None:
        _GLOBAL_ML_CLASSIFIER = MLDocumentClassifier()
    return _GLOBAL_ML_CLASSIFIER
