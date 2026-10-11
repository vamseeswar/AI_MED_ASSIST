import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.core.logging import app_logger
from backend.app.middleware.security_headers import SecurityHeadersMiddleware
from backend.app.middleware.logging_middleware import RequestLoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    app_logger.info(f"Starting {settings.APP_NAME} in {settings.APP_ENV} mode...")
    os.makedirs(settings.STORAGE_DIR, exist_ok=True)
    os.makedirs("./data/chroma_db", exist_ok=True)
    os.makedirs("./logs", exist_ok=True)
    yield
    # Shutdown actions
    app_logger.info(f"Shutting down {settings.APP_NAME}...")


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Medical Information & Document Intelligence Platform (Educational & Research Non-Diagnostic Tool)",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time", "X-Request-ID"]
)

# Custom Middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    app_logger.error(f"Unhandled exception on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred. Please contact the administrator.",
            "error_type": type(exc).__name__
        }
    )


from backend.app.api.v1.router import api_router

# Include API Routers
app.include_router(api_router, prefix=settings.API_V1_STR)


# Health check endpoint required by Phase 1
@app.get("/api/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "version": "1.0.0",
        "llm_provider": settings.LLM_PROVIDER,
        "medical_safety_guardrails": "active"
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "docs": "/api/docs",
        "disclaimer": "This is an educational & medical information intelligence platform. It does NOT diagnose diseases, prescribe medication, or replace licensed medical professionals."
    }
