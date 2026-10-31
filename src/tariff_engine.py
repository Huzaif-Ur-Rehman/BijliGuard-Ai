"""
Statutory NEPRA Multi-Utility Tariff & Billing Cycle Rule Engine.
Supports utility-specific schedules (IESCO, LESCO, PESCO, HAZECO, K-Electric, MEPCO, FESCO, QESCO)
under NEPRA SRO Determinations, Consumer Service Manual (CSM §4.1), and Electricity Act 1997.
"""

from typing import Dict, Any

# Statutory NEPRA Domestic Base Tariffs (PKR / kWh)
TARIFF_SLABS = {
    "PROTECTED": [
        {"max": 50, "rate": 3.95},
        {"max": 100, "rate": 7.74},
        {"max": 200, "rate": 14.16},
    ],
    "UNPROTECTED": [
        {"max": 100, "rate": 16.48},
        {"max": 200, "rate": 22.95},
        {"max": 300, "rate": 34.26},
        {"max": 400, "rate": 39.15},
        {"max": 700, "rate": 42.78},
        {"max": float("inf"), "rate": 48.84},
    ],
}

# Utility-Specific Taxes and Surcharge Multipliers
DISCO_RULES = {
    "IESCO": {"ed_rate": 0.015, "meter_rent": 25.0, "tv_fee": 35.0, "name": "Islamabad Electric Supply Company"},
    "LESCO": {"ed_rate": 0.020, "meter_rent": 30.0, "tv_fee": 35.0, "name": "Lahore Electric Supply Company"},
    "PESCO": {"ed_rate": 0.010, "meter_rent": 20.0, "tv_fee": 35.0, "name": "Peshawar Electric Supply Company"},
    "HAZECO": {"ed_rate": 0.010, "meter_rent": 20.0, "tv_fee": 35.0, "name": "Hazara Electric Supply Company"},
    "K-Electric": {"ed_rate": 0.025, "meter_rent": 40.0, "tv_fee": 35.0, "name": "K-Electric Karachi"},
    "MEPCO": {"ed_rate": 0.015, "meter_rent": 25.0, "tv_fee": 35.0, "name": "Multan Electric Power Company"},
    "FESCO": {"ed_rate": 0.015, "meter_rent": 25.0, "tv_fee": 35.0, "name": "Faisalabad Electric Supply Company"},
    "QESCO": {"ed_rate": 0.010, "meter_rent": 20.0, "tv_fee": 35.0, "name": "Quetta Electric Supply Company"},
}

GST_RATE = 0.18  # 18% General Sales Tax


def compute_baseline_cost(units: float) -> tuple[float, bool]:
    """Computes exact generation and distribution cost based on NEPRA slab rules."""
    if units <= 200:
        is_protected = True
        cost = 0.0
        remaining = units
        prev_limit = 0.0
        for slab in TARIFF_SLABS["PROTECTED"]:
            slab_capacity = slab["max"] - prev_limit
            allocated = min(remaining, slab_capacity)
            if allocated > 0:
                cost += allocated * slab["rate"]
                remaining -= allocated
                prev_limit = slab["max"]
            if remaining <= 0:
                break
        return round(cost, 2), is_protected
    else:
        is_protected = False
        cost = 0.0
        remaining = units
        prev_limit = 0.0
        for slab in TARIFF_SLABS["UNPROTECTED"]:
            slab_capacity = slab["max"] - prev_limit
            allocated = min(remaining, slab_capacity)
            if allocated > 0:
                cost += allocated * slab["rate"]
                remaining -= allocated
                prev_limit = slab["max"]
            if remaining <= 0:
                break
        return round(cost, 2), is_protected


def audit_bill(bill: Dict[str, Any], disco_code: str = "IESCO") -> Dict[str, Any]:
    """
    Forensically validates a bill against statutory NEPRA rules and specific DISCO schedules.
    """
    disco_cfg = DISCO_RULES.get(disco_code, DISCO_RULES["IESCO"])
    units = float(bill.get("units_consumed", 0.0))
    days = int(bill.get("billing_days", 30))
    claimed_total = float(bill.get("total_payable", 0.0))
    fpa = float(bill.get("fpa_amount", 0.0))
    fc_surcharge = float(bill.get("fc_surcharge", 0.0))

    # 1. Billing Cycle Compliance (CSM §4.1)
    is_cycle_scam = days > 30
    normalized_30d_units = round((units / days) * 30, 2) if days > 0 else units
    protected_lost_by_scam = (units > 200) and (normalized_30d_units <= 200)

    # 2. Statutory Calculation on Claimed Units
    statutory_energy_cost, is_protected = compute_baseline_cost(units)
    electricity_duty = round(statutory_energy_cost * disco_cfg["ed_rate"], 2)
    taxable_subtotal = statutory_energy_cost + fpa + fc_surcharge + electricity_duty
    statutory_gst = round(taxable_subtotal * GST_RATE, 2)
    statutory_total = round(taxable_subtotal + statutory_gst + disco_cfg["tv_fee"] + disco_cfg["meter_rent"], 2)

    # 3. Normalized 30-Day Fair Window Liability
    statutory_30d_energy, was_30d_protected = compute_baseline_cost(normalized_30d_units)
    duty_30d = round(statutory_30d_energy * disco_cfg["ed_rate"], 2)
    taxable_30d = (
        statutory_30d_energy 
        + (fpa * (30 / days) if days > 0 else fpa) 
        + (fc_surcharge * (30 / days) if days > 0 else fc_surcharge) 
        + duty_30d
    )
    statutory_30d_gst = round(taxable_30d * GST_RATE, 2)
    fair_30d_total = round(taxable_30d + statutory_30d_gst + disco_cfg["tv_fee"] + disco_cfg["meter_rent"], 2)

    overbilling_delta = round(claimed_total - statutory_total, 2)
    cycle_scam_penalty = round(claimed_total - fair_30d_total, 2) if is_cycle_scam else 0.0

    return {
        "disco": disco_code,
        "disco_full_name": disco_cfg["name"],
        "units": units,
        "billing_days": days,
        "is_cycle_scam": is_cycle_scam,
        "days_over_limit": max(0, days - 30),
        "normalized_30d_units": normalized_30d_units,
        "protected_lost_by_scam": protected_lost_by_scam,
        "current_status": "Protected" if is_protected else "Unprotected",
        "statutory_energy_cost": statutory_energy_cost,
        "electricity_duty": electricity_duty,
        "statutory_total": statutory_total,
        "claimed_total": claimed_total,
        "overbilling_delta": overbilling_delta,
        "fair_30d_total": fair_30d_total,
        "cycle_scam_penalty": cycle_scam_penalty,
        "audit_passed": abs(overbilling_delta) < 5.0 and not is_cycle_scam,
    }


def audit_meter_reading(billed_units: float, live_meter_kwh: float) -> Dict[str, Any]:
    """Forensic verification of live meter counter vs. claimed utility bill index."""
    is_fraud = live_meter_kwh < billed_units
    phantom_units = round(billed_units - live_meter_kwh, 2) if is_fraud else 0.0
    estimated_unjust_enrichment = round(phantom_units * 34.26, 2)

    return {
        "billed_units": billed_units,
        "live_meter_kwh": live_meter_kwh,
        "is_ghost_reading": is_fraud,
        "phantom_units_billed": phantom_units,
        "estimated_unjust_enrichment_pkr": estimated_unjust_enrichment,
        "status": "GHOST READING FRAUD CONFIRMED" if is_fraud else "VERIFIED: Physical Reading Matches",
    }