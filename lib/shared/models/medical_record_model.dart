enum RecordSource {
  currentSystem,
  uploadedDocument,
  externalHospital,
}

class MedicalRecordModel {
  final String id;
  final String title;
  final String date;
  final String year;
  final String provider;
  final String recordType;
  final RecordSource source;
  final String summary;
  final String? diagnosis;
  final Map<String, String>? vitals;
  final List<String>? findings;

  MedicalRecordModel({
    required this.id,
    required this.title,
    required this.date,
    required this.year,
    required this.provider,
    required this.recordType,
    required this.source,
    required this.summary,
    this.diagnosis,
    this.vitals,
    this.findings,
  });

  factory MedicalRecordModel.fromJson(Map<String, dynamic> json) {
    RecordSource parseSource(String? s) {
      switch (s?.toLowerCase()) {
        case 'uploaded_document':
        case 'uploaded':
          return RecordSource.uploadedDocument;
        case 'external_hospital':
        case 'external':
          return RecordSource.externalHospital;
        case 'current_system':
        default:
          return RecordSource.currentSystem;
      }
    }

    return MedicalRecordModel(
      id: json['id'] as String? ?? '',
      title: json['title'] as String? ?? '',
      date: json['date'] as String? ?? '',
      year: json['year'] as String? ?? '2026',
      provider: json['provider'] as String? ?? '',
      recordType: json['record_type'] as String? ?? 'Consultation',
      source: parseSource(json['source'] as String?),
      summary: json['summary'] as String? ?? '',
      diagnosis: json['diagnosis'] as String?,
      vitals: (json['vitals'] as Map<String, dynamic>?)?.map(
        (key, value) => MapEntry(key, value.toString()),
      ),
      findings: (json['findings'] as List<dynamic>?)
          ?.map((e) => e.toString())
          .toList(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'date': date,
      'year': year,
      'provider': provider,
      'record_type': recordType,
      'source': source.name,
      'summary': summary,
      'diagnosis': diagnosis,
      'vitals': vitals,
      'findings': findings,
    };
  }
}
