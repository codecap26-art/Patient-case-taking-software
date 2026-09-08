import json
import os
import google.generativeai as genai

key = os.getenv("GEMINI_API_KEY", "")
genai.configure(api_key=key)

model = genai.GenerativeModel(
    "models/gemini-3.6-flash",
    generation_config={"response_mime_type": "application/json"}
)

prompt = """
You are an expert Clinical Informatics AI Assistant.
Analyze this OCR text:
Hemoglobin: 11.2 g/dL (Ref: 13.0 - 17.0) LOW
Total WBC: 5,400 /uL (Ref: 4,000 - 11,000) NORMAL
Platelets: 180,000 /uL (Ref: 150,000 - 450,000) NORMAL
BP: 120/80 mmHg   Pulse: 74 bpm

Extract into JSON with keys:
"summary": "narrative summary",
"structured_data": {"test_name": "value with unit and ref"},
"lab_findings": [{"test_name": "...", "value": "...", "unit": "...", "reference_range": "...", "flag": "..."}],
"vital_signs": {"blood_pressure": "...", "pulse": "..."}
"""

resp = model.generate_content(prompt)
print("Response text:\n", resp.text)
data = json.loads(resp.text)
print("Parsed summary:", data.get("summary"))
print("Parsed structured_data:", data.get("structured_data"))
