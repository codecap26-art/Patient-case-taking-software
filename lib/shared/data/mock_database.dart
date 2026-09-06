import '../models/patient_model.dart';
import '../models/document_model.dart';
import '../models/medical_record_model.dart';
import '../models/prescription_model.dart';
import '../models/consultation_model.dart';
import '../models/consent_request_model.dart';
import '../models/notification_model.dart';

/// In-memory Mock Database containing rich clinical data for testing & offline demonstration.
class MockDatabase {
  MockDatabase._();

  static PatientModel currentPatient = PatientModel(
    id: 'PCT-PAT-88492',
    name: 'Ramesh Kumar',
    phone: '9876543210',
    email: 'ramesh.kumar@healthmail.com',
    dateOfBirth: '1984-06-15',
    gender: 'Male',
    bloodGroup: 'O+',
    emergencyContact: '9876543211',
    address: 'Flat 402, Green Meadows Residency, Outer Ring Road, Bengaluru - 560103',
    qrCodeToken: 'PCT:IDENTITY:v1:88492:SEC9218FA72',
    allergies: ['Penicillin', 'Dust Mites'],
    chronicConditions: ['Hypertension (Stage 1)'],
  );

  static List<MedicalDocumentModel> documents = [
    MedicalDocumentModel(
      id: 'DOC-101',
      title: 'Complete Blood Count (CBC) & Lipid Profile',
      documentType: 'Blood Test Report',
      hospitalName: 'Apollo Speciality Diagnostics',
      date: '2026-02-18',
      status: DocumentStatus.available,
      fileSize: '1.8 MB',
      extractedSummary:
          'Hemoglobin: 14.2 g/dL (Normal), Total WBC: 7,800 /uL (Normal), Platelets: 240,000 /uL. Total Cholesterol: 210 mg/dL (Borderline High), HDL: 44 mg/dL, LDL: 132 mg/dL. Fasting Blood Glucose: 98 mg/dL (Normal).',
      structuredData: {
        'Hemoglobin': '14.2 g/dL',
        'Total WBC': '7,800 /uL',
        'Cholesterol': '210 mg/dL',
        'Fasting Blood Sugar': '98 mg/dL',
      },
    ),
    MedicalDocumentModel(
      id: 'DOC-102',
      title: 'Chest X-Ray PA View Report',
      documentType: 'X-Ray Report',
      hospitalName: 'Fortis Hospital Imaging Centre',
      date: '2026-01-10',
      status: DocumentStatus.available,
      fileSize: '3.4 MB',
      extractedSummary:
          'Normal bronchovascular markings. No focal consolidation, pneumothorax, or pleural effusion noted. Cardiac size within normal physiological limits. Visualized bony thorax appears intact.',
      structuredData: {
        'Impression': 'Normal Chest Radiograph',
        'Lungs': 'Clear bilaterally',
        'Heart Size': 'Normal',
      },
    ),
    MedicalDocumentModel(
      id: 'DOC-103',
      title: 'Ultrasound Whole Abdomen Scan',
      documentType: 'Scan Report (MRI / CT / Ultrasound)',
      hospitalName: 'Manipal Hospital Radiology',
      date: '2025-11-22',
      status: DocumentStatus.available,
      fileSize: '4.1 MB',
      extractedSummary:
          'Liver is normal in size and echotexture with mild Grade 1 fatty infiltration. Gall bladder, pancreas, spleen, and kidneys appear sonographically normal. No calculi or hydronephrosis.',
      structuredData: {
        'Liver': 'Grade 1 Fatty Infiltration',
        'Kidneys': 'Normal bilateral',
        'Gall Bladder': 'No Calculi',
      },
    ),
    MedicalDocumentModel(
      id: 'DOC-104',
      title: 'Discharge Summary - Acute Gastroenteritis',
      documentType: 'Discharge Summary',
      hospitalName: 'Narayana Health City',
      date: '2025-08-04',
      status: DocumentStatus.available,
      fileSize: '2.2 MB',
      extractedSummary:
          'Patient admitted with vomiting, abdominal cramps, and dehydration. IV hydration and antiemetics administered. Recovered uneventfully. Vitals stable at discharge.',
    ),
  ];

