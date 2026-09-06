import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'config/app_config.dart';
import 'config/theme/app_theme.dart';
import 'core/localization/app_localizations.dart';
import 'core/network/api_client.dart';
import 'core/routing/app_router.dart';
import 'core/storage/token_storage.dart';
import 'features/auth/data/auth_service.dart';
import 'features/auth/state/auth_notifier.dart';
import 'features/home/state/home_notifier.dart';
import 'features/profile/state/profile_notifier.dart';
import 'features/documents/data/document_service.dart';
import 'features/documents/state/document_notifier.dart';
import 'features/medical_history/data/history_service.dart';
import 'features/medical_history/state/history_notifier.dart';
import 'features/prescriptions/data/prescription_service.dart';
import 'features/prescriptions/state/prescription_notifier.dart';
import 'features/consultations/data/consultation_service.dart';
import 'features/consultations/state/consultation_notifier.dart';
import 'features/consent/data/consent_service.dart';
import 'features/consent/state/consent_notifier.dart';
import 'features/notifications/data/notification_service.dart';
import 'features/notifications/state/notification_notifier.dart';

class PatientApp extends StatelessWidget {
  final TokenStorage tokenStorage;
  final ApiClient apiClient;

  const PatientApp({
    super.key,
    required this.tokenStorage,
    required this.apiClient,
  });

  @override
  Widget build(BuildContext context) {
    // Services
    final authService = AuthServiceImpl(
      apiClient: apiClient,
      tokenStorage: tokenStorage,
    );
    final documentService = DocumentServiceImpl(apiClient: apiClient);
    final historyService = HistoryServiceImpl(apiClient: apiClient);
    final prescriptionService = PrescriptionServiceImpl(apiClient: apiClient);
    final consultationService = ConsultationServiceImpl(apiClient: apiClient);
    final consentService = ConsentServiceImpl(apiClient: apiClient);
    final notificationService = NotificationServiceImpl(apiClient: apiClient);

    return MultiProvider(
      providers: [
        // App Localizations
        ChangeNotifierProvider<AppLocalizations>(
          create: (_) => AppLocalizations(tokenStorage),
        ),

        // Auth
        ChangeNotifierProvider<AuthNotifier>(
          create: (_) => AuthNotifier(
            authService: authService,
            tokenStorage: tokenStorage,
          ),
        ),

        // Home
        ChangeNotifierProvider<HomeNotifier>(
          create: (_) => HomeNotifier(),
        ),

        // Profile (depends on AuthNotifier)
        ChangeNotifierProxyProvider<AuthNotifier, ProfileNotifier>(
          create: (ctx) => ProfileNotifier(ctx.read<AuthNotifier>()),
          update: (_, auth, profile) => profile ?? ProfileNotifier(auth),
        ),

        // Documents
        ChangeNotifierProvider<DocumentNotifier>(
          create: (_) => DocumentNotifier(documentService),
        ),

        // Medical History
        ChangeNotifierProvider<HistoryNotifier>(
          create: (_) => HistoryNotifier(historyService),
        ),

        // Prescriptions
        ChangeNotifierProvider<PrescriptionNotifier>(
          create: (_) => PrescriptionNotifier(prescriptionService),
        ),

        // Consultations
        ChangeNotifierProvider<ConsultationNotifier>(
          create: (_) => ConsultationNotifier(consultationService),
        ),

        // Consent & Access Control
        ChangeNotifierProvider<ConsentNotifier>(
          create: (_) => ConsentNotifier(consentService),
        ),

        // Notifications
        ChangeNotifierProvider<NotificationNotifier>(
          create: (_) => NotificationNotifier(notificationService),
        ),
      ],
      child: Consumer<AppLocalizations>(
        builder: (context, localizations, _) {
          return AppLocalizationsProvider(
            localizations: localizations,
            child: MaterialApp.router(
              title: AppConfig.appName,
              debugShowCheckedModeBanner: false,
              theme: AppTheme.lightTheme,
              locale: localizations.currentLocale,
              supportedLocales: AppLocalizations.supportedLocales,
              routerConfig: AppRouter.router,
            ),
          );
        },
      ),
    );
  }
}
