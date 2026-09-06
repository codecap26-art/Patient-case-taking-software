/// FastAPI Backend Endpoints
class ApiEndpoints {
  ApiEndpoints._();

  // Authentication
  static const String sendOtp = '/auth/send-otp';
  static const String verifyOtp = '/auth/verify-otp';
  static const String register = '/auth/register';
  static const String refreshToken = '/auth/refresh-token';
  static const String logout = '/auth/logout';

  // Patient Profile
  static const String profile = '/patient/profile';
  static const String updateProfile = '/patient/profile';
  static const String qrIdentity = '/patient/qr-code';

  // Medical Documents
  static const String documents = '/patient/documents';
  static const String uploadDocument = '/patient/documents/upload';
  static String documentDetail(String id) => '/patient/documents/$id';

  // Medical History
  static const String medicalHistory = '/patient/medical-history';
  static String medicalRecordDetail(String id) => '/patient/medical-history/$id';

  // Prescriptions
  static const String prescriptions = '/patient/prescriptions';
  static String prescriptionDetail(String id) => '/patient/prescriptions/$id';

  // Consultations
  static const String consultations = '/patient/consultations';
  static String consultationDetail(String id) => '/patient/consultations/$id';

  // Consent & Access Control
  static const String consentRequests = '/patient/consent/requests';
  static const String activeConsents = '/patient/consent/active';
  static const String consentHistory = '/patient/consent/history';
  static String respondConsent(String id) => '/patient/consent/requests/$id/respond';
  static String revokeConsent(String id) => '/patient/consent/active/$id/revoke';

  // Notifications
  static const String notifications = '/patient/notifications';
  static String markNotificationRead(String id) => '/patient/notifications/$id/read';
  static const String markAllNotificationsRead = '/patient/notifications/read-all';
}
