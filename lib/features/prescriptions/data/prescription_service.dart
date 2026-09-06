import '../../../config/app_config.dart';
import '../../../core/constants/api_endpoints.dart';
import '../../../core/network/api_client.dart';
import '../../../shared/data/mock_database.dart';
import '../../../shared/models/prescription_model.dart';

abstract class PrescriptionService {
  Future<List<PrescriptionModel>> getPrescriptions();
  Future<PrescriptionModel> getPrescriptionById(String id);
}

class PrescriptionServiceImpl implements PrescriptionService {
  final ApiClient apiClient;

  PrescriptionServiceImpl({required this.apiClient});

  @override
  Future<List<PrescriptionModel>> getPrescriptions() async {
    if (AppConfig.useMockData) {
      await Future.delayed(const Duration(milliseconds: 400));
      return MockDatabase.prescriptions;
    }

    final res = await apiClient.get(ApiEndpoints.prescriptions);
    final list = res.data as List<dynamic>;
    return list.map((e) => PrescriptionModel.fromJson(e as Map<String, dynamic>)).toList();
  }

  @override
  Future<PrescriptionModel> getPrescriptionById(String id) async {
    if (AppConfig.useMockData) {
      await Future.delayed(const Duration(milliseconds: 300));
      return MockDatabase.prescriptions.firstWhere(
        (p) => p.id == id,
        orElse: () => MockDatabase.prescriptions.first,
      );
    }

    final res = await apiClient.get(ApiEndpoints.prescriptionDetail(id));
    return PrescriptionModel.fromJson(res.data as Map<String, dynamic>);
  }
}
