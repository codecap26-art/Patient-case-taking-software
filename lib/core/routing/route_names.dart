class RouteNames {
  RouteNames._();

  static const String splash = '/';
  static const String login = '/login';
  static const String otp = '/otp';
  static const String register = '/register';

  // Main Dashboard Shell Tabs
  static const String home = '/home';
  static const String records = '/records';
  static const String prescriptions = '/prescriptions';
  static const String notifications = '/notifications';
  static const String profile = '/profile';

  // Detail & Action Screens
  static const String editProfile = '/profile/edit';
  static const String qr = '/qr';
  static const String uploadDocument = '/documents/upload';
  static const String documentDetail = '/documents/:id';
  static const String medicalHistory = '/medical-history';
  static const String recordDetail = '/medical-history/:id';
  static const String prescriptionDetail = '/prescriptions/:id';
  static const String consultations = '/consultations';
  static const String consultationDetail = '/consultations/:id';
  static const String consentAccess = '/consent-access';
  static const String settings = '/settings';
  static const String languageSelection = '/settings/language';
  static const String helpFaq = '/settings/help';
}
