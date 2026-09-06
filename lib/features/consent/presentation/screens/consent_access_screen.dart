import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../../../config/theme/app_colors.dart';
import '../../../../core/localization/app_localizations.dart';
import '../../../../shared/models/consent_request_model.dart';
import '../../../../shared/widgets/app_card.dart';
import '../../../../shared/widgets/custom_button.dart';
import '../../../../shared/widgets/empty_state_view.dart';
import '../../../../shared/widgets/status_badge.dart';
import '../state/consent_notifier.dart';

class ConsentAccessScreen extends StatefulWidget {
  const ConsentAccessScreen({super.key});

  @override
  State<ConsentAccessScreen> createState() => _ConsentAccessScreenState();
}

class _ConsentAccessScreenState extends State<ConsentAccessScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ConsentNotifier>().fetchConsentRequests();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  void _handleRespond(ConsentRequestModel req, bool allow) async {
    final consentNotifier = context.read<ConsentNotifier>();
    final actionName = allow ? 'allow' : 'deny';

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text(allow ? 'Allow Medical Record Access?' : 'Deny Access Request?'),
          content: Text(
            allow
                ? 'Are you sure you want to allow ${req.providerName} to access ${req.requestedScope}?'
                : 'Are you sure you want to deny ${req.providerName}\'s access request?',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () => Navigator.pop(context, true),
              style: ElevatedButton.styleFrom(
                backgroundColor: allow ? AppColors.primary : AppColors.error,
              ),
              child: Text(allow ? 'Allow Access' : 'Deny'),
            ),
          ],
        );
      },
    );

    if (confirmed == true) {
      final success = await consentNotifier.respond(req.id, allow);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            success ? 'Access request updated successfully' : 'Failed to update request',
          ),
          backgroundColor: allow ? AppColors.success : AppColors.error,
        ),
      );
    }
  }

  void _handleRevoke(ConsentRequestModel req) async {
    final consentNotifier = context.read<ConsentNotifier>();

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Revoke Active Access?'),
          content: Text(
            'This will immediately terminate ${req.providerName}\'s access to your medical records.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () => Navigator.pop(context, true),
              style: ElevatedButton.styleFrom(backgroundColor: AppColors.error),
              child: const Text('Revoke Now'),
            ),
          ],
        );
      },
    );

    if (confirmed == true) {
      final success = await consentNotifier.revoke(req.id);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            success ? 'Access revoked successfully' : 'Failed to revoke access',
          ),
          backgroundColor: AppColors.textPrimary,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final consentNotifier = context.watch<ConsentNotifier>();
    final pending = consentNotifier.pendingRequests;
    final active = consentNotifier.activeConsents;
    final history = consentNotifier.auditHistory;
    final isLoading = consentNotifier.isLoading;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text(
          context.tr('consent_and_access'),
          style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 18),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, size: 20),
          onPressed: () => context.pop(),
        ),
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: AppColors.primary,
          labelColor: AppColors.primary,
          unselectedLabelColor: AppColors.textSecondary,
          labelStyle: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
          tabs: [
            Tab(text: '${context.tr('pending_requests')} (${pending.length})'),
            Tab(text: '${context.tr('active_access')} (${active.length})'),
            Tab(text: context.tr('access_history')),
          ],
        ),
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
          : TabBarView(
              controller: _tabController,
              children: [
                // Tab 1: Pending Requests
                _buildPendingList(pending),

                // Tab 2: Active Permissions
                _buildActiveList(active),

                // Tab 3: History
                _buildHistoryList(history),
              ],
            ),
    );
  }

  Widget _buildPendingList(List<ConsentRequestModel> list) {
    if (list.isEmpty) {
      return const EmptyStateView(
        icon: Icons.shield_outlined,
        title: 'No Pending Consent Requests',
        message: 'Healthcare providers requesting record access will appear here for your explicit authorization.',
      );
    }

    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemCount: list.length,
      separatorBuilder: (_, __) => const SizedBox(height: 14),
      itemBuilder: (context, index) {
        final req = list[index];
        return AppCard(
          padding: const EdgeInsets.all(16),
          borderSide: const BorderSide(color: AppColors.warning, width: 1.2),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  StatusBadge.consentStatus(req.status),
                  Text(
                    req.requestDate,
                    style: const TextStyle(fontSize: 12, color: AppColors.textTertiary),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                req.providerName,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                ),
              ),
              if (req.doctorName != null) ...[
                const SizedBox(height: 2),
                Text(
                  'Requested by: ${req.doctorName}',
                  style: const TextStyle(
                    fontSize: 12.5,
                    color: AppColors.primary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
              const SizedBox(height: 10),
              const Divider(),
              const SizedBox(height: 8),
              _buildFieldRow('Requested Info:', req.requestedScope),
              const SizedBox(height: 6),
              _buildFieldRow('Purpose:', req.purpose),
              const SizedBox(height: 6),
              _buildFieldRow('Validity:', req.validUntil),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () => _handleRespond(req, false),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: AppColors.error,
                        side: const BorderSide(color: AppColors.error),
                        minimumSize: const Size.fromHeight(44),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                      child: Text(context.tr('deny')),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () => _handleRespond(req, true),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.primary,
                        foregroundColor: Colors.white,
                        minimumSize: const Size.fromHeight(44),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                      child: Text(context.tr('allow')),
                    ),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildActiveList(List<ConsentRequestModel> list) {
    if (list.isEmpty) {
      return const EmptyStateView(
        icon: Icons.lock_open_rounded,
        title: 'No Active Authorizations',
        message: 'You have not granted ongoing access to any healthcare facilities.',
      );
    }

    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemCount: list.length,
      separatorBuilder: (_, __) => const SizedBox(height: 14),
      itemBuilder: (context, index) {
        final req = list[index];
        return AppCard(
          padding: const EdgeInsets.all(16),
          borderSide: const BorderSide(color: AppColors.success, width: 1),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  StatusBadge.consentStatus(req.status),
                  Text(
                    'Granted: ${req.responseDate ?? req.requestDate}',
                    style: const TextStyle(fontSize: 12, color: AppColors.textTertiary),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                req.providerName,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                ),
              ),
              const SizedBox(height: 8),
              _buildFieldRow('Scope:', req.requestedScope),
              const SizedBox(height: 6),
              _buildFieldRow('Valid Until:', req.validUntil),
              const SizedBox(height: 14),
              CustomButton(
                text: context.tr('revoke'),
                variant: ButtonVariant.danger,
                height: 42,
                onPressed: () => _handleRevoke(req),
                icon: Icons.block,
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildHistoryList(List<ConsentRequestModel> list) {
    if (list.isEmpty) {
      return const EmptyStateView(
        icon: Icons.history_rounded,
        title: 'No Consent History',
        message: 'Your consent decision history and audit trails will appear here.',
      );
    }

    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemCount: list.length,
      separatorBuilder: (_, __) => const SizedBox(height: 12),
      itemBuilder: (context, index) {
        final req = list[index];
        return AppCard(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    req.providerName,
                    style: const TextStyle(
                      fontSize: 14.5,
                      fontWeight: FontWeight.bold,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  StatusBadge.consentStatus(req.status),
                ],
              ),
              const SizedBox(height: 6),
              Text(
                'Scope: ${req.requestedScope}',
                style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
              ),
              const SizedBox(height: 4),
              Text(
                'Date: ${req.requestDate}',
                style: const TextStyle(fontSize: 11, color: AppColors.textTertiary),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildFieldRow(String label, String value) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 100,
          child: Text(
            label,
            style: const TextStyle(
              fontSize: 12.5,
              fontWeight: FontWeight.w600,
              color: AppColors.textTertiary,
            ),
          ),
        ),
        Expanded(
          child: Text(
            value,
            style: const TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w500,
              color: AppColors.textPrimary,
            ),
          ),
        ),
      ],
    );
  }
}
