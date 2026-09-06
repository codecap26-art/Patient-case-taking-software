import '../../../config/app_config.dart';
import '../../../core/constants/api_endpoints.dart';
import '../../../core/network/api_client.dart';
import '../../../shared/data/mock_database.dart';
import '../../../shared/models/medical_record_model.dart';

abstract class HistoryService {
  Future<List<MedicalRecordModel>> getMedicalHistory();
  Future<MedicalRecordModel> getRecordById(String id);
}

class HistoryServiceImpl implements HistoryService {
  final ApiClient apiClient;

  HistoryServiceImpl({required this.apiClient});

  @override
  Future<List<MedicalRecordModel>> getMedicalHistory() async {
    if (AppConfig.useMockData) {
      await Future.delayed(const Duration(milliseconds: 400));
      return MockDatabase.medicalRecords;
    }

    final res = await apiClient.get(ApiEndpoints.medicalHistory);
    final list = res.data as List<dynamic>;
    return list.map((e) => MedicalRecordModel.fromJson(e as Map<String, dynamic>)).toList();
  }

  @override
  Future<MedicalRecordModel> getRecordById(String id) async {
    if (AppConfig.useMockData) {
      await Future.delayed(const Duration(milliseconds: 300));
      return MockDatabase.medicalRecords.firstWhere(
        (r) => r.id == id,
        orElse: () => MockDatabase.medicalRecords.first,
      );
    }

    final res = await apiClient.get(ApiEndpoints.medicalRecordDetail(id));
    return MedicalRecordModel.fromJson(res.data as Map<String, dynamic>);
  }
}
