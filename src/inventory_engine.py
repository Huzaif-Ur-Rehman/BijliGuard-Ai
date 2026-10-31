"""
BijliGuard AI - National Enterprise Grid Asset & Inventory ERP Engine
Enforces NEPRA-mandated material tracking, transformer balance, and role-based operations.
"""

import pandas as pd
from datetime import datetime

# Official DISCO Hierarchy Designations
ORGANIZATIONAL_HIERARCHY = {
    "NEPRA": ["Chairman NEPRA", "Member (Tariff)", "Member (Technical)", "Director General (CAD)"],
    "DISCO_HQ": ["Chief Executive Officer (CEO)", "Chief Engineer (Operations)", "Director (Procurement & Material Management)"],
    "CIRCLE": ["Superintending Engineer (SE)", "Deputy Director (Vigilance)"],
    "DIVISION": ["Executive Engineer (XEN)", "Divisional Accounts Officer (DAO)"],
    "SUB_DIVISION": ["Sub-Divisional Officer (SDO)", "Revenue Officer (RO)", "Line Superintendent-I (LS-1)", "Line Superintendent-II (LS-2)"],
    "GROUND_FIELD": ["Lineman-I (LM-1)", "Lineman-II (LM-2)", "Assistant Lineman (ALM)", "Commercial Meter Reader"]
}

# Initial Central Warehouse Asset Registry
DEFAULT_INVENTORY = [
    {"Item_Code": "TR-200KVA", "Category": "Transformers", "Description": "Distribution Transformer 200 kVA, 11/.415 kV", "Unit": "Units", "Total_Stock": 45, "Allocated": 38, "Available": 7, "Min_Threshold": 10},
    {"Item_Code": "TR-100KVA", "Category": "Transformers", "Description": "Distribution Transformer 100 kVA, 11/.415 kV", "Unit": "Units", "Total_Stock": 120, "Allocated": 112, "Available": 8, "Min_Threshold": 15},
    {"Item_Code": "TR-50KVA", "Category": "Transformers", "Description": "Distribution Transformer 50 kVA, 11/.415 kV", "Unit": "Units", "Total_Stock": 80, "Allocated": 75, "Available": 5, "Min_Threshold": 12},
    {"Item_Code": "TR-25KVA", "Category": "Transformers", "Description": "Distribution Transformer 25 kVA, 11/.415 kV", "Unit": "Units", "Total_Stock": 60, "Allocated": 58, "Available": 2, "Min_Threshold": 8},
    {"Item_Code": "POL-PCC-31", "Category": "Poles & Structures", "Description": "PCC Pole 31ft (Low Tension)", "Unit": "Units", "Total_Stock": 450, "Allocated": 390, "Available": 60, "Min_Threshold": 50},
    {"Item_Code": "POL-PCC-36", "Category": "Poles & Structures", "Description": "PCC Pole 36ft (11 kV High Tension)", "Unit": "Units", "Total_Stock": 310, "Allocated": 285, "Available": 25, "Min_Threshold": 40},
    {"Item_Code": "POL-STEEL-TUB", "Category": "Poles & Structures", "Description": "Steel Tubular Pole Heavy Duty 36ft", "Unit": "Units", "Total_Stock": 140, "Allocated": 110, "Available": 30, "Min_Threshold": 20},
    {"Item_Code": "CND-DOG-ACSR", "Category": "Conductors & Cables", "Description": "ACSR Conductor 'DOG' (11 kV Feeders)", "Unit": "Km", "Total_Stock": 85.0, "Allocated": 72.5, "Available": 12.5, "Min_Threshold": 15.0},
    {"Item_Code": "CND-RABBIT", "Category": "Conductors & Cables", "Description": "ACSR Conductor 'RABBIT' (11 kV Rural)", "Unit": "Km", "Total_Stock": 110.0, "Allocated": 98.0, "Available": 12.0, "Min_Threshold": 20.0},
    {"Item_Code": "CBL-ABC-95", "Category": "Conductors & Cables", "Description": "LT Aerial Bundled Cable (Anti-Kunda) 95mm2", "Unit": "Km", "Total_Stock": 55.0, "Allocated": 46.0, "Available": 9.0, "Min_Threshold": 10.0},
    {"Item_Code": "INS-PIN-11KV", "Category": "Hardware & Protection", "Description": "Porcelain Pin Insulator 11 kV with Spindle", "Unit": "Pieces", "Total_Stock": 1200, "Allocated": 1050, "Available": 150, "Min_Threshold": 200},
    {"Item_Code": "FUS-DO-11KV", "Category": "Hardware & Protection", "Description": "Drop-Out Fuse Cutout Unit 11 kV", "Unit": "Sets", "Total_Stock": 240, "Allocated": 210, "Available": 30, "Min_Threshold": 40},
    {"Item_Code": "MTR-STATIC-1P", "Category": "Metering Devices", "Description": "Single Phase Digital Static Energy Meter", "Unit": "Units", "Total_Stock": 3200, "Allocated": 2890, "Available": 310, "Min_Threshold": 500},
    {"Item_Code": "MTR-LT-3P-TOU", "Category": "Metering Devices", "Description": "Three Phase Time-of-Use (TOU) AMR Meter", "Unit": "Units", "Total_Stock": 420, "Allocated": 385, "Available": 35, "Min_Threshold": 60}
]

