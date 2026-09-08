import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../../../config/theme/app_colors.dart';
import '../../../../core/localization/app_localizations.dart';
import '../../../../shared/models/medical_record_model.dart';
import '../../../../shared/widgets/app_card.dart';
import '../../../../shared/widgets/empty_state_view.dart';
import '../../../../shared/widgets/status_badge.dart';
import '../../state/history_notifier.dart';

class MedicalHistoryScreen extends StatefulWidget {
  const MedicalHistoryScreen({super.key});

  @override
  State<MedicalHistoryScreen> createState() => _MedicalHistoryScreenState();
}

class _MedicalHistoryScreenState extends State<MedicalHistoryScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<HistoryNotifier>().fetchHistory();
    });
  }

  @override
  Widget build(BuildContext context) {
    final historyNotifier = context.watch<HistoryNotifier>();
    final grouped = historyNotifier.groupedByYear;
    final isLoading = historyNotifier.isLoading;
    final selectedFilter = historyNotifier.selectedSourceFilter;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text(
          context.tr('medical_history'),
          style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 18),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, size: 20),
          onPressed: () => context.pop(),
        ),
      ),
      body: Column(
        children: [
          // Filter Tabs (All, Current System, Uploaded, External)
          Container(
            height: 52,
            padding: const EdgeInsets.symmetric(vertical: 8),
            color: AppColors.surface,
            child: ListView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              children: [
                _buildFilterChip('All Records', null, selectedFilter == null, historyNotifier),
                const SizedBox(width: 8),
                _buildFilterChip(
                  context.tr('source_system'),
                  RecordSource.currentSystem,
                  selectedFilter == RecordSource.currentSystem,
                  historyNotifier,
                ),
                const SizedBox(width: 8),
                _buildFilterChip(
                  context.tr('source_uploaded'),
                  RecordSource.uploadedDocument,
                  selectedFilter == RecordSource.uploadedDocument,
                  historyNotifier,
                ),
                const SizedBox(width: 8),
                _buildFilterChip(
                  context.tr('source_external'),
                  RecordSource.externalHospital,
                  selectedFilter == RecordSource.externalHospital,
                  historyNotifier,
                ),
              ],
            ),
          ),
          const Divider(height: 1),

          // Timeline Content
          Expanded(
            child: isLoading
                ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
                : grouped.isEmpty
                    ? const EmptyStateView(
                        icon: Icons.history_toggle_off_rounded,
                        title: 'No Medical Records Found',
                        message: 'No health records match the selected source filter.',
                      )
                    : RefreshIndicator(
                        onRefresh: () => context.read<HistoryNotifier>().fetchHistory(),
                        color: AppColors.primary,
                        child: ListView.builder(
                          padding: const EdgeInsets.fromLTRB(16, 16, 16, 32),
                          itemCount: grouped.keys.length,
                          itemBuilder: (context, index) {
                            final year = grouped.keys.elementAt(index);
                            final recordsInYear = grouped[year]!;

                            return Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                // Year Header Badge
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: 14, vertical: 6),
                                  decoration: BoxDecoration(
                                    color: AppColors.textPrimary,
                                    borderRadius: BorderRadius.circular(20),
                                  ),
                                  child: Text(
                                    year,
                                    style: const TextStyle(
                                      fontSize: 14,
                                      fontWeight: FontWeight.bold,
                                      color: Colors.white,
                                    ),
                                  ),
                                ),
                                const SizedBox(height: 12),

                                // Timeline Items in this year
                                ...recordsInYear.map((rec) => _buildTimelineCard(rec)),
                                const SizedBox(height: 16),
                              ],
                            );
                          },
                        ),
                      ),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterChip(
    String label,
    RecordSource? source,
    bool isSelected,
    HistoryNotifier notifier,
  ) {
    return ChoiceChip(
      label: Text(label),
      selected: isSelected,
      selectedColor: AppColors.primaryContainer,
      labelStyle: TextStyle(
        fontSize: 12.5,
        fontWeight: FontWeight.w600,
        color: isSelected ? AppColors.primary : AppColors.textSecondary,
      ),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
        side: BorderSide(
          color: isSelected ? AppColors.primary : AppColors.outline,
        ),
      ),
      onSelected: (_) => notifier.filterBySource(source),
    );
  }

  Widget _buildTimelineCard(MedicalRecordModel record) {
    return Padding(
      padding: const EdgeInsets.only(left: 12, bottom: 12),
      child: IntrinsicHeight(
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Timeline line + node
            Column(
              children: [
                Container(
                  width: 14,
                  height: 14,
                  decoration: BoxDecoration(
                    color: AppColors.primary,
                    shape: BoxShape.circle,
                    border: Border.all(color: Colors.white, width: 2),
                    boxShadow: [
                      BoxShadow(
                        color: AppColors.primary.withOpacity(0.4),
                        blurRadius: 4,
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: Container(
                    width: 2,
                    color: AppColors.outline,
                  ),
                ),
              ],
            ),
            const SizedBox(width: 14),

            // Card Body
            Expanded(
              child: AppCard(
                padding: const EdgeInsets.all(16),
                onTap: () => context.push('/medical-history/${record.id}'),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          record.date,
                          style: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: AppColors.textTertiary,
                          ),
                        ),
                        StatusBadge.recordSource(record.source),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      record.title,
                      style: const TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      record.provider,
                      style: const TextStyle(
                        fontSize: 12.5,
                        fontWeight: FontWeight.w500,
                        color: AppColors.primary,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      record.summary,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        fontSize: 13,
                        color: AppColors.textSecondary,
                        height: 1.35,
                      ),
                    ),
                    const SizedBox(height: 10),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        Text(
                          context.tr('view_details'),
                          style: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: AppColors.primary,
                          ),
                        ),
                        const Icon(Icons.chevron_right, size: 16, color: AppColors.primary),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
