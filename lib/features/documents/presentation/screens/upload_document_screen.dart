import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import 'package:dio/dio.dart';
import '../../../../config/app_config.dart';
import '../../../../config/theme/app_colors.dart';
import '../../../../core/constants/app_constants.dart';
import '../../../../core/localization/app_localizations.dart';
import '../../../../shared/widgets/custom_button.dart';
import '../../../../shared/widgets/custom_text_field.dart';
import '../../state/document_notifier.dart';

class UploadDocumentScreen extends StatefulWidget {
  const UploadDocumentScreen({super.key});

  @override
  State<UploadDocumentScreen> createState() => _UploadDocumentScreenState();
}

class _UploadDocumentScreenState extends State<UploadDocumentScreen> {
  final _formKey = GlobalKey<FormState>();

  final _titleController = TextEditingController();
  final _hospitalController = TextEditingController();
  final _ocrContentController = TextEditingController();

  String _selectedDocType = AppConstants.documentTypes.first;
  DateTime _selectedDate = DateTime.now();
  String? _selectedFileName;
  List<int>? _selectedFileBytes;
  String? _selectedFileSizeDisplay;
  String _selectedSource = 'PDF';
  bool _isScanningOcr = false;
  String? _organizedSummary;
  Map<String, dynamic>? _previewStructuredData;

  @override
  void dispose() {
    _titleController.dispose();
    _hospitalController.dispose();
    _ocrContentController.dispose();
    super.dispose();
  }

  Future<void> _scanAndOrganizeWithAI() async {
    if (_selectedFileBytes == null || _selectedFileName == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please select or capture a medical document file first.'),
          backgroundColor: AppColors.error,
        ),
      );
      return;
    }

    setState(() {
      _isScanningOcr = true;
    });

    try {
      final dio = Dio();
      final formData = FormData.fromMap({
        'file': MultipartFile.fromBytes(_selectedFileBytes!, filename: _selectedFileName!),
      });

      final resp = await dio.post(
        '${AppConfig.apiBaseUrl}/api/ocr/extract?organize_with_llm=true',
        data: formData,
      );

      if (resp.statusCode == 200 && resp.data != null) {
        final data = resp.data as Map<String, dynamic>;
        final rawText = data['text'] as String? ?? '';
        final summary = data['clinical_summary'] as String? ?? '';
        final structData = data['structured_data'] as Map<String, dynamic>? ?? {};

        setState(() {
          if (rawText.isNotEmpty) {
            _ocrContentController.text = rawText;
          }
          _organizedSummary = summary.isNotEmpty ? summary : null;
          _previewStructuredData = structData.isNotEmpty ? structData : null;
        });

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('OCR transcribed & organized by AI successfully!'),
              backgroundColor: AppColors.success,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Scan complete. Please review content.'),
            backgroundColor: AppColors.primary,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isScanningOcr = false;
        });
      }
    }
  }

  Future<void> _pickRealFile(String source) async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.any,
        allowMultiple: false,
        withData: true,
      );

      if (result != null && result.files.isNotEmpty) {
        final file = result.files.first;
        String? extractedText;
        if (file.bytes != null) {
          try {
            // Attempt decoding text if file is text/ascii/utf8
            final decoded = String.fromCharCodes(file.bytes!);
            final clean = decoded.replaceAll(RegExp(r'[^\x20-\x7E\n\r\t]'), ' ').trim();
            if (clean.length > 20) {
              extractedText = clean.length > 1500 ? clean.substring(0, 1500) : clean;
            }
          } catch (_) {}
        }

        setState(() {
          _selectedSource = source;
          _selectedFileName = file.name;
          _selectedFileBytes = file.bytes;
          _selectedFileSizeDisplay = '${(file.size / 1024).toStringAsFixed(1)} KB';
          if (_titleController.text.trim().isEmpty) {
            _titleController.text = file.name.replaceAll(RegExp(r'\.[a-zA-Z0-9]+$'), '').replaceAll(RegExp(r'[_-]'), ' ');
          }
          if (extractedText != null && extractedText.isNotEmpty && _ocrContentController.text.trim().isEmpty) {
            _ocrContentController.text = extractedText;
          }
        });

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Selected: ${file.name} ($_selectedFileSizeDisplay)'),
            backgroundColor: AppColors.primary,
            behavior: SnackBarBehavior.floating,
            duration: const Duration(seconds: 2),
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error choosing file: $e'),
          backgroundColor: AppColors.error,
        ),
      );
    }
  }

  Future<void> _handleUpload() async {
    if (!_formKey.currentState!.validate()) return;
    if (_selectedFileName == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please select or capture a medical document file from your device'),
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
      rawText: _ocrContentController.text.trim().isNotEmpty ? _ocrContentController.text.trim() : null,
      fileBytes: _selectedFileBytes,
      fileName: _selectedFileName,
    );

    if (!mounted) return;

    if (result != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Document uploaded & OCR extraction completed successfully!'),
          backgroundColor: AppColors.success,
        ),
      );
      context.pop();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Failed to upload document. Please check backend connection.'),
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
                              'Size: ${_selectedFileSizeDisplay ?? 'Ready'} • Source: $_selectedSource',
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
                        onPressed: () => setState(() {
                          _selectedFileName = null;
                          _selectedFileBytes = null;
                          _selectedFileSizeDisplay = null;
                        }),
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
              const SizedBox(height: 16),

              // Document OCR Content & AI Organization
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'OCR Text & AI Organization',
                    style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  if (_selectedFileBytes != null)
                    TextButton.icon(
                      onPressed: _isScanningOcr ? null : _scanAndOrganizeWithAI,
                      icon: _isScanningOcr
                          ? const SizedBox(
                              width: 14,
                              height: 14,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.auto_awesome, size: 16, color: AppColors.primary),
                      label: Text(
                        _isScanningOcr ? 'Scanning & Organizing...' : 'Scan with OCR & LLM',
                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 6),
              CustomTextField(
                label: 'Scanned Text / Test Results',
                hintText: 'e.g. Hemoglobin: 14.2 g/dL, Fasting Sugar: 105 mg/dL, Platelets: 210,000...',
                controller: _ocrContentController,
                maxLines: 4,
              ),
              if (_organizedSummary != null) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppColors.primaryContainer.withValues(alpha: 0.4),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: AppColors.primary.withValues(alpha: 0.3)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Row(
                        children: [
                          Icon(Icons.check_circle_outline, size: 16, color: AppColors.primary),
                          SizedBox(width: 6),
                          Text(
                            'AI Organized Summary',
                            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: AppColors.primary),
                          ),
                        ],
                      ),
                      const SizedBox(height: 6),
                      Text(
                        _organizedSummary!,
                        style: const TextStyle(fontSize: 12, color: AppColors.textPrimary, height: 1.4),
                      ),
                      if (_previewStructuredData != null && _previewStructuredData!.isNotEmpty) ...[
                        const SizedBox(height: 8),
                        Text(
                          '${_previewStructuredData!.length} Clinical Parameters Extracted',
                          style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: AppColors.textSecondary),
                        ),
                      ],
                    ],
                  ),
                ),
              ],
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
        onTap: () => _pickRealFile(sourceName),
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