# Active Dispatched Citizen Complaints & Emergency Tickets
DEFAULT_TICKETS = [
    {
        "Ticket_ID": "BG-TK-9081",
        "Timestamp": "2026-10-31 11:20",
        "Utility": "IESCO",
        "Sub_Division": "G-9 Sub-Division",
        "Feeder": "Sector G-9/1 Feeder",
        "Caller_Name": "Tariq Mehmood",
        "Contact": "0300-5544211",
        "Category": "Fallen Conductor / Public Threat",
        "Assigned_Officer": "Engr. Bilal Khan (SDO)",
        "Line_Superintendent": "LS-1 Aslam Parvez",
        "Required_Asset": "ACSR Conductor DOG (150m) + 2x Pin Insulators",
        "Status": "Crew Dispatched",
        "Priority": "CRITICAL"
    },
    {
        "Ticket_ID": "BG-TK-9082",
        "Timestamp": "2026-10-31 12:45",
        "Utility": "HAZECO",
        "Sub_Division": "Cantt Sub-Division Abbottabad",
        "Feeder": "Kakul Rural Feeder-03",
        "Caller_Name": "Sardar Aurangzeb",
        "Contact": "0312-9876543",
        "Category": "Transformer Burnout (Overload)",
        "Assigned_Officer": "Engr. Huzaif Ur Rehman (SDO)",
        "Line_Superintendent": "LS-2 Tariq Shah",
        "Required_Asset": "1x 100 kVA Transformer + D-Fuse Set",
        "Status": "Pending Stock Release",
        "Priority": "HIGH"
    },
    {
        "Ticket_ID": "BG-TK-9083",
        "Timestamp": "2026-10-31 13:10",
        "Utility": "LESCO",
        "Sub_Division": "DHA Sub-Division Lahore",
        "Feeder": "Barki Feeder",
        "Caller_Name": "Malik Zafar",
        "Contact": "0321-4433221",
        "Category": "Billing Cycle Discrepancy (33 Days)",
        "Assigned_Officer": "Farooq Butt (Revenue Officer)",
        "Line_Superintendent": "N/A (Commercial Wing)",
        "Required_Asset": "Statutory SRO Bill Amendment",
        "Status": "Hearing Scheduled",
        "Priority": "MEDIUM"
    }
]


def get_inventory_dataframe() -> pd.DataFrame:
    df = pd.DataFrame(DEFAULT_INVENTORY)
    df["Stock_Health"] = df.apply(
        lambda r: "CRITICAL RE-ORDER" if r["Available"] <= r["Min_Threshold"] else "ADEQUATE", axis=1
    )
    return df


def get_tickets_dataframe() -> pd.DataFrame:
    return pd.DataFrame(DEFAULT_TICKETS)


def create_new_emergency_dispatch(caller_name: str, phone: str, disco: str, sub_div: str, feeder: str, issue: str, required_equipment: str, priority: str) -> dict:
    ticket_id = f"BG-TK-{datetime.now().strftime('%M%S')}"
    return {
        "Ticket_ID": ticket_id,
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Utility": disco,
        "Sub_Division": sub_div,
        "Feeder": feeder,
        "Caller_Name": caller_name,
        "Contact": phone,
        "Category": issue,
        "Assigned_Officer": f"SDO Office ({sub_div})",
        "Line_Superintendent": "On-Duty Shift In-Charge",
        "Required_Asset": required_equipment,
        "Status": "Dispatched to Line Crew",
        "Priority": priority
    }