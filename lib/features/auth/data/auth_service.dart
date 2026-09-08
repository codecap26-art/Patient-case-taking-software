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
        data: {
          'phone': mobileNumber,
          'mobile_number': mobileNumber,
        },
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
        data: {
          'phone': mobileNumber,
          'mobile_number': mobileNumber,
          'otp': otp,
        },
      );

      final data = res.data as Map<String, dynamic>;
      final token = data['access_token'] as String;
      final refreshToken = data['refresh_token'] as String?;
      
      await tokenStorage.saveTokens(
        accessToken: token,
        refreshToken: refreshToken,
      );

      Map<String, dynamic>? patientJson = data['patient'] as Map<String, dynamic>?;
      if (patientJson == null) {
        // Fetch patient profile directly
        final profileRes = await apiClient.get(ApiEndpoints.profile);
        patientJson = profileRes.data as Map<String, dynamic>;
      }

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
      final names = patient.name.trim().split(' ');
      final firstName = names.isNotEmpty ? names.first : 'Patient';
      final lastName = names.length > 1 ? names.sublist(1).join(' ') : 'User';

      final res = await apiClient.post(
        ApiEndpoints.register,
        data: {
          'phone': patient.phone,
          'first_name': firstName,
          'last_name': lastName,
          'date_of_birth': patient.dateOfBirth,
          'gender': patient.gender,
          'blood_group': patient.bloodGroup,
          'emergency_contact': patient.emergencyContact,
          'address': patient.address,
          'email': patient.email,
          'allergies': patient.allergies,
          'chronic_conditions': patient.chronicConditions,
          'otp': otp,
          'password': 'Patient@123',
        },
      );
      final data = res.data as Map<String, dynamic>;
      final token = data['access_token'] as String;
      final patientJson = (data['patient'] as Map<String, dynamic>?) ?? data;

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

