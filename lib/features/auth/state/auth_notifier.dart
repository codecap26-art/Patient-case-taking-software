import 'package:flutter/material.dart';
import '../../../core/storage/token_storage.dart';
import '../../../shared/models/patient_model.dart';
import '../data/auth_service.dart';

enum AuthStateStatus { initial, loading, authenticated, unauthenticated, error }

class AuthNotifier extends ChangeNotifier {
  final AuthService _authService;
  final TokenStorage _tokenStorage;

  AuthStateStatus _status = AuthStateStatus.initial;
  PatientModel? _currentPatient;
  String? _errorMessage;
  String? _pendingMobileNumber;

  AuthNotifier({
    required AuthService authService,
    required TokenStorage tokenStorage,
  })  : _authService = authService,
        _tokenStorage = tokenStorage;

  AuthStateStatus get status => _status;
  PatientModel? get currentPatient => _currentPatient;
  String? get errorMessage => _errorMessage;
  String? get pendingMobileNumber => _pendingMobileNumber;
  bool get isAuthenticated => _status == AuthStateStatus.authenticated;
  bool get isLoading => _status == AuthStateStatus.loading;

  void setPendingMobileNumber(String phone) {
    _pendingMobileNumber = phone;
  }

  Future<bool> checkAuthStatus() async {
    final hasToken = _tokenStorage.hasToken();
    if (hasToken) {
      _currentPatient = await _authService.getCachedProfile();
      _status = AuthStateStatus.authenticated;
      notifyListeners();
      return true;
    } else {
      _status = AuthStateStatus.unauthenticated;
      notifyListeners();
      return false;
    }
  }

  Future<bool> sendOtp(String mobileNumber) async {
    _status = AuthStateStatus.loading;
    _errorMessage = null;
    notifyListeners();

    try {
      final success = await _authService.sendOtp(mobileNumber);
      _pendingMobileNumber = mobileNumber;
      _status = AuthStateStatus.unauthenticated;
      notifyListeners();
      return success;
    } catch (e) {
      _status = AuthStateStatus.error;
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
      return false;
    }
  }

  Future<bool> verifyOtp(String otp) async {
    if (_pendingMobileNumber == null) {
      _errorMessage = 'Mobile number missing. Please try again.';
      notifyListeners();
      return false;
    }

    _status = AuthStateStatus.loading;
    _errorMessage = null;
    notifyListeners();

    try {
      final patient = await _authService.verifyOtp(_pendingMobileNumber!, otp);
      _currentPatient = patient;
      _status = AuthStateStatus.authenticated;
      notifyListeners();
      return true;
    } catch (e) {
      _status = AuthStateStatus.error;
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
      return false;
    }
  }

  Future<bool> register(PatientModel patient, String otp) async {
    _status = AuthStateStatus.loading;
    _errorMessage = null;
    notifyListeners();

    try {
      final registered = await _authService.register(patient, otp);
      _currentPatient = registered;
      _status = AuthStateStatus.authenticated;
      notifyListeners();
      return true;
    } catch (e) {
      _status = AuthStateStatus.error;
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
      return false;
    }
  }

  void updateCurrentPatient(PatientModel updated) {
    _currentPatient = updated;
    notifyListeners();
  }

  Future<void> logout() async {
    await _authService.logout();
    _currentPatient = null;
    _pendingMobileNumber = null;
    _status = AuthStateStatus.unauthenticated;
    notifyListeners();
  }

  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
}