  static List<MedicalRecordModel> medicalRecords = [
    MedicalRecordModel(
      id: 'REC-2026-01',
      title: 'Acute Upper Respiratory Tract Infection',
      date: '2026-02-24',
      year: '2026',
      provider: 'Dr. Priya Sharma, Apollo Clinic',
      recordType: 'Consultation',
      source: RecordSource.currentSystem,
      summary:
          'Patient presented with sore throat, dry cough, and low-grade fever for 3 days. Throat congestion noted. Prescribed symptomatic relief.',
      diagnosis: 'Acute Pharyngitis & Rhinopharyngitis',
      vitals: {
        'BP': '124/82 mmHg',
        'Pulse': '78 bpm',
        'Temp': '99.4 °F',
        'SpO2': '98%',
      },
      findings: [
        'Congested pharyngeal mucosa',
        'No tonsillar exudates',
        'Bilateral chest clear',
      ],
    ),
    MedicalRecordModel(
      id: 'REC-2026-02',
      title: 'Routine Health Checkup & Blood Panel',
      date: '2026-02-18',
      year: '2026',
      provider: 'Apollo Speciality Diagnostics',
      recordType: 'Lab Test',
      source: RecordSource.uploadedDocument,
      summary:
          'Complete metabolic and lipid screening. Mild hyperlipidemia noted; lifestyle modification and exercise advised.',
      diagnosis: 'Borderline Hypercholesterolemia',
      vitals: {
        'Weight': '74.5 kg',
        'BMI': '24.8 kg/m²',
      },
    ),
    MedicalRecordModel(
      id: 'REC-2025-01',
      title: 'Cardiology Review & ECG',
      date: '2025-10-15',
      year: '2025',
      provider: 'Fortis Hospital - Department of Cardiology',
      recordType: 'Consultation',
      source: RecordSource.externalHospital,
      summary:
          'Periodic hypertension evaluation. Blood pressure well controlled on low dose Telmisartan. Resting 12-lead ECG normal sinus rhythm.',
      diagnosis: 'Primary Essential Hypertension (Controlled)',
      vitals: {
        'BP': '122/80 mmHg',
        'Pulse': '72 bpm',
      },
      findings: [
        'Normal Sinus Rhythm',
        'No ST-T wave abnormalities',
      ],
    ),
    MedicalRecordModel(
      id: 'REC-2025-02',
      title: 'Acute Gastroenteritis Inpatient Episode',
      date: '2025-08-04',
      year: '2025',
      provider: 'Narayana Health City',
      recordType: 'Hospitalization',
      source: RecordSource.uploadedDocument,
      summary:
          'Treated with intravenous rehydration therapy, antispasmodics, and probiotics. Stool routine clear for parasites.',
      diagnosis: 'Acute Food-borne Gastroenteritis',
    ),
  ];

