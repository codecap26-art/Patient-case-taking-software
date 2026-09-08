import uuid
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.doctor import Doctor
from app.db.models.knowledge import KnowledgeDocument, KnowledgeChunk
from app.schemas.doctor_ai import (
    DoctorAIQueryRequest,
    DoctorAIQueryResponse,
    MessageInput,
    AIResponseSchema,
    AISource,
)
from app.services.doctor_ai_service import DoctorAIService
from app.core.dependencies import require_doctor, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/doctor-ai", tags=["Doctor AI & Clinical RAG"])


@router.post("/query", response_model=DoctorAIQueryResponse)
async def query_doctor_ai(
    req: DoctorAIQueryRequest,
    doctor_info: tuple[User, Doctor] = Depends(require_doctor),
    db: Session = Depends(get_db),
):
    """
    Doctor AI Clinical Decision Support Query Endpoint.
    1. Authenticates doctor.
    2. Enforces consent and patient data boundary.
    3. Retrieves Layer 1 (Patient EHR + OCR diagnostic summaries) and Layer 2 (Guidelines).
    4. Executes LLM synthesis with source attribution and clinical disclaimer.
    """
    user, _ = doctor_info
    return await DoctorAIService.query(db, req, user)


@router.post("/conversations/{conversation_id}/message", response_model=AIResponseSchema)
async def send_conversation_message(
    conversation_id: str,
    payload: MessageInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Interactive clinical history taking / MediKiosk intake assistant.
    Guides through chief complaints, HPI, Ayush profile, and detects emergency flags.
    """
    return await DoctorAIService.process_conversation_message(
        db=db,
        conversation_id=conversation_id,
        message=payload.message,
    )


@router.get("/knowledge")
def list_knowledge(
    q: Optional[str] = Query(None, description="Search term for guidelines"),
    db: Session = Depends(get_db),
):
    """
    Retrieve clinical reference guidelines from the knowledge base.
    """
    stmt = select(KnowledgeDocument).limit(10)
    if q:
        stmt = stmt.where(KnowledgeDocument.title.ilike(f"%{q}%"))
    docs = db.scalars(stmt).all()
    return [
        {
            "id": doc.id,
            "title": doc.title,
            "category": doc.category,
            "source": doc.source,
            "chunks_count": len(doc.chunks) if doc.chunks else 0,
        }
        for doc in docs
    ]


@router.post("/knowledge/seed")
def seed_knowledge(db: Session = Depends(get_db)):
    """
    Seed standard evidence-based clinical and Ayush guidelines into pgvector knowledge base.
    """
    existing = db.scalar(select(KnowledgeDocument).limit(1))
    if existing:
        return {"message": "Knowledge base already seeded", "count": 3}

    # 1. Hypertension Guideline
    doc1 = KnowledgeDocument(
        id=str(uuid.uuid4()),
        title="National Clinical Management Guideline: Essential Hypertension",
        category="Cardiology / Internal Medicine",
        source="ICMR / WHO Hypertension Guidelines",
        content="Stage 1 Hypertension (130-139 / 80-89 mmHg). Stage 2 Hypertension (>=140 / >=90 mmHg). First-line therapies include ARBs (Telmisartan 40mg), CCBs (Amlodipine 5mg), or Thiazides. Sodium restriction (<2g/day) is recommended.",
    )
    chunk1 = KnowledgeChunk(
        id=str(uuid.uuid4()),
        document=doc1,
        section="hypertension_management",
        content="Hypertension Stage 2 requires dual therapy: ARB + CCB (e.g. Telmisartan + Amlodipine). Target BP is <130/80 mmHg in diabetic patients.",
        metadata_json={"disease": "hypertension", "category": "allopathy"},
    )

    # 2. Beta-Lactam Allergy & Anaphylaxis Safety
    doc2 = KnowledgeDocument(
        id=str(uuid.uuid4()),
        title="Drug Allergy & Anaphylaxis Prevention Protocol",
        category="Pharmacology & Clinical Safety",
        source="British Society for Allergy and Clinical Immunology / CDSCO",
        content="Patients with confirmed immediate-type hypersensitivity (anaphylaxis, angioedema, urticaria) to Penicillins must strictly avoid all beta-lactams including ampicillin, amoxicillin, and co-amoxiclav due to cross-reactivity.",
    )
    chunk2 = KnowledgeChunk(
        id=str(uuid.uuid4()),
        document=doc2,
        section="penicillin_allergy",
        content="Absolute Contraindication: Penicillin allergy with anaphylaxis history precludes beta-lactam usage. Utilize macrolides (e.g. Azithromycin) or fluoroquinolones.",
        metadata_json={"allergen": "penicillin", "category": "safety"},
    )

    # 3. Ayush Prakriti & Dosha Guidelines
    doc3 = KnowledgeDocument(
        id=str(uuid.uuid4()),
        title="Ayush Clinical Guidelines for Prakriti & Metabolic Balance",
        category="Ayush / Ayurveda",
        source="Ministry of Ayush, Government of India",
        content="Prakriti represents constitutional genetic predisposition (Vata, Pitta, Kapha). Vata governs motion and dryness; Pitta governs digestion and heat; Kapha governs structure and stability. Treatment balances Dosha through Ahara (diet), Vihara (lifestyle), and Aushadha.",
    )
    chunk3 = KnowledgeChunk(
        id=str(uuid.uuid4()),
        document=doc3,
        section="ayush_prakriti_dosha",
        content="Pitta dosha elevation causes acidity, hypertension, and heat intolerance. Recommended Ahara includes Sheetala (cooling) dravyas and avoiding excessive Ushna/Lavana.",
        metadata_json={"system": "ayush", "category": "dosha"},
    )

    db.add_all([doc1, doc2, doc3, chunk1, chunk2, chunk3])
    db.commit()

    return {"message": "Knowledge guidelines seeded successfully into knowledge_documents and knowledge_chunks.", "count": 3}
