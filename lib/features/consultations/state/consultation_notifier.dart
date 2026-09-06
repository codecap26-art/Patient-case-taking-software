import 'package:flutter/material.dart';
import '../../../shared/models/consultation_model.dart';
import '../data/consultation_service.dart';

class ConsultationNotifier extends ChangeNotifier {
  final ConsultationService _consultationService;

  List<ConsultationModel> _consultations = [];
  bool _isLoading = false;
  String? _errorMessage;

  ConsultationNotifier(this._consultationService);

  List<ConsultationModel> get consultations => _consultations;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  Future<void> fetchConsultations() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _consultations = await _consultationService.getConsultations();
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _isLoading = false;
      _errorMessage = e.toString();
      notifyListeners();
    }
  }
}
