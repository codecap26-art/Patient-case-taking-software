/// Global application configuration
class AppConfig {
  AppConfig._();

  /// App Info
  static const String appName = 'Patient Case Taking';
  static const String appVersion = '1.0.0';

  /// Toggle between Mock Repositories (for standalone UI testing)
  /// and live FastAPI backend endpoints connected to Supabase.
  static const bool useMockData = true;

  /// Base API URL for FastAPI backend
  /// For Chrome / Web / Desktop: 'http://127.0.0.1:8000/api/v1'
  /// For Android Emulator: 'http://10.0.2.2:8000/api/v1'
  static const String apiBaseUrl = 'http://127.0.0.1:8000/api/v1';

  /// Supabase Configuration
  static const String supabaseUrl = 'https://huaopeotprnbwshwkceb.supabase.co';
  static const String supabaseAnonKey =
      'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh1YW9wZW90cHJuYndzaHdrY2ViIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODg3Mjk4NTUsImV4cCI6MjEwNDMwNTg1NX0.if0PPUVry8LsKBNqOfP4zpY1ZYfWMmw9N6fg_hrrwRs';

  /// Groq LLM API Configuration for Document Extraction
  static const String groqApiKey = String.fromEnvironment('GROQ_API_KEY', defaultValue: '');
  static const String groqApiUrl = 'https://api.groq.com/openai/v1/chat/completions';
  static const String groqModel = 'openai/gpt-oss-120b';

  /// Network Timeouts (in milliseconds)
  static const int connectTimeout = 15000;
  static const int receiveTimeout = 15000;

  /// Seeded Demo Patient Credentials
  static const String demoPatientPhone = '+919876500001';
  static const String demoPatientPassword = 'Patient@123';
  static const String mockMobileNumber = '9876500001';
  static const String mockOtp = '123456';
}


