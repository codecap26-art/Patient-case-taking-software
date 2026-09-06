enum DocumentStatus {
  uploading,
  processing,
  extracted,
  available,
}

class MedicalDocumentModel {
  final String id;
  final String title;
  final String documentType;
  final String hospitalName;
  final String date;
  final DocumentStatus status;
  final String? fileUrl;
  final String? fileSize;
  final String? extractedSummary;
  final Map<String, dynamic>? structuredData;

  MedicalDocumentModel({
    required this.id,
    required this.title,
    required this.documentType,
    required this.hospitalName,
    required this.date,
    required this.status,
    this.fileUrl,
    this.fileSize,
    this.extractedSummary,
    this.structuredData,
  });

  factory MedicalDocumentModel.fromJson(Map<String, dynamic> json) {
    DocumentStatus parseStatus(String? s) {
      switch (s?.toLowerCase()) {
        case 'uploading':
          return DocumentStatus.uploading;
        case 'processing':
          return DocumentStatus.processing;
        case 'extracted':
          return DocumentStatus.extracted;
        case 'available':
        default:
          return DocumentStatus.available;
      }
    }

    return MedicalDocumentModel(
      id: json['id'] as String? ?? '',
      title: json['title'] as String? ?? 'Medical Document',
      documentType: json['document_type'] as String? ?? 'General Report',
      hospitalName: json['hospital_name'] as String? ?? 'Unknown Hospital',
      date: json['date'] as String? ?? '',
      status: parseStatus(json['status'] as String?),
      fileUrl: json['file_url'] as String?,
      fileSize: json['file_size'] as String? ?? '1.2 MB',
      extractedSummary: json['extracted_summary'] as String?,
      structuredData: json['structured_data'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'document_type': documentType,
      'hospital_name': hospitalName,
      'date': date,
      'status': status.name,
      'file_url': fileUrl,
      'file_size': fileSize,
      'extracted_summary': extractedSummary,
      'structured_data': structuredData,
    };
  }
}
