import 'package:flutter/material.dart';
import '../../../shared/data/mock_database.dart';
import '../../../shared/models/consultation_model.dart';
import '../../../shared/models/prescription_model.dart';
import '../../../shared/models/document_model.dart';
import '../../../shared/models/consent_request_model.dart';

class HomeNotifier extends ChangeNotifier {
  bool _isLoading = false;
  ConsultationModel? _upcomingConsultation;
  PrescriptionModel? _latestPrescription;
  List<MedicalDocumentModel> _recentDocuments = [];
  int _pendingConsentCount = 0;

  bool get isLoading => _isLoading;
  ConsultationModel? get upcomingConsultation => _upcomingConsultation;
  PrescriptionModel? get latestPrescription => _latestPrescription;
  List<MedicalDocumentModel> get recentDocuments => _recentDocuments;
  int get pendingConsentCount => _pendingConsentCount;

  Future<void> loadDashboardData() async {
    _isLoading = true;
    notifyListeners();

    // Simulate async data loading
    await Future.delayed(const Duration(milliseconds: 400));

    _upcomingConsultation = MockDatabase.consultations.isNotEmpty
        ? MockDatabase.consultations.first
        : null;

    _latestPrescription = MockDatabase.prescriptions.isNotEmpty
        ? MockDatabase.prescriptions.firstWhere(
            (p) => p.isActive,
            orElse: () => MockDatabase.prescriptions.first,
          )
        : null;

    _recentDocuments = MockDatabase.documents.take(3).toList();

    _pendingConsentCount = MockDatabase.consentRequests
        .where((c) => c.status == ConsentStatus.pending)
        .length;

    _isLoading = false;
    notifyListeners();
  }
}
