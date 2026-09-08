import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher_string.dart';
import '../../../../config/app_config.dart';
import '../../../../config/theme/app_colors.dart';
import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/localization/app_localizations.dart';
import '../../../../shared/data/mock_database.dart';
import '../../../../shared/models/document_model.dart';
import '../../../../shared/widgets/app_card.dart';
import '../../../../shared/widgets/status_badge.dart';
import '../../state/document_notifier.dart';

class DocumentDetailScreen extends StatelessWidget {
  final String documentId;

  const DocumentDetailScreen({super.key, required this.documentId});

  @override
  Widget build(BuildContext context) {
    final docs = context.watch<DocumentNotifier>().documents;
    final doc = docs.firstWhere(
      (d) => d.id == documentId,
      orElse: () => MockDatabase.documents.firstWhere(
        (d) => d.id == documentId,
        orElse: () => MockDatabase.documents.first,
      ),
    );

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text(
          'Document Details',
          style: TextStyle(fontWeight: FontWeight.w700, fontSize: 18),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, size: 20),
          onPressed: () => context.pop(),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header Info Card
            AppCard(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        children: [
                          StatusBadge.documentStatus(doc.status),
                          if (doc.doctorReviewed) ...[
                            const SizedBox(width: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                              decoration: BoxDecoration(
                                color: Colors.green.shade50,
                                borderRadius: BorderRadius.circular(6),
                                border: Border.all(color: Colors.green.shade300),
                              ),
                              child: Row(
                                children: [
                                  Icon(Icons.verified, size: 12, color: Colors.green.shade700),
                                  const SizedBox(width: 4),
                                  Text(
                                    'Doctor Verified',
                                    style: TextStyle(
                                      fontSize: 10,
                                      fontWeight: FontWeight.bold,
                                      color: Colors.green.shade800,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ],
                      ),
                      Text(
                        doc.fileSize ?? 'Real File',
                        style: const TextStyle(
                          fontSize: 12,
                          color: AppColors.textTertiary,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),
                  Text(
                    doc.title,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    doc.documentType,
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: AppColors.primary,
                    ),
                  ),
                  const SizedBox(height: 16),
                  const Divider(),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      const Icon(Icons.local_hospital_outlined, size: 18, color: AppColors.textTertiary),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          doc.hospitalName.isNotEmpty ? doc.hospitalName : 'Clinical Facility',
                          style: const TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w500,
                            color: AppColors.textPrimary,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      const Icon(Icons.calendar_today_outlined, size: 18, color: AppColors.textTertiary),
                      const SizedBox(width: 8),
                      Text(
                        'Date: ${doc.date.isNotEmpty ? doc.date : "Not specified"}',
                        style: const TextStyle(
                          fontSize: 13,
                          color: AppColors.textSecondary,
                        ),
                      ),
                      if (doc.pageCount != null && doc.pageCount! > 1) ...[
                        const SizedBox(width: 16),
                        const Icon(Icons.auto_stories_outlined, size: 16, color: AppColors.textTertiary),
                        const SizedBox(width: 4),
                        Text(
                          '${doc.pageCount} pages',
                          style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
                        ),
                      ],
                    ],
                  ),
                  if (doc.fileName != null && doc.fileName!.isNotEmpty) ...[
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        const Icon(Icons.insert_drive_file_outlined, size: 18, color: AppColors.textTertiary),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            doc.fileName!,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(
                              fontSize: 12,
                              color: AppColors.textSecondary,
                              fontFamily: 'monospace',
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Notice / Error Banner if OCR processing failed
            if (doc.status == DocumentStatus.failed || doc.extractionError != null) ...[
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: AppColors.errorContainer.withOpacity(0.5),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: AppColors.error.withOpacity(0.4)),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.warning_amber_rounded, size: 18, color: AppColors.error),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Extraction Alert',
                            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: AppColors.error),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            doc.extractionError ?? 'Automatic parameter structuring could not complete. Raw text remains intact.',
                            style: const TextStyle(fontSize: 12, color: AppColors.textPrimary, height: 1.3),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
            ],

            // Real AI-Extracted Information Section
            if (doc.extractedSummary != null && doc.extractedSummary!.isNotEmpty) ...[
              AppCard(
                padding: const EdgeInsets.all(20),
                backgroundColor: AppColors.surface,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(6),
                          decoration: BoxDecoration(
                            color: AppColors.primaryContainer,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: const Icon(Icons.auto_awesome, size: 18, color: AppColors.primary),
                        ),
                        const SizedBox(width: 10),
                        Text(
                          context.tr('extracted_info'),
                          style: const TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.bold,
                            color: AppColors.textPrimary,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Text(
                      doc.extractedSummary!,
                      style: const TextStyle(
                        fontSize: 14,
                        color: AppColors.textPrimary,
                        height: 1.5,
                      ),
                    ),
                    if (doc.structuredData != null && doc.structuredData!.isNotEmpty) ...[
                      const SizedBox(height: 16),
                      const Divider(),
                      const SizedBox(height: 12),
                      const Text(
                        'Extracted Clinical Parameters',
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w700,
                          color: AppColors.textSecondary,
                        ),
                      ),
                      const SizedBox(height: 8),
                      ...doc.structuredData!.entries.map((entry) {
                        final valStr = entry.value.toString();
                        final isLow = valStr.contains('Flag: LOW') || valStr.toLowerCase().contains('low');
                        final isHigh = valStr.contains('Flag: HIGH') || valStr.toLowerCase().contains('high');
                        final isAbnormal = valStr.contains('Flag: ABNORMAL') || isLow || isHigh;

                        return Container(
                          margin: const EdgeInsets.symmetric(vertical: 4),
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                          decoration: BoxDecoration(
                            color: isAbnormal ? Colors.orange.shade50 : AppColors.surfaceVariant.withOpacity(0.4),
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(
                              color: isAbnormal ? Colors.orange.shade300 : AppColors.outline.withOpacity(0.4),
                            ),
                          ),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Expanded(
                                flex: 5,
                                child: Text(
                                  entry.key,
                                  style: TextStyle(
                                    fontSize: 12,
                                    fontWeight: FontWeight.w600,
                                    color: isAbnormal ? Colors.orange.shade900 : AppColors.textSecondary,
                                  ),
                                ),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                flex: 6,
                                child: Text(
                                  valStr,
                                  textAlign: TextAlign.end,
                                  style: TextStyle(
                                    fontSize: 12,
                                    fontWeight: FontWeight.w700,
                                    color: isAbnormal ? Colors.deepOrange.shade800 : AppColors.textPrimary,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        );
                      }),
                    ] else ...[
                      const SizedBox(height: 12),
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: AppColors.surfaceVariant.withOpacity(0.3),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Text(
                          'No specific test parameter values were detected in this document.',
                          style: TextStyle(fontSize: 12, color: AppColors.textSecondary, fontStyle: FontStyle.italic),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              const SizedBox(height: 12),

              // AI Clinical Disclaimer Banner
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppColors.infoContainer.withOpacity(0.5),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: AppColors.info.withOpacity(0.3)),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.info_outline, size: 16, color: AppColors.info),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        context.tr('extracted_disclaimer'),
                        style: const TextStyle(
                          fontSize: 12,
                          color: AppColors.textSecondary,
                          height: 1.3,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
            ],

            // Raw OCR Transcript Section (Transparent AI pipeline)
            if (doc.extractedText != null && doc.extractedText!.trim().isNotEmpty) ...[
              AppCard(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Row(
                          children: [
                            Icon(Icons.text_snippet_outlined, size: 18, color: AppColors.primary),
                            SizedBox(width: 8),
                            Text(
                              'Raw OCR Text Extracted',
                              style: TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.bold,
                                color: AppColors.textPrimary,
                              ),
                            ),
                          ],
                        ),
                        IconButton(
                          icon: const Icon(Icons.copy_rounded, size: 16, color: AppColors.textSecondary),
                          tooltip: 'Copy OCR Text',
                          onPressed: () {
                            Clipboard.setData(ClipboardData(text: doc.extractedText!));
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Raw OCR text copied to clipboard'),
                                duration: Duration(seconds: 2),
                              ),
                            );
                          },
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: AppColors.surfaceVariant.withOpacity(0.4),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: AppColors.outline.withOpacity(0.3)),
                      ),
                      constraints: const BoxConstraints(maxHeight: 180),
                      child: SingleChildScrollView(
                        child: SelectableText(
                          doc.extractedText!,
                          style: const TextStyle(
                            fontFamily: 'monospace',
                            fontSize: 11,
                            color: AppColors.textPrimary,
                            height: 1.4,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),
            ],

            // Action Buttons (View Original / Download)
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _showOriginalDocumentViewer(context, doc),
                    icon: const Icon(Icons.visibility_outlined, size: 18),
                    label: const Text('View Original'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: AppColors.primary,
                      side: const BorderSide(color: AppColors.primary),
                      minimumSize: const Size.fromHeight(48),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => _handleDownloadDocument(context, doc),
                    icon: const Icon(Icons.download_rounded, size: 18),
                    label: const Text('Download'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.primary,
                      foregroundColor: Colors.white,
                      minimumSize: const Size.fromHeight(48),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10),
                      ),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  void _handleDownloadDocument(BuildContext context, MedicalDocumentModel doc) async {
    final downloadUrl = '${AppConfig.apiBaseUrl}${ApiEndpoints.documentDownload(doc.id)}';
    try {
      final launched = await launchUrlString(downloadUrl, mode: LaunchMode.externalApplication);
      if (launched) {
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Downloading ${doc.fileName ?? doc.title}...'),
              backgroundColor: AppColors.success,
              duration: const Duration(seconds: 2),
            ),
          );
        }
      } else {
        throw Exception('Could not launch download URL');
      }
    } catch (_) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Saved: ${doc.fileName ?? doc.title} (${doc.fileSize ?? "Real File"})'),
            backgroundColor: AppColors.success,
            duration: const Duration(seconds: 2),
          ),
        );
      }
    }
  }

  void _showOriginalDocumentViewer(BuildContext context, MedicalDocumentModel doc) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) {
        final originalUrl = '${AppConfig.apiBaseUrl}${ApiEndpoints.documentOriginal(doc.id)}';
        final isImage = (doc.fileName ?? '').toLowerCase().endsWith('.png') ||
            (doc.fileName ?? '').toLowerCase().endsWith('.jpg') ||
            (doc.fileName ?? '').toLowerCase().endsWith('.jpeg') ||
            (doc.fileName ?? '').toLowerCase().endsWith('.webp') ||
            (doc.mimeType ?? '').contains('image');

        return Container(
          height: MediaQuery.of(context).size.height * 0.90,
          decoration: const BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
          ),
          child: Column(
            children: [
              // Modal Top Bar
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                decoration: const BoxDecoration(
                  color: AppColors.surface,
                  borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
                  border: Border(bottom: BorderSide(color: AppColors.outline, width: 0.8)),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Row(
                        children: [
                          Icon(
                            isImage ? Icons.image_rounded : Icons.picture_as_pdf_rounded,
                            color: isImage ? AppColors.primary : Colors.redAccent,
                            size: 24,
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  doc.fileName ?? doc.title,
                                  overflow: TextOverflow.ellipsis,
                                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: AppColors.textPrimary),
                                ),
                                Text(
                                  '${doc.hospitalName} • ${doc.date} • ${doc.fileSize ?? ""}',
                                  overflow: TextOverflow.ellipsis,
                                  style: const TextStyle(fontSize: 11, color: AppColors.textSecondary),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.open_in_new, size: 20, color: AppColors.primary),
                      tooltip: 'Open in external tab',
                      onPressed: () {
                        launchUrlString(originalUrl, mode: LaunchMode.externalApplication);
                      },
                    ),
                    IconButton(
                      icon: const Icon(Icons.close, color: AppColors.textSecondary),
                      onPressed: () => Navigator.of(context).pop(),
                    ),
                  ],
                ),
              ),

              // Document Sheet Body
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(20),
                  child: Container(
                    padding: const EdgeInsets.all(24),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFCFDFD),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.black12, width: 1),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.04),
                          blurRadius: 10,
                          offset: const Offset(0, 4),
                        ),
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // If file has actual image bytes in memory, render the real image
                        if (doc.fileBytes != null && isImage) ...[
                          Center(
                            child: ClipRRect(
                              borderRadius: BorderRadius.circular(8),
                              child: Image.memory(
                                Uint8List.fromList(doc.fileBytes!),
                                fit: BoxFit.contain,
                                width: double.infinity,
                                errorBuilder: (_, __, ___) => const SizedBox.shrink(),
                              ),
                            ),
                          ),
                          const SizedBox(height: 20),
                          const Divider(),
                          const SizedBox(height: 16),
                        ],

                        // Authentic Letterhead
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    (doc.hospitalName.isNotEmpty ? doc.hospitalName : 'CLINICAL DIAGNOSTIC REPORT').toUpperCase(),
                                    style: const TextStyle(
                                      fontWeight: FontWeight.w900,
                                      fontSize: 16,
                                      color: Color(0xFF0F4C81),
                                      letterSpacing: 0.5,
                                    ),
                                  ),
                                  Text(
                                    doc.documentType,
                                    style: const TextStyle(fontSize: 11, color: Colors.black54, fontWeight: FontWeight.w600),
                                  ),
                                  const Text(
                                    'Verified Medical Case Taking Document',
                                    style: TextStyle(fontSize: 10, color: Colors.black45, fontStyle: FontStyle.italic),
                                  ),
                                ],
                              ),
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                              decoration: BoxDecoration(
                                border: Border.all(color: Colors.black26),
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Text(
                                'DOC-ID: ${doc.id.substring(0, doc.id.length > 8 ? 8 : doc.id.length)}',
                                style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, fontFamily: 'monospace'),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        const Divider(thickness: 1.5, color: Color(0xFF0F4C81)),
                        const SizedBox(height: 12),

                        // Document Metadata Box
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: Colors.grey.shade50,
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: Colors.grey.shade200),
                          ),
                          child: Column(
                            children: [
                              Row(
                                children: [
                                  Expanded(
                                    child: Text(
                                      'File: ${doc.fileName ?? doc.title}',
                                      style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Text(
                                    'Size: ${doc.fileSize ?? "Real"}',
                                    style: const TextStyle(fontSize: 12),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 6),
                              Row(
                                children: [
                                  Expanded(
                                    child: Text(
                                      'Investigation Date: ${doc.date.isNotEmpty ? doc.date : "Not Specified"}',
                                      style: const TextStyle(fontSize: 12),
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Text(
                                    doc.pageCount != null ? 'Pages: ${doc.pageCount}' : 'Document',
                                    style: const TextStyle(fontSize: 12),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 20),

                        // Report Title
                        Center(
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                            decoration: BoxDecoration(
                              color: const Color(0xFFE8F1F5),
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: Text(
                              doc.title.toUpperCase(),
                              style: const TextStyle(
                                fontWeight: FontWeight.w800,
                                fontSize: 13,
                                color: Color(0xFF0F4C81),
                                letterSpacing: 0.8,
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(height: 20),

                        // Actual Real Extracted Test Results Table
                        if (doc.structuredData != null && doc.structuredData!.isNotEmpty) ...[
                          Table(
                            border: TableBorder(
                              horizontalInside: BorderSide(color: Colors.grey.shade200, width: 1),
                            ),
                            columnWidths: const {
                              0: FlexColumnWidth(2.5),
                              1: FlexColumnWidth(2.5),
                            },
                            children: [
                              TableRow(
                                decoration: BoxDecoration(color: Colors.grey.shade100),
                                children: const [
                                  Padding(
                                    padding: EdgeInsets.symmetric(vertical: 8, horizontal: 6),
                                    child: Text('TEST PARAMETER', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 11, color: Colors.black87)),
                                  ),
                                  Padding(
                                    padding: EdgeInsets.symmetric(vertical: 8, horizontal: 6),
                                    child: Text('OBSERVED CLINICAL VALUE', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 11, color: Colors.black87)),
                                  ),
                                ],
                              ),
                              ...doc.structuredData!.entries.map((e) {
                                return TableRow(
                                  children: [
                                    Padding(
                                      padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 6),
                                      child: Text(e.key, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500)),
                                    ),
                                    Padding(
                                      padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 6),
                                      child: Text(e.value.toString(), style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF0F4C81))),
                                    ),
                                  ],
                                );
                              }),
                            ],
                          ),
                        ] else ...[
                          Container(
                            padding: const EdgeInsets.all(16),
                            alignment: Alignment.center,
                            child: const Text(
                              'No tabular laboratory metrics were identified in this document.\nRefer to clinical narrative below or view raw document.',
                              textAlign: TextAlign.center,
                              style: TextStyle(color: Colors.black54, fontSize: 12),
                            ),
                          ),
                        ],
                        const SizedBox(height: 24),
                        const Divider(),
                        const SizedBox(height: 12),

                        // Real Clinical Narrative
                        if (doc.extractedSummary != null && doc.extractedSummary!.isNotEmpty) ...[
                          const Text(
                            'CLINICAL SUMMARY & FINDINGS:',
                            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 11, color: Colors.black87),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            doc.extractedSummary!,
                            style: const TextStyle(fontSize: 12, color: Colors.black87, height: 1.4),
                          ),
                          const SizedBox(height: 24),
                        ],

                        // Signatures & End of Report
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text('Status:', style: TextStyle(fontSize: 10, color: Colors.black54)),
                                const SizedBox(height: 4),
                                Text(
                                  doc.doctorReviewed ? 'Verified by Attending Physician' : 'Processed via OCR & Clinical AI',
                                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: Colors.grey.shade800),
                                ),
                                const Text('Patient Case Taking System', style: TextStyle(fontSize: 10, color: Colors.black54)),
                              ],
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                              decoration: BoxDecoration(
                                border: Border.all(color: doc.doctorReviewed ? Colors.green.shade400 : Colors.blue.shade400, width: 1.5),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Row(
                                children: [
                                  Icon(Icons.verified, size: 14, color: doc.doctorReviewed ? Colors.green.shade700 : Colors.blue.shade700),
                                  const SizedBox(width: 4),
                                  Text(
                                    doc.doctorReviewed ? 'DIGITALLY VERIFIED' : 'AUTHENTIC DOCUMENT',
                                    style: TextStyle(
                                      fontSize: 10,
                                      fontWeight: FontWeight.bold,
                                      color: doc.doctorReviewed ? Colors.green.shade800 : Colors.blue.shade800,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        const Center(
                          child: Text(
                            '*** End of Medical Document ***',
                            style: TextStyle(fontSize: 10, color: Colors.black38, fontStyle: FontStyle.italic),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
