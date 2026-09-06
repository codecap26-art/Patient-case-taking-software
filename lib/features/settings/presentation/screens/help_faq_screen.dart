import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../../config/theme/app_colors.dart';
import '../../../../core/localization/app_localizations.dart';
import '../../../../shared/widgets/app_card.dart';

class HelpFaqScreen extends StatelessWidget {
  const HelpFaqScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final faqs = [
      {
        'q': 'How does Doctor-Patient QR linking work?',
        'a':
            'When you visit a clinic or hospital, show your unique Patient QR code. The doctor or provider scans it to identify your profile. However, they cannot view your private records until you explicitly click [Allow] in your Consent & Access screen.',
      },
      {
        'q': 'Can I edit AI-extracted lab values or prescriptions?',
        'a':
            'No. To protect clinical accuracy and medical compliance, patient medical records and prescriptions cannot be manually altered. Extracted document values are labeled for reference and doctor review.',
      },
      {
        'q': 'Where do my medical timeline records come from?',
        'a':
            'Your medical timeline displays records from three sources: (1) Current system consultations, (2) Your uploaded reports/scans, and (3) Authorized external hospital EHR networks.',
      },
      {
        'q': 'How do I revoke access from a doctor or hospital?',
        'a':
            'Navigate to "Consent & Access" -> "Active Permissions" and tap "Revoke Access". The provider\'s access will immediately be severed.',
      },
      {
        'q': 'Is my data secure?',
        'a':
            'Yes. All API requests use SSL/TLS encryption, JWT authentication with auto-expiry, and fine-grained access control.',
      },
    ];

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text(
          context.tr('help_support'),
          style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 18),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, size: 20),
          onPressed: () => context.pop(),
        ),
      ),
      body: ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: faqs.length,
        separatorBuilder: (_, __) => const SizedBox(height: 12),
        itemBuilder: (context, index) {
          final item = faqs[index];
          return AppCard(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      padding: const EdgeInsets.all(6),
                      decoration: const BoxDecoration(
                        color: AppColors.primaryContainer,
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.question_mark_rounded,
                          size: 14, color: AppColors.primary),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        item['q']!,
                        style: const TextStyle(
                          fontSize: 14.5,
                          fontWeight: FontWeight.bold,
                          color: AppColors.textPrimary,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                Padding(
                  padding: const EdgeInsets.only(left: 30),
                  child: Text(
                    item['a']!,
                    style: const TextStyle(
                      fontSize: 13.5,
                      color: AppColors.textSecondary,
                      height: 1.4,
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
