class AppConstants {
  AppConstants._();

  // Storage Keys
  static const String keyAuthToken = 'pct_auth_token';
  static const String keyRefreshToken = 'pct_refresh_token';
  static const String keyPatientData = 'pct_patient_profile';
  static const String keyLocale = 'pct_selected_locale';
  static const String keyBiometricEnabled = 'pct_biometric_enabled';
  static const String keyNotificationsEnabled = 'pct_notifications_enabled';

  // Supported Locales
  static const String localeEn = 'en';
  static const String localeTa = 'ta';
  static const String localeHi = 'hi';

  // Document Types
  static const List<String> documentTypes = [
    'Blood Test Report',
    'Scan Report (MRI / CT / Ultrasound)',
    'Prescription',
    'Discharge Summary',
    'X-Ray Report',
    'Other Medical Document',
  ];

  // Blood Groups
  static const List<String> bloodGroups = [
    'A+',
    'A-',
    'B+',
    'B-',
    'AB+',
    'AB-',
    'O+',
    'O-',
  ];

  // Genders
  static const List<String> genders = [
    'Male',
    'Female',
    'Other',
  ];
}
