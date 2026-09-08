import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../../../config/theme/app_colors.dart';
import '../../../../core/localization/app_localizations.dart';
import '../../../../shared/models/notification_model.dart';
import '../../../../shared/widgets/app_card.dart';
import '../../../../shared/widgets/empty_state_view.dart';
import '../../state/notification_notifier.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<NotificationNotifier>().fetchNotifications();
    });
  }

  IconData _getCategoryIcon(NotificationCategory cat) {
    switch (cat) {
      case NotificationCategory.consultation:
        return Icons.medical_services_outlined;
      case NotificationCategory.prescription:
        return Icons.medication_outlined;
      case NotificationCategory.document:
        return Icons.description_outlined;
      case NotificationCategory.consent:
        return Icons.shield_outlined;
      case NotificationCategory.system:
        return Icons.info_outline;
    }
  }

  Color _getCategoryColor(NotificationCategory cat) {
    switch (cat) {
      case NotificationCategory.consultation:
        return AppColors.primary;
      case NotificationCategory.prescription:
        return const Color(0xFF8B5CF6);
      case NotificationCategory.document:
        return AppColors.secondary;
      case NotificationCategory.consent:
        return AppColors.warning;
      case NotificationCategory.system:
        return AppColors.textTertiary;
    }
  }

  @override
  Widget build(BuildContext context) {
    final notifNotifier = context.watch<NotificationNotifier>();
    final notifications = notifNotifier.notifications;
    final isLoading = notifNotifier.isLoading;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text(
          context.tr('nav_notifications'),
          style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 18),
        ),
        actions: [
          if (notifications.any((n) => !n.isRead))
            TextButton(
              onPressed: () => context.read<NotificationNotifier>().markAllAsRead(),
              child: const Text('Mark all as read'),
            ),
        ],
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
          : notifications.isEmpty
              ? const EmptyStateView(
                  icon: Icons.notifications_off_outlined,
                  title: 'No Notifications',
                  message: 'You are all caught up! Updates regarding your consultations and prescriptions will appear here.',
                )
              : RefreshIndicator(
                  onRefresh: () => context.read<NotificationNotifier>().fetchNotifications(),
                  color: AppColors.primary,
                  child: ListView.separated(
                    padding: const EdgeInsets.all(16),
                    itemCount: notifications.length,
                    separatorBuilder: (_, __) => const SizedBox(height: 10),
                    itemBuilder: (context, index) {
                      final notif = notifications[index];
                      final catColor = _getCategoryColor(notif.category);

                      return AppCard(
                        padding: const EdgeInsets.all(16),
                        backgroundColor: notif.isRead
                            ? AppColors.surface
                            : AppColors.primaryContainer.withOpacity(0.3),
                        onTap: () {
                          context.read<NotificationNotifier>().markAsRead(notif.id);
                          if (notif.targetRoute != null) {
                            context.push(notif.targetRoute!);
                          }
                        },
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Container(
                              padding: const EdgeInsets.all(10),
                              decoration: BoxDecoration(
                                color: catColor.withOpacity(0.15),
                                shape: BoxShape.circle,
                              ),
                              child: Icon(
                                _getCategoryIcon(notif.category),
                                color: catColor,
                                size: 20,
                              ),
                            ),
                            const SizedBox(width: 14),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Expanded(
                                        child: Text(
                                          notif.title,
                                          style: TextStyle(
                                            fontSize: 14,
                                            fontWeight: notif.isRead
                                                ? FontWeight.w600
                                                : FontWeight.bold,
                                            color: AppColors.textPrimary,
                                          ),
                                        ),
                                      ),
                                      if (!notif.isRead)
                                        Container(
                                          width: 8,
                                          height: 8,
                                          decoration: const BoxDecoration(
                                            color: AppColors.primary,
                                            shape: BoxShape.circle,
                                          ),
                                        ),
                                    ],
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    notif.message,
                                    style: const TextStyle(
                                      fontSize: 13,
                                      color: AppColors.textSecondary,
                                      height: 1.35,
                                    ),
                                  ),
                                  const SizedBox(height: 6),
                                  Text(
                                    notif.timestamp,
                                    style: const TextStyle(
                                      fontSize: 11,
                                      color: AppColors.textTertiary,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                ),
    );
  }
}
