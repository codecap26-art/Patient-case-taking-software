import 'package:flutter/material.dart';
import '../../../../config/theme/app_colors.dart';
import '../../../../core/localization/app_localizations.dart';
import '../../../../shared/models/patient_model.dart';
import '../../../../shared/widgets/app_card.dart';

class HealthSummaryCard extends StatelessWidget {
  final PatientModel patient;

  const HealthSummaryCard({super.key, required this.patient});

  @override
  Widget build(BuildContext context) {
    return AppCard(
      padding: const EdgeInsets.all(20),
      backgroundColor: AppColors.surface,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                context.tr('quick_health_summary'),
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w700,
                  color: AppColors.textPrimary,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: AppColors.primaryContainer,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  'ID: ${patient.id}',
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    color: AppColors.primary,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              // Blood Group Item
              Expanded(
                child: _buildMetricTile(
                  icon: Icons.water_drop_rounded,
                  iconColor: AppColors.error,
                  bgColor: AppColors.errorContainer,
                  title: 'Blood Group',
                  value: patient.bloodGroup,
                ),
              ),
              const SizedBox(width: 12),
              // Known Allergies Item
              Expanded(
                child: _buildMetricTile(
                  icon: Icons.shield_outlined,
                  iconColor: AppColors.warning,
                  bgColor: AppColors.warningContainer,
                  title: 'Allergies',
                  value: patient.allergies.isNotEmpty
                      ? '${patient.allergies.length} Recorded'
                      : 'None Noted',
                ),
              ),
              const SizedBox(width: 12),
              // Chronic Conditions
              Expanded(
                child: _buildMetricTile(
                  icon: Icons.favorite_border_rounded,
                  iconColor: AppColors.secondary,
                  bgColor: AppColors.secondaryContainer,
                  title: 'Conditions',
                  value: patient.chronicConditions.isNotEmpty
                      ? '${patient.chronicConditions.length} Active'
                      : 'None',
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMetricTile({
    required IconData icon,
    required Color iconColor,
    required Color bgColor,
    required String title,
    required String value,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
      decoration: BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.outlineLight),
      ),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: bgColor,
              shape: BoxShape.circle,
            ),
            child: Icon(icon, size: 18, color: iconColor),
          ),
          const SizedBox(height: 8),
          Text(
            title,
            style: const TextStyle(
              fontSize: 11,
              color: AppColors.textTertiary,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            value,
            textAlign: TextAlign.center,
            style: const TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w700,
              color: AppColors.textPrimary,
            ),
          ),
        ],
      ),
    );
  }
}
