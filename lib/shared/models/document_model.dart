enum DocumentStatus {
  uploading,
  processing,
  extracted,
  available,
  failed,
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
  final String? fileName;
  final String? mimeType;
  final String? extractedSummary;
  final String? extractedText;
  final Map<String, dynamic>? structuredData;
  final int? pageCount;
  final String? extractionError;
  final bool doctorReviewed;
  final String? doctorNotes;
  final List<int>? fileBytes;

  MedicalDocumentModel({
    required this.id,
    required this.title,
    required this.documentType,
    required this.hospitalName,
    required this.date,
    required this.status,
    this.fileUrl,
    this.fileSize,
    this.fileName,
    this.mimeType,
    this.extractedSummary,
    this.extractedText,
    this.structuredData,
    this.pageCount,
    this.extractionError,
    this.doctorReviewed = false,
    this.doctorNotes,
    this.fileBytes,
  });

  factory MedicalDocumentModel.fromJson(Map<String, dynamic> json) {
    DocumentStatus parseStatus(String? s) {
      switch (s?.toLowerCase()) {
        case 'uploading':
          return DocumentStatus.uploading;
        case 'processing':
          return DocumentStatus.processing;
        case 'ocr_completed':
        case 'extraction_completed':
        case 'processed':
        case 'extracted':
          return DocumentStatus.extracted;
        case 'failed':
          return DocumentStatus.failed;
        case 'available':
        default:
          return DocumentStatus.available;
      }
    }

    return MedicalDocumentModel(
      id: json['id'] as String? ?? '',
      title: json['title'] as String? ?? 'Medical Document',
      documentType: json['document_type'] as String? ?? 'General Report',
      hospitalName: json['hospital_name'] as String? ?? 'Clinical Diagnostics',
      date: json['document_date'] as String? ?? json['date'] as String? ?? '',
      status: parseStatus(json['processing_status'] as String? ?? json['status'] as String?),
      fileUrl: json['file_url'] as String?,
      fileSize: json['file_size_display'] as String? ?? json['file_size'] as String? ?? '1.2 MB',
      fileName: json['file_name'] as String?,
      mimeType: json['mime_type'] as String?,
      extractedSummary: json['extracted_summary'] as String?,
      extractedText: json['extracted_text'] as String?,
      structuredData: json['structured_data'] as Map<String, dynamic>?,
      pageCount: json['page_count'] as int? ?? 1,
      extractionError: json['extraction_error'] as String?,
      doctorReviewed: json['doctor_reviewed'] as bool? ?? false,
      doctorNotes: json['doctor_notes'] as String?,
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
      'file_name': fileName,
      'mime_type': mimeType,
      'extracted_summary': extractedSummary,
      'extracted_text': extractedText,
      'structured_data': structuredData,
      'page_count': pageCount,
      'extraction_error': extractionError,
      'doctor_reviewed': doctorReviewed,
      'doctor_notes': doctorNotes,
    };
  }
}
