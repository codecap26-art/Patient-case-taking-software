import 'package:flutter/material.dart';
import '../../../shared/models/medical_record_model.dart';
import '../data/history_service.dart';

class HistoryNotifier extends ChangeNotifier {
  final HistoryService _historyService;

  List<MedicalRecordModel> _records = [];
  bool _isLoading = false;
  String? _errorMessage;
  RecordSource? _selectedSourceFilter;

  HistoryNotifier(this._historyService);

  List<MedicalRecordModel> get records {
    if (_selectedSourceFilter == null) return _records;
    return _records.where((r) => r.source == _selectedSourceFilter).toList();
  }

  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  RecordSource? get selectedSourceFilter => _selectedSourceFilter;

  // Group records by Year
  Map<String, List<MedicalRecordModel>> get groupedByYear {
    final map = <String, List<MedicalRecordModel>>{};
    for (var r in records) {
      if (!map.containsKey(r.year)) {
        map[r.year] = [];
      }
      map[r.year]!.add(r);
    }
    return map;
  }

  void filterBySource(RecordSource? source) {
    _selectedSourceFilter = source;
    notifyListeners();
  }

  Future<void> fetchHistory() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _records = await _historyService.getMedicalHistory();
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _isLoading = false;
      _errorMessage = e.toString();
      notifyListeners();
    }
  }
}
