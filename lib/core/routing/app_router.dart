import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../features/splash/presentation/screens/splash_screen.dart';
import '../../features/auth/presentation/screens/login_screen.dart';
import '../../features/auth/presentation/screens/otp_screen.dart';
import '../../features/auth/presentation/screens/register_screen.dart';
import '../../features/home/presentation/screens/home_dashboard_screen.dart';
import '../../features/documents/presentation/screens/documents_list_screen.dart';
import '../../features/documents/presentation/screens/upload_document_screen.dart';
import '../../features/documents/presentation/screens/document_detail_screen.dart';
import '../../features/medical_history/presentation/screens/medical_history_screen.dart';
import '../../features/medical_history/presentation/screens/record_detail_screen.dart';
import '../../features/prescriptions/presentation/screens/prescriptions_list_screen.dart';
import '../../features/prescriptions/presentation/screens/prescription_detail_screen.dart';
import '../../features/consultations/presentation/screens/consultations_list_screen.dart';
import '../../features/consultations/presentation/screens/consultation_detail_screen.dart';
import '../../features/qr/presentation/screens/patient_qr_screen.dart';
import '../../features/consent/presentation/screens/consent_access_screen.dart';
import '../../features/notifications/presentation/screens/notifications_screen.dart';
import '../../features/profile/presentation/screens/profile_screen.dart';
import '../../features/profile/presentation/screens/edit_profile_screen.dart';
import '../../features/settings/presentation/screens/settings_screen.dart';
import '../../features/settings/presentation/screens/language_selection_screen.dart';
import '../../features/settings/presentation/screens/help_faq_screen.dart';
import '../../shared/widgets/app_shell_scaffold.dart';
import 'route_names.dart';

final GlobalKey<NavigatorState> _rootNavigatorKey =
    GlobalKey<NavigatorState>(debugLabel: 'root');
final GlobalKey<NavigatorState> _homeNavigatorKey =
    GlobalKey<NavigatorState>(debugLabel: 'homeNav');
final GlobalKey<NavigatorState> _recordsNavigatorKey =
    GlobalKey<NavigatorState>(debugLabel: 'recordsNav');
final GlobalKey<NavigatorState> _rxNavigatorKey =
    GlobalKey<NavigatorState>(debugLabel: 'rxNav');
final GlobalKey<NavigatorState> _notifNavigatorKey =
    GlobalKey<NavigatorState>(debugLabel: 'notifNav');
final GlobalKey<NavigatorState> _profileNavigatorKey =
    GlobalKey<NavigatorState>(debugLabel: 'profileNav');

class AppRouter {
  AppRouter._();

  static final GoRouter router = GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: RouteNames.splash,
    debugLogDiagnostics: false,
    routes: [
      // Splash Screen
      GoRoute(
        path: RouteNames.splash,
        builder: (context, state) => const SplashScreen(),
      ),

      // Auth Routes
      GoRoute(
        path: RouteNames.login,
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: RouteNames.otp,
        builder: (context, state) => const OtpScreen(),
      ),
      GoRoute(
        path: RouteNames.register,
        builder: (context, state) => const RegisterScreen(),
      ),

      // Stateful Bottom Navigation Shell (5 Branches)
      StatefulShellRoute.indexedStack(
        builder: (context, state, navigationShell) {
          return AppShellScaffold(navigationShell: navigationShell);
        },
        branches: [
          // Branch 0: Home Dashboard
          StatefulShellBranch(
            navigatorKey: _homeNavigatorKey,
            routes: [
              GoRoute(
                path: RouteNames.home,
                builder: (context, state) => const HomeDashboardScreen(),
              ),
            ],
          ),

          // Branch 1: Records
          StatefulShellBranch(
            navigatorKey: _recordsNavigatorKey,
            routes: [
              GoRoute(
                path: RouteNames.records,
                builder: (context, state) => const DocumentsListScreen(),
              ),
            ],
          ),

          // Branch 2: Prescriptions
          StatefulShellBranch(
            navigatorKey: _rxNavigatorKey,
            routes: [
              GoRoute(
                path: RouteNames.prescriptions,
                builder: (context, state) => const PrescriptionsListScreen(),
              ),
            ],
          ),

          // Branch 3: Notifications
          StatefulShellBranch(
            navigatorKey: _notifNavigatorKey,
            routes: [
              GoRoute(
                path: RouteNames.notifications,
                builder: (context, state) => const NotificationsScreen(),
              ),
            ],
          ),

          // Branch 4: Profile
          StatefulShellBranch(
            navigatorKey: _profileNavigatorKey,
            routes: [
              GoRoute(
                path: RouteNames.profile,
                builder: (context, state) => const ProfileScreen(),
              ),
            ],
          ),
        ],
      ),

      // Push Screens (Over the Shell)
      GoRoute(
        parentNavigatorKey: _rootNavigatorKey,
        path: RouteNames.editProfile,
        builder: (context, state) => const EditProfileScreen(),
      ),
      GoRoute(
        parentNavigatorKey: _rootNavigatorKey,
        path: RouteNames.qr,
        builder: (context, state) => const PatientQrScreen(),
      ),
      GoRoute(
        parentNavigatorKey: _rootNavigatorKey,
        path: RouteNames.uploadDocument,
        builder: (context, state) => const UploadDocumentScreen(),
      ),
      GoRoute(
        parentNavigatorKey: _rootNavigatorKey,
        path: RouteNames.documentDetail,
        builder: (context, state) {
          final id = state.pathParameters['id'] ?? '';
          return DocumentDetailScreen(documentId: id);
        },
      ),
      GoRoute(
        parentNavigatorKey: _rootNavigatorKey,
        path: RouteNames.medicalHistory,
        builder: (context, state) => const MedicalHistoryScreen(),
      ),
      GoRoute(
        parentNavigatorKey: _rootNavigatorKey,
        path: RouteNames.recordDetail,
        builder: (context, state) {
          final id = state.pathParameters['id'] ?? '';
          return RecordDetailScreen(recordId: id);
        },
      ),
      GoRoute(
        parentNavigatorKey: _rootNavigatorKey,
        path: RouteNames.prescriptionDetail,
        builder: (context, state) {
          final id = state.pathParameters['id'] ?? '';
          return PrescriptionDetailScreen(prescriptionId: id);
        },
      ),
      GoRoute(
        parentNavigatorKey: _rootNavigatorKey,
        path: RouteNames.consultations,
        builder: (context, state) => const ConsultationsListScreen(),
      ),
      GoRoute(
        parentNavigatorKey: _rootNavigatorKey,
        path: RouteNames.consultationDetail,
        builder: (context, state) {
          final id = state.pathParameters['id'] ?? '';
          return ConsultationDetailScreen(consultationId: id);
        },
      ),
      GoRoute(
        parentNavigatorKey: _rootNavigatorKey,
        path: RouteNames.consentAccess,
        builder: (context, state) => const ConsentAccessScreen(),
      ),
      GoRoute(
        parentNavigatorKey: _rootNavigatorKey,
        path: RouteNames.settings,
        builder: (context, state) => const SettingsScreen(),
      ),
      GoRoute(
        parentNavigatorKey: _rootNavigatorKey,
        path: RouteNames.languageSelection,
        builder: (context, state) => const LanguageSelectionScreen(),
      ),
      GoRoute(
        parentNavigatorKey: _rootNavigatorKey,
        path: RouteNames.helpFaq,
        builder: (context, state) => const HelpFaqScreen(),
      ),
    ],
  );
}
