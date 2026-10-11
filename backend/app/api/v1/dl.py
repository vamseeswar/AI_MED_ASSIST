from fastapi import APIRouter, Depends, Request
from backend.app.schemas.ml import DLClassifyRequest, DLClassifyResponse
from backend.app.services.auth_service import get_current_user
from backend.app.models.user import User
from dl.models.classifier_model import get_dl_classifier

router = APIRouter(prefix="/dl", tags=["Deep Learning"])


@router.post("/classify", response_model=DLClassifyResponse)
def classify_document_dl(
    req: DLClassifyRequest,
    current_user: User = Depends(get_current_user)
):
    """Classifies document using PyTorch / Transformer deep learning component."""
    classifier = get_dl_classifier()
    result = classifier.classify(req.text)
    return DLClassifyResponse(
        label=result["label"],
        confidence=result["confidence"],
        model_version=result["model_version"],
        inference_time_ms=result["inference_time_ms"]
    )
