import 'dart:io';
import '../../../config/app_config.dart';
import '../../../core/constants/api_endpoints.dart';
import '../../../core/network/api_client.dart';
import '../../../shared/data/mock_database.dart';
import '../../../shared/models/document_model.dart';

abstract class DocumentService {
  Future<List<MedicalDocumentModel>> getDocuments();
  Future<MedicalDocumentModel> getDocumentById(String id);
  Future<MedicalDocumentModel> uploadDocument({
    required String title,
    required String documentType,
    required String hospitalName,
    required String date,
    File? file,
  });
}

class DocumentServiceImpl implements DocumentService {
  final ApiClient apiClient;

  DocumentServiceImpl({required this.apiClient});

  @override
  Future<List<MedicalDocumentModel>> getDocuments() async {
    if (AppConfig.useMockData) {
      await Future.delayed(const Duration(milliseconds: 500));
      return MockDatabase.documents;
    }

    final res = await apiClient.get(ApiEndpoints.documents);
    final list = res.data as List<dynamic>;
    return list.map((e) => MedicalDocumentModel.fromJson(e as Map<String, dynamic>)).toList();
  }

  @override
  Future<MedicalDocumentModel> getDocumentById(String id) async {
    if (AppConfig.useMockData) {
      await Future.delayed(const Duration(milliseconds: 300));
      return MockDatabase.documents.firstWhere(
        (doc) => doc.id == id,
        orElse: () => MockDatabase.documents.first,
      );
    }

    final res = await apiClient.get(ApiEndpoints.documentDetail(id));
    return MedicalDocumentModel.fromJson(res.data as Map<String, dynamic>);
  }

  @override
  Future<MedicalDocumentModel> uploadDocument({
    required String title,
    required String documentType,
    required String hospitalName,
    required String date,
    File? file,
  }) async {
    if (AppConfig.useMockData) {
      // Simulate progressive upload and extraction
      await Future.delayed(const Duration(milliseconds: 1200));

      final newDoc = MedicalDocumentModel(
        id: 'DOC-${105 + MockDatabase.documents.length}',
        title: title,
        documentType: documentType,
        hospitalName: hospitalName,
        date: date,
        status: DocumentStatus.extracted,
        fileSize: file != null ? '${(file.lengthSync() / 1024).toStringAsFixed(1)} KB' : '2.1 MB',
        extractedSummary:
            'Clinical report processed by AI parser. Key markers identified and structured for doctor consultation case file.',
        structuredData: {
          'Document Category': documentType,
          'Clinical Facility': hospitalName,
          'Date of Investigation': date,
          'Processing Status': 'Completed',
        },
      );

      MockDatabase.documents.insert(0, newDoc);
      return newDoc;
    }

    // In live mode, send Multipart FormData to FastAPI backend
    final res = await apiClient.post(
      ApiEndpoints.uploadDocument,
      data: {
        'title': title,
        'document_type': documentType,
        'hospital_name': hospitalName,
        'date': date,
      },
    );
    return MedicalDocumentModel.fromJson(res.data as Map<String, dynamic>);
  }
}
