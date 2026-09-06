/// Global application configuration
/// Toggle [useMockData] to false to connect directly to the FastAPI backend.
class AppConfig {
  AppConfig._();

  /// App Info
  static const String appName = 'Patient Case Taking';
  static const String appVersion = '1.0.0';

  /// Toggle between Mock Repositories (for standalone UI testing)
  /// and live FastAPI backend endpoints.
  static const bool useMockData = true;

  /// Base API URL for FastAPI backend
  /// For Android Emulator: 'http://10.0.2.2:8000/api'
  /// For iOS Simulator: 'http://localhost:8000/api'
  /// For Physical Device: 'http://<YOUR_LOCAL_IP>:8000/api'
  /// For Production: 'https://api.patientcasetaking.health/api'
  static const String apiBaseUrl = 'http://10.0.2.2:8000/api';

  /// Network Timeouts (in milliseconds)
  static const int connectTimeout = 15000;
  static const int receiveTimeout = 15000;

  /// Mock Authentication Credentials (for testing)
  static const String mockMobileNumber = '9876543210';
  static const String mockOtp = '123456';
}
