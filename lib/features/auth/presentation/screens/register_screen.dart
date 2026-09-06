import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import '../../../../config/theme/app_colors.dart';
import '../../../../core/constants/app_constants.dart';
import '../../../../core/localization/app_localizations.dart';
import '../../../../core/routing/route_names.dart';
import '../../../../shared/models/patient_model.dart';
import '../../../../shared/widgets/custom_button.dart';
import '../../../../shared/widgets/custom_text_field.dart';
import '../../state/auth_notifier.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();

  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _emailController = TextEditingController();
  final _emergencyController = TextEditingController();
  final _addressController = TextEditingController();

  DateTime? _selectedDob;
  String _selectedGender = AppConstants.genders.first;
  String _selectedBloodGroup = AppConstants.bloodGroups.first;

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _emergencyController.dispose();
    _addressController.dispose();
    super.dispose();
  }

  Future<void> _pickDateOfBirth() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: DateTime(1995, 1, 1),
      firstDate: DateTime(1920),
      lastDate: DateTime.now(),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.light(
              primary: AppColors.primary,
              onPrimary: Colors.white,
              onSurface: AppColors.textPrimary,
            ),
          ),
          child: child!,
        );
      },
    );

    if (picked != null) {
      setState(() => _selectedDob = picked);
    }
  }

  Future<void> _handleRegister() async {
    if (!_formKey.currentState!.validate()) return;
    if (_selectedDob == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please select your Date of Birth'),
          backgroundColor: AppColors.error,
        ),
      );
      return;
    }

    final newPatient = PatientModel(
      id: '',
      name: _nameController.text.trim(),
      phone: _phoneController.text.trim(),
      email: _emailController.text.trim().isEmpty ? null : _emailController.text.trim(),
      dateOfBirth: DateFormat('yyyy-MM-dd').format(_selectedDob!),
      gender: _selectedGender,
      bloodGroup: _selectedBloodGroup,
      emergencyContact: _emergencyController.text.trim(),
      address: _addressController.text.trim(),
      qrCodeToken: '',
    );

    final authNotifier = context.read<AuthNotifier>();
    final success = await authNotifier.register(newPatient, '123456');

    if (!mounted) return;

    if (success) {
      context.go(RouteNames.home);
    } else {
      final err = authNotifier.errorMessage ?? 'Registration failed';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(err),
          backgroundColor: AppColors.error,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final isLoading = context.watch<AuthNotifier>().isLoading;

    return Scaffold(
      backgroundColor: AppColors.surface,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, size: 20),
          onPressed: () => context.pop(),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  context.tr('register_title'),
                  style: Theme.of(context).textTheme.displayLarge?.copyWith(fontSize: 26),
                ),
                const SizedBox(height: 6),
                Text(
                  context.tr('register_subtitle'),
                  style: const TextStyle(
                    fontSize: 14,
                    color: AppColors.textSecondary,
                  ),
                ),
                const SizedBox(height: 24),

                // Full Name
                CustomTextField(
                  label: context.tr('full_name'),
                  hintText: context.tr('name_hint'),
                  controller: _nameController,
                  validator: (val) =>
                      val == null || val.trim().isEmpty ? 'Name is required' : null,
                ),
                const SizedBox(height: 16),

                // Mobile Number
                CustomTextField(
                  label: context.tr('phone_number'),
                  hintText: context.tr('phone_hint'),
                  controller: _phoneController,
                  keyboardType: TextInputType.phone,
                  inputFormatters: [
                    FilteringTextInputFormatter.digitsOnly,
                    LengthLimitingTextInputFormatter(10),
                  ],
                  validator: (val) {
                    if (val == null || val.trim().length < 10) {
                      return 'Valid 10-digit mobile number required';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),

                // Date of Birth & Gender Row
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            context.tr('dob'),
                            style: const TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w600,
                              color: AppColors.textPrimary,
                            ),
                          ),
                          const SizedBox(height: 6),
                          InkWell(
                            onTap: _pickDateOfBirth,
                            borderRadius: BorderRadius.circular(12),
                            child: Container(
                              height: 54,
                              padding: const EdgeInsets.symmetric(horizontal: 12),
                              decoration: BoxDecoration(
                                color: AppColors.surfaceVariant.withOpacity(0.5),
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(color: AppColors.outline),
                              ),
                              child: Row(
                                children: [
                                  const Icon(Icons.calendar_today_outlined,
                                      size: 18, color: AppColors.textSecondary),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      _selectedDob != null
                                          ? DateFormat('dd MMM yyyy').format(_selectedDob!)
                                          : 'Select DOB',
                                      style: TextStyle(
                                        fontSize: 14,
                                        color: _selectedDob != null
                                            ? AppColors.textPrimary
                                            : AppColors.textTertiary,
                                        fontWeight: FontWeight.w500,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            context.tr('gender'),
                            style: const TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w600,
                              color: AppColors.textPrimary,
                            ),
                          ),
                          const SizedBox(height: 6),
                          Container(
                            height: 54,
                            padding: const EdgeInsets.symmetric(horizontal: 12),
                            decoration: BoxDecoration(
                              color: AppColors.surfaceVariant.withOpacity(0.5),
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(color: AppColors.outline),
                            ),
                            child: DropdownButtonHideUnderline(
                              child: DropdownButton<String>(
                                value: _selectedGender,
                                isExpanded: true,
                                icon: const Icon(Icons.keyboard_arrow_down,
                                    color: AppColors.textSecondary),
                                items: AppConstants.genders.map((g) {
                                  return DropdownMenuItem(
                                    value: g,
                                    child: Text(g,
                                        style: const TextStyle(
                                            fontSize: 14, fontWeight: FontWeight.w500)),
                                  );
                                }).toList(),
                                onChanged: (val) {
                                  if (val != null) setState(() => _selectedGender = val);
                                },
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                // Blood Group Selection
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      context.tr('blood_group'),
                      style: const TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: AppConstants.bloodGroups.map((bg) {
                        final isSelected = _selectedBloodGroup == bg;
                        return ChoiceChip(
                          label: Text(bg),
                          selected: isSelected,
                          selectedColor: AppColors.primaryContainer,
                          labelStyle: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                            color: isSelected ? AppColors.primary : AppColors.textSecondary,
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                            side: BorderSide(
                              color: isSelected ? AppColors.primary : AppColors.outline,
                            ),
                          ),
                          onSelected: (selected) {
                            if (selected) setState(() => _selectedBloodGroup = bg);
                          },
                        );
                      }).toList(),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                // Email Address
                CustomTextField(
                  label: context.tr('email'),
                  hintText: context.tr('email_hint'),
                  controller: _emailController,
                  keyboardType: TextInputType.emailAddress,
                ),
                const SizedBox(height: 16),

                // Emergency Contact
                CustomTextField(
                  label: context.tr('emergency_contact'),
                  hintText: context.tr('emergency_hint'),
                  controller: _emergencyController,
                  keyboardType: TextInputType.phone,
                  inputFormatters: [
                    FilteringTextInputFormatter.digitsOnly,
                    LengthLimitingTextInputFormatter(10),
                  ],
                  validator: (val) =>
                      val == null || val.trim().length < 10 ? 'Emergency contact number required' : null,
                ),
                const SizedBox(height: 16),

                // Address
                CustomTextField(
                  label: context.tr('address'),
                  hintText: context.tr('address_hint'),
                  controller: _addressController,
                  maxLines: 2,
                  validator: (val) =>
                      val == null || val.trim().isEmpty ? 'Address is required' : null,
                ),
                const SizedBox(height: 32),

                // Submit Button
                CustomButton(
                  text: context.tr('complete_registration'),
                  isLoading: isLoading,
                  onPressed: _handleRegister,
                  icon: Icons.app_registration_rounded,
                ),
                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
