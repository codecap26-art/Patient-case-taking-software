import 'package:flutter/material.dart';
import '../../config/theme/app_colors.dart';
import '../models/document_model.dart';
import '../models/medical_record_model.dart';
import '../models/consent_request_model.dart';

class StatusBadge extends StatelessWidget {
  final String label;
  final Color textColor;
  final Color backgroundColor;
  final IconData? icon;

  const StatusBadge({
    super.key,
    required this.label,
    required this.textColor,
    required this.backgroundColor,
    this.icon,
  });

  factory StatusBadge.documentStatus(DocumentStatus status) {
    switch (status) {
      case DocumentStatus.uploading:
        return const StatusBadge(
          label: 'Uploading',
          textColor: AppColors.info,
          backgroundColor: AppColors.infoContainer,
          icon: Icons.cloud_upload_outlined,
        );
      case DocumentStatus.processing:
        return const StatusBadge(
          label: 'Processing',
          textColor: AppColors.warning,
          backgroundColor: AppColors.warningContainer,
          icon: Icons.sync_outlined,
        );
      case DocumentStatus.extracted:
        return const StatusBadge(
          label: 'Extracted',
          textColor: AppColors.primary,
          backgroundColor: AppColors.primaryContainer,
          icon: Icons.auto_awesome,
        );
      case DocumentStatus.available:
        return const StatusBadge(
          label: 'Available',
          textColor: AppColors.success,
          backgroundColor: AppColors.successContainer,
          icon: Icons.check_circle_outline,
        );
      case DocumentStatus.failed:
        return const StatusBadge(
          label: 'Failed',
          textColor: AppColors.error,
          backgroundColor: AppColors.errorContainer,
          icon: Icons.error_outline,
        );
    }
  }

  factory StatusBadge.recordSource(RecordSource source) {
    switch (source) {
      case RecordSource.currentSystem:
        return const StatusBadge(
          label: 'Current System',
          textColor: AppColors.sourceSystem,
          backgroundColor: AppColors.sourceSystemBg,
          icon: Icons.verified_outlined,
        );
      case RecordSource.uploadedDocument:
        return const StatusBadge(
          label: 'Uploaded Doc',
          textColor: AppColors.sourceUploaded,
          backgroundColor: AppColors.sourceUploadedBg,
          icon: Icons.file_present_outlined,
        );
      case RecordSource.externalHospital:
        return const StatusBadge(
          label: 'External Hospital',
          textColor: AppColors.sourceExternal,
          backgroundColor: AppColors.sourceExternalBg,
          icon: Icons.local_hospital_outlined,
        );
    }
  }

  factory StatusBadge.consentStatus(ConsentStatus status) {
    switch (status) {
      case ConsentStatus.pending:
        return const StatusBadge(
          label: 'Pending Consent',
          textColor: AppColors.warning,
          backgroundColor: AppColors.warningContainer,
          icon: Icons.pending_actions_outlined,
        );
      case ConsentStatus.allowed:
        return const StatusBadge(
          label: 'Access Allowed',
          textColor: AppColors.success,
          backgroundColor: AppColors.successContainer,
          icon: Icons.check_circle_outline,
        );
      case ConsentStatus.denied:
        return const StatusBadge(
          label: 'Denied',
          textColor: AppColors.error,
          backgroundColor: AppColors.errorContainer,
          icon: Icons.cancel_outlined,
        );
      case ConsentStatus.revoked:
        return const StatusBadge(
          label: 'Access Revoked',
          textColor: AppColors.textTertiary,
          backgroundColor: AppColors.surfaceVariant,
          icon: Icons.block_outlined,
        );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            Icon(icon, size: 13, color: textColor),
            const SizedBox(width: 4),
          ],
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: textColor,
            ),
          ),
        ],
      ),
    );
  }
}
