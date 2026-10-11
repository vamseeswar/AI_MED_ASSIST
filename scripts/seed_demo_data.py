"""
Seed script for MedAssist AI.
Creates demo users (Doctor, Admin, Patient) and sample medical documents for immediate RAG retrieval.
"""

import sys
import uuid
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.core.database import SessionLocal, Base, engine
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.models.chunk import DocumentChunk
from backend.app.services.auth_service import get_password_hash
from rag.embeddings.embedding_provider import get_embedding_provider
from rag.retrieval.vector_store import get_vector_store
from rag.retrieval.keyword_index import get_keyword_index


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Seed Users
        users_data = [
            {
                "email": "demo@medassist.ai",
                "password": "DemoPassword123!",
                "full_name": "Dr. Sarah Chen, MD",
                "role": "DOCTOR"
            },
            {
                "email": "admin@medassist.ai",
                "password": "AdminPassword123!",
                "full_name": "System Administrator",
                "role": "ADMIN"
            },
            {
                "email": "patient@medassist.ai",
                "password": "PatientPassword123!",
                "full_name": "John Doe",
                "role": "USER"
            }
        ]

        seeded_users = {}
        for u_info in users_data:
            existing = db.query(User).filter(User.email == u_info["email"]).first()
            if not existing:
                user = User(
                    email=u_info["email"],
                    hashed_password=get_password_hash(u_info["password"]),
                    full_name=u_info["full_name"],
                    role=u_info["role"],
                    is_active=True
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                seeded_users[u_info["email"]] = user
                print(f"[+] Created user: {u_info['email']} (Role: {u_info['role']})")
            else:
                seeded_users[u_info["email"]] = existing
                print(f"[=] User already exists: {u_info['email']}")

        doc_user = seeded_users["demo@medassist.ai"]

        # 2. Seed Sample Clinical Practice Guidelines
        guidelines = [
            {
                "filename": "AHA_ACC_2023_Hypertension_Guideline.txt",
                "title": "AHA/ACC Clinical Practice Guideline for the Management of High Blood Pressure",
                "category": "Cardiology",
                "content": (
                    "American College of Cardiology / American Heart Association Clinical Practice Guideline.\n\n"
                    "Section 1: Classification of Blood Pressure\n"
                    "Normal blood pressure is defined as systolic blood pressure < 120 mm Hg and diastolic < 80 mm Hg. "
                    "Elevated blood pressure is systolic 120-129 mm Hg and diastolic < 80 mm Hg. "
                    "Stage 1 hypertension is systolic 130-139 mm Hg or diastolic 80-89 mm Hg. "
                    "Stage 2 hypertension is systolic >= 140 mm Hg or diastolic >= 90 mm Hg.\n\n"
                    "Section 2: Nonpharmacological Lifestyle Interventions\n"
                    "Weight loss is recommended for overweight or obese adults with hypertension. "
                    "A heart-healthy dietary pattern such as the DASH (Dietary Approaches to Stop Hypertension) diet "
                    "is recommended to achieve significant reduction in blood pressure. "
                    "Dietary sodium reduction to < 1,500 mg/day or at least a 1,000 mg/day reduction lowers blood pressure. "
                    "Enhanced intake of dietary potassium is recommended unless contraindicated by chronic kidney disease. "
                    "Increased physical activity via a structured aerobic exercise regimen of 90-150 minutes per week "
                    "provides measurable systolic blood pressure reductions of 5-8 mm Hg."
                )
            },
            {
                "filename": "GINA_2024_Asthma_Management_Strategy.txt",
                "title": "Global Initiative for Asthma (GINA) Strategy Report",
                "category": "Pulmonology",
                "content": (
                    "Global Initiative for Asthma (GINA) Global Strategy for Asthma Management and Prevention.\n\n"
                    "Section 1: Definition and Clinical Presentation\n"
                    "Asthma is a heterogeneous disease, usually characterized by chronic airway inflammation. "
                    "It is defined by the history of respiratory symptoms such as wheeze, shortness of breath (dyspnea), "
                    "chest tightness, and cough that vary over time and in intensity, together with variable expiratory airflow limitation.\n\n"
                    "Section 2: Diagnostic Assessment\n"
                    "Spirometry confirming variable expiratory airflow limitation is the gold standard for clinical confirmation. "
                    "An increase in FEV1 of > 12% and > 200 mL after bronchodilator inhalation indicates significant reversibility.\n\n"
                    "Section 3: Management Principles\n"
                    "The primary goals of asthma management are symptom control and risk reduction for exacerbations. "
                    "Inhaled corticosteroid (ICS) containing therapy is the foundational maintenance anti-inflammatory backbone."
                )
            },
            {
                "filename": "ADA_2024_Standards_of_Care_Diabetes.txt",
                "title": "American Diabetes Association Standards of Care in Diabetes",
                "category": "Endocrinology",
                "content": (
                    "American Diabetes Association Standards of Care in Diabetes.\n\n"
                    "Section 1: Diagnostic Criteria for Diabetes Mellitus\n"
                    "Diabetes may be diagnosed based on plasma glucose criteria, either the fasting plasma glucose (FPG) value "
                    "or the 2-hour plasma glucose (2-h PG) value during a 75-g oral glucose tolerance test (OGTT), "
                    "or A1C criteria. Diagnostic thresholds:\n"
                    "- Fasting Plasma Glucose >= 126 mg/dL (7.0 mmol/L).\n"
                    "- 2-hour Plasma Glucose >= 200 mg/dL (11.1 mmol/L) during OGTT.\n"
                    "- Glycated Hemoglobin (HbA1c) >= 6.5% (48 mmol/mol).\n"
                    "- In a patient with classic symptoms of hyperglycemia or hyperglycemic crisis, a random plasma glucose >= 200 mg/dL.\n\n"
                    "Section 2: Comprehensive Lifestyle Management\n"
                    "Medical nutrition therapy emphasizes individualized macronutrient distribution, whole grains, fiber, and lean proteins. "
                    "Adults with type 2 diabetes should engage in 150 minutes or more of moderate-to-vigorous intensity aerobic activity weekly."
                )
            }
        ]

        embedder = get_embedding_provider()
        vector_store = get_vector_store()
        bm25_index = get_keyword_index()

        for g in guidelines:
            existing_doc = db.query(Document).filter(Document.filename == g["filename"]).first()
            if existing_doc and db.query(DocumentChunk).filter(DocumentChunk.document_id == existing_doc.id).count() == 0:
                db.delete(existing_doc)
                db.commit()
                existing_doc = None

            if not existing_doc:
                import hashlib
                content_bytes = g["content"].encode("utf-8")
                doc = Document(
                    user_id=doc_user.id,
                    filename=g["filename"],
                    stored_filename=g["filename"],
                    file_type="txt",
                    file_size_bytes=len(content_bytes),
                    file_hash=hashlib.sha256(content_bytes).hexdigest(),
                    status="COMPLETED",
                    title=g["title"],
                    category=g["category"],
                    page_count=1
                )
                db.add(doc)
                db.commit()
                db.refresh(doc)

                # Create chunks
                sections = g["content"].split("\n\n")
                chunk_dicts = []
                chunk_texts = []

                for idx, sec in enumerate(sections):
                    chunk_id = str(uuid.uuid4())
                    heading = sec.split("\n")[0] if "\n" in sec else "General Overview"
                    import json
                    db_chunk = DocumentChunk(
                        id=chunk_id,
                        document_id=doc.id,
                        chunk_index=idx,
                        content=sec,
                        cleaned_content=sec,
                        token_count=len(sec.split()),
                        page_number=1,
                        section_heading=heading,
                        chunk_metadata=json.dumps({
                            "document_name": g["title"],
                            "category": g["category"]
                        })
                    )
                    db.add(db_chunk)
                    chunk_texts.append(sec)
                    chunk_dicts.append({
                        "id": chunk_id,
                        "document_id": doc.id,
                        "chunk_index": idx,
                        "content": sec,
                        "page_number": 1,
                        "section_heading": heading,
                        "document_name": g["title"],
                        "category": g["category"]
                    })

                db.commit()

                # Ingest to ChromaDB and BM25
                embeddings = embedder.embed_documents(chunk_texts)
                vector_store.add_chunks(chunk_dicts, embeddings)
                bm25_index.add_chunks(chunk_dicts)

                print(f"[+] Indexed document: {g['filename']} with {len(sections)} chunks into Vector & BM25 indices.")
            else:
                print(f"[=] Document already indexed: {g['filename']}")

        print("\n[SUCCESS] Seed data completed successfully!")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
