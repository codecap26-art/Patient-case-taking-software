import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'package:qr_flutter/qr_flutter.dart';
import '../../../../config/theme/app_colors.dart';
import '../../../../core/localization/app_localizations.dart';
import '../../../../shared/data/mock_database.dart';
import '../../../../shared/widgets/app_card.dart';
import '../../../../shared/widgets/custom_button.dart';
import '../../../auth/state/auth_notifier.dart';

class PatientQrScreen extends StatefulWidget {
  const PatientQrScreen({super.key});

  @override
  State<PatientQrScreen> createState() => _PatientQrScreenState();
}

class _PatientQrScreenState extends State<PatientQrScreen> {
  late String _currentQrPayload;
  bool _isRefreshing = false;

  @override
  void initState() {
    super.initState();
    final patient = context.read<AuthNotifier>().currentPatient ?? MockDatabase.currentPatient;
    _currentQrPayload = patient.qrCodeToken;
  }

  void _refreshQrCode() async {
    setState(() => _isRefreshing = true);
    await Future.delayed(const Duration(milliseconds: 600));
    final patient = context.read<AuthNotifier>().currentPatient ?? MockDatabase.currentPatient;
    setState(() {
      _currentQrPayload =
          'PCT:IDENTITY:v1:${patient.id}:SEC${DateTime.now().millisecondsSinceEpoch}';
      _isRefreshing = false;
    });

    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Patient QR code refreshed with a new dynamic security token'),
        backgroundColor: AppColors.success,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  void _showQrInfoBottomSheet() {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppColors.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    context.tr('qr_help_title'),
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              _buildHelpItem(
                icon: Icons.qr_code_scanner,
                title: '1. Provider Scans Your QR',
                description:
                    'When visiting a hospital or clinic, the receptionist or doctor scans this code to identify your patient profile.',
              ),
              const SizedBox(height: 14),
              _buildHelpItem(
                icon: Icons.security,
                title: '2. Explicit Consent Required',
                description:
                    'Scanning the QR code only establishes identity. Doctors must still send an access request which you can approve or deny.',
              ),
              const SizedBox(height: 14),
              _buildHelpItem(
                icon: Icons.timer_outlined,
                title: '3. Dynamic Security',
                description:
                    'Your QR token refreshes periodically to prevent unauthorized copying or reuse.',
              ),
              const SizedBox(height: 20),
            ],
          ),
        );
      },
    );
  }

  Widget _buildHelpItem({
    required IconData icon,
    required String title,
    required String description,
  }) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: AppColors.primaryContainer,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, size: 20, color: AppColors.primary),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                description,
                style: const TextStyle(
                  fontSize: 13,
                  color: AppColors.textSecondary,
                  height: 1.3,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final patient = context.watch<AuthNotifier>().currentPatient ?? MockDatabase.currentPatient;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text(
          context.tr('my_qr_title'),
          style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 18),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, size: 20),
          onPressed: () => context.pop(),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.help_outline_rounded, color: AppColors.primary),
            tooltip: 'QR Help',
            onPressed: _showQrInfoBottomSheet,
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
        child: Column(
          children: [
            // Main QR Card
            AppCard(
              padding: const EdgeInsets.all(24),
              child: Column(
                children: [
                  // Patient Name & ID
                  Text(
                    patient.name,
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        'ID: ${patient.id}',
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: AppColors.primary,
                        ),
                      ),
                      const SizedBox(width: 6),
                      InkWell(
                        onTap: () {
                          Clipboard.setData(ClipboardData(text: patient.id));
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('Patient ID copied to clipboard'),
                              duration: Duration(seconds: 2),
                            ),
                          );
                        },
                        child: const Icon(Icons.copy_rounded, size: 16, color: AppColors.textTertiary),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),

                  // Dynamic QR Code Rendering
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppColors.outline),
                      boxShadow: AppColors.softShadow,
                    ),
                    child: _isRefreshing
                        ? const SizedBox(
                            width: 220,
                            height: 220,
                            child: Center(
                              child: CircularProgressIndicator(color: AppColors.primary),
                            ),
                          )
                        : QrImageView(
                            data: _currentQrPayload,
                            version: QrVersions.auto,
                            size: 220,
                            gapless: true,
                            eyeStyle: const QrEyeStyle(
                              eyeShape: QrEyeShape.square,
                              color: AppColors.primaryDark,
                            ),
                            dataModuleStyle: const QrDataModuleStyle(
                              dataModuleShape: QrDataModuleShape.square,
                              color: AppColors.textPrimary,
                            ),
                          ),
                  ),
                  const SizedBox(height: 20),

                  // Instructions
                  Text(
                    context.tr('qr_instruction'),
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                      fontSize: 14,
                      color: AppColors.textSecondary,
                      height: 1.4,
                    ),
                  ),
                  const SizedBox(height: 20),

                  // Refresh Button
                  OutlinedButton.icon(
                    onPressed: _isRefreshing ? null : _refreshQrCode,
                    icon: const Icon(Icons.refresh_rounded, size: 18),
                    label: Text(context.tr('refresh_qr')),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: AppColors.primary,
                      side: const BorderSide(color: AppColors.primary),
                      minimumSize: const Size(180, 42),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Security Notice Card
            AppCard(
              backgroundColor: AppColors.primaryContainer.withOpacity(0.4),
              borderSide: BorderSide(color: AppColors.primary.withOpacity(0.3)),
              padding: const EdgeInsets.all(16),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(Icons.lock_outline_rounded, color: AppColors.primary, size: 22),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      context.tr('qr_security_note'),
                      style: const TextStyle(
                        fontSize: 12.5,
                        color: AppColors.textPrimary,
                        height: 1.4,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
