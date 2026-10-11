import os
import pytest

os.environ["APP_ENV"] = "test"
os.environ["EMBEDDING_PROVIDER"] = "mock"
os.environ["LLM_PROVIDER"] = "mock"
os.environ["RERANKER_ENABLED"] = "False"
os.environ["DATABASE_URL"] = "sqlite:///./data/test_suite.db"

from backend.app.core.config import settings
settings.APP_ENV = "test"
settings.EMBEDDING_PROVIDER = "mock"
settings.LLM_PROVIDER = "mock"
settings.RERANKER_ENABLED = False
settings.DATABASE_URL = "sqlite:///./data/test_suite.db"

from backend.app.main import app

from backend.app.core.database import Base, engine
import backend.app.models

# Initialize database schema for all tests
Base.metadata.create_all(bind=engine)

import rag.retrieval.vector_store as vs
import rag.retrieval.keyword_index as ki
import rag.pipelines.rag_pipeline as rp

# Use in-memory stores for testing
vs._GLOBAL_VECTOR_STORE = vs.InMemoryVectorStore()
ki._GLOBAL_BM25_INDEX = ki.BM25KeywordIndex()
rp._GLOBAL_RAG_PIPELINE = rp.RAGPipeline()


@pytest.fixture(autouse=True)
def ensure_clean_test_state():
    """Ensures clean database state and clears overrides between tests."""
    app.dependency_overrides.clear()
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
    yield
    app.dependency_overrides.clear()
