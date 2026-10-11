from pydantic import BaseModel, Field


class MLClassifyRequest(BaseModel):
    text: str = Field(..., min_length=5, description="Document or section text to classify")


class MLClassifyResponse(BaseModel):
    category: str
    confidence: float
    model_version: str
    inference_time_ms: float


class DLClassifyRequest(BaseModel):
    text: str = Field(..., min_length=5, description="Text to classify using deep learning transformer")


class DLClassifyResponse(BaseModel):
    label: str
    confidence: float
    model_version: str
    inference_time_ms: float
