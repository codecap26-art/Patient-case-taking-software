import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'app.dart';
import 'core/network/api_client.dart';
import 'core/storage/token_storage.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Set preferred portrait orientation & modern system overlays
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);

  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
      systemNavigationBarColor: Colors.white,
      systemNavigationBarIconBrightness: Brightness.dark,
    ),
  );

  // Initialize Core Services
  final tokenStorage = await TokenStorage.getInstance();
  final apiClient = ApiClient(tokenStorage: tokenStorage);

  runApp(
    PatientApp(
      tokenStorage: tokenStorage,
      apiClient: apiClient,
    ),
  );
}
