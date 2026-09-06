enum NotificationCategory {
  consultation,
  prescription,
  document,
  consent,
  system,
}

class NotificationModel {
  final String id;
  final String title;
  final String message;
  final NotificationCategory category;
  final String timestamp;
  final bool isRead;
  final String? targetRoute;

  NotificationModel({
    required this.id,
    required this.title,
    required this.message,
    required this.category,
    required this.timestamp,
    required this.isRead,
    this.targetRoute,
  });

  factory NotificationModel.fromJson(Map<String, dynamic> json) {
    NotificationCategory parseCategory(String? c) {
      switch (c?.toLowerCase()) {
        case 'consultation':
          return NotificationCategory.consultation;
        case 'prescription':
          return NotificationCategory.prescription;
        case 'document':
          return NotificationCategory.document;
        case 'consent':
          return NotificationCategory.consent;
        case 'system':
        default:
          return NotificationCategory.system;
      }
    }

    return NotificationModel(
      id: json['id'] as String? ?? '',
      title: json['title'] as String? ?? '',
      message: json['message'] as String? ?? '',
      category: parseCategory(json['category'] as String?),
      timestamp: json['timestamp'] as String? ?? '',
      isRead: json['is_read'] as bool? ?? false,
      targetRoute: json['target_route'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'message': message,
      'category': category.name,
      'timestamp': timestamp,
      'is_read': isRead,
      'target_route': targetRoute,
    };
  }

  NotificationModel copyWith({
    String? id,
    String? title,
    String? message,
    NotificationCategory? category,
    String? timestamp,
    bool? isRead,
    String? targetRoute,
  }) {
    return NotificationModel(
      id: id ?? this.id,
      title: title ?? this.title,
      message: message ?? this.message,
      category: category ?? this.category,
      timestamp: timestamp ?? this.timestamp,
      isRead: isRead ?? this.isRead,
      targetRoute: targetRoute ?? this.targetRoute,
    );
  }
}
