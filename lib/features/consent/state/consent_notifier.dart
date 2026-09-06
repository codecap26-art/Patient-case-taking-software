import 'package:flutter/material.dart';
import '../../../shared/models/consent_request_model.dart';
import '../data/consent_service.dart';

class ConsentNotifier extends ChangeNotifier {
  final ConsentService _consentService;

  List<ConsentRequestModel> _requests = [];
  bool _isLoading = false;
  String? _errorMessage;

  ConsentNotifier(this._consentService);

  List<ConsentRequestModel> get allRequests => _requests;
  List<ConsentRequestModel> get pendingRequests =>
      _requests.where((r) => r.status == ConsentStatus.pending).toList();
  List<ConsentRequestModel> get activeConsents =>
      _requests.where((r) => r.status == ConsentStatus.allowed).toList();
  List<ConsentRequestModel> get auditHistory =>
      _requests.where((r) => r.status != ConsentStatus.pending).toList();

  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  Future<void> fetchConsentRequests() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _requests = await _consentService.getConsentRequests();
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _isLoading = false;
      _errorMessage = e.toString();
      notifyListeners();
    }
  }

  Future<bool> respond(String requestId, bool allow) async {
    try {
      final success = await _consentService.respondToConsent(requestId, allow);
      if (success) {
        await fetchConsentRequests();
      }
      return success;
    } catch (e) {
      _errorMessage = e.toString();
      notifyListeners();
      return false;
    }
  }

  Future<bool> revoke(String requestId) async {
    try {
      final success = await _consentService.revokeConsent(requestId);
      if (success) {
        await fetchConsentRequests();
      }
      return success;
    } catch (e) {
      _errorMessage = e.toString();
      notifyListeners();
      return false;
    }
  }
}
