class ConsultationModel {
  final String id;
  final String date;
  final String time;
  final String doctorName;
  final String doctorSpecialization;
  final String hospitalName;
  final String status; // Completed, Upcoming, In-Progress
  final String chiefComplaint;
  final List<String> symptoms;
  final String duration;
  final Map<String, String> vitals;
  final List<String> pastHistoryConsidered;
  final List<String> allergiesNoted;
  final List<String> currentMedications;
  final String doctorNotes;
  final String? clinicalSummary;
  final String? linkedPrescriptionId;

  ConsultationModel({
    required this.id,
    required this.date,
    required this.time,
    required this.doctorName,
    required this.doctorSpecialization,
    required this.hospitalName,
    required this.status,
    required this.chiefComplaint,
    required this.symptoms,
    required this.duration,
    required this.vitals,
    this.pastHistoryConsidered = const [],
    this.allergiesNoted = const [],
    this.currentMedications = const [],
    required this.doctorNotes,
    this.clinicalSummary,
    this.linkedPrescriptionId,
  });

  factory ConsultationModel.fromJson(Map<String, dynamic> json) {
    return ConsultationModel(
      id: json['id'] as String? ?? '',
      date: json['date'] as String? ?? '',
      time: json['time'] as String? ?? '',
      doctorName: json['doctor_name'] as String? ?? '',
      doctorSpecialization: json['doctor_specialization'] as String? ?? 'Consultant',
      hospitalName: json['hospital_name'] as String? ?? '',
      status: json['status'] as String? ?? 'Completed',
      chiefComplaint: json['chief_complaint'] as String? ?? '',
      symptoms: (json['symptoms'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      duration: json['duration'] as String? ?? '',
      vitals: (json['vitals'] as Map<String, dynamic>?)?.map(
            (k, v) => MapEntry(k, v.toString()),
          ) ??
          {},
      pastHistoryConsidered: (json['past_history'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      allergiesNoted: (json['allergies'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      currentMedications: (json['current_medications'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      doctorNotes: json['doctor_notes'] as String? ?? '',
      clinicalSummary: json['clinical_summary'] as String?,
      linkedPrescriptionId: json['linked_prescription_id'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'date': date,
      'time': time,
      'doctor_name': doctorName,
      'doctor_specialization': doctorSpecialization,
      'hospital_name': hospitalName,
      'status': status,
      'chief_complaint': chiefComplaint,
      'symptoms': symptoms,
      'duration': duration,
      'vitals': vitals,
      'past_history': pastHistoryConsidered,
      'allergies': allergiesNoted,
      'current_medications': currentMedications,
      'doctor_notes': doctorNotes,
      'clinical_summary': clinicalSummary,
      'linked_prescription_id': linkedPrescriptionId,
    };
  }
}
