import 'dart:io';
import 'package:dio/dio.dart';
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
    String? rawText,
    File? file,
    List<int>? fileBytes,
    String? fileName,
  });
  String getDocumentOriginalUrl(String id);
  String getDocumentDownloadUrl(String id);
  Future<MedicalDocumentModel?> retryExtraction(String id);
  Future<MedicalDocumentModel?> reviewDocument({
    required String id,
    required Map<String, dynamic> structuredData,
    String? notes,
  });
}

class DocumentServiceImpl implements DocumentService {
  final ApiClient apiClient;

  DocumentServiceImpl({required this.apiClient});

  @override
  String getDocumentOriginalUrl(String id) {
    return '${AppConfig.apiBaseUrl}${ApiEndpoints.documentOriginal(id)}';
  }

  @override
  String getDocumentDownloadUrl(String id) {
    return '${AppConfig.apiBaseUrl}${ApiEndpoints.documentDownload(id)}';
  }

  @override
  Future<List<MedicalDocumentModel>> getDocuments() async {
    try {
      final res = await apiClient.get(ApiEndpoints.documents);
      final list = res.data as List<dynamic>;
      final remoteDocs = list.map((e) => MedicalDocumentModel.fromJson(e as Map<String, dynamic>)).toList();
      if (remoteDocs.isNotEmpty) {
        return remoteDocs;
      }
    } catch (_) {
      // Fallback to local session store if backend is unreachable
    }
    return MockDatabase.documents;
  }

  @override
  Future<MedicalDocumentModel> getDocumentById(String id) async {
    try {
      final res = await apiClient.get(ApiEndpoints.documentDetail(id));
      return MedicalDocumentModel.fromJson(res.data as Map<String, dynamic>);
    } catch (_) {
      return MockDatabase.documents.firstWhere(
        (doc) => doc.id == id,
        orElse: () => MockDatabase.documents.first,
      );
    }
  }

  @override
  Future<MedicalDocumentModel?> retryExtraction(String id) async {
    try {
      final res = await apiClient.post(ApiEndpoints.documentRetry(id));
      final updated = MedicalDocumentModel.fromJson(res.data as Map<String, dynamic>);
      final idx = MockDatabase.documents.indexWhere((d) => d.id == id);
      if (idx != -1) {
        MockDatabase.documents[idx] = updated;
      }
      return updated;
    } catch (_) {
      return null;
    }
  }

  @override
  Future<MedicalDocumentModel?> reviewDocument({
    required String id,
    required Map<String, dynamic> structuredData,
    String? notes,
  }) async {
    try {
      final res = await apiClient.post(
        ApiEndpoints.documentReview(id),
        data: {
          'structured_data': structuredData,
          'doctor_notes': notes,
          'confirmed': true,
        },
      );
      final updated = MedicalDocumentModel.fromJson(res.data as Map<String, dynamic>);
      final idx = MockDatabase.documents.indexWhere((d) => d.id == id);
      if (idx != -1) {
        MockDatabase.documents[idx] = updated;
      }
      return updated;
    } catch (_) {
      return null;
    }
  }

  @override
  Future<MedicalDocumentModel> uploadDocument({
    required String title,
    required String documentType,
    required String hospitalName,
    required String date,
    String? rawText,
    File? file,
    List<int>? fileBytes,
    String? fileName,
  }) async {
    // 1. Attempt live backend upload via multipart POST /api/v1/documents/upload
    try {
      final formMap = <String, dynamic>{
        'title': title,
        'document_type': documentType,
        'hospital_name': hospitalName,
        'document_date': date,
      };

      if (fileBytes != null && fileName != null) {
        formMap['file'] = MultipartFile.fromBytes(fileBytes, filename: fileName);
      } else if (file != null) {
        formMap['file'] = await MultipartFile.fromFile(file.path, filename: fileName ?? file.path.split('/').last);
      } else if (rawText != null && rawText.isNotEmpty) {
        formMap['file'] = MultipartFile.fromBytes(
          rawText.codeUnits,
          filename: fileName ?? 'clinical_document.txt',
        );
      }

      final formData = FormData.fromMap(formMap);
      final res = await apiClient.post(
        ApiEndpoints.uploadDocument,
        data: formData,
      );

      final doc = MedicalDocumentModel.fromJson(res.data as Map<String, dynamic>);
      // Store in memory for instant local view and history
      final enrichedDoc = MedicalDocumentModel(
        id: doc.id,
        title: doc.title,
        documentType: doc.documentType,
        hospitalName: doc.hospitalName,
        date: doc.date,
        status: doc.status,
        fileUrl: getDocumentOriginalUrl(doc.id),
        fileSize: doc.fileSize,
        fileName: doc.fileName ?? fileName,
        mimeType: doc.mimeType,
        extractedSummary: doc.extractedSummary,
        extractedText: doc.extractedText ?? rawText,
        structuredData: doc.structuredData,
        pageCount: doc.pageCount,
        extractionError: doc.extractionError,
        doctorReviewed: doc.doctorReviewed,
        doctorNotes: doc.doctorNotes,
        fileBytes: fileBytes,
      );

      MockDatabase.documents.insert(0, enrichedDoc);
      return enrichedDoc;
    } catch (e) {
      // 2. Direct client fallback via backend OCR organize (Without Groq)
      Map<String, dynamic> clinicalData = {};
      String summary = 'Document uploaded for clinical record keeping.';

      try {
        if (rawText != null && rawText.isNotEmpty) {
          final dio = Dio();
          final organizeResp = await dio.post(
            '${AppConfig.apiBaseUrl}/api/ocr/organize',
            data: {
              'ocr_text': rawText,
              'title': title,
              'document_type': documentType,
              'hospital_name': hospitalName,
            },
          );
          if (organizeResp.statusCode == 200 && organizeResp.data != null) {
            final oData = organizeResp.data as Map<String, dynamic>;
            clinicalData = Map<String, dynamic>.from(oData['structured_data'] ?? {});
            summary = oData['clinical_summary'] as String? ?? summary;
          }
        }
      } catch (_) {}

      final fallbackDoc = MedicalDocumentModel(
        id: 'DOC-${DateTime.now().millisecondsSinceEpoch}',
        title: title,
        documentType: documentType,
        hospitalName: hospitalName,
        date: date,
        status: clinicalData.isNotEmpty ? DocumentStatus.extracted : DocumentStatus.available,
        fileSize: fileBytes != null
            ? '${(fileBytes.length / 1024).toStringAsFixed(1)} KB'
            : file != null
                ? '${(file.lengthSync() / 1024).toStringAsFixed(1)} KB'
                : '0.5 MB',
        fileName: fileName,
        extractedSummary: summary,
        extractedText: rawText,
        structuredData: clinicalData,
        fileBytes: fileBytes,
      );

      MockDatabase.documents.insert(0, fallbackDoc);
      return fallbackDoc;
    }
  }
}
