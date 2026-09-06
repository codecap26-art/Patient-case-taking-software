import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../config/theme/app_colors.dart';
import '../../core/localization/app_localizations.dart';

class AppShellScaffold extends StatelessWidget {
  final StatefulNavigationShell navigationShell;

  const AppShellScaffold({
    super.key,
    required this.navigationShell,
  });

  @override
  Widget build(BuildContext context) {
    final currentIndex = navigationShell.currentIndex;

    return Scaffold(
      body: navigationShell,
      bottomNavigationBar: Container(
        decoration: const BoxDecoration(
          color: AppColors.surface,
          border: Border(
            top: BorderSide(color: AppColors.outline, width: 1),
          ),
          boxShadow: [
            BoxShadow(
              color: Color(0x0A000000),
              blurRadius: 8,
              offset: Offset(0, -2),
            ),
          ],
        ),
        child: NavigationBar(
          selectedIndex: currentIndex,
          onDestinationSelected: (index) {
            navigationShell.goBranch(
              index,
              initialLocation: index == navigationShell.currentIndex,
            );
          },
          backgroundColor: AppColors.surface,
          surfaceTintColor: Colors.transparent,
          indicatorColor: AppColors.primaryContainer,
          elevation: 0,
          labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
          destinations: [
            NavigationDestination(
              icon: const Icon(Icons.home_outlined, color: AppColors.textSecondary),
              selectedIcon: const Icon(Icons.home_rounded, color: AppColors.primary),
              label: context.tr('nav_home'),
            ),
            NavigationDestination(
              icon: const Icon(Icons.folder_outlined, color: AppColors.textSecondary),
              selectedIcon: const Icon(Icons.folder_rounded, color: AppColors.primary),
              label: context.tr('nav_records'),
            ),
            NavigationDestination(
              icon: const Icon(Icons.medication_outlined, color: AppColors.textSecondary),
              selectedIcon: const Icon(Icons.medication_rounded, color: AppColors.primary),
              label: context.tr('nav_prescriptions'),
            ),
            NavigationDestination(
              icon: const Icon(Icons.notifications_none_rounded, color: AppColors.textSecondary),
              selectedIcon: const Icon(Icons.notifications_rounded, color: AppColors.primary),
              label: context.tr('nav_notifications'),
            ),
            NavigationDestination(
              icon: const Icon(Icons.person_outline_rounded, color: AppColors.textSecondary),
              selectedIcon: const Icon(Icons.person_rounded, color: AppColors.primary),
              label: context.tr('nav_profile'),
            ),
          ],
        ),
      ),
    );
  }
}
