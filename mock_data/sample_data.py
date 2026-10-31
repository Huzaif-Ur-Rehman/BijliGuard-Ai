"""
Pre-loaded mock responses and fallback data for safe offline demo execution.
"""

MOCK_BILL_EXTRACT = {
    "disco_name": "IESCO",
    "reference_number": "04 14123 0987654 U",
    "customer_name": "Muhammad Arshad",
    "billing_month": "October 2024",
    "issue_date": "2024-10-02",
    "due_date": "2024-10-16",
    "billing_days": 33,  # Scam trigger: > 30 days pushed consumer over 200 units
    "units_consumed": 218,
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