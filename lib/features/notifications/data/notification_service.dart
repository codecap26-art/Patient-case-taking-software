import '../../../config/app_config.dart';
import '../../../core/constants/api_endpoints.dart';
import '../../../core/network/api_client.dart';
import '../../../shared/data/mock_database.dart';
import '../../../shared/models/notification_model.dart';

abstract class NotificationService {
  Future<List<NotificationModel>> getNotifications();
  Future<bool> markAsRead(String id);
  Future<bool> markAllAsRead();
}

class NotificationServiceImpl implements NotificationService {
  final ApiClient apiClient;

  NotificationServiceImpl({required this.apiClient});

  @override
  Future<List<NotificationModel>> getNotifications() async {
    if (AppConfig.useMockData) {
      await Future.delayed(const Duration(milliseconds: 300));
      return MockDatabase.notifications;
    }

    final res = await apiClient.get(ApiEndpoints.notifications);
    final list = res.data as List<dynamic>;
    return list.map((e) => NotificationModel.fromJson(e as Map<String, dynamic>)).toList();
  }

  @override
  Future<bool> markAsRead(String id) async {
    if (AppConfig.useMockData) {
      final index = MockDatabase.notifications.indexWhere((n) => n.id == id);
      if (index != -1) {
        MockDatabase.notifications[index] =
            MockDatabase.notifications[index].copyWith(isRead: true);
      }
      return true;
    }

    final res = await apiClient.post(ApiEndpoints.markNotificationRead(id));
    return res.statusCode == 200;
  }

  @override
  Future<bool> markAllAsRead() async {
    if (AppConfig.useMockData) {
      for (int i = 0; i < MockDatabase.notifications.length; i++) {
        MockDatabase.notifications[i] =
            MockDatabase.notifications[i].copyWith(isRead: true);
      }
      return true;
    }

    final res = await apiClient.post(ApiEndpoints.markAllNotificationsRead);
    return res.statusCode == 200;
  }
}