  static List<PrescriptionModel> prescriptions = [
    PrescriptionModel(
      id: 'RX-2026-089',
      doctorName: 'Dr. Priya Sharma',
      doctorSpecialization: 'General Physician, MBBS, MD (Internal Medicine)',
      hospitalName: 'Apollo Clinic, Koramangala',
      date: '2026-02-24',
      diagnosis: 'Acute Pharyngitis & Dry Cough',
      isActive: true,
      medicines: [
        MedicineItem(
          name: 'Tab. Paracetamol 650mg (Dolo)',
          dosage: '650 mg',
          frequency: '1-0-1 (Morning & Night)',
          duration: '3 Days',
          timing: 'After food',
          instructions: 'Take only when fever > 99.5°F or body ache occurs',
        ),
        MedicineItem(
          name: 'Tab. Montair-LC (Montelukast + Levocetirizine)',
          dosage: '10mg / 5mg',
          frequency: '0-0-1 (Night only)',
          duration: '5 Days',
          timing: 'At bedtime after dinner',
          instructions: 'May cause mild drowsiness',
        ),
        MedicineItem(
          name: 'Syrup Ascoril-D Cough Relief',
          dosage: '10 ml',
          frequency: '1-1-1 (TID)',
          duration: '5 Days',
          timing: 'After meals',
          instructions: 'Warm water gargles 3 times a day',
        ),
      ],
      generalAdvice:
          'Maintain adequate oral hydration. Avoid cold liquids and fried foods. Return for review if symptoms persist beyond 5 days.',
      doctorNotes: 'Patient advised to review if temperature exceeds 101°F.',
    ),
    PrescriptionModel(
      id: 'RX-2025-412',
      doctorName: 'Dr. Arvind Menon',
      doctorSpecialization: 'Cardiologist, MD, DM (Cardiology)',
      hospitalName: 'Fortis Heart Centre',
      date: '2025-10-15',
      diagnosis: 'Stage 1 Hypertension Maintenance',
      isActive: true,
      medicines: [
        MedicineItem(
          name: 'Tab. Telmisartan 40mg (Telma 40)',
          dosage: '40 mg',
          frequency: '1-0-0 (Morning)',
          duration: '90 Days (Ongoing)',
          timing: 'Morning after breakfast',
          instructions: 'Take consistently at the same time daily',
        ),
      ],
      generalAdvice: 'Low sodium diet (< 2.5g salt/day), 30 mins brisk walking daily.',
      doctorNotes: 'Monitor BP weekly. Routine kidney function test in 6 months.',
    ),
    PrescriptionModel(
      id: 'RX-2025-190',
      doctorName: 'Dr. Neha Kulkarni',
      doctorSpecialization: 'Gastroenterologist',
      hospitalName: 'Narayana Health City',
      date: '2025-08-04',
      diagnosis: 'Post-Gastroenteritis Recovery',
      isActive: false,
      medicines: [
        MedicineItem(
          name: 'Cap. Vizylac Probiotic',
          dosage: '1 Capsule',
          frequency: '1-0-1',
          duration: '7 Days',
          timing: 'Before meals',
        ),
        MedicineItem(
          name: 'Tab. Pantoprazole 40mg (Pan 40)',
          dosage: '40 mg',
          frequency: '1-0-0',
          duration: '5 Days',
          timing: '30 mins before breakfast',
        ),
      ],
      generalAdvice: 'Bland diet for 3 days. Hydrate with ORS.',
    ),
  ];

  static List<ConsultationModel> consultations = [
    ConsultationModel(
      id: 'CON-2026-104',
      date: '2026-02-24',
      time: '11:30 AM',
      doctorName: 'Dr. Priya Sharma',
      doctorSpecialization: 'General Physician, MD',
      hospitalName: 'Apollo Clinic, Koramangala',
      status: 'Completed',
      chiefComplaint: 'Sore throat, throat irritation, dry irritating cough',
      symptoms: [
        'Sore throat and pain on swallowing',
        'Dry irritating cough',
        'Mild low-grade fever',
        'General malaise and fatigue',
      ],
      duration: '3 Days',
      vitals: {
        'Blood Pressure': '124/82 mmHg',
        'Pulse Rate': '78 bpm',
        'Temperature': '99.4 °F',
        'SpO2': '98% on room air',
        'Weight': '74.5 kg',
      },
      pastHistoryConsidered: [
        'Essential Hypertension (on Telmisartan 40mg)',
        'No prior asthma or chronic bronchitis',
      ],
      allergiesNoted: [
        'Known Penicillin Allergy (Severe rash)',
      ],
      currentMedications: [
        'Tab. Telmisartan 40mg once daily',
      ],
      doctorNotes:
          'Pharyngeal erythema observed without purulent exudates. Clear chest sounds bilaterally. Recommended symptomatic antipyretics and antihistamines. Penicillin avoidance verified.',
      clinicalSummary:
          'Diagnosis: Acute Viral Pharyngitis. Treatment initiated with symptomatic oral therapy. Expected recovery in 3-5 days.',
      linkedPrescriptionId: 'RX-2026-089',
    ),
    ConsultationModel(
      id: 'CON-2025-081',
      date: '2025-10-15',
      time: '04:00 PM',
      doctorName: 'Dr. Arvind Menon',
      doctorSpecialization: 'Senior Consultant Cardiologist',
      hospitalName: 'Fortis Heart Centre',
      status: 'Completed',
      chiefComplaint: 'Routine 6-month blood pressure review',
      symptoms: ['Asymptomatic, checking BP parameters'],
      duration: 'Ongoing review',
      vitals: {
        'Blood Pressure': '122/80 mmHg',
        'Pulse Rate': '72 bpm',
        'Weight': '75.0 kg',
      },
      pastHistoryConsidered: ['Hypertension diagnosed in 2023'],
      allergiesNoted: ['Penicillin'],
      currentMedications: ['Tab. Telmisartan 40mg OD'],
      doctorNotes: 'Target blood pressure achieved. Medication continued without changes.',
      clinicalSummary: 'Well-managed primary hypertension.',
      linkedPrescriptionId: 'RX-2025-412',
    ),
  ];

