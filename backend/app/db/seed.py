import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.database import SessionLocal, engine
from app.db.base import Base
from app.db.models import (
    User,
    UserRole,
    Patient,
    Doctor,
    Hospital,
    Consultation,
    ConsultationStatus,
    ClinicalCase,
    ClinicalCaseStatus,
    Prescription,
    PrescriptionStatus,
    Document,
    DocumentProcessingStatus,
    MedicalRecord,
    Consent,
    ConsentStatus,
    Notification,
    NotificationCategory,
)
from app.core.security import get_password_hash


def seed_database():
    print("Initializing tables...")
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if already seeded
        existing_doc = db.scalar(select(Doctor).where(Doctor.doctor_identifier == "DOC-IND-1049"))
        if existing_doc:
            print("Database already contains seed data.")
            return

        print("Seeding development data...")

        # 1. Hospitals
        hosp_a = Hospital(
            name="Apollo Speciality Diagnostics",
            code="HOSP_A_APOLLO",
            base_url="https://api.apollo-diagnostics.internal/fhir",
            integration_type="REST_JSON",
            is_active=True,
        )
        hosp_b = Hospital(
            name="Fortis Hospital - Department of Cardiology",
            code="HOSP_B_FORTIS",
            base_url="https://fhir.fortis-healthcare.internal/r4",
            integration_type="FHIR_R4",
            is_active=True,
        )
        hosp_c = Hospital(
            name="Manipal Hospital & Ayush Integrative Health Centre",
            code="HOSP_C_AYUSH",
            base_url="https://ayush.manipal.internal/api/v1",
            integration_type="AYUSH_HUB",
            is_active=True,
        )
        db.add_all([hosp_a, hosp_b, hosp_c])
        db.flush()

        # 2. Doctor User
        doctor_user = User(
            email="dr.priya.sharma@apollohealth.com",
            phone="9876543200",
            password_hash=get_password_hash("doctor123"),
            role=UserRole.DOCTOR,
            is_active=True,
        )
        db.add(doctor_user)
        db.flush()

        doctor = Doctor(
            user_id=doctor_user.id,
            doctor_identifier="DOC-IND-1049",
            name="Dr. Priya Sharma",
            specialization="General Physician, MBBS, MD (Internal Medicine)",
            registration_number="MCI-KMC-2014-9812",
            hospital_id=hosp_a.id,
        )
        db.add(doctor)
        db.flush()

        # 3. Patient 1 User (Ramesh Kumar - Primary test patient)
        p1_user = User(
            email="ramesh.kumar@healthmail.com",
            phone="9876543210",
            password_hash=get_password_hash("patient123"),
            role=UserRole.PATIENT,
            is_active=True,
        )
        db.add(p1_user)
        db.flush()

        p1 = Patient(
            user_id=p1_user.id,
            patient_identifier="PCT-PAT-88492",
            first_name="Ramesh",
            last_name="Kumar",
            date_of_birth="1984-06-15",
            gender="Male",
            blood_group="O+",
            phone="9876543210",
            email="ramesh.kumar@healthmail.com",
            address="Flat 402, Green Meadows Residency, Outer Ring Road, Bengaluru - 560103",
            emergency_contact="9876543211",
            allergies=["Penicillin (Severe rash)", "Dust Mites"],
            chronic_conditions=["Hypertension (Stage 1)"],
        )
        db.add(p1)

        # 4. Patient 2 User (Anita Desai)
        p2_user = User(
            email="anita.desai@healthmail.com",
            phone="9876543222",
            password_hash=get_password_hash("patient123"),
            role=UserRole.PATIENT,
            is_active=True,
        )
        db.add(p2_user)
        db.flush()

        p2 = Patient(
            user_id=p2_user.id,
            patient_identifier="PCT-PAT-44019",
            first_name="Anita",
            last_name="Desai",
            date_of_birth="1992-11-20",
            gender="Female",
            blood_group="B+",
            phone="9876543222",
            email="anita.desai@healthmail.com",
            address="12th Main, Indiranagar, Bengaluru - 560038",
            emergency_contact="9876543223",
            allergies=["Sulfa drugs"],
            chronic_conditions=["Hypothyroidism"],
        )
        db.add(p2)
        db.flush()

        # 5. Consultation & Diarized Transcript
        consultation = Consultation(
            patient_id=p1.id,
            doctor_id=doctor.id,
            status=ConsultationStatus.COMPLETED,
            started_at=datetime(2026, 2, 24, 11, 30, tzinfo=timezone.utc),
            ended_at=datetime(2026, 2, 24, 11, 45, tzinfo=timezone.utc),
            audio_storage_key="audio/cons_2026_02_24_88492.wav",
            transcript=[
                {"speaker": "doctor", "text": "Good morning Ramesh ji. What brings you in today?", "start": 0.0, "end": 3.2},
                {"speaker": "patient", "text": "Doctor, I have had a severe dry cough and throat irritation for 3 days.", "start": 3.8, "end": 8.5},
                {"speaker": "doctor", "text": "Any fever or difficulty swallowing?", "start": 9.0, "end": 11.2},
                {"speaker": "patient", "text": "Yes, mild fever in the evening and pain while swallowing solid foods.", "start": 11.5, "end": 16.0},
                {"speaker": "doctor", "text": "Are you continuing your daily Telmisartan 40mg?", "start": 16.5, "end": 19.8},
                {"speaker": "patient", "text": "Yes, taking it every morning without fail.", "start": 20.2, "end": 22.8},
            ],
        )
        db.add(consultation)
        db.flush()

        # 6. Clinical Case
        clinical_case = ClinicalCase(
            consultation_id=consultation.id,
            patient_id=p1.id,
            status=ClinicalCaseStatus.CONFIRMED,
            symptoms=["Sore throat", "Dry irritating cough", "Mild low-grade fever", "General malaise"],
            complaints="Sore throat, throat irritation, dry irritating cough",
            duration="3 Days",
            medical_history=["Essential Hypertension (on Telmisartan 40mg)", "No prior asthma"],
            allergies=["Known Penicillin Allergy (Severe rash)"],
            medications=["Tab. Telmisartan 40mg once daily"],
            family_history="Father had hypertension and diabetes mellitus",
            examination={
                "Blood Pressure": "124/82 mmHg",
                "Pulse Rate": "78 bpm",
                "Temperature": "99.4 °F",
                "SpO2": "98% on room air",
                "Weight": "74.5 kg",
            },
            doctor_notes="Pharyngeal erythema observed without purulent exudates. Penicillin avoidance verified. Prescribed symptomatic relief.",
            confirmed_by_doctor_id=doctor.id,
            confirmed_at=datetime(2026, 2, 24, 11, 45, tzinfo=timezone.utc),
        )
        db.add(clinical_case)

        # 7. Prescriptions
        rx1 = Prescription(
            consultation_id=consultation.id,
            patient_id=p1.id,
            doctor_id=doctor.id,
            diagnosis_notes="Acute Pharyngitis & Dry Cough",
            medicines=[
                {
                    "name": "Tab. Paracetamol 650mg (Dolo)",
                    "dosage": "650 mg",
                    "frequency": "1-0-1 (Morning & Night)",
                    "duration": "3 Days",
                    "timing": "After food",
                    "instructions": "Take only when fever > 99.5°F or body ache occurs",
                },
                {
                    "name": "Tab. Montair-LC (Montelukast + Levocetirizine)",
                    "dosage": "10mg / 5mg",
                    "frequency": "0-0-1 (Night only)",
                    "duration": "5 Days",
                    "timing": "At bedtime after dinner",
                    "instructions": "May cause mild drowsiness",
                },
                {
                    "name": "Syrup Ascoril-D Cough Relief",
                    "dosage": "10 ml",
                    "frequency": "1-1-1 (TID)",
                    "duration": "5 Days",
                    "timing": "After meals",
                    "instructions": "Warm water gargles 3 times a day",
                },
            ],
            general_advice="Maintain adequate oral hydration. Avoid cold liquids and fried foods.",
            doctor_notes="Patient advised to review if temperature exceeds 101°F.",
            follow_up_date="2026-03-02",
            status=PrescriptionStatus.ACTIVE,
            is_active=True,
        )
        db.add(rx1)

        # 8. Documents
        doc1 = Document(
            patient_id=p1.id,
            uploaded_by=p1_user.id,
            title="Complete Blood Count (CBC) & Lipid Profile",
            document_type="Blood Test Report",
            hospital_name="Apollo Speciality Diagnostics",
            document_date="2026-02-18",
            file_name="cbc_lipid_report.pdf",
            mime_type="application/pdf",
            file_size_bytes=1887436,
            file_size_display="1.8 MB",
            storage_key="documents/seed_doc_101_cbc.pdf",
            processing_status=DocumentProcessingStatus.PROCESSED,
            extracted_summary="Hemoglobin: 14.2 g/dL (Normal), Total WBC: 7,800 /uL (Normal). Total Cholesterol: 210 mg/dL (Borderline High).",
            structured_data={"Hemoglobin": "14.2 g/dL", "Total WBC": "7,800 /uL", "Total Cholesterol": "210 mg/dL"},
        )
        doc2 = Document(
            patient_id=p1.id,
            uploaded_by=p1_user.id,
            title="Chest X-Ray PA View Report",
            document_type="X-Ray Report",
            hospital_name="Fortis Hospital Imaging Centre",
            document_date="2026-01-10",
            file_name="chest_xray_pa.pdf",
            mime_type="application/pdf",
            file_size_bytes=3565158,
            file_size_display="3.4 MB",
            storage_key="documents/seed_doc_102_xray.pdf",
            processing_status=DocumentProcessingStatus.PROCESSED,
            extracted_summary="Normal bronchovascular markings. No focal consolidation, pneumothorax, or pleural effusion noted.",
            structured_data={"Impression": "Normal Chest Radiograph", "Lungs": "Clear bilaterally"},
        )
        db.add_all([doc1, doc2])

        # 9. Medical Records
        rec1 = MedicalRecord(
            patient_id=p1.id,
            title="Acute Upper Respiratory Tract Infection",
            source_type="CURRENT_SYSTEM",
            source_hospital_id=hosp_a.id,
            record_type="Consultation",
            provider="Dr. Priya Sharma, Apollo Clinic",
            summary="Patient presented with sore throat and cough. Prescribed symptomatic relief.",
            diagnosis="Acute Pharyngitis & Rhinopharyngitis",
            year="2026",
            recorded_at="2026-02-24",
            data={"BP": "124/82 mmHg", "Pulse": "78 bpm", "SpO2": "98%"},
        )
        rec2 = MedicalRecord(
            patient_id=p1.id,
            title="Routine Health Checkup & Blood Panel",
            source_type="UPLOADED_DOCUMENT",
            source_hospital_id=hosp_a.id,
            record_type="Lab Test",
            provider="Apollo Speciality Diagnostics",
            summary="Complete metabolic and lipid screening. Mild hyperlipidemia noted.",
            diagnosis="Borderline Hypercholesterolemia",
            year="2026",
            recorded_at="2026-02-18",
            data={"Weight": "74.5 kg", "BMI": "24.8 kg/m²"},
        )
        db.add_all([rec1, rec2])

        # 10. Consent Requests
        c1 = Consent(
            patient_id=p1.id,
            provider_name="Manipal Hospital Whitefield",
            provider_type="Multi-Specialty Hospital",
            doctor_name="Dr. S. Ranganathan (ENT)",
            purpose="Specialist In-person Clinical Consultation & Case Assessment",
            requested_scope="Medical History + Previous Prescriptions & Lab Reports",
            status=ConsentStatus.PENDING,
            valid_until="24 Hours",
        )
        c2 = Consent(
            patient_id=p1.id,
            provider_name="Apollo Clinic, Koramangala",
            provider_type="Outpatient Clinic",
            doctor_name="Dr. Priya Sharma",
            purpose="General Outpatient Case Taking & Record Linking",
            requested_scope="Full Medical Timeline + Active Medications",
            status=ConsentStatus.GRANTED,
            valid_until="30 Days",
        )
        db.add_all([c1, c2])

        # 11. Notifications
        n1 = Notification(
            user_id=p1_user.id,
            title="Consent Access Request",
            message="Manipal Hospital has requested temporary access to your medical history.",
            category=NotificationCategory.CONSENT,
            target_route="/consent-access",
            is_read=False,
        )
        n2 = Notification(
            user_id=p1_user.id,
            title="Prescription Added",
            message="Dr. Priya Sharma issued a new prescription for Acute Pharyngitis.",
            category=NotificationCategory.PRESCRIPTION,
            target_route="/prescriptions",
            is_read=False,
        )
        db.add_all([n1, n2])

        db.commit()
        print("Database seeded successfully with 1 doctor, 2 patients, clinical records, documents, and hospital connectors!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
