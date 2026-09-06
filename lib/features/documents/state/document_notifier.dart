import 'dart:io';
import 'package:flutter/material.dart';
import '../../../shared/models/document_model.dart';
import '../data/document_service.dart';

enum DocumentUploadStage { idle, uploading, processing, completed, error }

class DocumentNotifier extends ChangeNotifier {
  final DocumentService _documentService;

  List<MedicalDocumentModel> _documents = [];
  bool _isLoading = false;
  String? _errorMessage;
  String _selectedCategory = 'All';

  DocumentUploadStage _uploadStage = DocumentUploadStage.idle;
  double _uploadProgress = 0.0;

  DocumentNotifier(this._documentService);

  List<MedicalDocumentModel> get documents {
    if (_selectedCategory == 'All') return _documents;
    return _documents.where((d) => d.documentType.contains(_selectedCategory)).toList();
  }

  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  String get selectedCategory => _selectedCategory;
  DocumentUploadStage get uploadStage => _uploadStage;
  double get uploadProgress => _uploadProgress;

  void filterByCategory(String category) {
    _selectedCategory = category;
    notifyListeners();
  }

  Future<void> fetchDocuments() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _documents = await _documentService.getDocuments();
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _isLoading = false;
      _errorMessage = e.toString();
      notifyListeners();
    }
  }

  Future<MedicalDocumentModel?> uploadDocument({
    required String title,
    required String documentType,
    required String hospitalName,
    required String date,
    File? file,
  }) async {
    _uploadStage = DocumentUploadStage.uploading;
    _uploadProgress = 0.3;
    notifyListeners();

    try {
      await Future.delayed(const Duration(milliseconds: 500));
      _uploadProgress = 0.7;
      _uploadStage = DocumentUploadStage.processing;
      notifyListeners();

      final result = await _documentService.uploadDocument(
        title: title,
        documentType: documentType,
        hospitalName: hospitalName,
        date: date,
        file: file,
      );

      _uploadProgress = 1.0;
      _uploadStage = DocumentUploadStage.completed;
      _documents.insert(0, result);
      notifyListeners();

      // Reset stage after a short delay
      Future.delayed(const Duration(seconds: 2), () {
        _uploadStage = DocumentUploadStage.idle;
        _uploadProgress = 0.0;
        notifyListeners();
      });

      return result;
    } catch (e) {
      _uploadStage = DocumentUploadStage.error;
      _errorMessage = e.toString();
      notifyListeners();
      return null;
    }
  }
}
