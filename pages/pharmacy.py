"""
pages/pharmacy.py - Pharmacy Dashboard and Features

Pharmacy portal including:
- View prescriptions
- Mark medicines as purchased
- Upload bills
- Adherence tracking
"""

import streamlit as st
from datetime import datetime
import pandas as pd

from data import (
    PATIENTS, PRESCRIPTIONS,
    get_pharmacy, get_prescription, update_prescription,
    get_patient
)

from utils import calculate_adherence, generate_qr_code

from auth import get_current_user, get_current_user_id, logout


def render_pharmacy_dashboard():
    """
    Main function to render the complete pharmacy dashboard.
    """
    user = get_current_user()
    pharmacy_id = get_current_user_id()
    
    if not user:
        st.error("Session expired. Please login again.")
        return
    
    # Sidebar navigation
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/hospital-2.png", width=80)
        st.markdown(f"### 💊 {user['name']}")
        st.markdown(f"**ID:** `{pharmacy_id}`")
        st.markdown("---")
        
        menu_options = [
            ("🏠 Dashboard", "dashboard"),
            ("🔍 Search Prescription", "search"),
            ("📋 All Prescriptions", "prescriptions"),
            ("📊 Adherence Reports", "adherence"),
            ("📷 Scan QR", "scan"),
        ]
        
        for label, key in menu_options:
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.current_page = key
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            logout()
            st.rerun()
    
    # Main content
    page = st.session_state.get('current_page', 'dashboard')
    
    if page == "dashboard":
        render_pharmacy_home(user, pharmacy_id)
    elif page == "search":
        render_prescription_search(pharmacy_id)
    elif page == "prescriptions":
        render_all_prescriptions(pharmacy_id)
    elif page == "adherence":
        render_adherence_reports(pharmacy_id)
    elif page == "scan":
        render_qr_scanner(pharmacy_id)


# ============================================================================
# DASHBOARD HOME
# ============================================================================

