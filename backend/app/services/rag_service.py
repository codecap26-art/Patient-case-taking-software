import logging
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, or_
from app.db.models.patient import Patient
from app.db.models.document import Document
from app.db.models.prescription import Prescription
from app.db.models.consultation import Consultation
from app.db.models.medical_record import MedicalRecord
from app.db.models.clinical_case import ClinicalCase
from app.db.models.knowledge import KnowledgeChunk, KnowledgeDocument
from app.schemas.doctor_ai import AISource

logger = logging.getLogger(__name__)


class RAGService:
    """
    Dual-Layer Clinical RAG Service.
    Ported & adapted from DoctorAI repository.
    Layer 1: Authorized Patient EHR Context (Demographics, Allergies, Prescriptions, Cases, OCR Docs).
    Layer 2: Clinical Guidelines & Ayush Knowledge Chunks.
    """

    @staticmethod
    def retrieve_authorized_context(
        db: Session,
        patient_id: str,
        question: str,
    ) -> Tuple[str, List[AISource]]:
        sources: List[AISource] = []
        context_blocks: List[str] = []

        if not patient_id:
            return "", []

        # 1. Fetch Patient Demographics & Allergies
        patient = db.scalar(
            select(Patient).where(
                or_(
                    Patient.id == patient_id,
                    Patient.patient_identifier == patient_id,
                    Patient.patient_identifier.ilike(f"%{patient_id}%"),
                )
            )
        )

        if patient:
            allergies_str = ", ".join(patient.allergies or ["None reported"])
            conditions_str = ", ".join(patient.chronic_conditions or ["None reported"])
            p_summary = (
                f"PATIENT DEMOGRAPHICS & RECORD SUMMARY:\n"
                f"• Patient Name: {patient.first_name} {patient.last_name}\n"
                f"• Patient ID: {patient.patient_identifier or patient.id}\n"
                f"• Date of Birth: {patient.date_of_birth or 'N/A'}, Gender: {patient.gender or 'N/A'}, Blood Group: {patient.blood_group or 'N/A'}\n"
                f"• Documented Allergies: {allergies_str}\n"
                f"• Chronic Conditions: {conditions_str}"
            )
            context_blocks.append(p_summary)
            sources.append(
                AISource(
                    source_type="patient_profile",
                    type="Patient Profile",
                    id=patient.id,
                    title=f"Patient EHR Chart ({patient.first_name} {patient.last_name})",
                    date=str(patient.updated_at.date()) if getattr(patient, "updated_at", None) else None,
                    snippet=f"Allergies: {allergies_str} | Conditions: {conditions_str}",
                )
            )

        # 2. Fetch Active & Historical Prescriptions
        actual_pid = patient.id if patient else patient_id
        prescriptions = db.scalars(
            select(Prescription).where(Prescription.patient_id == actual_pid).order_by(desc(Prescription.created_at)).limit(5)
        ).all()
        if prescriptions:
            rx_blocks = ["ACTIVE & HISTORICAL MEDICATIONS:"]
            for rx in prescriptions:
                med_lines = []
                for m in rx.medicines or []:
                    med_lines.append(f"{m.get('name')} {m.get('dosage')} ({m.get('frequency')}) for {m.get('duration')}")
                meds_str = "; ".join(med_lines) or "No medications detailed"
                rx_blocks.append(f"• Prescription [{rx.status.value if hasattr(rx.status, 'value') else rx.status}]: {rx.diagnosis_notes or 'Consultation Rx'} -> {meds_str}")
                sources.append(
                    AISource(
                        source_type="prescription",
                        type="Prescription",
                        id=rx.id,
                        title=f"Prescription: {rx.diagnosis_notes or 'Medical Rx'}",
                        date=str(rx.created_at.date()) if rx.created_at else None,
                        snippet=f"Medications: {meds_str[:160]}",
                    )
                )
            context_blocks.append("\n".join(rx_blocks))

        # 3. Fetch Confirmed Clinical Cases
        cases = db.scalars(
            select(ClinicalCase).where(ClinicalCase.patient_id == actual_pid).order_by(desc(ClinicalCase.created_at)).limit(5)
        ).all()
        if cases:
            case_blocks = ["CLINICAL CONSULTATION ASSESSMENTS:"]
            for c in cases:
                symptoms_str = ", ".join(c.symptoms or []) if isinstance(c.symptoms, list) else str(c.symptoms or "None")
                case_blocks.append(
                    f"• Case ({c.status.value if hasattr(c.status, 'value') else c.status}): Complaints: {c.complaints or 'None'}. "
                    f"Symptoms: {symptoms_str}. Notes: {c.doctor_notes or 'None'}."
                )
                sources.append(
                    AISource(
                        source_type="clinical_case",
                        type="Clinical Case",
                        id=c.id,
                        title=f"Clinical Case ({c.case_number if hasattr(c, 'case_number') else 'Assessment'})",
                        date=str(c.created_at.date()) if c.created_at else None,
                        snippet=f"Complaints: {c.complaints}; Symptoms: {symptoms_str[:120]}",
                    )
                )
            context_blocks.append("\n".join(case_blocks))

        # 4. Fetch Medical Documents & OCR Extracted Parameters
        docs = db.scalars(
            select(Document).where(Document.patient_id == actual_pid).order_by(desc(Document.created_at)).limit(6)
        ).all()
        if docs:
            doc_blocks = ["OCR-SCANNED DIAGNOSTIC & LAB DOCUMENTS:"]
            for d in docs:
                doc_lines = [f"• Document: {d.title} (Type: {d.document_type}, Date: {d.document_date or 'Recent'}, Facility: {d.hospital_name or 'Diagnostics Lab'})"]
                if d.extracted_summary:
                    doc_lines.append(f"  OCR Summary: {d.extracted_summary}")
                if d.structured_data:
                    metrics_str = ", ".join([f"{k}: {v}" for k, v in d.structured_data.items() if k not in ("Document Name", "OCR Status", "Processed Date")])
                    if metrics_str:
                        doc_lines.append(f"  Structured Lab Parameters: {metrics_str}")
                if d.extracted_text and len(d.extracted_text) < 1200:
                    doc_lines.append(f"  Raw OCR Excerpt:\n  {d.extracted_text[:600]}")

                doc_blocks.append("\n".join(doc_lines))

                snippet = d.extracted_summary or ""
                if d.structured_data:
                    filtered_metrics = [f"{k}: {v}" for k, v in list(d.structured_data.items())[:4] if k not in ("Document Name", "OCR Status")]
                    if filtered_metrics:
                        snippet += (" | " if snippet else "") + ", ".join(filtered_metrics)
                sources.append(
                    AISource(
                        source_type="document",
                        type="Medical Document (OCR)",
                        id=d.id,
                        title=f"{d.title} ({d.document_type})",
                        date=d.document_date or (str(d.created_at.date()) if d.created_at else None),
                        snippet=snippet[:180] or f"Indexed OCR diagnostic file: {d.file_name}",
                    )
                )
            context_blocks.append("\n\n".join(doc_blocks))

        full_context = "\n\n--------------------\n\n".join(context_blocks)
        return full_context, sources

    @staticmethod
    def retrieve_knowledge_context(
        db: Session,
        query: str,
        top_k: int = 3,
    ) -> Tuple[str, List[AISource]]:
        """
        Layer 2: Retrieve clinical knowledge guidelines from knowledge_chunks.
        """
        knowledge_sources: List[AISource] = []
        chunks_text: List[str] = []

        try:
            stmt = select(KnowledgeChunk).limit(top_k)
            q_lower = query.lower()
            if "hypertension" in q_lower or "bp" in q_lower:
                stmt = stmt.where(KnowledgeChunk.section.ilike("%hypertension%"))
            elif "allergy" in q_lower or "penicillin" in q_lower:
                stmt = stmt.where(KnowledgeChunk.section.ilike("%allergy%"))
            elif "ayush" in q_lower or "dosha" in q_lower or "prakriti" in q_lower:
                stmt = stmt.where(KnowledgeChunk.section.ilike("%ayush%"))

            chunks = db.scalars(stmt).all()
            if not chunks:
                chunks = db.scalars(select(KnowledgeChunk).limit(top_k)).all()

            for chunk in chunks:
                chunks_text.append(f"[Clinical Guideline - {chunk.section}]:\n{chunk.content}")
                knowledge_sources.append(
                    AISource(
                        source_type="knowledge_chunk",
                        type="Clinical Reference Guideline",
                        id=chunk.id,
                        title=f"Clinical Guideline ({chunk.section})",
                        snippet=chunk.content[:160],
                    )
                )
        except Exception as e:
            logger.warning("Knowledge chunk retrieval error: %s", e)

        return "\n\n".join(chunks_text), knowledge_sources

    @classmethod
    def retrieve_dual_layer_context(
        cls,
        db: Session,
        patient_id: str,
        question: str,
    ) -> Tuple[str, List[AISource]]:
        patient_context, patient_sources = cls.retrieve_authorized_context(db, patient_id, question)
        knowledge_context, knowledge_sources = cls.retrieve_knowledge_context(db, question)

        sections = []
        if patient_context:
            sections.append(f"=== AUTHORIZED PATIENT EHR CONTEXT ===\n{patient_context}")
        if knowledge_context:
            sections.append(f"=== EVIDENCE-BASED CLINICAL & AYUSH GUIDELINES ===\n{knowledge_context}")

        combined_context = "\n\n====================\n\n".join(sections)
        combined_sources = patient_sources + knowledge_sources
        return combined_context, combined_sources


rag_service = RAGService()
