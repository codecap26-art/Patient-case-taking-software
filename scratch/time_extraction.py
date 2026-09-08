import asyncio
import time
import sys
sys.path.insert(0, ".")
from app.services.extraction_service import MedicalExtractionService

async def main():
    s = MedicalExtractionService()
    text = """PATIENT: John Doe, 50Y/M
BP: 130/85 mmHg
Hemoglobin: 10.5 g/dL (13.0 - 17.0) LOW
WBC: 6200 /uL (4000 - 11000) NORMAL
Tab. Iron 100mg once daily"""
    t0 = time.time()
    res = await s.extract_clinical_data(text, "Blood Report")
    dt = time.time() - t0
    print(f"Done in {dt:.2f}s, success={res.get('success')}")
    print("Summary:", res.get("summary"))
    print("Vitals:", res.get("vital_signs"))
    print("Labs:", res.get("lab_findings"))

if __name__ == "__main__":
    asyncio.run(main())
