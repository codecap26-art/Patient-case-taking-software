import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../../config/theme/app_colors.dart';
import '../../../../core/localization/app_localizations.dart';
import '../../../../core/routing/route_names.dart';
import '../../../../shared/widgets/app_card.dart';

class QuickActionsGrid extends StatelessWidget {
  final int pendingConsentCount;

  const QuickActionsGrid({
    super.key,
    this.pendingConsentCount = 0,
  });

  @override
  Widget build(BuildContext context) {
    final actions = [
      _ActionItem(
        title: context.tr('action_records'),
        icon: Icons.folder_shared_outlined,
        color: AppColors.primary,
        bgColor: AppColors.primaryContainer,
        route: RouteNames.medicalHistory,
      ),
      _ActionItem(
        title: context.tr('action_upload'),
        icon: Icons.cloud_upload_outlined,
        color: AppColors.secondary,
        bgColor: AppColors.secondaryContainer,
        route: RouteNames.uploadDocument,
      ),
      _ActionItem(
        title: context.tr('action_prescriptions'),
        icon: Icons.medication_outlined,
        color: const Color(0xFF8B5CF6),
        bgColor: const Color(0xFFF3E8FF),
        route: RouteNames.prescriptions,
      ),
      _ActionItem(
        title: context.tr('action_consultations'),
        icon: Icons.assignment_outlined,
        color: const Color(0xFFF59E0B),
        bgColor: const Color(0xFFFEF3C7),
        route: RouteNames.consultations,
      ),
      _ActionItem(
        title: context.tr('action_my_qr'),
        icon: Icons.qr_code_2_rounded,
        color: const Color(0xFF0D9488),
        bgColor: const Color(0xFFCCFBF1),
        route: RouteNames.qr,
      ),
      _ActionItem(
        title: context.tr('action_consent'),
        icon: Icons.verified_user_outlined,
        color: const Color(0xFFEC4899),
        bgColor: const Color(0xFFFCE7F3),
        route: RouteNames.consentAccess,
        badgeCount: pendingConsentCount,
      ),
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          context.tr('quick_actions'),
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w700,
            color: AppColors.textPrimary,
          ),
        ),
        const SizedBox(height: 12),
        GridView.builder(
          physics: const NeverScrollableScrollParametric(),
          shrinkWrap: true,
          itemCount: actions.length,
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 3,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            childAspectRatio: 0.95,
          ),
          itemBuilder: (context, index) {
            final item = actions[index];
            return AppCard(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 12),
              onTap: () => context.push(item.route),
              child: Stack(
                clipBehavior: Clip.none,
                children: [
                  Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: item.bgColor,
                            shape: BoxShape.circle,
                          ),
                          child: Icon(item.icon, size: 24, color: item.color),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          item.title,
                          textAlign: TextAlign.center,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: AppColors.textPrimary,
                          ),
                        ),
                      ],
                    ),
                  ),
                  if (item.badgeCount > 0)
                    Positioned(
                      top: -4,
                      right: -4,
                      child: Container(
                        padding: const EdgeInsets.all(6),
                        decoration: const BoxDecoration(
                          color: AppColors.error,
                          shape: BoxShape.circle,
                        ),
                        child: Text(
                          '${item.badgeCount}',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            );
          },
        ),
      ],
    );
  }
}

class _ActionItem {
  final String title;
  final IconData icon;
  final Color color;
  final Color bgColor;
  final String route;
  final int badgeCount;

  _ActionItem({
    required this.title,
    required this.icon,
    required this.color,
    required this.bgColor,
    required this.route,
    this.badgeCount = 0,
  });
}
