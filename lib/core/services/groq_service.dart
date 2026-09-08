import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../../../config/app_config.dart';

class GroqService {
  static final Dio _dio = Dio(
    BaseOptions(
      baseUrl: 'https://api.groq.com/openai/v1',
      headers: {
        'Authorization': 'Bearer ${AppConfig.groqApiKey}',
        'Content-Type': 'application/json',
      },
      connectTimeout: const Duration(seconds: 20),
      receiveTimeout: const Duration(seconds: 20),
    ),
  );

  /// Parse and structure medical OCR or document text using Groq LLM
  static Future<Map<String, dynamic>?> structureMedicalDocument({
    required String title,
    required String documentType,
    required String hospitalName,
    String? rawText,
    String? fileName,
  }) async {
    try {
      final prompt = '''
You are a specialized clinical healthcare AI assistant.
Analyze this medical document investigation:
- Document Title: $title
- Category: $documentType
- Medical Facility: $hospitalName
- File Name: ${fileName ?? 'document.pdf'}
- OCR / Content Hint: ${rawText ?? 'Clinical diagnostic test report'}

Your goal is to extract realistic, accurate, and structured clinical parameters for this document.
Extract:
1. "summary": A professional clinical narrative summary (2-3 sentences) describing findings, normality, or notable values.
2. "structured_data": A dictionary of 4 to 8 key clinical parameters where keys are parameter names (e.g. "Hemoglobin (Hb)", "Fasting Glucose", "Total Cholesterol", "TSH", "Serum Creatinine") and values are string values containing observed values and reference ranges (e.g. "13.8 g/dL (Normal: 13.0 - 17.0)").

Respond ONLY in valid JSON format:
{
  "summary": "...",
  "structured_data": {
    "Parameter Name": "Observed Value (Reference Range)"
  }
}
''';

      final response = await _dio.post(
        '/chat/completions',
        data: {
          'model': AppConfig.groqModel,
          'messages': [
            {
              'role': 'system',
              'content': 'You are an expert clinical laboratory document extraction AI. Always respond with pure, valid JSON.',
            },
            {
              'role': 'user',
              'content': prompt,
            }
          ],
          'temperature': 0.2,
          'max_tokens': 800,
          'response_format': {'type': 'json_object'},
        },
      );

      if (response.statusCode == 200) {
        final content = response.data['choices'][0]['message']['content'];
        final Map<String, dynamic> parsed = jsonDecode(content);
        return {
          'summary': parsed['summary'] as String?,
          'structured_data': parsed['structured_data'] as Map<String, dynamic>?,
        };
      }
    } catch (e) {
      if (kDebugMode) {
        print('Groq LLM Extraction Exception: $e');
      }
    }
    return null;
  }
}
