import httpx
import json

BASE_URL = "http://127.0.0.1:8000"

def test_ocr_extract_with_llm_organize():
    print("\n--- TEST 1: POST /api/ocr/extract with LLM Organization ---")
    image_path = r"C:\Users\Hp\.gemini\antigravity-ide\brain\9e4566e8-d708-4ec5-b99f-409b61f73c2d\scratch\SIH_OCR\frontend\public\samples\sample1_bilingual.jpg"
    with open(image_path, "rb") as f:
        files = {"file": ("sample1_bilingual.jpg", f, "image/jpeg")}
        resp = httpx.post(f"{BASE_URL}/api/ocr/extract?organize_with_llm=true", files=files, timeout=75.0)
    
    print(f"Status Code: {resp.status_code}")
    assert resp.status_code == 200, f"Expected 200, got {resp.text}"
    data = resp.json()
    print("Success:", data.get("success"))
    print("Lines Extracted:", len(data.get("lines", [])))
    print("OCR Text Snippet:\n", data.get("text", "")[:200].encode("ascii", "backslashreplace").decode())
    summary = data.get("clinical_summary") or ""
    print("\nLLM Organized Clinical Summary:\n", summary.encode("ascii", "backslashreplace").decode())
    print("\nLLM Organized Information Keys:", list(data.get("organized_information", {}).keys()))
    print("LLM Structured Data Preview:", json.dumps(data.get("structured_data", {}), indent=2))

def test_ocr_organize_direct_text():
    print("\n--- TEST 2: POST /api/ocr/organize with Real Converted OCR Text ---")
    ocr_converted_text = """
    METROPOLIS HEALTHCARE LABS
    PATIENT NAME: Rajesh Kumar   AGE: 45 Yrs / Male
    DATE: 2026-09-05   REF BY: Dr. S. Sharma
    
    COMPLETE BLOOD COUNT (CBC)
    Hemoglobin : 11.2 g/dL (Reference: 13.0 - 17.0 g/dL) - LOW
    Total WBC Count : 5,400 /uL (Reference: 4,000 - 11,000 /uL) - NORMAL
    Platelet Count : 180,000 /uL (Reference: 150,000 - 450,000 /uL) - NORMAL
    RBC Count : 4.15 million/uL (Reference: 4.50 - 5.90 million/uL) - LOW
    PCV (Packed Cell Volume) : 34.5 % (Reference: 40.0 - 50.0 %) - LOW
    
    VITALS:
    BP: 120/80 mmHg   Pulse: 74 bpm   SpO2: 98%
    
    RX / MEDICATIONS:
    1. Tab. Ferrous Ascorbate 100mg - 1 tablet OD after meals for 30 days
    2. Tab. Vitamin C 500mg - 1 tablet OD after meals
    """
    
    payload = {
        "ocr_text": ocr_converted_text,
        "title": "Complete Blood Count & Prescription",
        "document_type": "Blood Test & Prescription",
        "hospital_name": "Metropolis Healthcare Labs"
    }
    
    resp = httpx.post(f"{BASE_URL}/api/ocr/organize", json=payload, timeout=60.0)
    print(f"Status Code: {resp.status_code}")
    assert resp.status_code == 200, f"Expected 200, got {resp.text}"
    data = resp.json()
    def safe_print(title, obj):
        if isinstance(obj, str):
            print(f"{title}: {obj.encode('ascii', 'backslashreplace').decode()}")
        else:
            print(f"{title}:\n{json.dumps(obj, indent=2)}")

    safe_print("LLM Summary", data.get("clinical_summary"))
    safe_print("Organized Patient Info", data.get("patient_info"))
    safe_print("Organized Vitals", data.get("vital_signs"))
    safe_print("Organized Lab Findings", data.get("lab_findings"))
    safe_print("Organized Medications", data.get("medications"))
    safe_print("Organized Structured Data Table", data.get("structured_data"))

if __name__ == "__main__":
    test_ocr_organize_direct_text()
    test_ocr_extract_with_llm_organize()
