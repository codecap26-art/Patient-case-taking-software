import 'package:flutter/material.dart';
import '../../config/theme/app_colors.dart';

enum ButtonVariant { primary, secondary, outline, text, danger }

class CustomButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final bool isLoading;
  final IconData? icon;
  final ButtonVariant variant;
  final double? width;
  final double height;
  final double borderRadius;

  const CustomButton({
    super.key,
    required this.text,
    this.onPressed,
    this.isLoading = false,
    this.icon,
    this.variant = ButtonVariant.primary,
    this.width,
    this.height = 52,
    this.borderRadius = 12,
  });

  @override
  Widget build(BuildContext context) {
    Color getBackgroundColor() {
      switch (variant) {
        case ButtonVariant.primary:
          return AppColors.primary;
        case ButtonVariant.secondary:
          return AppColors.secondary;
        case ButtonVariant.danger:
          return AppColors.error;
        case ButtonVariant.outline:
        case ButtonVariant.text:
          return Colors.transparent;
      }
    }

    Color getForegroundColor() {
      switch (variant) {
        case ButtonVariant.primary:
        case ButtonVariant.secondary:
        case ButtonVariant.danger:
          return Colors.white;
        case ButtonVariant.outline:
          return AppColors.primary;
        case ButtonVariant.text:
          return AppColors.primary;
      }
    }

    BorderSide? getBorderSide() {
      if (variant == ButtonVariant.outline) {
        return const BorderSide(color: AppColors.primary, width: 1.5);
      }
      return BorderSide.none;
    }

    return SizedBox(
      width: width ?? double.infinity,
      height: height,
      child: ElevatedButton(
        onPressed: isLoading ? null : onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: getBackgroundColor(),
          foregroundColor: getForegroundColor(),
          disabledBackgroundColor: AppColors.textTertiary.withOpacity(0.3),
          disabledForegroundColor: Colors.white,
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(borderRadius),
            side: getBorderSide() ?? BorderSide.none,
          ),
          padding: const EdgeInsets.symmetric(horizontal: 20),
        ),
        child: isLoading
            ? const SizedBox(
                height: 22,
                width: 22,
                child: CircularProgressIndicator(
                  strokeWidth: 2.5,
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                ),
              )
            : Row(
                mainAxisAlignment: MainAxisAlignment.center,
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (icon != null) ...[
                    Icon(icon, size: 20, color: getForegroundColor()),
                    const SizedBox(width: 8),
                  ],
                  Text(
                    text,
                    style: TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w600,
                      color: getForegroundColor(),
                    ),
                  ),
                ],
              ),
      ),
    );
  }
}
