enum ConsentStatus {
  pending,
  allowed,
  denied,
  revoked,
}

class ConsentRequestModel {
  final String id;
  final String providerName;
  final String providerType; // Hospital, Clinic, Diagnostic Lab
  final String requestedScope; // e.g. "Medical History + Previous Prescriptions"
  final String purpose; // e.g. "In-person Consultation & Case Review"
  final ConsentStatus status;
  final String requestDate;
  final String? responseDate;
  final String validUntil;
  final String? doctorName;

  ConsentRequestModel({
    required this.id,
    required this.providerName,
    required this.providerType,
    required this.requestedScope,
    required this.purpose,
    required this.status,
    required this.requestDate,
    this.responseDate,
    required this.validUntil,
    this.doctorName,
  });

  factory ConsentRequestModel.fromJson(Map<String, dynamic> json) {
    ConsentStatus parseStatus(String? s) {
      switch (s?.toLowerCase()) {
        case 'allowed':
        case 'granted':
          return ConsentStatus.allowed;
        case 'denied':
        case 'rejected':
          return ConsentStatus.denied;
        case 'revoked':
          return ConsentStatus.revoked;
        case 'pending':
        default:
          return ConsentStatus.pending;
      }
    }

    return ConsentRequestModel(
      id: json['id'] as String? ?? '',
      providerName: json['provider_name'] as String? ?? 'Healthcare Provider',
      providerType: json['provider_type'] as String? ?? 'Hospital',
      requestedScope: json['requested_scope'] as String? ?? 'Medical History',
      purpose: json['purpose'] as String? ?? 'Patient Consultation',
      status: parseStatus(json['status'] as String?),
      requestDate: json['request_date'] as String? ?? '',
      responseDate: json['response_date'] as String?,
      validUntil: json['valid_until'] as String? ?? '24 Hours',
      doctorName: json['doctor_name'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'provider_name': providerName,
      'provider_type': providerType,
      'requested_scope': requestedScope,
      'purpose': purpose,
      'status': status.name,
      'request_date': requestDate,
      'response_date': responseDate,
      'valid_until': validUntil,
      'doctor_name': doctorName,
    };
  }

  ConsentRequestModel copyWith({
    String? id,
    String? providerName,
    String? providerType,
    String? requestedScope,
    String? purpose,
    ConsentStatus? status,
    String? requestDate,
    String? responseDate,
    String? validUntil,
    String? doctorName,
  }) {
    return ConsentRequestModel(
      id: id ?? this.id,
      providerName: providerName ?? this.providerName,
      providerType: providerType ?? this.providerType,
      requestedScope: requestedScope ?? this.requestedScope,
      purpose: purpose ?? this.purpose,
      status: status ?? this.status,
      requestDate: requestDate ?? this.requestDate,
      responseDate: responseDate ?? this.responseDate,
      validUntil: validUntil ?? this.validUntil,
      doctorName: doctorName ?? this.doctorName,
    );
  }
}
