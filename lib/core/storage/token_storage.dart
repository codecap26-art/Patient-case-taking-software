import 'package:shared_preferences/shared_preferences.dart';
import '../constants/app_constants.dart';

/// Manages local JWT persistence and patient session info
class TokenStorage {
  static TokenStorage? _instance;
  static SharedPreferences? _prefs;

  TokenStorage._();

  static Future<TokenStorage> getInstance() async {
    if (_instance == null) {
      _instance = TokenStorage._();
      _prefs = await SharedPreferences.getInstance();
    }
    return _instance!;
  }

  // Token Management
  Future<void> saveTokens({required String accessToken, String? refreshToken}) async {
    await _prefs?.setString(AppConstants.keyAuthToken, accessToken);
    if (refreshToken != null) {
      await _prefs?.setString(AppConstants.keyRefreshToken, refreshToken);
    }
  }

  String? getAccessToken() {
    return _prefs?.getString(AppConstants.keyAuthToken);
  }

  String? getRefreshToken() {
    return _prefs?.getString(AppConstants.keyRefreshToken);
  }

  bool hasToken() {
    final token = getAccessToken();
    return token != null && token.isNotEmpty;
  }

  // User Profile Caching
  Future<void> savePatientJson(String jsonString) async {
    await _prefs?.setString(AppConstants.keyPatientData, jsonString);
  }

  String? getPatientJson() {
    return _prefs?.getString(AppConstants.keyPatientData);
  }

  // Locale Preference
  Future<void> saveLocale(String languageCode) async {
    await _prefs?.setString(AppConstants.keyLocale, languageCode);
  }

  String getLocale() {
    return _prefs?.getString(AppConstants.keyLocale) ?? AppConstants.localeEn;
  }

  // Clear Session / Logout
  Future<void> clearSession() async {
    await _prefs?.remove(AppConstants.keyAuthToken);
    await _prefs?.remove(AppConstants.keyRefreshToken);
    await _prefs?.remove(AppConstants.keyPatientData);
  }
}
