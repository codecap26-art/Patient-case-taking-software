import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../../config/theme/app_colors.dart';
import '../../../../core/localization/app_localizations.dart';
import '../../../../shared/widgets/app_card.dart';

class LanguageSelectionScreen extends StatelessWidget {
  const LanguageSelectionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final locProvider = AppLocalizationsProvider.of(context);
    final currentCode = locProvider?.currentLocale.languageCode ?? 'en';

    final languages = [
      {'code': 'en', 'title': 'English', 'native': 'English'},
      {'code': 'ta', 'title': 'Tamil', 'native': 'தமிழ்'},
      {'code': 'hi', 'title': 'Hindi', 'native': 'हिन्दी'},
    ];

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text(
          context.tr('language'),
          style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 18),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, size: 20),
          onPressed: () => context.pop(),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Select Preferred Language',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: AppColors.textPrimary,
              ),
            ),
            const SizedBox(height: 6),
            const Text(
              'Choose your language for application text and case summary views.',
              style: TextStyle(
                fontSize: 13,
                color: AppColors.textSecondary,
              ),
            ),
            const SizedBox(height: 20),
            ListView.separated(
              shrinkWrap: true,
              itemCount: languages.length,
              separatorBuilder: (_, __) => const SizedBox(height: 12),
              itemBuilder: (context, index) {
                final lang = languages[index];
                final isSelected = currentCode == lang['code'];

                return AppCard(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                  borderSide: BorderSide(
                    color: isSelected ? AppColors.primary : AppColors.outline,
                    width: isSelected ? 2 : 1,
                  ),
                  onTap: () async {
                    await locProvider?.changeLocale(lang['code']!);
                  },
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            lang['native']!,
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: isSelected ? AppColors.primary : AppColors.textPrimary,
                            ),
                          ),
                          Text(
                            lang['title']!,
                            style: const TextStyle(
                              fontSize: 12,
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ],
                      ),
                      if (isSelected)
                        const Icon(Icons.check_circle, color: AppColors.primary, size: 22)
                      else
                        const Icon(Icons.radio_button_unchecked,
                            color: AppColors.textTertiary, size: 22),
                    ],
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}
