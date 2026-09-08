/// FastAPI Backend Endpoints
class ApiEndpoints {
  ApiEndpoints._();

  // Authentication
  static const String sendOtp = '/auth/send-otp';
  static const String verifyOtp = '/auth/verify-otp';
  static const String login = '/auth/login';
  static const String register = '/auth/register';
  static const String getMe = '/auth/me';
  static const String logout = '/auth/logout';

  // Patient Profile & Identity
  static const String profile = '/patients/me';
  static const String updateProfile = '/patients/me';
  static const String qrGenerate = '/patients/qr/generate';
  static const String qrLink = '/patients/qr/link';

  // Medical Documents
  static const String documents = '/documents/my-documents';
  static const String uploadDocument = '/documents/upload';
  static String documentDetail(String id) => '/documents/$id';
  static String documentOriginal(String id) => '/documents/$id/original';
  static String documentDownload(String id) => '/documents/$id/download';
  static String documentRetry(String id) => '/documents/$id/retry';
  static String documentReview(String id) => '/documents/$id/review';

  // Medical History & Records
  static const String medicalHistory = '/medical-records/my-records';
  static String medicalRecordDetail(String id) => '/medical-records/$id';

  // Prescriptions
  static const String prescriptions = '/prescriptions/my-prescriptions';
  static String prescriptionDetail(String id) => '/prescriptions/$id';

  // Consultations
  static const String consultations = '/consultations/my-consultations';
  static String consultationDetail(String id) => '/consultations/$id';

  // Consent & Data Sharing
  static const String consentRequests = '/consents/my-consents';
  static String respondConsent(String id) => '/consents/$id/respond';
  static String revokeConsent(String id) => '/consents/$id/revoke';

  // Notifications
  static const String notifications = '/notifications/my-notifications';
  static String markNotificationRead(String id) => '/notifications/$id/read';
  static const String markAllNotificationsRead = '/notifications/read-all';
}


