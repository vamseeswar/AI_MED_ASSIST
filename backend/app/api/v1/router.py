from fastapi import APIRouter
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.documents import router as documents_router
from backend.app.api.v1.search import router as search_router
from backend.app.api.v1.ml import router as ml_router
from backend.app.api.v1.dl import router as dl_router
from backend.app.api.v1.chat import router as chat_router
from backend.app.api.v1.admin import router as admin_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(documents_router)
api_router.include_router(search_router)
api_router.include_router(ml_router)
api_router.include_router(dl_router)
api_router.include_router(chat_router)
api_router.include_router(admin_router)
