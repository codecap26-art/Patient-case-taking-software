import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../../../config/theme/app_colors.dart';
import '../../../../core/constants/app_constants.dart';
import '../../../../core/localization/app_localizations.dart';
import '../../../../shared/models/patient_model.dart';
import '../../../../shared/widgets/custom_button.dart';
import '../../../../shared/widgets/custom_text_field.dart';
import '../state/profile_notifier.dart';

class EditProfileScreen extends StatefulWidget {
  const EditProfileScreen({super.key});

  @override
  State<EditProfileScreen> createState() => _EditProfileScreenState();
}

class _EditProfileScreenState extends State<EditProfileScreen> {
  final _formKey = GlobalKey<FormState>();

  late TextEditingController _nameController;
  late TextEditingController _emailController;
  late TextEditingController _emergencyController;
  late TextEditingController _addressController;

  late String _selectedGender;
  late String _selectedBloodGroup;

  @override
  void initState() {
    super.initState();
    final patient = context.read<ProfileNotifier>().patient;
    _nameController = TextEditingController(text: patient.name);
    _emailController = TextEditingController(text: patient.email ?? '');
    _emergencyController = TextEditingController(text: patient.emergencyContact);
    _addressController = TextEditingController(text: patient.address);
    _selectedGender = patient.gender;
    _selectedBloodGroup = patient.bloodGroup;
  }

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _emergencyController.dispose();
    _addressController.dispose();
    super.dispose();
  }

  Future<void> _handleSave() async {
    if (!_formKey.currentState!.validate()) return;

    final profileNotifier = context.read<ProfileNotifier>();
    final current = profileNotifier.patient;

    final updated = current.copyWith(
      name: _nameController.text.trim(),
      email: _emailController.text.trim().isEmpty ? null : _emailController.text.trim(),
      emergencyContact: _emergencyController.text.trim(),
      address: _addressController.text.trim(),
      gender: _selectedGender,
      bloodGroup: _selectedBloodGroup,
    );

    final success = await profileNotifier.updateProfile(updated);

    if (!mounted) return;

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Profile updated successfully'),
          backgroundColor: AppColors.success,
          behavior: SnackBarBehavior.floating,
        ),
      );
      context.pop();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Failed to update profile'),
          backgroundColor: AppColors.error,
          behavior: SnackBarBehavior.floating,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final isLoading = context.watch<ProfileNotifier>().isLoading;

    return Scaffold(
      backgroundColor: AppColors.surface,
      appBar: AppBar(
        title: Text(
          context.tr('edit_profile'),
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
              // Full Name
              CustomTextField(
                label: context.tr('full_name'),
                controller: _nameController,
                validator: (val) =>
                    val == null || val.trim().isEmpty ? 'Name cannot be empty' : null,
              ),
              const SizedBox(height: 16),

              // Blood Group
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
              const SizedBox(height: 16),

              // Email
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
                validator: (val) =>
                    val == null || val.trim().length < 10 ? 'Enter valid emergency contact' : null,
              ),
              const SizedBox(height: 16),

              // Residential Address
              CustomTextField(
                label: context.tr('address'),
                hintText: context.tr('address_hint'),
                controller: _addressController,
                maxLines: 3,
                validator: (val) =>
                    val == null || val.trim().isEmpty ? 'Address cannot be empty' : null,
              ),
              const SizedBox(height: 32),

              // Save Button
              CustomButton(
                text: context.tr('save'),
                isLoading: isLoading,
                onPressed: _handleSave,
                icon: Icons.check,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
