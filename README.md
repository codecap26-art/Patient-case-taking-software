# Patient Case Taking — Flutter Mobile Application (Patient App)

A modern, production-grade Flutter mobile application built exclusively for the **Patient** side of the *Patient Case Taking* healthcare platform.

Developed with **Clean Architecture**, **Material 3 Healthcare Design Tokens**, **GoRouter navigation**, **Provider state management**, **Dio REST API Client**, **JWT Authentication & Token Storage**, and **Multilingual Localization (English, Tamil, Hindi)**.

---

## 📱 App Highlights & Features

1. **Splash & Seamless Onboarding**
   - Animated splash screen with automatic authentication session check.
   - Mobile Number + OTP verification flow (no passwords or Aadhaar requirements).
   - Complete patient registration (Name, DOB, Gender, Blood Group, Emergency Contact, Address).

2. **Clean Health Dashboard**
   - Patient health vitals overview (Blood Group, Allergies count, Chronic Conditions).
   - Actionable banners for pending consent requests.
   - Quick highlights of upcoming/recent consultations, active prescriptions, and recent lab documents.
   - Quick action grid: *Medical Records, Upload Document, Prescriptions, Consultations, My QR, Consent & Access*.

3. **My Patient QR Code (Identity & Linking)**
   - Dynamic QR Code representing patient identity for healthcare provider linking.
   - Clear Patient ID copy action.
   - Strict security note: *QR scan does NOT bypass explicit patient consent*.
   - Refresh QR token & interactive explanation modal.

4. **Medical Documents & AI Clinical Parsing**
   - Multi-source document upload: **Camera**, **Gallery**, and **PDF Document Picker**.
   - Processing status pipeline: `Uploading` → `Processing` → `Extracted` → `Available`.
   - Structured AI-extracted clinical highlights with clinical disclaimer badges.

5. **Medical History Timeline**
   - Interactive chronological timeline grouped by year (2026, 2025...).
   - Source distinction:
     - 🟣 **Current System** (In-app consultations)
     - 🟢 **Uploaded Doc** (User uploaded lab tests/scans)
     - 🔵 **External Hospital** (Authorized hospital network integration)

6. **Prescriptions**
   - Active and Past prescription tabs.
   - Clear medicine schedule badges (Dosage, Frequency, Duration, Meal timing).
   - Certified doctor verification badges.

7. **Consultation History**
   - Structured clinical case details: Chief complaints, symptom duration, recorded vitals, allergies noted, doctor clinical notes, and linked prescription shortcut.

8. **Consent & Access Control**
   - Explicit permission gating: Healthcare providers must request access before viewing private clinical records.
   - One-tap **[Allow]**, **[Deny]**, and **[Revoke Access]** with confirmation dialogs.
   - Full audit history of past permissions.

9. **Notifications Center**
   - Categorized alerts for Consultations, Prescriptions, Documents, Consent requests, and System notices.

10. **Multilingual Localization**
    - Instant language switching between **English**, **Tamil (தமிழ்)**, and **Hindi (हिन्दी)**.

---

## 🗂️ Project Directory Structure

```
lib/
├── app.dart                                 # MultiProvider root & MaterialApp configuration
├── main.dart                                # Application entry point & system overlays
│
├── config/
│   ├── app_config.dart                      # Environment configs, Base URL, Mock toggle
│   └── theme/
│       ├── app_colors.dart                  # Healthcare design tokens (Teal, Sapphire, Emerald)
│       └── app_theme.dart                   # Material 3 typography & widget themes
│
├── core/
│   ├── constants/
│   │   ├── api_endpoints.dart               # REST API paths for FastAPI backend
│   │   └── app_constants.dart               # Storage keys, blood groups, genders, document types
│   ├── errors/
│   │   ├── exceptions.dart                  # Network, Auth, Server exceptions
│   │   └── failures.dart                    # UI-friendly error failures
│   ├── localization/
│   │   ├── app_localizations.dart           # Multilingual provider & context.tr() extension
│   │   └── strings/                         # Translation dictionaries (en, ta, hi)
│   ├── network/
│   │   └── api_client.dart                  # Dio HTTP Client with JWT interceptors
│   ├── routing/
│   │   ├── app_router.dart                  # GoRouter with StatefulShellRoute (5 tabs)
│   │   └── route_names.dart                 # Named route constants
│   └── storage/
│       └── token_storage.dart               # SharedPreferences & Token management
│
├── shared/
│   ├── data/
│   │   └── mock_database.dart               # Rich clinical mock dataset for offline testing
│   ├── models/                              # PatientModel, DocumentModel, RecordModel, etc.
│   └── widgets/                             # CustomButton, CustomTextField, StatusBadge, AppCard, etc.
│
└── features/
    ├── splash/                              # Splash screen
    ├── auth/                                # Login, OTP, Registration
    ├── home/                                # Health dashboard & quick actions
    ├── profile/                             # Patient profile & edit screen
    ├── qr/                                  # Dynamic QR identity screen
    ├── documents/                           # Documents list, upload & AI detail view
    ├── medical_history/                     # Timeline history & record details
    ├── prescriptions/                       # Active & past prescription schedules
    ├── consultations/                       # Structured case consultation details
    ├── consent/                             # Consent & access authorization
    ├── notifications/                       # Patient alerts & updates
    └── settings/                            # Settings, Language selection, Help & FAQs
```

---

## ⚙️ Configuration & Backend Integration

### 1. Toggle Between Mock Data & Live FastAPI Backend
In `lib/config/app_config.dart`:

```dart
// Set to 'false' to connect to real FastAPI backend
static const bool useMockData = true;

// FastAPI Backend URL
static const String apiBaseUrl = 'http://10.0.2.2:8000/api';
```

### 2. Demo & Mock Login Credentials
When `useMockData = true`:
- **Mobile Number**: `9876543210`
- **Verification OTP**: `123456`

---

## 🔌 Expected FastAPI Backend Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/send-otp` | Sends SMS OTP to mobile number |
| `POST` | `/api/auth/verify-otp` | Verifies OTP and returns JWT tokens |
| `POST` | `/api/auth/register` | Registers new patient profile |
| `GET` | `/api/patient/profile` | Fetches authenticated patient profile |
| `PUT` | `/api/patient/profile` | Updates patient profile |
| `GET` | `/api/patient/documents` | Lists uploaded medical documents |
| `POST` | `/api/patient/documents/upload` | Uploads multipart document and triggers AI parser |
| `GET` | `/api/patient/documents/{id}` | Gets document details & AI summary |
| `GET` | `/api/patient/medical-history` | Fetches consolidated medical history timeline |
| `GET` | `/api/patient/prescriptions` | Lists active and past prescriptions |
| `GET` | `/api/patient/consultations` | Lists structured case consultations |
| `GET` | `/api/patient/consent/requests` | Fetches pending, active, and history consent records |
| `POST` | `/api/patient/consent/requests/{id}/respond` | Allows or denies a provider access request |
| `POST` | `/api/patient/consent/active/{id}/revoke` | Revokes an active hospital's access |
| `GET` | `/api/patient/notifications` | Fetches patient notifications |

---

## 🚀 How to Run the App

1. Ensure Flutter SDK `>= 3.0.0` is installed.
2. Install dependencies:
   ```bash
   flutter pub get
   ```
3. Run on your connected device, emulator, or simulator:
   ```bash
   flutter run
   ```
4. For Web preview:
   ```bash
   flutter run -d chrome
   ```
