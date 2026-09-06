class MedicineItem {
  final String name;
  final String dosage;
  final String frequency; // e.g. "1-0-1" (Morning-Afternoon-Night)
  final String duration;  // e.g. "5 days"
  final String timing;    // e.g. "After food"
  final String? instructions;

  MedicineItem({
    required this.name,
    required this.dosage,
    required this.frequency,
    required this.duration,
    required this.timing,
    this.instructions,
  });

  factory MedicineItem.fromJson(Map<String, dynamic> json) {
    return MedicineItem(
      name: json['name'] as String? ?? '',
      dosage: json['dosage'] as String? ?? '',
      frequency: json['frequency'] as String? ?? '',
      duration: json['duration'] as String? ?? '',
      timing: json['timing'] as String? ?? 'After food',
      instructions: json['instructions'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'dosage': dosage,
      'frequency': frequency,
      'duration': duration,
      'timing': timing,
      'instructions': instructions,
    };
  }
}

class PrescriptionModel {
  final String id;
  final String doctorName;
  final String doctorSpecialization;
  final String hospitalName;
  final String date;
  final String diagnosis;
  final bool isActive;
  final List<MedicineItem> medicines;
  final String? generalAdvice;
  final String? doctorNotes;

  PrescriptionModel({
    required this.id,
    required this.doctorName,
    required this.doctorSpecialization,
    required this.hospitalName,
    required this.date,
    required this.diagnosis,
    required this.isActive,
    required this.medicines,
    this.generalAdvice,
    this.doctorNotes,
  });

  factory PrescriptionModel.fromJson(Map<String, dynamic> json) {
    return PrescriptionModel(
      id: json['id'] as String? ?? '',
      doctorName: json['doctor_name'] as String? ?? '',
      doctorSpecialization: json['doctor_specialization'] as String? ?? 'General Physician',
      hospitalName: json['hospital_name'] as String? ?? '',
      date: json['date'] as String? ?? '',
      diagnosis: json['diagnosis'] as String? ?? '',
      isActive: json['is_active'] as bool? ?? true,
      medicines: (json['medicines'] as List<dynamic>?)
              ?.map((e) => MedicineItem.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      generalAdvice: json['general_advice'] as String?,
      doctorNotes: json['doctor_notes'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'doctor_name': doctorName,
      'doctor_specialization': doctorSpecialization,
      'hospital_name': hospitalName,
      'date': date,
      'diagnosis': diagnosis,
      'is_active': isActive,
      'medicines': medicines.map((e) => e.toJson()).toList(),
      'general_advice': generalAdvice,
      'doctor_notes': doctorNotes,
    };
  }
}
