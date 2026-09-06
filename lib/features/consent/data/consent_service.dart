import '../../../config/app_config.dart';
import '../../../core/constants/api_endpoints.dart';
import '../../../core/network/api_client.dart';
import '../../../shared/data/mock_database.dart';
import '../../../shared/models/consent_request_model.dart';

abstract class ConsentService {
  Future<List<ConsentRequestModel>> getConsentRequests();
  Future<bool> respondToConsent(String requestId, bool allow);
  Future<bool> revokeConsent(String requestId);
}

class ConsentServiceImpl implements ConsentService {
  final ApiClient apiClient;

  ConsentServiceImpl({required this.apiClient});

  @override
  Future<List<ConsentRequestModel>> getConsentRequests() async {
    if (AppConfig.useMockData) {
      await Future.delayed(const Duration(milliseconds: 400));
      return MockDatabase.consentRequests;
    }

    final res = await apiClient.get(ApiEndpoints.consentRequests);
    final list = res.data as List<dynamic>;
    return list.map((e) => ConsentRequestModel.fromJson(e as Map<String, dynamic>)).toList();
  }

  @override
  Future<bool> respondToConsent(String requestId, bool allow) async {
    if (AppConfig.useMockData) {
      await Future.delayed(const Duration(milliseconds: 500));
      final index = MockDatabase.consentRequests.indexWhere((c) => c.id == requestId);
      if (index != -1) {
        final existing = MockDatabase.consentRequests[index];
        MockDatabase.consentRequests[index] = existing.copyWith(
          status: allow ? ConsentStatus.allowed : ConsentStatus.denied,
          responseDate: DateTime.now().toString().substring(0, 16),
        );
      }
      return true;
    }

    final res = await apiClient.post(
      ApiEndpoints.respondConsent(requestId),
      data: {'allow': allow},
    );
    return res.statusCode == 200;
  }

  @override
  Future<bool> revokeConsent(String requestId) async {
    if (AppConfig.useMockData) {
      await Future.delayed(const Duration(milliseconds: 500));
      final index = MockDatabase.consentRequests.indexWhere((c) => c.id == requestId);
      if (index != -1) {
        final existing = MockDatabase.consentRequests[index];
        MockDatabase.consentRequests[index] = existing.copyWith(
          status: ConsentStatus.revoked,
          responseDate: DateTime.now().toString().substring(0, 16),
        );
      }
      return true;
    }

    final res = await apiClient.post(ApiEndpoints.revokeConsent(requestId));
    return res.statusCode == 200;
  }
}
