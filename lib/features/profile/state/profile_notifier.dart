import 'package:flutter/material.dart';
import '../../../shared/data/mock_database.dart';
import '../../../shared/models/patient_model.dart';
import '../../auth/state/auth_notifier.dart';

class ProfileNotifier extends ChangeNotifier {
  final AuthNotifier _authNotifier;
  bool _isLoading = false;
  String? _errorMessage;

  ProfileNotifier(this._authNotifier);

  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  PatientModel get patient => _authNotifier.currentPatient ?? MockDatabase.currentPatient;

  Future<bool> updateProfile(PatientModel updatedPatient) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      await Future.delayed(const Duration(milliseconds: 600));
      MockDatabase.currentPatient = updatedPatient;
      _authNotifier.updateCurrentPatient(updatedPatient);
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _isLoading = false;
      _errorMessage = e.toString();
      notifyListeners();
      return false;
    }
  }
}
