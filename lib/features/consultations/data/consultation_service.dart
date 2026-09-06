import '../../../config/app_config.dart';
import '../../../core/constants/api_endpoints.dart';
import '../../../core/network/api_client.dart';
import '../../../shared/data/mock_database.dart';
import '../../../shared/models/consultation_model.dart';

abstract class ConsultationService {
  Future<List<ConsultationModel>> getConsultations();
  Future<ConsultationModel> getConsultationById(String id);
}

class ConsultationServiceImpl implements ConsultationService {
  final ApiClient apiClient;

  ConsultationServiceImpl({required this.apiClient});

  @override
  Future<List<ConsultationModel>> getConsultations() async {
    if (AppConfig.useMockData) {
      await Future.delayed(const Duration(milliseconds: 400));
      return MockDatabase.consultations;
    }

    final res = await apiClient.get(ApiEndpoints.consultations);
    final list = res.data as List<dynamic>;
    return list.map((e) => ConsultationModel.fromJson(e as Map<String, dynamic>)).toList();
  }

  @override
  Future<ConsultationModel> getConsultationById(String id) async {
    if (AppConfig.useMockData) {
      await Future.delayed(const Duration(milliseconds: 300));
      return MockDatabase.consultations.firstWhere(
        (c) => c.id == id,
        orElse: () => MockDatabase.consultations.first,
      );
    }

    final res = await apiClient.get(ApiEndpoints.consultationDetail(id));
    return ConsultationModel.fromJson(res.data as Map<String, dynamic>);
  }
}
