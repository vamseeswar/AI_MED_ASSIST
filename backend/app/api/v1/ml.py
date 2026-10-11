from fastapi import APIRouter, Depends, Request
from backend.app.schemas.ml import MLClassifyRequest, MLClassifyResponse
from backend.app.services.auth_service import get_current_user
from backend.app.models.user import User
from ml.inference.classifier import get_ml_classifier

router = APIRouter(prefix="/ml", tags=["Machine Learning"])


@router.post("/classify-document", response_model=MLClassifyResponse)
def classify_document_ml(
    req: MLClassifyRequest,
    current_user: User = Depends(get_current_user)
):
    """Classifies medical document text using trained Scikit-learn model."""
    classifier = get_ml_classifier()
    result = classifier.classify(req.text)
    return MLClassifyResponse(
        category=result["category"],
        confidence=result["confidence"],
        model_version=result["model_version"],
        inference_time_ms=result["inference_time_ms"]
    )
