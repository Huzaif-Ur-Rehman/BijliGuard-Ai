import io
from gtts import gTTS


def generate_legal_petition(audit_report: dict, bill_data: dict) -> str:
    """Generates an official complaint under Section 38 of the NEPRA Act 1997."""
    disco_name = audit_report.get('disco_full_name', bill_data.get('disco_name', 'The Distribution Utility'))
    return f"""
BEFORE THE HONOURABLE PROVINCIAL ELECTRIC POWER OMBUDSMAN (POWER SECTOR DISPUTE TRIBUNAL)

SUBJECT: STATUTORY GRIEVANCE UNDER SECTION 38 OF THE REGULATION OF GENERATION, TRANSMISSION AND DISTRIBUTION OF ELECTRIC POWER ACT, 1997
AGAINST SYSTEMIC OVERBILLING, UNLAWFUL CYCLE EXTENSION, AND CSM VIOLATIONS BY {disco_name}.

1. PARTICULARS OF THE PARTIES:
   Complainant: {bill_data.get('customer_name', 'Aggrieved Consumer')}
   Reference Number: {bill_data.get('reference_number', 'N/A')}
   Meter Number: {bill_data.get('meter_number', 'N/A')}
   Distribution Utility: {disco_name}
   Billing Month: {bill_data.get('billing_month', 'N/A')}

2. STATUTORY VIOLATIONS ESTABLISHED:
   a. NEPRA CONSUMER SERVICE MANUAL (CSM §4.1) VIOLATION:
      The Respondent Utility issued a bill spanning {audit_report.get('billing_days')} days. 
      Under NEPRA CSM Section 4.1, a domestic billing cycle must not exceed 30 days. 
      Normalized to the statutory 30-day window, actual consumption stands at {audit_report.get('normalized_30d_units')} kWh.
      {'CRITICAL: This artificial delay intentionally stripped the Complainant of their statutory Protected Bracket (<200 units), triggering higher slabs (>PKR 34/unit).' if audit_report.get('protected_lost_by_scam') else 'The extended window pushed units into an elevated marginal tariff bracket.'}

   b. UNLAWFUL EXTRACTION OF FUNDS:
      - Statutory Fair Amount Due: PKR {audit_report.get('fair_30d_total'):,.2f}
      - Disputed Bill Amount Demanded: PKR {audit_report.get('claimed_total'):,.2f}
      - Unlawful Excess Surcharge Demanded: PKR {audit_report.get('cycle_scam_penalty' if audit_report.get('is_cycle_scam') else audit_report.get('overbilling_delta')):,.2f}

3. PRAYER:
   i.   Order the immediate recall and nullification of the disputed bill.
   ii.  Direct {disco_name} to issue an amended bill reflecting the 30-day normalized sum of PKR {audit_report.get('fair_30d_total'):,.2f}.
   iii. Restrain the Respondent from executing any coercive disconnection of supply during adjudication.
   iv.  Initiate an inquiry against the Sub-Divisional Officer (SDO) and Revenue Officer concerned for willful non-compliance with statutory NEPRA determinations.

Submitted by:
National Power Sector Civic Sentinel (BijliGuard AI)
Authorized Civic Representative
    """.strip()


def generate_hazard_dispatch_memo(hazard_data: dict, location_data: dict) -> str:
    """Generates an official emergency line crew dispatch notice with verified coordinates."""
    return f"""
========================================================================================
URGENT: DISCO SUB-DIVISION EMERGENCY DISPATCH & CIVIC SAFETY HAZARD ESCALATION
NATIONAL POWER SECTOR CIVIC SENTINEL (BIJLIGUARD AI HAZARD TELEMETRY)
========================================================================================
TIMESTAMP: Official Record
FEEDER JURISDICTION: {location_data.get('feeder_name', 'Unspecified Feeder')}
SUB-DIVISION: {location_data.get('sub_division', 'SDO Office')}
CIVIC ADDRESS: {location_data.get('street_address', 'N/A')}
LANDMARK / POLE TAG: {location_data.get('pole_tag', 'N/A')}
GPS COORDINATES: Latitude {location_data.get('lat', 'N/A')}, Longitude {location_data.get('lon', 'N/A')}

HAZARD CLASSIFICATION:
- Hazard Identified: {hazard_data.get('hazard_type')}
- Threat Urgency Score: {hazard_data.get('priority_score')} / 100
- Structural Severity: {hazard_data.get('severity_level')}
- Immediate Public Risk: {hazard_data.get('public_safety_risk')}

REQUIRED LINE CREW GEAR & SAFETY PROTOCOLS:
{hazard_data.get('estimated_repair_equipment')}

DIRECTIVE TO SDO & LINE SUPERINTENDENT:
Under Section 27-A of the NEPRA Act, failure to secure hazardous 11kV/LT conductors resulting in injury
or loss of life constitutes criminal negligence. Immediate trip and isolation of Feeder {location_data.get('feeder_name')}
is recommended until the physical repair is certified by the on-duty Line Superintendent.
========================================================================================
    """.strip()


def generate_urdu_explanation(audit_report: dict) -> str:
    """Colloquial spoken Urdu briefing for citizens and consumers."""
    if audit_report.get("is_cycle_scam"):
        text = (
            f"محترم شہری، آپ کے بجلی کے بل میں نیپرا قوانین کی خلاف ورزی پکڑی گئی ہے۔ "
            f"قانون کے تحت ریڈنگ کا دورانیہ تیس دن ہونا چاہیے، لیکن بل {audit_report.get('billing_days')} دن کا بنایا گیا ہے۔ "
            f"اس ناجائز تاخیر سے آپ کے پروٹیکٹڈ یونٹ ضائع کر کے آپ پر غیر قانونی سلیب نافذ کیا گیا ہے۔ "
            f"آپ سے تقریباً {int(audit_report.get('cycle_scam_penalty', 0))} روپے اضافی مانگے جا رہے ہیں۔ قانونی درخواست اور نوٹس تیار کر دیا گیا ہے۔"
        )
    else:
        text = (
            f"محترم شہری، آپ کے بل کی تفصیلی قانونی جانچ مکمل ہو گئی ہے۔ "
            f"کل استعمال شدہ یونٹ {audit_report.get('units')} ہیں اور نیپرا شیڈول کے مطابق جائز رقم {int(audit_report.get('statutory_total', 0))} روپے بنتی ہے۔ "
            f"اگر بل پر زائد رقم درج ہے تو بجلی محتسب کے لیے قانونی کارروائی تیار ہے۔"
        )
    return text


def synthesize_urdu_voice(text: str) -> io.BytesIO:
    """Synthesizes high-clarity Urdu audio stream."""
    tts = gTTS(text=text, lang="ur", slow=False)
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer