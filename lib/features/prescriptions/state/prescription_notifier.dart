import 'package:flutter/material.dart';
import '../../../shared/models/prescription_model.dart';
import '../data/prescription_service.dart';

class PrescriptionNotifier extends ChangeNotifier {
  final PrescriptionService _prescriptionService;

  List<PrescriptionModel> _prescriptions = [];
  bool _isLoading = false;
  String? _errorMessage;
  bool _showActiveOnly = true;

  PrescriptionNotifier(this._prescriptionService);

  List<PrescriptionModel> get prescriptions => _prescriptions;
  List<PrescriptionModel> get activePrescriptions =>
      _prescriptions.where((p) => p.isActive).toList();
  List<PrescriptionModel> get pastPrescriptions =>
      _prescriptions.where((p) => !p.isActive).toList();

  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  bool get showActiveOnly => _showActiveOnly;

  void toggleFilter(bool activeOnly) {
    _showActiveOnly = activeOnly;
    notifyListeners();
  }

  Future<void> fetchPrescriptions() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _prescriptions = await _prescriptionService.getPrescriptions();
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _isLoading = false;
      _errorMessage = e.toString();
      notifyListeners();
    }
  }
}