  static List<ConsentRequestModel> consentRequests = [
    ConsentRequestModel(
      id: 'CSR-901',
      providerName: 'Manipal Hospital Whitefield',
      providerType: 'Multi-Specialty Hospital',
      doctorName: 'Dr. S. Ranganathan (ENT)',
      requestedScope: 'Medical History + Previous Prescriptions & Lab Reports',
      purpose: 'Specialist In-person Clinical Consultation & Case Assessment',
      status: ConsentStatus.pending,
      requestDate: '2026-09-06 14:15',
      validUntil: '24 Hours',
    ),
    ConsentRequestModel(
      id: 'CSR-882',
      providerName: 'Apollo Clinic, Koramangala',
      providerType: 'Outpatient Clinic',
      doctorName: 'Dr. Priya Sharma',
      requestedScope: 'Full Medical Timeline + Active Medications',
      purpose: 'General Outpatient Case Taking & Record Linking',
      status: ConsentStatus.allowed,
      requestDate: '2026-02-24 11:20',
      responseDate: '2026-02-24 11:22',
      validUntil: '30 Days',
    ),
    ConsentRequestModel(
      id: 'CSR-701',
      providerName: 'MediScan Diagnostic Labs',
      providerType: 'Diagnostic Centre',
      requestedScope: 'All Medical Records & Imaging Archive',
      purpose: 'Promotional Health Assessment & Tele-marketing',
      status: ConsentStatus.denied,
      requestDate: '2026-01-05 09:00',
      responseDate: '2026-01-05 09:02',
      validUntil: 'Expired',
    ),
  ];

  static List<NotificationModel> notifications = [
    NotificationModel(
      id: 'NOTIF-1',
      title: 'Consent Access Request',
      message: 'Manipal Hospital has requested temporary access to your medical history for your consultation.',
      category: NotificationCategory.consent,
      timestamp: '15 mins ago',
      isRead: false,
      targetRoute: '/consent-access',
    ),
    NotificationModel(
      id: 'NOTIF-2',
      title: 'Prescription Added',
      message: 'Dr. Priya Sharma (Apollo Clinic) issued a new prescription for Acute Pharyngitis.',
      category: NotificationCategory.prescription,
      timestamp: '2 hours ago',
      isRead: false,
      targetRoute: '/prescriptions',
    ),
    NotificationModel(
      id: 'NOTIF-3',
      title: 'Document Extracted',
      message: 'Complete Blood Count report has been parsed and clinical summary is available.',
      category: NotificationCategory.document,
      timestamp: '1 day ago',
      isRead: true,
      targetRoute: '/records',
    ),
    NotificationModel(
      id: 'NOTIF-4',
      title: 'Consultation Recorded',
      message: 'Clinical case notes for your consultation on 24 Feb 2026 have been synchronized.',
      category: NotificationCategory.consultation,
      timestamp: '3 days ago',
      isRead: true,
      targetRoute: '/consultations',
    ),
  ];
}
