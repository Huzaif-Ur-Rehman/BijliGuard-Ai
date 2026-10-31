import streamlit as st
import pandas as pd
from PIL import Image
from extractor import extract_bill_data, extract_meter_reading, classify_grid_hazard
from tariff_engine import audit_bill, audit_meter_reading, DISCO_RULES
from dispute_generator import (
    generate_legal_petition, 
    generate_hazard_dispatch_memo,
    generate_urdu_explanation, 
    synthesize_urdu_voice
)
from inventory_engine import (
    get_inventory_dataframe, 
    get_tickets_dataframe,
    create_new_emergency_dispatch
)

st.set_page_config(
    page_title="BijliGuard AI | قومی بجلی آڈٹ نیٹ ورک",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# HIGH-IMPACT INSTITUTIONAL THEME (CSS)
# -------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&family=Noto+Nastaliq+Urdu:wght@400;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at 15% 10%, #031814 0%, #010c09 45%, #000504 100%);
        color: #E6EDF3;
    }

    .hud-ticker {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(4, 25, 19, 0.7);
        border: 1px solid rgba(0, 245, 160, 0.25);
        border-radius: 50px;
        padding: 8px 22px;
        margin-bottom: 20px;
        box-shadow: 0 0 20px rgba(0, 245, 160, 0.08);
    }
    
    .pulse-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: #00F5A0;
        box-shadow: 0 0 0 0 rgba(0, 245, 160, 0.7);
        animation: pulse 1.8s infinite;
        margin-right: 8px;
    }

    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 245, 160, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(0, 245, 160, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 245, 160, 0); }
    }

    .sentinel-hero {
        background: linear-gradient(135deg, rgba(3, 38, 28, 0.7) 0%, rgba(1, 19, 14, 0.85) 100%);
        border: 1px solid rgba(0, 245, 160, 0.2);
        border-radius: 18px;
        padding: 24px 28px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }

    .glass-card {
        background: rgba(7, 24, 19, 0.6);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 20px;
        transition: all 0.25s ease;
    }
    .glass-card:hover {
        border-color: rgba(0, 245, 160, 0.25);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.45);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(3, 16, 12, 0.85);
        padding: 8px;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.07);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        color: #8B9D98;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 10px 20px;
        border: 1px solid transparent;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00A36C 0%, #00744D 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(0, 245, 160, 0.4) !important;
        box-shadow: 0 4px 15px rgba(0, 163, 108, 0.35);
    }

    .alert-banner {
        background: linear-gradient(90deg, rgba(84, 11, 20, 0.9) 0%, rgba(45, 6, 11, 0.95) 100%);
        border-left: 6px solid #FF3B56;
        border-radius: 10px;
        padding: 18px 22px;
        color: #FFF2F4;
        margin: 16px 0;
        box-shadow: 0 6px 24px rgba(255, 59, 86, 0.25);
    }

    .verified-banner {
        background: linear-gradient(90deg, rgba(4, 53, 34, 0.9) 0%, rgba(2, 33, 21, 0.95) 100%);
        border-left: 6px solid #00F5A0;
        border-radius: 10px;
        padding: 18px 22px;
        color: #E8FFF5;
        margin: 16px 0;
        box-shadow: 0 6px 24px rgba(0, 245, 160, 0.18);
    }

    .urdu-box {
        font-family: 'Noto Nastaliq Urdu', serif;
        direction: rtl;
        font-size: 1.3rem;
        line-height: 2.3;
        color: #B2F7DC;
        background: rgba(2, 22, 16, 0.7);
        border-radius: 12px;
        padding: 18px 24px;
        border: 1px solid rgba(0, 245, 160, 0.2);
    }

    .chip {
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        border-radius: 30px;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.6px;
        text-transform: uppercase;
    }
    .chip-protected { background: rgba(0, 245, 160, 0.15); color: #00F5A0; border: 1px solid rgba(0, 245, 160, 0.4); }
    .chip-unprotected { background: rgba(255, 183, 3, 0.15); color: #FFB703; border: 1px solid rgba(255, 183, 3, 0.4); }
    .chip-hazard { background: rgba(255, 59, 86, 0.15); color: #FF3B56; border: 1px solid rgba(255, 59, 86, 0.4); }
</style>
""", unsafe_allow_html=True)

# Maintain Session Tickets
if "dispatch_tickets" not in st.session_state:
    st.session_state["dispatch_tickets"] = get_tickets_dataframe()

# -------------------------------------------------------------
# SIDEBAR NAVIGATION
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 8px 0 16px 0;">
            <div style="font-size: 3rem; filter: drop-shadow(0 0 12px rgba(0, 245, 160, 0.5)); margin-bottom: 4px;">⚡</div>
            <h2 style="color: #00F5A0; margin: 0; font-weight: 800; font-size: 1.5rem; letter-spacing: -0.5px;">BijliGuard AI</h2>
            <div style="color: #A7F3D0; font-family: 'Noto Nastaliq Urdu', serif; font-size: 1.15rem; font-weight: 700;">روشن پاکستان</div>
            <span style="color: #64748B; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px;">National Power Civic Audit Network</span>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="glass-card" style="padding: 14px;">', unsafe_allow_html=True)
    st.markdown("#### 🏢 Operational Role Portal")
    active_portal = st.selectbox(
        "Select Portal View",
        [
            "👤 Citizen Public Grievance Portal",
            "⚡ SDO Sub-Division & Line Crew Ops",
            "🏢 DISCO Central Asset & Warehouse ERP",
            "🏛️ NEPRA Apex Regulatory Oversight"
        ],
        index=0
    )
    st.markdown('</div>', unsafe_allow_html=True)

    selected_disco = st.selectbox(
        "Governing Distribution Utility (DISCO)",
        list(DISCO_RULES.keys()),
        index=0,
        help="Applies utility-specific statutory determinations, surcharges, and municipal duties."
    )

    use_mock_data = st.toggle(
        "🛡️ Safe Mode (Synthetic Data)", 
        value=False, 
        help="Ensures zero downtime or crashes during evaluation."
    )

    st.markdown(f"""
    <div style="margin-top: 20px; padding: 14px; background: rgba(255, 255, 255, 0.02); border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05); font-size: 0.78rem; color: #8B9D98;">
        <strong style="color: #00F5A0;">Statutory Basis:</strong><br>
        • NEPRA Act 1997 (§27A, §38)<br>
        • Consumer Service Manual (CSM §4.1)<br>
        • Provincial Power Ombudsman SROs
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------
# TOP HUD TICKER
# -------------------------------------------------------------
st.markdown(f"""
<div class="hud-ticker">
    <div style="display: flex; align-items: center;">
        <span class="pulse-dot"></span>
        <span style="font-weight: 700; font-size: 0.82rem; letter-spacing: 0.5px; color: #00F5A0;">SYSTEM SECURE</span>
        <span style="color: #475569; margin: 0 10px;">|</span>
        <span style="color: #94A3B8; font-size: 0.82rem;">Utility: <strong style="color: #FFFFFF;">{DISCO_RULES[selected_disco]['name']} ({selected_disco})</strong></span>
    </div>
    <div>
        <span class="chip chip-protected">{active_portal.split(' ')[1]} Active</span>
    </div>
</div>
""", unsafe_allow_html=True)

# =========================================================================
# PORTAL 1: CITIZEN PUBLIC GRIEVANCE PORTAL (عوامی پورٹل)
# =========================================================================
if "CITIZEN" in active_portal.upper():
    st.markdown(f"""
    <div class="sentinel-hero">
        <h1 style="color: #FFFFFF; margin: 0 0 6px 0; font-weight: 800; font-size: 2rem;">عوامی پورٹل — Citizen Public Grievance Desk</h1>
        <p style="color: #94A3B8; margin: 0; font-size: 0.95rem;">
            Autonomous civic tools for electricity consumers. Audit your monthly bill against illegal slab jumps, verify your physical meter counter, calculate 30-day billing cycle theft, or dispatch emergency field help.
        </p>
    </div>
    """, unsafe_allow_html=True)

    citizen_tabs = st.tabs([
        "Scan & Audit My Bill",
        "Verify My Physical Meter (Anti-Ghost Reading)",
        "30-Day Billing Cycle Scam Detector",
        "1-Click Emergency Incident Hotline"
    ])

    # Tab 1: Citizen Bill Audit
    with citizen_tabs[0]:
        st.subheader("Forensic Bill Verification & Tariff Dispute")
        c1, c2 = st.columns([1, 1.25], gap="large")

        with c1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### 📤 Upload Bill Photo")
            st.write(f"Take a picture of your paper bill issued by **{selected_disco}**.")
            bill_file = st.file_uploader("Upload Bill (JPG / PNG)", type=["png", "jpg", "jpeg"], key="cit_bill_uploader")
            img = Image.open(bill_file) if bill_file else Image.new("RGB", (300, 300), color=(10, 28, 22))
            run_bill_audit = st.button("⚡ Audit My Bill with AI Vision", key="btn_cit_bill", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            if run_bill_audit or bill_file:
                with st.spinner("Extracting parameters and computing statutory NEPRA slabs..."):
                    extracted = extract_bill_data(img, use_mock=use_mock_data)
                    audit = audit_bill(extracted.model_dump(), disco_code=selected_disco)

                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                status_chip = '<span class="chip chip-protected">Protected Bracket (<200 Units)</span>' if audit["current_status"] == "Protected" else '<span class="chip chip-unprotected">Unprotected Bracket (>200 Units)</span>'
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0; color: #FFFFFF;">{extracted.customer_name}</h3>
                    {status_chip}
                </div>
                <p style="color: #64748B; margin: 4px 0 16px 0; font-size: 0.85rem;">Utility: <strong style="color: #CBD5E1;">{audit['disco_full_name']}</strong> | Ref: <code style="color: #00F5A0;">{extracted.reference_number}</code> | Meter: <code>{extracted.meter_number}</code></p>
                """, unsafe_allow_html=True)

                m1, m2, m3 = st.columns(3)
                m1.metric("Billed Units", f"{extracted.units_consumed:,.0f} kWh")
                m2.metric("Billing Window", f"{extracted.billing_days} Days", delta=f"{extracted.billing_days - 30} Days Excess" if extracted.billing_days > 30 else "Normal 30 Days", delta_color="inverse")
                m3.metric("Billed Amount", f"PKR {extracted.total_payable:,.2f}")

                st.markdown("<hr style='border-color: rgba(255,255,255,0.06); margin: 16px 0;'>", unsafe_allow_html=True)

                if not audit["audit_passed"]:
                    overcharge_val = audit["cycle_scam_penalty"] if audit["is_cycle_scam"] else audit["overbilling_delta"]
                    st.markdown(f"""
                    <div class="alert-banner">
                        <div style="font-size: 1.1rem; font-weight: 700;">⚠️ ILLEGAL OVERBILLING CONFIRMED</div>
                        <div>Statutory Lawful Liability: <strong>PKR {audit['fair_30d_total']:,.2f}</strong></div>
                        <div style="font-size: 1.25rem; font-weight: 800; margin-top: 4px; color: #FFE0E4;">Excess Amount Demanded: PKR {overcharge_val:,.2f}</div>
                        <div style="font-size: 0.82rem; margin-top: 6px; opacity: 0.9;">Protected status breached due to reading window exceeding 30 days (CSM §4.1).</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="verified-banner">
                        <div style="font-size: 1.1rem; font-weight: 700;">✅ BILL FULLY VERIFIED</div>
                        <div>No slab discrepancies or overcharges detected under NEPRA determinations.</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("#### صوتی وضاحت (Spoken Urdu Explanation)")
                urdu_text = generate_urdu_explanation(audit)
                st.markdown(f'<div class="urdu-box">{urdu_text}</div>', unsafe_allow_html=True)
                st.write("")
                st.audio(synthesize_urdu_voice(urdu_text), format="audio/mp3")

                with st.expander("⚖️ Auto-Drafted Ombudsman Dispute Complaint"):
                    petition_text = generate_legal_petition(audit, extracted.model_dump())
                    st.code(petition_text, language="markdown")
                    st.download_button("📥 Download Legal Petition (.txt)", data=petition_text, file_name=f"petition_{extracted.reference_number}.txt", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

    # Tab 2: Citizen Meter Anti-Ghost Reading
    with citizen_tabs[1]:
        st.subheader("Anti-Ghost Reading: Physical Meter vs Utility Index")
        st.write("Compare your physical electric meter display against the reading printed on your utility bill to catch fabricated 'table readings'.")

        gm_col1, gm_col2 = st.columns(2, gap="large")
        with gm_col1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            billed_kwh = st.number_input("Units Recorded on Disputed Bill (kWh)", value=218.0, step=1.0)
            meter_img_file = st.file_uploader("Upload Clear Photo of Meter LCD", type=["png", "jpg", "jpeg"], key="cit_meter_uploader")
            meter_img = Image.open(meter_img_file) if meter_img_file else Image.new("RGB", (300, 300), color=(14, 25, 20))
            run_meter_audit = st.button("🔍 Check Physical Reading", key="btn_cit_meter", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with gm_col2:
            if run_meter_audit or meter_img_file:
                with st.spinner("Decoding LCD counter using Multimodal Vision..."):
                    meter_data = extract_meter_reading(meter_img, use_mock=use_mock_data)
                    fraud_result = audit_meter_reading(billed_kwh, meter_data.current_reading_kwh)

                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                r1, r2, r3 = st.columns(3)
                r1.metric("Live Meter LCD", f"{meter_data.current_reading_kwh} kWh")
                r2.metric("Claimed on Bill", f"{billed_kwh} kWh")
                r3.metric("Phantom Units", f"{fraud_result['phantom_units_billed']} kWh", delta=f"-{fraud_result['phantom_units_billed']} Unconsumed" if fraud_result['is_ghost_reading'] else "Coherent", delta_color="inverse")

                if fraud_result["is_ghost_reading"]:
                    st.markdown(f"""
                    <div class="alert-banner">
                        <div style="font-size: 1.15rem; font-weight: 800;">🚨 GHOST READING DETECTED!</div>
                        <p style="margin: 8px 0;">
                            Your physical meter currently reads only <strong>{meter_data.current_reading_kwh} kWh</strong>, but the meter reader entered <strong>{billed_kwh} kWh</strong>.<br>
                            You have been charged for <strong>{fraud_result['phantom_units_billed']} unconsumed units</strong>.
                        </p>
                        <div style="font-size: 1.1rem; font-weight: 700; color: #FFE0E4;">Excess Extracted: PKR {fraud_result['estimated_unjust_enrichment_pkr']:,.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="verified-banner">
                        <div style="font-size: 1.1rem; font-weight: 700;">✅ METER READING COHERENT</div>
                        <div>Your live physical meter reading aligns with the utility records.</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    # Tab 3: 30-Day Billing Cycle Scam Detector
    with citizen_tabs[2]:
        st.subheader("30-Day Billing Cycle Scam Detector")
        st.write("DISCO meter readers routinely log entries 2–6 days late (32–36 days). This inflates monthly consumption over 200 units, knocking you into unprotected high tariffs (>PKR 34/unit).")

        cs_col1, cs_col2 = st.columns(2, gap="large")
        with cs_col1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            scam_days = st.slider("Days in Your Billing Cycle", 25, 40, 33)
            raw_units = st.slider("Units Incurred on Bill (kWh)", 50, 400, 218)
            st.markdown('</div>', unsafe_allow_html=True)

        dummy_bill = {
            "units_consumed": raw_units,
            "billing_days": scam_days,
            "total_payable": 9480.0,
            "fpa_amount": 890.50,
            "fc_surcharge": 420.0
        }
        scam_audit = audit_bill(dummy_bill, disco_code=selected_disco)

        with cs_col2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            col_a.metric("Claimed Consumption", f"{raw_units} kWh")
            col_a.metric("Normalized 30-Day Units", f"{scam_audit['normalized_30d_units']} kWh")
            col_b.metric("Days Over Statutory Limit", f"{scam_audit['days_over_limit']} Days")
            col_b.metric("Protected Status Stolen?", "YES" if scam_audit['protected_lost_by_scam'] else "NO", delta="Illegal Shift" if scam_audit['protected_lost_by_scam'] else "Compliant", delta_color="inverse")

            if scam_audit["is_cycle_scam"]:
                st.markdown(f"""
                <div class="alert-banner">
                    <h4 style="margin: 0; color: #FFE0E4;">Illegal Slab Inflation Triggered</h4>
                    <p style="margin: 6px 0;">
                        In a legal 30-day window, true usage was <strong>{scam_audit['normalized_30d_units']} units (PROTECTED)</strong>.<br>
                        Excess Surcharge Imposed on You: <strong>PKR {scam_audit['cycle_scam_penalty']:,.2f}</strong>.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Tab 4: Emergency Incident Hotline
    with citizen_tabs[3]:
        st.subheader("📞 1-Click Citizen Emergency Hotline")
        st.write("Report fallen live electrical wires, burning transformers, or leaning poles directly to the local Sub-Divisional Line Superintendent.")

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        ec1, ec2 = st.columns(2)
        with ec1:
            caller_name = st.text_input("Your Full Name", value="Muhammad Arshad")
            caller_phone = st.text_input("Mobile Contact Number", value="0300-1234567")
            cit_subdiv = st.text_input("Nearest Sub-Division", value=f"Cantt Sub-Division ({selected_disco})")
        with ec2:
            cit_feeder = st.text_input("Feeder / Mohallah Name", value="Civil Lines Feeder")
            cit_issue = st.selectbox("Type of Hazard", [
                "11 kV Broken Wire / Sagging on Road (Shock Threat)",
                "Distribution Transformer Exploded / Leaking Oil",
                "PCC Pole Snapped / Leaning on Civilian House",
                "Phase Failure / Mohallah Voltage Drop"
            ])
            cit_req = st.text_input("Urgent Repair Need", value="Emergency Feeder Tripping & Line Crew Team")

        if st.button("🚨 Dispatch Emergency Work Order to Line Crew", use_container_width=True):
            new_ticket = create_new_emergency_dispatch(
                caller_name=caller_name,
                phone=caller_phone,
                disco=selected_disco,
                sub_div=cit_subdiv,
                feeder=cit_feeder,
                issue=cit_issue,
                required_equipment=cit_req,
                priority="CRITICAL"
            )
            st.session_state["dispatch_tickets"] = pd.concat([pd.DataFrame([new_ticket]), st.session_state["dispatch_tickets"]], ignore_index=True)
            st.success(f"Emergency Ticket {new_ticket['Ticket_ID']} registered! Shift In-Charge at {cit_subdiv} notified.")
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================================
# PORTAL 2: SDO SUB-DIVISION & LINE CREW OPERATIONS
# =========================================================================
elif "SDO" in active_portal.upper():
    st.markdown(f"""
    <div class="sentinel-hero">
        <h1 style="color: #FFFFFF; margin: 0 0 6px 0; font-weight: 800; font-size: 2rem;">SDO Sub-Divisional Operations & Line Dispatch Desk</h1>
        <p style="color: #94A3B8; margin: 0; font-size: 0.95rem;">
            Operational workspace for Sub-Divisional Officers (SDO), Line Superintendents (LS-1/LS-2), and Linemen. 
            Manage active work orders, analyze high-voltage field hazards, and generate emergency dispatch work orders.
        </p>
    </div>
    """, unsafe_allow_html=True)

    sdo_tabs = st.tabs([
        "Active Line Crew Dispatch Queue", 
        "Field Hazard Triage & Geolocation Mapping", 
        "Sub-Divisional Transformer Health Radar"
    ])

    # Tab 1: Active Work Order Queue
    with sdo_tabs[0]:
        st.subheader("📋 Active Field Work Orders & Line Crew Dispatches")
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.dataframe(st.session_state["dispatch_tickets"], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Tab 2: Hazard Triage & Geolocation Mapping
    with sdo_tabs[1]:
        st.subheader("Field Hazard Structural Analysis & SDO Notice Generation")
        h_col1, h_col2 = st.columns([1.1, 1.2], gap="large")

        with h_col1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("#### 📍 Geolocation & Asset Identifier")
            f1, f2 = st.columns(2)
            with f1:
                feeder_name = st.text_input("11 kV Feeder Name", value="Kakul Rural Feeder-03")
                sub_div_name = st.text_input("Sub-Division Jurisdiction", value="Cantt Sub-Division Abbottabad")
            with f2:
                pole_tag = st.text_input("Pole / Structure Tag", value="XFR-11KV-092")
                landmark = st.text_input("Physical Landmark", value="Near Mandian Bridge, Main Mansehra Road")

            street_addr = st.text_area("Full Field Address", value="Mohallah Gulshan-e-Iqbal, Street 4, Mandian, Abbottabad, KP")
            g1, g2 = st.columns(2)
            with g1:
                lat_val = st.number_input("GPS Latitude", value=34.1989, format="%.4f")
            with g2:
                lon_val = st.number_input("GPS Longitude", value=73.2415, format="%.4f")

            h_file = st.file_uploader("Upload Field Photo (Fallen Pole / Leaning Structure / Broken Wire)", type=["png", "jpg", "jpeg"], key="sdo_field_hazard")
            h_img = Image.open(h_file) if h_file else Image.new("RGB", (300, 300), color=(25, 12, 12))
            run_h = st.button("⚠️ Triage Threat with Vision AI", key="btn_sdo_hazard", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with h_col2:
            if run_h or h_file:
                with st.spinner("Classifying high-voltage threat level..."):
                    hazard_res = classify_grid_hazard(h_img, use_mock=use_mock_data)

                loc_data = {
                    "feeder_name": feeder_name,
                    "sub_division": sub_div_name,
                    "pole_tag": pole_tag,
                    "street_address": street_addr,
                    "lat": lat_val,
                    "lon": lon_val
                }

                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0; color: #FFFFFF;">Structural Assessment</h3>
                    <span class="chip chip-hazard">Priority: {hazard_res.priority_score}/100</span>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="alert-banner" style="background: rgba(90, 15, 25, 0.7); border-left-color: #FF3B56;">
                    <strong>Threat:</strong> {hazard_res.hazard_type}<br>
                    <strong>Severity:</strong> <code>{hazard_res.severity_level}</code><br>
                    <strong>Location:</strong> {street_addr} (Feeder: {feeder_name})
                </div>
                """, unsafe_allow_html=True)

                st.write(f"**Public Safety Risk:** {hazard_res.public_safety_risk}")
                st.info(f"**Required Line Crew Dispatch Gear:** {hazard_res.estimated_repair_equipment}")

                st.map(pd.DataFrame([{"lat": lat_val, "lon": lon_val}]), zoom=13)

                with st.expander("🚨 Official SDO Emergency Line Crew Dispatch Order"):
                    memo = generate_hazard_dispatch_memo(hazard_res.model_dump(), loc_data)
                    st.code(memo, language="markdown")
                    st.download_button("📥 Download SDO Work Order (.txt)", data=memo, file_name=f"sdo_dispatch_{pole_tag}.txt", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

    # Tab 3: Sub-Divisional Transformer Health Radar
    with sdo_tabs[2]:
        st.subheader("Sub-Divisional Distribution Transformers & Thermal Health")
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        df_subdiv_tr = pd.DataFrame([
            {"Transformer_ID": "TR-CANTT-01", "Capacity": "200 kVA", "Feeder": "Kakul Rural-03", "Load_Factor": "88%", "Oil_Level": "Normal", "Status": "Optimal"},
            {"Transformer_ID": "TR-CANTT-02", "Capacity": "50 kVA", "Feeder": "Mandian-01", "Load_Factor": "142%", "Oil_Level": "Low / Leakage", "Status": "CRITICAL OVERLOAD"},
            {"Transformer_ID": "TR-CANTT-03", "Capacity": "100 kVA", "Feeder": "Supply Feeder", "Load_Factor": "74%", "Oil_Level": "Normal", "Status": "Optimal"},
            {"Transformer_ID": "TR-CANTT-04", "Capacity": "25 kVA", "Feeder": "Dhamtour Feeder", "Load_Factor": "180%", "Oil_Level": "Critical", "Status": "BURNING RISK"}
        ])
        st.dataframe(df_subdiv_tr, use_container_width=True)
        st.markdown("""
        <div class="alert-banner" style="background: rgba(90, 35, 12, 0.7); border-left-color: #FFB703;">
            <strong style="color: #FFE0A3;">SDO Operational Action Required:</strong><br>
            TR-CANTT-02 and TR-CANTT-04 are operating above 140% capacity. Requisition replacement 100 kVA units from Central Warehouse to prevent mid-phase burnout.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================================
# PORTAL 3: DISCO CENTRAL ASSET & WAREHOUSE ERP
# =========================================================================
elif "WAREHOUSE" in active_portal.upper() or "CENTRAL ASSET" in active_portal.upper():
    st.markdown(f"""
    <div class="sentinel-hero">
        <h1 style="color: #FFFFFF; margin: 0 0 6px 0; font-weight: 800; font-size: 2rem;">{selected_disco} Central Material & Asset ERP</h1>
        <p style="color: #94A3B8; margin: 0; font-size: 0.95rem;">
            Official material inventory management for Director (Procurement) and Warehouse In-Charge under <strong>{DISCO_RULES[selected_disco]['name']}</strong>. 
            Track high-voltage capital assets, manage minimum stock thresholds, and issue Sub-Divisional store vouchers.
        </p>
    </div>
    """, unsafe_allow_html=True)

    inv_df = get_inventory_dataframe()

    w1, w2, w3, w4 = st.columns(4)
    w1.metric("Available Transformers", f"{inv_df[inv_df['Category']=='Transformers']['Available'].sum()} Units", delta="State Reserve")
    w2.metric("Conductor Cables (ACSR/ABC)", f"{inv_df[inv_df['Category']=='Conductors & Cables']['Available'].sum():.1f} Km", delta="Feeder Ready")
    w3.metric("Concrete & Steel Poles", f"{inv_df[inv_df['Category']=='Poles & Structures']['Available'].sum()} Units", delta="Civil Stock")
    w4.metric("Metering Assets", f"{inv_df[inv_df['Category']=='Metering Devices']['Available'].sum()} Units", delta="Single & 3-Phase")

    erp_tabs = st.tabs([
        "Live Warehouse Inventory Registry", 
        "Store Material Requisition Desk", 
        "Material Shortage & Re-Order Alerts"
    ])

    # Tab 1: Inventory Registry
    with erp_tabs[0]:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f"### 📦 Material Stock Registry ({selected_disco})")
        cat_filter = st.multiselect("Filter by Material Category", options=inv_df["Category"].unique(), default=inv_df["Category"].unique())
        st.dataframe(inv_df[inv_df["Category"].isin(cat_filter)], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Tab 2: Requisition Voucher Desk
    with erp_tabs[1]:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📤 Issue Sub-Divisional Material Store Voucher")
        req_c1, req_c2, req_c3 = st.columns(3)
        with req_c1:
            req_item = st.selectbox("Select Equipment Code", inv_df["Item_Code"].tolist())
        with req_c2:
            req_qty = st.number_input("Issue Quantity", min_value=1, value=5)
        with req_c3:
            req_subdiv = st.text_input("Destination Sub-Division", value=f"Cantt Sub-Division ({selected_disco})")

        if st.button("📦 Authorize Store Issue Order", use_container_width=True):
            st.success(f"Voucher Authorized: Dispatched {req_qty}x {req_item} to {req_subdiv} under store release order #DISCO-MAT-{req_item[:4]}-2026.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Tab 3: Re-Order Alerts
    with erp_tabs[2]:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### ⚠️ Critical Re-Order Alerts")
        reorder_df = inv_df[inv_df["Stock_Health"] == "CRITICAL RE-ORDER"]
        if not reorder_df.empty:
            st.dataframe(reorder_df[["Item_Code", "Description", "Available", "Min_Threshold", "Stock_Health"]], use_container_width=True)
            st.markdown("""
            <div class="alert-banner">
                Stock is below the mandatory NEPRA minimum reserve threshold for emergency storm/flood readiness. Trigger procurement tenders immediately.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="verified-banner">✅ All material categories meet statutory minimum reserve thresholds.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================================
# PORTAL 4: NEPRA APEX REGULATORY OVERSIGHT
# =========================================================================
elif "NEPRA" in active_portal.upper():
    st.markdown("""
    <div class="sentinel-hero">
        <h1 style="color: #FFFFFF; margin: 0 0 6px 0; font-weight: 800; font-size: 2rem;">NEPRA Apex Regulatory Audit Command</h1>
        <p style="color: #94A3B8; margin: 0; font-size: 0.95rem;">
            Central regulatory dashboard under the National Electric Power Regulatory Authority. 
            Auditing multi-utility statutory billing compliance, 31+ day illegal cycle extensions, and political transformer diversion across all 14 DISCOs.
        </p>
    </div>
    """, unsafe_allow_html=True)

    n1, n2, n3, n4 = st.columns(4)
    n1.metric("DISCOs Under Active Audit", "14 Utilities", delta="National Grid")
    n2.metric("30-Day Cycle Breaches", "14,892 Cases", delta="+312 Detected", delta_color="inverse")
    n3.metric("Ghost Reading Penalties", "PKR 48.6M", delta="Unjust Enrichment")
    n4.metric("Diverted VIP Transformers", "87 Units Audited", delta="Re-allocated")

    nepra_tabs = st.tabs([
        "National Statutory Tariff Verification", 
        "VIP Political Asset Diversion Radar (The Hujra / Dera Audit)", 
        "Systemic 30-Day Delay Audit Analytics"
    ])

    # Tab 1: Regulatory Bill Audit
    with nepra_tabs[0]:
        st.subheader("Automated Statutory Tariff & SRO Verification")
        col1, col2 = st.columns([1, 1.25], gap="large")
        with col1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            bill_file = st.file_uploader("Upload Utility Bill Specimen", type=["png", "jpg", "jpeg"], key="reg_bill_file")
            img = Image.open(bill_file) if bill_file else Image.new("RGB", (300, 300), color=(10, 28, 22))
            run_audit = st.button("⚡ Execute Regulatory Audit", key="btn_reg_audit", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            if run_audit or bill_file:
                with st.spinner("Executing statutory NEPRA determination schedule..."):
                    extracted = extract_bill_data(img, use_mock=use_mock_data)
                    audit = audit_bill(extracted.model_dump(), disco_code=selected_disco)

                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                m1, m2, m3 = st.columns(3)
                m1.metric("Billed Units", f"{extracted.units_consumed:,.0f} kWh")
                m2.metric("Billing Days", f"{extracted.billing_days} Days", delta=f"{extracted.billing_days - 30} Days Stretch" if extracted.billing_days > 30 else "Compliant", delta_color="inverse")
                m3.metric("Billed Amount", f"PKR {extracted.total_payable:,.2f}")

                if not audit["audit_passed"]:
                    overcharge = audit["cycle_scam_penalty"] if audit["is_cycle_scam"] else audit["overbilling_delta"]
                    st.markdown(f"""
                    <div class="alert-banner">
                        <div style="font-size: 1.1rem; font-weight: 700;">⚠️ DISCO STATUTORY BREACH DETECTED</div>
                        <div>Statutory Fair Liability: <strong>PKR {audit['fair_30d_total']:,.2f}</strong></div>
                        <div style="font-size: 1.2rem; font-weight: 800; margin-top: 4px;">Unlawful Revenue Extraction: PKR {overcharge:,.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with st.expander("⚖️ Official Ombudsman Regulatory Complaint Notice"):
                    petition = generate_legal_petition(audit, extracted.model_dump())
                    st.code(petition, language="markdown")
                st.markdown('</div>', unsafe_allow_html=True)

    # Tab 2: Political Diversion
    with nepra_tabs[1]:
        st.subheader("Political Asset Diversion Radar (The Hujra / Dera Audit)")
        df_grid = pd.DataFrame([
            {"Transformer_ID": "XFR-ISB-01", "Capacity": "200 kVA", "Location": "Private Dera Compound", "Connected_Houses": 3, "Status": "Diverted (Political)", "lat": 33.6844, "lon": 73.0479},
            {"Transformer_ID": "XFR-ISB-02", "Capacity": "25 kVA", "Location": "Mohallah Farooqia", "Connected_Houses": 184, "Status": "Overloaded (Burning)", "lat": 33.6930, "lon": 73.0550},
            {"Transformer_ID": "XFR-ISB-03", "Capacity": "100 kVA", "Location": "Main Bazaar Feeder", "Connected_Houses": 92, "Status": "Balanced", "lat": 33.7000, "lon": 73.0600},
            {"Transformer_ID": "XFR-ISB-04", "Capacity": "200 kVA", "Location": "VIP Hujra Farmhouse", "Connected_Houses": 2, "Status": "Diverted (Political)", "lat": 33.7120, "lon": 73.0720},
        ])
        m_c1, m_c2 = st.columns([1.2, 1], gap="large")
        with m_c1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.map(df_grid, latitude="lat", longitude="lon", size=30, zoom=12)
            st.markdown('</div>', unsafe_allow_html=True)
        with m_c2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.dataframe(df_grid[["Transformer_ID", "Capacity", "Connected_Houses", "Status"]], use_container_width=True)
            st.markdown("""
            <div class="alert-banner" style="background: rgba(90, 35, 12, 0.7); border-left-color: #FFB703;">
                <strong style="color: #FFE0A3;">NEPRA Statutory Enforcement Directive:</strong><br>
                400 kVA of state transformer capacity is diverted to only 5 private consumers, while 184 rural families are tethered to an overloaded 25 kVA unit. Immediate recovery order generated for SDO concerned.
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Tab 3: Systemic Analytics
    with nepra_tabs[2]:
        st.subheader("DISCO-Wide 30-Day Billing Cycle Delay Index")
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        df_delay = pd.DataFrame([
            {"DISCO": "PESCO", "Avg_Cycle_Days": 34.2, "Impacted_Consumers": "410,000", "Excess_Revenue_Extracted": "PKR 142.5M"},
            {"DISCO": "IESCO", "Avg_Cycle_Days": 31.8, "Impacted_Consumers": "180,000", "Excess_Revenue_Extracted": "PKR 54.2M"},
            {"DISCO": "LESCO", "Avg_Cycle_Days": 33.4, "Impacted_Consumers": "520,000", "Excess_Revenue_Extracted": "PKR 188.0M"},
            {"DISCO": "HAZECO", "Avg_Cycle_Days": 32.9, "Impacted_Consumers": "95,000", "Excess_Revenue_Extracted": "PKR 28.4M"},
            {"DISCO": "MEPCO", "Avg_Cycle_Days": 33.9, "Impacted_Consumers": "380,000", "Excess_Revenue_Extracted": "PKR 126.1M"}
        ])
        st.dataframe(df_delay, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
