import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import '../../../../config/theme/app_colors.dart';
import '../../../../core/constants/app_constants.dart';
import '../../../../core/localization/app_localizations.dart';
import '../../../../shared/widgets/custom_button.dart';
import '../../../../shared/widgets/custom_text_field.dart';
import '../state/document_notifier.dart';

class UploadDocumentScreen extends StatefulWidget {
  const UploadDocumentScreen({super.key});

  @override
  State<UploadDocumentScreen> createState() => _UploadDocumentScreenState();
}

class _UploadDocumentScreenState extends State<UploadDocumentScreen> {
  final _formKey = GlobalKey<FormState>();

  final _titleController = TextEditingController();
  final _hospitalController = TextEditingController();

  String _selectedDocType = AppConstants.documentTypes.first;
  DateTime _selectedDate = DateTime.now();
  String? _selectedFileName;
  String _selectedSource = 'PDF';

  @override
  void dispose() {
    _titleController.dispose();
    _hospitalController.dispose();
    super.dispose();
  }

  void _simulateFilePick(String source) {
    setState(() {
      _selectedSource = source;
      if (source == 'Camera') {
        _selectedFileName = 'IMG_SCAN_${DateTime.now().millisecondsSinceEpoch}.jpg';
      } else if (source == 'Gallery') {
        _selectedFileName = 'MEDICAL_REPORT_${DateTime.now().millisecondsSinceEpoch}.png';
      } else {
        _selectedFileName = 'DIAGNOSTIC_REPORT_${DateFormat('yyyyMMdd').format(DateTime.now())}.pdf';
      }
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Selected file: $_selectedFileName ($source)'),
        backgroundColor: AppColors.primary,
        behavior: SnackBarBehavior.floating,
        duration: const Duration(seconds: 2),
      ),
    );
  }

