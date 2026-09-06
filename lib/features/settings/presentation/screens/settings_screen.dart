import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../../../config/app_config.dart';
import '../../../../config/theme/app_colors.dart';
import '../../../../core/localization/app_localizations.dart';
import '../../../../core/routing/route_names.dart';
import '../../../../shared/widgets/app_card.dart';
import '../../../auth/state/auth_notifier.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  void _handleLogout(BuildContext context) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text(context.tr('logout_confirm_title')),
          content: Text(context.tr('logout_confirm_msg')),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: Text(context.tr('cancel')),
            ),
            ElevatedButton(
              onPressed: () => Navigator.pop(context, true),
              style: ElevatedButton.styleFrom(backgroundColor: AppColors.error),
              child: Text(context.tr('logout')),
            ),
          ],
        );
      },
    );

    if (confirmed == true) {
      final authNotifier = context.read<AuthNotifier>();
      await authNotifier.logout();
      if (context.mounted) {
        context.go(RouteNames.login);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text(
          context.tr('settings'),
          style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 18),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, size: 20),
          onPressed: () => context.pop(),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        child: Column(
          children: [
            // Account & Preferences
            AppCard(
              padding: EdgeInsets.zero,
              child: Column(
                children: [
                  _buildSettingTile(
                    icon: Icons.person_outline_rounded,
                    title: context.tr('patient_profile'),
                    onTap: () => context.push(RouteNames.profile),
                  ),
                  const Divider(height: 1),
                  _buildSettingTile(
                    icon: Icons.language_rounded,
                    title: context.tr('language'),
                    subtitle: 'English / தமிழ் / हिन्दी',
                    onTap: () => context.push(RouteNames.languageSelection),
                  ),
                  const Divider(height: 1),
                  _buildSettingTile(
                    icon: Icons.shield_outlined,
                    title: context.tr('consent_and_access'),
                    onTap: () => context.push(RouteNames.consentAccess),
                  ),
                  const Divider(height: 1),
                  _buildSettingTile(
                    icon: Icons.qr_code_2_rounded,
                    title: context.tr('action_my_qr'),
                    onTap: () => context.push(RouteNames.qr),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Support & About
            AppCard(
              padding: EdgeInsets.zero,
              child: Column(
                children: [
                  _buildSettingTile(
                    icon: Icons.help_outline_rounded,
                    title: context.tr('help_support'),
                    onTap: () => context.push(RouteNames.helpFaq),
                  ),
                  const Divider(height: 1),
                  _buildSettingTile(
                    icon: Icons.privacy_tip_outlined,
                    title: context.tr('privacy_policy'),
                    onTap: () {
                      showDialog(
                        context: context,
                        builder: (ctx) => AlertDialog(
                          title: const Text('Privacy & Data Governance'),
                          content: const Text(
                            'Your medical records and consultation history are strictly confidential under Patient Health Information (PHI) standards. No healthcare provider can access your clinical timeline without your explicit consent.',
                          ),
                          actions: [
                            TextButton(
                              onPressed: () => Navigator.pop(ctx),
                              child: const Text('OK'),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                  const Divider(height: 1),
                  _buildSettingTile(
                    icon: Icons.info_outline_rounded,
                    title: context.tr('about_app'),
                    subtitle: 'Version ${AppConfig.appVersion}',
                    onTap: () {
                      showAboutDialog(
                        context: context,
                        applicationName: AppConfig.appName,
                        applicationVersion: AppConfig.appVersion,
                        applicationLegalese: '© 2026 Patient Case Taking Platform. All rights reserved.',
                      );
                    },
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Logout Button
            AppCard(
              padding: EdgeInsets.zero,
              child: ListTile(
                leading: const Icon(Icons.logout_rounded, color: AppColors.error),
                title: Text(
                  context.tr('logout'),
                  style: const TextStyle(
                    fontWeight: FontWeight.w600,
                    color: AppColors.error,
                  ),
                ),
                onTap: () => _handleLogout(context),
              ),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildSettingTile({
    required IconData icon,
    required String title,
    String? subtitle,
    required VoidCallback onTap,
  }) {
    return ListTile(
      leading: Icon(icon, color: AppColors.primary),
      title: Text(
        title,
        style: const TextStyle(
          fontSize: 14.5,
          fontWeight: FontWeight.w600,
          color: AppColors.textPrimary,
        ),
      ),
      subtitle: subtitle != null
          ? Text(
              subtitle,
              style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
            )
          : null,
      trailing: const Icon(Icons.chevron_right, color: AppColors.textTertiary, size: 20),
      onTap: onTap,
    );
  }
}
