import 'package:flutter/material.dart';

/// Design tokens and harmonious healthcare color palette
class AppColors {
  AppColors._();

  // Primary Palette - Modern Medical Teal & Cyan
  static const Color primary = Color(0xFF00897B); // Teal 600
  static const Color primaryDark = Color(0xFF005B4F);
  static const Color primaryLight = Color(0xFF4EBAAA);
  static const Color primaryContainer = Color(0xFFE0F2F1);
  static const Color onPrimaryContainer = Color(0xFF004D40);

  // Secondary Palette - Calming Healthcare Sapphire Blue
  static const Color secondary = Color(0xFF0284C7); // Sky 600
  static const Color secondaryContainer = Color(0xFFE0F2FE);
  static const Color onSecondaryContainer = Color(0xFF0369A1);

  // Accent / Status Colors
  static const Color success = Color(0xFF10B981); // Emerald
  static const Color successContainer = Color(0xFFD1FAE5);
  static const Color warning = Color(0xFFF59E0B); // Amber
  static const Color warningContainer = Color(0xFFFEF3C7);
  static const Color error = Color(0xFFEF4444); // Red 500
  static const Color errorContainer = Color(0xFFFEE2E2);
  static const Color info = Color(0xFF3B82F6); // Blue 500
  static const Color infoContainer = Color(0xFFDBEAFE);

  // Document & History Source Badges
  static const Color sourceSystem = Color(0xFF6366F1); // Indigo
  static const Color sourceSystemBg = Color(0xFFEEF2FF);
  static const Color sourceUploaded = Color(0xFF0D9488); // Teal
  static const Color sourceUploadedBg = Color(0xFFCCFBF1);
  static const Color sourceExternal = Color(0xFF8B5CF6); // Purple
  static const Color sourceExternalBg = Color(0xFFF3E8FF);

  // Neutral Colors - Clean Light Healthcare Aesthetic
  static const Color background = Color(0xFFF8FAFC); // Slate 50
  static const Color surface = Color(0xFFFFFFFF);
  static const Color surfaceVariant = Color(0xFFF1F5F9);
  static const Color outline = Color(0xFFE2E8F0);
  static const Color outlineLight = Color(0xFFF1F5F9);

  // Typography Colors
  static const Color textPrimary = Color(0xFF0F172A); // Slate 900
  static const Color textSecondary = Color(0xFF475569); // Slate 600
  static const Color textTertiary = Color(0xFF94A3B8); // Slate 400
  static const Color textWhite = Color(0xFFFFFFFF);

  // Shadows
  static const List<BoxShadow> softShadow = [
    BoxShadow(
      color: Color(0x0A0F172A),
      blurRadius: 10,
      offset: Offset(0, 4),
      spreadRadius: 0,
    ),
  ];

  static const List<BoxShadow> mediumShadow = [
    BoxShadow(
      color: Color(0x140F172A),
      blurRadius: 16,
      offset: Offset(0, 6),
      spreadRadius: -2,
    ),
  ];
}