  Future<void> _handleUpload() async {
    if (!_formKey.currentState!.validate()) return;
    if (_selectedFileName == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please select or capture a medical document file'),
          backgroundColor: AppColors.error,
        ),
      );
      return;
    }

    final docNotifier = context.read<DocumentNotifier>();
    final result = await docNotifier.uploadDocument(
      title: _titleController.text.trim(),
      documentType: _selectedDocType,
      hospitalName: _hospitalController.text.trim(),
      date: DateFormat('yyyy-MM-dd').format(_selectedDate),
    );

    if (!mounted) return;

    if (result != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Document uploaded & AI parsing completed successfully!'),
          backgroundColor: AppColors.success,
        ),
      );
      context.pop();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Failed to upload document. Please try again.'),
          backgroundColor: AppColors.error,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final docNotifier = context.watch<DocumentNotifier>();
    final isUploading = docNotifier.uploadStage == DocumentUploadStage.uploading ||
        docNotifier.uploadStage == DocumentUploadStage.processing;

    return Scaffold(
      backgroundColor: AppColors.surface,
      appBar: AppBar(
        title: Text(
          context.tr('upload_document'),
          style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 18),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, size: 20),
          onPressed: () => context.pop(),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Choose File Source Section
              Text(
                context.tr('select_file_source'),
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                  color: AppColors.textPrimary,
                ),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  _buildSourceTile(
                    icon: Icons.camera_alt_outlined,
                    label: context.tr('camera'),
                    sourceName: 'Camera',
                  ),
                  const SizedBox(width: 10),
                  _buildSourceTile(
                    icon: Icons.photo_library_outlined,
                    label: context.tr('gallery'),
                    sourceName: 'Gallery',
                  ),
                  const SizedBox(width: 10),
                  _buildSourceTile(
                    icon: Icons.picture_as_pdf_outlined,
                    label: 'PDF / File',
                    sourceName: 'PDF',
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Selected File Preview Card
              if (_selectedFileName != null)
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppColors.primaryContainer.withOpacity(0.5),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: AppColors.primary.withOpacity(0.3)),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.insert_drive_file, color: AppColors.primary),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              _selectedFileName!,
                              style: const TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w600,
                                color: AppColors.textPrimary,
                              ),
                            ),
                            Text(
                              'Source: $_selectedSource • Ready for processing',
                              style: const TextStyle(
                                fontSize: 11,
                                color: AppColors.textSecondary,
                              ),
                            ),
                          ],
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.close, size: 18, color: AppColors.textSecondary),
                        onPressed: () => setState(() => _selectedFileName = null),
                      ),
                    ],
                  ),
                ),
              const SizedBox(height: 20),

              // Document Title
              CustomTextField(
                label: 'Document Title',
                hintText: 'e.g. CBC Blood Test Report',
                controller: _titleController,
                validator: (val) =>
                    val == null || val.trim().isEmpty ? 'Document title is required' : null,
              ),
              const SizedBox(height: 16),

              // Document Type Dropdown
              Text(
                context.tr('document_type'),
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textPrimary,
                ),
              ),
              const SizedBox(height: 6),
              Container(
                height: 54,
                padding: const EdgeInsets.symmetric(horizontal: 14),
                decoration: BoxDecoration(
                  color: AppColors.surfaceVariant.withOpacity(0.5),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppColors.outline),
                ),
                child: DropdownButtonHideUnderline(
                  child: DropdownButton<String>(
                    value: _selectedDocType,
                    isExpanded: true,
                    icon: const Icon(Icons.keyboard_arrow_down, color: AppColors.textSecondary),
                    items: AppConstants.documentTypes.map((type) {
                      return DropdownMenuItem(
                        value: type,
                        child: Text(type, style: const TextStyle(fontSize: 14)),
                      );
                    }).toList(),
                    onChanged: (val) {
                      if (val != null) setState(() => _selectedDocType = val);
                    },
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Hospital / Clinic Name
              CustomTextField(
                label: context.tr('hospital_clinic'),
                hintText: 'e.g. Apollo Diagnostics / Manipal Hospital',
                controller: _hospitalController,
                validator: (val) =>
                    val == null || val.trim().isEmpty ? 'Facility name is required' : null,
              ),
              const SizedBox(height: 16),

              // Document Date
              Text(
                context.tr('document_date'),
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textPrimary,
                ),
              ),
              const SizedBox(height: 6),
              InkWell(
                onTap: () async {
                  final picked = await showDatePicker(
                    context: context,
                    initialDate: _selectedDate,
                    firstDate: DateTime(2010),
                    lastDate: DateTime.now(),
                  );
                  if (picked != null) setState(() => _selectedDate = picked);
                },
                child: Container(
                  height: 54,
                  padding: const EdgeInsets.symmetric(horizontal: 14),
                  decoration: BoxDecoration(
                    color: AppColors.surfaceVariant.withOpacity(0.5),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: AppColors.outline),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        DateFormat('dd MMMM yyyy').format(_selectedDate),
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                          color: AppColors.textPrimary,
                        ),
                      ),
                      const Icon(Icons.calendar_today_outlined,
                          size: 18, color: AppColors.textSecondary),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // Progress Bar if uploading
              if (isUploading) ...[
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: AppColors.surfaceVariant,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            docNotifier.uploadStage == DocumentUploadStage.uploading
                                ? 'Uploading Document...'
                                : 'AI Processing & Parsing...',
                            style: const TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.w600,
                              color: AppColors.primary,
                            ),
                          ),
                          Text(
                            '${(docNotifier.uploadProgress * 100).toInt()}%',
                            style: const TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.bold,
                              color: AppColors.primary,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      LinearProgressIndicator(
                        value: docNotifier.uploadProgress,
                        backgroundColor: AppColors.outline,
                        valueColor: const AlwaysStoppedAnimation<Color>(AppColors.primary),
                        borderRadius: BorderRadius.circular(4),
                        minHeight: 6,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 20),
              ],

              // Upload Button
              CustomButton(
                text: 'Upload & Process Document',
                isLoading: isUploading,
                onPressed: _handleUpload,
                icon: Icons.cloud_upload_outlined,
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSourceTile({
    required IconData icon,
    required String label,
    required String sourceName,
  }) {
    final isSelected = _selectedSource == sourceName && _selectedFileName != null;

    return Expanded(
      child: InkWell(
        onTap: () => _simulateFilePick(sourceName),
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 8),
          decoration: BoxDecoration(
            color: isSelected ? AppColors.primaryContainer : AppColors.surfaceVariant.withOpacity(0.5),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: isSelected ? AppColors.primary : AppColors.outline,
              width: isSelected ? 1.5 : 1,
            ),
          ),
          child: Column(
            children: [
              Icon(
                icon,
                size: 24,
                color: isSelected ? AppColors.primary : AppColors.textSecondary,
              ),
              const SizedBox(height: 6),
              Text(
                label,
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: isSelected ? AppColors.primary : AppColors.textPrimary,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