def render_pharmacy_home(user, pharmacy_id):
    """Render pharmacy dashboard home page."""
    st.title("💊 Pharmacy Dashboard")
    st.markdown(f"Welcome, **{user['name']}**!")
    
    # Get all prescriptions
    all_prescriptions = list(PRESCRIPTIONS.values())
    active_prescriptions = [p for p in all_prescriptions if p['status'] == 'active']
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📋 Active Prescriptions", len(active_prescriptions))
    
    with col2:
        pending_meds = sum(
            len([m for m in p['medicines'] if not m.get('purchased')])
            for p in active_prescriptions
        )
        st.metric("💊 Pending Medicines", pending_meds)
    
    with col3:
        fulfilled = len([p for p in all_prescriptions if p.get('pharmacy_id') == pharmacy_id])
        st.metric("✅ Fulfilled by Us", fulfilled)
    
    with col4:
        st.metric("📅 Today's Date", datetime.now().strftime("%Y-%m-%d"))
    
    st.markdown("---")
    
    # Recent prescriptions
    st.subheader("📋 Recent Active Prescriptions")
    
    if not active_prescriptions:
        st.info("No active prescriptions in the system.")
    else:
        for rx in sorted(active_prescriptions, key=lambda x: x['created_at'], reverse=True)[:5]:
            patient = PATIENTS.get(rx['patient_health_id'], {})
            pending = len([m for m in rx['medicines'] if not m.get('purchased')])
            
            with st.expander(f"📋 {rx['prescription_id']} - {patient.get('name', 'Unknown')} ({pending} pending)"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Patient:** {patient.get('name', 'Unknown')}")
                    st.write(f"**Health ID:** {rx['patient_health_id']}")
                    st.write(f"**Doctor:** {rx['doctor_name']}")
                with col2:
                    st.write(f"**Date:** {rx['created_at'][:10]}")
                    st.write(f"**Diagnosis:** {rx['diagnosis']}")
                
                st.subheader("Medicines")
                for med in rx['medicines']:
                    icon = "✅" if med.get('purchased') else "⬜"
                    st.write(f"{icon} {med['name']} - {med['dosage']} ({med['frequency']})")
                
                if st.button("Process Prescription", key=f"process_{rx['prescription_id']}"):
                    st.session_state.selected_prescription = rx['prescription_id']
                    st.session_state.current_page = 'search'
                    st.rerun()


# ============================================================================
# PRESCRIPTION SEARCH
# ============================================================================

def render_prescription_search(pharmacy_id):
    """Render prescription search and processing page."""
    st.title("🔍 Search & Process Prescription")
    
    # Search options
    search_type = st.radio("Search by:", ["Prescription ID", "Patient Health ID"], horizontal=True)
    
    if search_type == "Prescription ID":
        search_query = st.text_input(
            "Enter Prescription ID",
            value=st.session_state.get('selected_prescription', ''),
            placeholder="RX-XXXXXXXXX-XXX"
        )
    else:
        search_query = st.text_input(
            "Enter Patient Health ID",
            placeholder="HID-XXXXXX"
        )
    
    if st.button("🔍 Search", type="primary"):
        if search_query:
            if search_type == "Prescription ID":
                rx = get_prescription(search_query)
                if rx:
                    display_prescription_details(rx, pharmacy_id)
                else:
                    st.error("Prescription not found.")
            else:
                # Find prescriptions for patient
                patient_rx = [
                    p for p in PRESCRIPTIONS.values()
                    if p['patient_health_id'] == search_query.upper()
                ]
                if patient_rx:
                    st.success(f"Found {len(patient_rx)} prescription(s) for this patient.")
                    for rx in sorted(patient_rx, key=lambda x: x['created_at'], reverse=True):
                        display_prescription_details(rx, pharmacy_id)
                else:
                    st.error("No prescriptions found for this patient.")
        else:
            st.warning("Please enter a search query.")


def display_prescription_details(rx, pharmacy_id):
    """Display prescription details with processing options."""
    patient = PATIENTS.get(rx['patient_health_id'], {})
    
    st.markdown("---")
    st.subheader(f"📋 Prescription: {rx['prescription_id']}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Patient:** {patient.get('name', 'Unknown')}")
        st.write(f"**Health ID:** {rx['patient_health_id']}")
        st.write(f"**Blood Group:** {patient.get('blood_group', 'N/A')}")
        
        allergies = patient.get('allergies', [])
        if allergies:
            st.warning(f"⚠️ **Allergies:** {', '.join(allergies)}")
    
    with col2:
        st.write(f"**Doctor:** {rx['doctor_name']}")
        st.write(f"**Date:** {rx['created_at'][:10]}")
        st.write(f"**Diagnosis:** {rx['diagnosis']}")
        st.write(f"**Status:** {rx['status'].title()}")
    
    st.markdown("---")
    st.subheader("💊 Medicines")
    
    # Display medicines with checkboxes
    all_purchased = True
    medicine_updates = []
    
    for i, med in enumerate(rx['medicines']):
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            purchased = st.checkbox(
                f"**{med['name']}** - {med['dosage']}",
                value=med.get('purchased', False),
                key=f"med_{rx['prescription_id']}_{i}"
            )
            medicine_updates.append(purchased)
        with col2:
            st.write(f"{med['frequency']} for {med['duration']}")
        with col3:
            if purchased:
                st.write("✅ Purchased")
            else:
                st.write("⬜ Pending")
                all_purchased = False
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        bill_amount = st.number_input("Bill Amount (₹)", min_value=0.0, step=10.0)
    with col2:
        bill_file = st.file_uploader("Upload Bill (optional)", type=['pdf', 'jpg', 'png'])
    
    if st.button("💾 Update Prescription", type="primary"):
        # Update medicine purchase status
        updated_medicines = []
        for i, med in enumerate(rx['medicines']):
            updated_med = med.copy()
            updated_med['purchased'] = medicine_updates[i]
            updated_medicines.append(updated_med)
        
        updates = {
            'medicines': updated_medicines,
            'pharmacy_id': pharmacy_id,
            'purchase_date': datetime.now().isoformat(),
            'bill_amount': bill_amount if bill_amount > 0 else None
        }
        
        # Check if all medicines are purchased
        if all(m['purchased'] for m in updated_medicines):
            updates['status'] = 'completed'
        
        update_prescription(rx['prescription_id'], updates)
        st.success("✅ Prescription updated successfully!")
        
        if 'selected_prescription' in st.session_state:
            del st.session_state.selected_prescription
        
        st.rerun()


# ============================================================================
# ALL PRESCRIPTIONS
# ============================================================================

def render_all_prescriptions(pharmacy_id):
    """Render all prescriptions page."""
    st.title("📋 All Prescriptions")
    
    all_prescriptions = list(PRESCRIPTIONS.values())
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox("Status", ["All", "Active", "Completed", "Cancelled"])
    with col2:
        fulfilled_filter = st.checkbox("Show only fulfilled by us")
    
    # Apply filters
    filtered = all_prescriptions
    if status_filter != "All":
        filtered = [p for p in filtered if p['status'] == status_filter.lower()]
    if fulfilled_filter:
        filtered = [p for p in filtered if p.get('pharmacy_id') == pharmacy_id]
    
    st.markdown("---")
    st.write(f"Showing {len(filtered)} prescription(s)")
    
    if not filtered:
        st.info("No prescriptions match your filters.")
    else:
        # Create DataFrame for display
        data = []
        for rx in filtered:
            patient = PATIENTS.get(rx['patient_health_id'], {})
            pending = len([m for m in rx['medicines'] if not m.get('purchased')])
            total = len(rx['medicines'])
            
            data.append({
                'Prescription ID': rx['prescription_id'],
                'Patient': patient.get('name', 'Unknown'),
                'Date': rx['created_at'][:10],
                'Medicines': f"{total - pending}/{total}",
                'Status': rx['status'].title(),
                'Bill': f"₹{rx.get('bill_amount', 0) or 0}"
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)


# ============================================================================
# ADHERENCE REPORTS
# ============================================================================

def render_adherence_reports(pharmacy_id):
    """Render adherence reports page."""
    st.title("📊 Adherence Reports")
    
    st.write("Track medicine adherence across patients.")
    
    # Group prescriptions by patient
    patient_adherence = {}
    
    for rx in PRESCRIPTIONS.values():
        health_id = rx['patient_health_id']
        if health_id not in patient_adherence:
            patient_adherence[health_id] = []
        patient_adherence[health_id].append(rx)
    
    if not patient_adherence:
        st.info("No prescription data available.")
        return
    
    # Overall stats
    st.subheader("📈 Overall Statistics")
    
    total_patients = len(patient_adherence)
    total_prescriptions = len(PRESCRIPTIONS)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Patients", total_patients)
    with col2:
        st.metric("Total Prescriptions", total_prescriptions)
    with col3:
        # Calculate overall adherence
        all_rx = list(PRESCRIPTIONS.values())
        overall = calculate_adherence(all_rx)
        st.metric("Overall Adherence", f"{overall['adherence_rate']}%")
    
    st.markdown("---")
    
    # Patient-wise adherence
    st.subheader("👥 Patient-wise Adherence")
    
    adherence_data = []
    for health_id, prescriptions in patient_adherence.items():
        patient = PATIENTS.get(health_id, {})
        adherence = calculate_adherence(prescriptions)
        
        adherence_data.append({
            'Patient': patient.get('name', 'Unknown'),
            'Health ID': health_id,
            'Prescriptions': len(prescriptions),
            'Adherence Rate': f"{adherence['adherence_rate']}%",
            'Pending': adherence['pending'],
            'Status': adherence['status'].replace('_', ' ').title()
        })
    
    df = pd.DataFrame(adherence_data)
    
    # Color code based on status
    st.dataframe(df, use_container_width=True)
    
    # Adherence distribution chart
    import plotly.express as px
    
    adherence_categories = {'good': 0, 'needs_attention': 0, 'poor': 0}
    for health_id, prescriptions in patient_adherence.items():
        adherence = calculate_adherence(prescriptions)
        adherence_categories[adherence['status']] += 1
    
    fig = px.pie(
        values=list(adherence_categories.values()),
        names=['Good (≥80%)', 'Needs Attention (50-79%)', 'Poor (<50%)'],
        title="Adherence Distribution",
        color_discrete_sequence=['#28a745', '#ffc107', '#dc3545']
    )
    st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# QR SCANNER
# ============================================================================

def render_qr_scanner(pharmacy_id):
    """Render QR scanner placeholder page."""
    st.title("📷 Scan QR Code")
    
    st.info("🚧 This is a demonstration interface. In a production system, this would integrate with a camera for QR scanning.")
    
    st.write("""
    ### How it works:
    1. Patient shows their Emergency QR code
    2. Scan the QR code to get their Health ID
    3. Search for their prescriptions
    """)
    
    # Manual entry option
    st.markdown("---")
    st.subheader("Manual Entry")
    
    health_id = st.text_input("Enter Health ID from QR Code", placeholder="HID-XXXXXX")
    
    if st.button("🔍 Find Prescriptions", type="primary"):
        if health_id:
            patient = get_patient(health_id.upper())
            if patient:
                st.success(f"Patient found: **{patient['name']}**")
                
                # Find prescriptions
                patient_rx = [
                    p for p in PRESCRIPTIONS.values()
                    if p['patient_health_id'] == health_id.upper() and p['status'] == 'active'
                ]
                
                if patient_rx:
                    st.write(f"Found {len(patient_rx)} active prescription(s)")
                    
                    for rx in patient_rx:
                        pending = len([m for m in rx['medicines'] if not m.get('purchased')])
                        st.write(f"• {rx['prescription_id']} - {pending} pending medicines")
                    
                    if st.button("Go to Process Prescriptions"):
                        st.session_state.current_page = 'search'
                        st.rerun()
                else:
                    st.info("No active prescriptions for this patient.")
            else:
                st.error("Patient not found.")
        else:
            st.warning("Please enter a Health ID.")
