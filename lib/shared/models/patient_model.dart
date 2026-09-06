class PatientModel {
  final String id;
  final String name;
  final String phone;
  final String? email;
  final String dateOfBirth;
  final String gender;
  final String bloodGroup;
  final String emergencyContact;
  final String address;
  final String qrCodeToken;
  final String? avatarUrl;
  final List<String> allergies;
  final List<String> chronicConditions;

  PatientModel({
    required this.id,
    required this.name,
    required this.phone,
    this.email,
    required this.dateOfBirth,
    required this.gender,
    required this.bloodGroup,
    required this.emergencyContact,
    required this.address,
    required this.qrCodeToken,
    this.avatarUrl,
    this.allergies = const [],
    this.chronicConditions = const [],
  });

  PatientModel copyWith({
    String? id,
    String? name,
    String? phone,
    String? email,
    String? dateOfBirth,
    String? gender,
    String? bloodGroup,
    String? emergencyContact,
    String? address,
    String? qrCodeToken,
    String? avatarUrl,
    List<String>? allergies,
    List<String>? chronicConditions,
  }) {
    return PatientModel(
      id: id ?? this.id,
      name: name ?? this.name,
      phone: phone ?? this.phone,
      email: email ?? this.email,
      dateOfBirth: dateOfBirth ?? this.dateOfBirth,
      gender: gender ?? this.gender,
      bloodGroup: bloodGroup ?? this.bloodGroup,
      emergencyContact: emergencyContact ?? this.emergencyContact,
      address: address ?? this.address,
      qrCodeToken: qrCodeToken ?? this.qrCodeToken,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      allergies: allergies ?? this.allergies,
      chronicConditions: chronicConditions ?? this.chronicConditions,
    );
  }

  factory PatientModel.fromJson(Map<String, dynamic> json) {
    return PatientModel(
      id: json['id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      phone: json['phone'] as String? ?? '',
      email: json['email'] as String?,
      dateOfBirth: json['date_of_birth'] as String? ?? '',
      gender: json['gender'] as String? ?? 'Other',
      bloodGroup: json['blood_group'] as String? ?? 'O+',
      emergencyContact: json['emergency_contact'] as String? ?? '',
      address: json['address'] as String? ?? '',
      qrCodeToken: json['qr_code_token'] as String? ?? json['id'] as String? ?? '',
      avatarUrl: json['avatar_url'] as String?,
      allergies: (json['allergies'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      chronicConditions: (json['chronic_conditions'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'phone': phone,
      'email': email,
      'date_of_birth': dateOfBirth,
      'gender': gender,
      'blood_group': bloodGroup,
      'emergency_contact': emergencyContact,
      'address': address,
      'qr_code_token': qrCodeToken,
      'avatar_url': avatarUrl,
      'allergies': allergies,
      'chronic_conditions': chronicConditions,
    };
  }
}
