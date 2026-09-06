import 'package:flutter/material.dart';
import '../storage/token_storage.dart';
import 'strings/en_strings.dart';
import 'strings/ta_strings.dart';
import 'strings/hi_strings.dart';

class AppLocalizations extends ChangeNotifier {
  final TokenStorage _tokenStorage;
  Locale _currentLocale = const Locale('en');

  AppLocalizations(this._tokenStorage) {
    _loadSavedLocale();
  }

  Locale get currentLocale => _currentLocale;

  static const List<Locale> supportedLocales = [
    Locale('en'),
    Locale('ta'),
    Locale('hi'),
  ];

  static const Map<String, String> languageNames = {
    'en': 'English',
    'ta': 'தமிழ் (Tamil)',
    'hi': 'हिन्दी (Hindi)',
  };

  void _loadSavedLocale() {
    final code = _tokenStorage.getLocale();
    _currentLocale = Locale(code);
  }

  Future<void> changeLocale(String languageCode) async {
    if (_currentLocale.languageCode == languageCode) return;
    _currentLocale = Locale(languageCode);
    await _tokenStorage.saveLocale(languageCode);
    notifyListeners();
  }

  String translate(String key) {
    switch (_currentLocale.languageCode) {
      case 'ta':
        return taStrings[key] ?? enStrings[key] ?? key;
      case 'hi':
        return hiStrings[key] ?? enStrings[key] ?? key;
      case 'en':
      default:
        return enStrings[key] ?? key;
    }
  }

  String t(String key) => translate(key);
}

extension LocalizationExtension on BuildContext {
  String tr(String key) {
    try {
      final loc = AppLocalizationsProvider.of(this);
      return loc?.translate(key) ?? key;
    } catch (_) {
      return key;
    }
  }
}

class AppLocalizationsProvider extends InheritedNotifier<AppLocalizations> {
  const AppLocalizationsProvider({
    super.key,
    required AppLocalizations localizations,
    required super.child,
  }) : super(notifier: localizations);

  static AppLocalizations? of(BuildContext context) {
    return context
        .dependOnInheritedWidgetOfExactType<AppLocalizationsProvider>()
        ?.notifier;
  }
}
