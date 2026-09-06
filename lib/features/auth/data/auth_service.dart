import 'dart:convert';
import '../../../config/app_config.dart';
import '../../../core/constants/api_endpoints.dart';
import '../../../core/errors/exceptions.dart';
import '../../../core/network/api_client.dart';
import '../../../core/storage/token_storage.dart';
import '../../../shared/data/mock_database.dart';
import '../../../shared/models/patient_model.dart';

abstract class AuthService {
  Future<bool> sendOtp(String mobileNumber);
  Future<PatientModel> verifyOtp(String mobileNumber, String otp);
  Future<PatientModel> register(PatientModel patient, String otp);
  Future<void> logout();
  Future<PatientModel?> getCachedProfile();
}

class AuthServiceImpl implements AuthService {
  final ApiClient apiClient;
  final TokenStorage tokenStorage;

  AuthServiceImpl({required this.apiClient, required this.tokenStorage});

  @override
  Future<bool> sendOtp(String mobileNumber) async {
    if (AppConfig.useMockData) {
      await Future.delayed(const Duration(milliseconds: 700));
      return true;
    }

    try {
      final res = await apiClient.post(
        ApiEndpoints.sendOtp,
        data: {'mobile_number': mobileNumber},
      );
      return res.statusCode == 200;
    } catch (e) {
      throw ServerException('Failed to send OTP: $e');
    }
  }

  @override
  Future<PatientModel> verifyOtp(String mobileNumber, String otp) async {
    if (AppConfig.useMockData) {
      await Future.delayed(const Duration(milliseconds: 900));
      if (otp != AppConfig.mockOtp && otp != '123456') {
        throw AuthException('Invalid OTP. Please enter 123456 for testing.');
      }
      final patient = MockDatabase.currentPatient.copyWith(phone: mobileNumber);
      await tokenStorage.saveTokens(
        accessToken: 'mock_jwt_token_${DateTime.now().millisecondsSinceEpoch}',
        refreshToken: 'mock_refresh_token_123',
      );
      await tokenStorage.savePatientJson(jsonEncode(patient.toJson()));
      return patient;
    }

    try {
      final res = await apiClient.post(
        ApiEndpoints.verifyOtp,
        data: {'mobile_number': mobileNumber, 'otp': otp},
      );

      final data = res.data as Map<String, dynamic>;
      final token = data['access_token'] as String;
      final refreshToken = data['refresh_token'] as String?;
      final patientJson = data['patient'] as Map<String, dynamic>;

      await tokenStorage.saveTokens(
        accessToken: token,
        refreshToken: refreshToken,
      );
      await tokenStorage.savePatientJson(jsonEncode(patientJson));

      return PatientModel.fromJson(patientJson);
    } catch (e) {
      if (e is AuthException) rethrow;
      throw ServerException('OTP Verification Failed: $e');
    }
  }

  @override
  Future<PatientModel> register(PatientModel patient, String otp) async {
    if (AppConfig.useMockData) {
      await Future.delayed(const Duration(milliseconds: 1000));
      final newPatient = patient.copyWith(
        id: 'PCT-PAT-${(10000 + DateTime.now().millisecond * 80)}',
        qrCodeToken: 'PCT:IDENTITY:v1:${patient.phone}:SEC${DateTime.now().millisecondsSinceEpoch}',
      );
      MockDatabase.currentPatient = newPatient;
      await tokenStorage.saveTokens(
        accessToken: 'mock_registered_jwt_${DateTime.now().millisecondsSinceEpoch}',
      );
      await tokenStorage.savePatientJson(jsonEncode(newPatient.toJson()));
      return newPatient;
    }

    try {
      final res = await apiClient.post(
        ApiEndpoints.register,
        data: {
          ...patient.toJson(),
          'otp': otp,
        },
      );
      final data = res.data as Map<String, dynamic>;
      final token = data['access_token'] as String;
      final patientJson = data['patient'] as Map<String, dynamic>;

      await tokenStorage.saveTokens(accessToken: token);
      await tokenStorage.savePatientJson(jsonEncode(patientJson));

      return PatientModel.fromJson(patientJson);
    } catch (e) {
      throw ServerException('Registration Failed: $e');
    }
  }

  @override
  Future<void> logout() async {
    if (!AppConfig.useMockData) {
      try {
        await apiClient.post(ApiEndpoints.logout);
      } catch (_) {}
    }
    await tokenStorage.clearSession();
  }

  @override
  Future<PatientModel?> getCachedProfile() async {
    final jsonStr = tokenStorage.getPatientJson();
    if (jsonStr != null && jsonStr.isNotEmpty) {
      try {
        return PatientModel.fromJson(jsonDecode(jsonStr));
      } catch (_) {
        return null;
      }
    }
    return null;
  }
}
