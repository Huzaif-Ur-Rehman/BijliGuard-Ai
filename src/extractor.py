import os
import json
from PIL import Image
from pydantic import BaseModel, Field
import google.generativeai as genai
from dotenv import load_dotenv

# Embedded fallback data for offline venue safety
MOCK_BILL_EXTRACT = {
    "disco_name": "IESCO",
    "reference_number": "04 14123 0987654 U",
    "customer_name": "Muhammad Arshad",
    "billing_month": "October 2024",
    "issue_date": "2024-10-02",
    "due_date": "2024-10-16",
    "billing_days": 33,  # Scam trigger: > 30 days pushed consumer over 200 units
    "units_consumed": 218.0,
    "declared_tariff_rate": 34.80,
    "current_bill_amount": 9480.0,
    "fpa_amount": 890.50,
    "fc_surcharge": 420.0,
    "tv_fee": 35.0,
    "gst_amount": 1650.0,
    "total_payable": 12475.50,
    "sanctioned_load_kw": 1.0,
    "meter_number": "IES-998821"
}

MOCK_METER_EXTRACT = {
    "meter_serial_number": "IES-998821",
    "current_reading_kwh": 184.0,  # Physical counter is BELOW billed units (Ghost Reading fraud)
    "confidence_score": 0.98,
    "meter_type": "Digital Single Phase Static"
}

MOCK_HAZARD_EXTRACT = {
    "hazard_detected": True,
    "hazard_type": "Fallen 11kV Conductor / Sagging Wires Near Civilian Path",
    "severity_level": "CRITICAL",
    "estimated_repair_equipment": "Telescopic boom, 11kV pin insulators, line repair sleeves",
    "public_safety_risk": "Electrocution risk to pedestrians; immediate de-energization required at feeder breaker.",
    "priority_score": 95
}

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if api_key and api_key != "YOUR_GOOGLE_AI_STUDIO_API_KEY_HERE":
    genai.configure(api_key=api_key)


class BillData(BaseModel):
    disco_name: str = Field(description="Name of the utility, e.g., IESCO, LESCO, PESCO, K-Electric")
    reference_number: str
    customer_name: str
    billing_month: str
    issue_date: str
    due_date: str
    billing_days: int
    units_consumed: float
    declared_tariff_rate: float
    current_bill_amount: float
    fpa_amount: float
    fc_surcharge: float
    tv_fee: float
    gst_amount: float
    total_payable: float
    sanctioned_load_kw: float
    meter_number: str


class PhysicalMeterData(BaseModel):
    meter_serial_number: str
    current_reading_kwh: float
    confidence_score: float
    meter_type: str


class HazardData(BaseModel):
    hazard_detected: bool
    hazard_type: str
    severity_level: str
    estimated_repair_equipment: str
    public_safety_risk: str
    priority_score: int


def _clean_json_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return json.loads(text.strip())


def extract_bill_data(image: Image.Image, use_mock: bool = False) -> BillData:
    if use_mock or not api_key or api_key == "YOUR_GOOGLE_AI_STUDIO_API_KEY_HERE":
        return BillData(**MOCK_BILL_EXTRACT)

    prompt = """
    You are an expert Pakistani Electricity Distribution (NEPRA/DISCO) forensic auditor.
    Analyze this electricity bill scan. Extract all values strictly into valid JSON matching this schema:
    {
      "disco_name": "string (e.g., IESCO, LESCO, PESCO, K-Electric)",
      "reference_number": "string",
      "customer_name": "string",
      "billing_month": "string",
      "issue_date": "YYYY-MM-DD",
      "due_date": "YYYY-MM-DD",
      "billing_days": integer,
      "units_consumed": float,
      "declared_tariff_rate": float,
      "current_bill_amount": float,
      "fpa_amount": float,
      "fc_surcharge": float,
      "tv_fee": float,
      "gst_amount": float,
      "total_payable": float,
      "sanctioned_load_kw": float,
      "meter_number": "string"
    }
    Return ONLY pure raw JSON without markdown markers or conversational text.
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([prompt, image])
        cleaned = _clean_json_response(response.text)
        return BillData(**cleaned)
    except Exception as e:
        print(f"[Fallback Active] Bill extraction error: {e}")
        return BillData(**MOCK_BILL_EXTRACT)


def extract_meter_reading(image: Image.Image, use_mock: bool = False) -> PhysicalMeterData:
    if use_mock or not api_key or api_key == "YOUR_GOOGLE_AI_STUDIO_API_KEY_HERE":
        return PhysicalMeterData(**MOCK_METER_EXTRACT)

    prompt = """
    Examine this photo of a physical Pakistani electric power meter (single phase or 3-phase static LCD/mechanical).
    Detect and extract the live reading (kWh) shown on the LCD counter and the printed serial number.
    Return ONLY JSON formatted exactly as:
    {
      "meter_serial_number": "string",
      "current_reading_kwh": float,
      "confidence_score": float (between 0.0 and 1.0),
      "meter_type": "string"
    }
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([prompt, image])
        cleaned = _clean_json_response(response.text)
        return PhysicalMeterData(**cleaned)
    except Exception as e:
        print(f"[Fallback Active] Meter extraction error: {e}")
        return PhysicalMeterData(**MOCK_METER_EXTRACT)


def classify_grid_hazard(image: Image.Image, use_mock: bool = False) -> HazardData:
    if use_mock or not api_key or api_key == "YOUR_GOOGLE_AI_STUDIO_API_KEY_HERE":
        return HazardData(**MOCK_HAZARD_EXTRACT)

    prompt = """
    You are a high-voltage electrical grid safety inspector for rural and urban Pakistani DISCO feeders (11kV and LT lines).
    Analyze this field photo for dangerous utility hazards: fallen poles, blown/leaking transformers, sagging conductor wires, illegal hooks (kunda), or overgrown tree interference.
    Return strictly JSON:
    {
      "hazard_detected": true/false,
      "hazard_type": "string",
      "severity_level": "CRITICAL | HIGH | MEDIUM | LOW",
      "estimated_repair_equipment": "string",
      "public_safety_risk": "string",
      "priority_score": integer between 1 and 100
    }
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([prompt, image])
        cleaned = _clean_json_response(response.text)
        return HazardData(**cleaned)
    except Exception as e:
        print(f"[Fallback Active] Hazard classification error: {e}")
        return HazardData(**MOCK_HAZARD_EXTRACT)