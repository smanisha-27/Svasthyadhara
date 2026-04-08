"""
pages/patient.py - Patient Dashboard and Features

Complete patient portal including:
- Profile management
- Medical timeline
- Appointment booking
- Health tracking
- Prescriptions
- Emergency QR
- Teleconsultation (placeholder)
"""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data import (
    PATIENTS, HOSPITALS, PHARMACIES,
    get_patient, update_patient,
    get_patient_appointments, create_appointment, update_appointment,
    get_patient_prescriptions,
    get_patient_medical_records,
    add_health_reading, get_health_readings,
    add_reminder, get_reminders,
    get_patient_consents, grant_consent, revoke_consent,
    link_family_member, get_family_members,
    NEARBY_HOSPITALS, NEARBY_PHARMACIES
)

from utils import (
    generate_emergency_qr, check_symptoms, predict_health_risks,
    check_drug_interactions, mock_ocr_scan, generate_smart_alerts,
    calculate_adherence
)

from auth import get_current_user, get_current_user_id, logout


def render_patient_dashboard():
    """
    Main function to render the complete patient dashboard.
    """
    user = get_current_user()
    health_id = get_current_user_id()
    
    if not user:
        st.error("Session expired. Please login again.")
        return
    
    # Sidebar navigation
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/hospital-2.png", width=80)        
        st.markdown(f"### 👤 {user['name']}")
        st.markdown(f"**Health ID:** `{health_id}`")
        st.markdown("---")
        
        # Navigation menu
        menu_options = [
            ("🏠 Dashboard", "dashboard"),
            ("👤 My Profile", "profile"),
            ("📅 Appointments", "appointments"),
            ("💊 Prescriptions", "prescriptions"),
            ("📋 Medical Records", "records"),
            ("📊 Health Tracking", "tracking"),
            ("🔔 Reminders", "reminders"),
            ("🚨 Emergency QR", "emergency"),
            ("🩺 Symptom Checker", "symptoms"),
            ("👨‍👩‍👧 Family Members", "family"),
            ("🔐 Consent Management", "consent"),
            ("📍 Nearby Facilities", "nearby"),
            ("💬 Teleconsultation", "teleconsult"),
        ]
        
        for label, key in menu_options:
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.current_page = key
        
        st.markdown("---")
        
        # Language selector
        languages = {"en": "🇺🇸 English", "es": "🇪🇸 Español", "hi": "🇮🇳 हिंदी", "fr": "🇫🇷 Français"}
        selected_lang = st.selectbox("Language", list(languages.keys()), 
                                     format_func=lambda x: languages[x])
        st.session_state.language = selected_lang
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            logout()
            st.rerun()
    
    # Main content area
    page = st.session_state.get('current_page', 'dashboard')
    
    if page == "dashboard":
        render_dashboard_home(user, health_id)
    elif page == "profile":
        render_profile(user, health_id)
    elif page == "appointments":
        render_appointments(user, health_id)
    elif page == "prescriptions":
        render_prescriptions(user, health_id)
    elif page == "records":
        render_medical_records(user, health_id)
    elif page == "tracking":
        render_health_tracking(user, health_id)
    elif page == "reminders":
        render_reminders(user, health_id)
    elif page == "emergency":
        render_emergency_qr(user, health_id)
    elif page == "symptoms":
        render_symptom_checker()
    elif page == "family":
        render_family_members(user, health_id)
    elif page == "consent":
        render_consent_management(user, health_id)
    elif page == "nearby":
        render_nearby_facilities()
    elif page == "teleconsult":
        render_teleconsultation(user, health_id)


# ============================================================================
# DASHBOARD HOME
# ============================================================================

def render_dashboard_home(user, health_id):
    """Render the main dashboard home page with overview."""
    st.title("🏥 Patient Dashboard")
    st.markdown(f"Welcome back, **{user['name']}**!")
    
    # Smart Alerts Section
    appointments = get_patient_appointments(health_id)
    prescriptions = get_patient_prescriptions(health_id)
    health_readings = get_health_readings(health_id)
    
    alerts = generate_smart_alerts(user, appointments, prescriptions, health_readings)
    
    if alerts:
        st.subheader("🔔 Smart Alerts")
        for alert in alerts[:3]:  # Show top 3 alerts
            priority_colors = {"high": "🔴", "medium": "🟡", "low": "🟢", "info": "🔵"}
            with st.expander(f"{priority_colors.get(alert['priority'], '⚪')} {alert['title']}", expanded=alert['priority'] == 'high'):
                st.write(alert['message'])
                st.caption(f"Action: {alert['action']}")
    
    st.markdown("---")
    
    # Quick Stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        upcoming_apts = len([a for a in appointments if a['status'] == 'scheduled'])
        st.metric("📅 Upcoming Appointments", upcoming_apts)
    
    with col2:
        active_rx = len([p for p in prescriptions if p['status'] == 'active'])
        st.metric("💊 Active Prescriptions", active_rx)
    
    with col3:
        adherence = calculate_adherence(prescriptions)
        st.metric("💪 Medicine Adherence", f"{adherence['adherence_rate']}%")
    
    with col4:
        records = get_patient_medical_records(health_id)
        st.metric("📋 Medical Records", len(records))
    
    st.markdown("---")
    
    # Recent Activity Timeline
    st.subheader("📜 Recent Activity")
    
    # Combine and sort recent activities
    activities = []
    
    for apt in appointments[-5:]:
        activities.append({
            'type': '📅 Appointment',
            'title': f"Appointment with {apt['doctor_name']}",
            'date': apt['appointment_date'],
            'status': apt['status'],
            'detail': f"{apt['department']} - {apt['appointment_time']}"
        })
    
    for rx in prescriptions[-5:]:
        activities.append({
            'type': '💊 Prescription',
            'title': f"Prescription from {rx['doctor_name']}",
            'date': rx['created_at'][:10],
            'status': rx['status'],
            'detail': f"{len(rx['medicines'])} medicine(s)"
        })
    
    for record in get_patient_medical_records(health_id)[-5:]:
        activities.append({
            'type': '📋 Record',
            'title': f"Consultation - {record['diagnosis']}",
            'date': record['created_at'][:10],
            'status': 'completed',
            'detail': f"Dr. {record['doctor_name']}"
        })
    
    # Sort by date descending
    activities.sort(key=lambda x: x['date'], reverse=True)
    
    if activities:
        for activity in activities[:5]:
            status_color = "🟢" if activity['status'] == 'completed' else "🟡" if activity['status'] == 'scheduled' else "🔴"
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{activity['type']}**: {activity['title']}")
                    st.caption(f"{activity['detail']} | {activity['date']}")
                with col2:
                    st.write(f"{status_color} {activity['status'].title()}")
                st.markdown("---")
    else:
        st.info("No recent activity. Start by booking an appointment!")
    
    # Quick Health Stats Chart
    if health_readings:
        st.subheader("📊 Quick Health Overview")
        render_quick_health_chart(health_readings)


def render_quick_health_chart(readings):
    """Render a quick overview chart of health readings."""
    bp_readings = [r for r in readings if r['type'] == 'bp']
    
    if bp_readings:
        dates = []
        systolic = []
        diastolic = []
        
        for r in bp_readings[-7:]:
            dates.append(r['recorded_at'][:10])
            try:
                sys, dia = map(int, r['value'].split('/'))
                systolic.append(sys)
                diastolic.append(dia)
            except (ValueError, AttributeError):
                systolic.append(None)
                diastolic.append(None)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=systolic, mode='lines+markers', name='Systolic'))
        fig.add_trace(go.Scatter(x=dates, y=diastolic, mode='lines+markers', name='Diastolic'))
        fig.update_layout(
            title="Blood Pressure Trend (Last 7 Readings)",
            xaxis_title="Date",
            yaxis_title="mmHg",
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# PROFILE
# ============================================================================

def render_profile(user, health_id):
    """Render patient profile page."""
    st.title("👤 My Profile")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Personal Information")
        
        with st.form("profile_form"):
            name = st.text_input("Full Name", value=user.get('name', ''))
            email = st.text_input("Email", value=user.get('email', ''), disabled=True)
            phone = st.text_input("Phone", value=user.get('phone', ''))
            dob = st.text_input("Date of Birth", value=user.get('dob', ''))
            blood_group = st.selectbox(
                "Blood Group",
                ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                index=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].index(user.get('blood_group', 'A+'))
            )
            emergency_contact = st.text_input("Emergency Contact", value=user.get('emergency_contact', ''))
            allergies = st.text_area(
                "Known Allergies (comma-separated)",
                value=', '.join(user.get('allergies', []))
            )
            
            if st.form_submit_button("Update Profile", type="primary"):
                updates = {
                    'name': name,
                    'phone': phone,
                    'dob': dob,
                    'blood_group': blood_group,
                    'emergency_contact': emergency_contact,
                    'allergies': [a.strip() for a in allergies.split(',') if a.strip()]
                }
                update_patient(health_id, updates)
                st.session_state.user_data.update(updates)
                st.success("Profile updated successfully!")
                st.rerun()
    
    with col2:
        st.subheader("Health ID Card")
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 15px; color: white;">
            <h4 style="margin: 0; color: white;">🏥 Health Card</h4>
            <hr style="border-color: rgba(255,255,255,0.3);">
            <p style="margin: 5px 0;"><strong>ID:</strong> {health_id}</p>
            <p style="margin: 5px 0;"><strong>Name:</strong> {user['name']}</p>
            <p style="margin: 5px 0;"><strong>Blood:</strong> {user.get('blood_group', 'N/A')}</p>
            <p style="margin: 5px 0;"><strong>Emergency:</strong> {user.get('emergency_contact', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("Insurance Information")
        
        insurance = user.get('insurance_info', {})
        with st.form("insurance_form"):
            provider = st.text_input("Insurance Provider", value=insurance.get('provider', ''))
            policy_number = st.text_input("Policy Number", value=insurance.get('policy_number', ''))
            coverage_type = st.selectbox(
                "Coverage Type",
                ["Basic", "Standard", "Premium", "Comprehensive"],
                index=0
            )
            
            if st.form_submit_button("Save Insurance Info"):
                insurance_updates = {
                    'insurance_info': {
                        'provider': provider,
                        'policy_number': policy_number,
                        'coverage_type': coverage_type
                    }
                }
                update_patient(health_id, insurance_updates)
                st.session_state.user_data.update(insurance_updates)
                st.success("Insurance information saved!")


# ============================================================================
# APPOINTMENTS
# ============================================================================

def render_appointments(user, health_id):
    """Render appointments page."""
    st.title("📅 My Appointments")
    
    tab1, tab2 = st.tabs(["📋 View Appointments", "➕ Book New Appointment"])
    
    with tab1:
        appointments = get_patient_appointments(health_id)
        
        if not appointments:
            st.info("You don't have any appointments yet. Book one using the tab above!")
        else:
            # Filter options
            status_filter = st.selectbox("Filter by Status", ["All", "Scheduled", "Completed", "Cancelled"])
            
            filtered_apts = appointments
            if status_filter != "All":
                filtered_apts = [a for a in appointments if a['status'] == status_filter.lower()]
            
            for apt in sorted(filtered_apts, key=lambda x: x['appointment_date'], reverse=True):
                status_colors = {"scheduled": "🟡", "completed": "🟢", "cancelled": "🔴"}
                
                with st.expander(f"{status_colors.get(apt['status'], '⚪')} {apt['appointment_date']} - {apt['doctor_name']} ({apt['status'].title()})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Appointment ID:** {apt['appointment_id']}")
                        st.write(f"**Doctor:** {apt['doctor_name']}")
                        st.write(f"**Department:** {apt['department']}")
                    with col2:
                        st.write(f"**Date:** {apt['appointment_date']}")
                        st.write(f"**Time:** {apt['appointment_time']}")
                        st.write(f"**Reason:** {apt['reason']}")
                    
                    if apt['status'] == 'scheduled':
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("❌ Cancel", key=f"cancel_{apt['appointment_id']}"):
                                update_appointment(apt['appointment_id'], {'status': 'cancelled'})
                                st.success("Appointment cancelled.")
                                st.rerun()
    
    with tab2:
        st.subheader("Book New Appointment")
        
        with st.form("book_appointment"):
            # Select hospital
            hospital_options = {h['hospital_id']: h['name'] for h in HOSPITALS.values()}
            selected_hospital = st.selectbox(
                "Select Hospital",
                list(hospital_options.keys()),
                format_func=lambda x: hospital_options[x]
            )
            
            # Get hospital details for departments
            hospital = HOSPITALS.get(selected_hospital, {})
            departments = hospital.get('specializations', ['General Medicine'])
            
            col1, col2 = st.columns(2)
            with col1:
                department = st.selectbox("Department", departments)
                doctor_name = st.text_input("Preferred Doctor (optional)")
            with col2:
                apt_date = st.date_input(
                    "Appointment Date",
                    min_value=datetime.now().date(),
                    max_value=datetime.now().date() + timedelta(days=30)
                )
                apt_time = st.selectbox(
                    "Time Slot",
                    ["09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", 
                     "02:00 PM", "03:00 PM", "04:00 PM", "05:00 PM"]
                )
            
            reason = st.text_area("Reason for Visit")
            
            if st.form_submit_button("📅 Book Appointment", type="primary"):
                if not reason:
                    st.error("Please provide a reason for the visit.")
                else:
                    apt_id = create_appointment(
                        patient_health_id=health_id,
                        hospital_id=selected_hospital,
                        doctor_name=doctor_name or f"Dr. {department} Specialist",
                        department=department,
                        appointment_date=apt_date.strftime("%Y-%m-%d"),
                        appointment_time=apt_time,
                        reason=reason
                    )
                    st.success(f"✅ Appointment booked successfully! ID: {apt_id}")
                    st.rerun()


# ============================================================================
# PRESCRIPTIONS
# ============================================================================

def render_prescriptions(user, health_id):
    """Render prescriptions page."""
    st.title("💊 My Prescriptions")
    
    prescriptions = get_patient_prescriptions(health_id)
    
    if not prescriptions:
        st.info("You don't have any prescriptions yet.")
        return
    
    # Summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        active = len([p for p in prescriptions if p['status'] == 'active'])
        st.metric("Active Prescriptions", active)
    with col2:
        adherence = calculate_adherence(prescriptions)
        st.metric("Adherence Rate", f"{adherence['adherence_rate']}%")
    with col3:
        pending = adherence['pending']
        st.metric("Pending Medicines", pending)
    
    st.markdown("---")
    
    # Drug interaction check
    all_medicines = []
    for rx in prescriptions:
        if rx['status'] == 'active':
            for med in rx.get('medicines', []):
                all_medicines.append(med['name'])
    
    if len(all_medicines) >= 2:
        interactions = check_drug_interactions(all_medicines)
        if interactions:
            st.warning("⚠️ Potential Drug Interactions Detected")
            for interaction in interactions:
                severity_icon = "🔴" if interaction['severity'] == 'high' else "🟡"
                st.write(f"{severity_icon} **{interaction['drug1']}** + **{interaction['drug2']}**: {interaction['description']}")
            st.caption("Always consult your doctor or pharmacist about these interactions.")
            st.markdown("---")
    
    # List prescriptions
    for rx in sorted(prescriptions, key=lambda x: x['created_at'], reverse=True):
        status_icon = "🟢" if rx['status'] == 'active' else "🔵" if rx['status'] == 'completed' else "🔴"
        
        with st.expander(f"{status_icon} {rx['prescription_id']} - {rx['diagnosis']} ({rx['status'].title()})"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Doctor:** {rx['doctor_name']}")
                st.write(f"**Date:** {rx['created_at'][:10]}")
                st.write(f"**Diagnosis:** {rx['diagnosis']}")
            with col2:
                if rx['notes']:
                    st.write(f"**Notes:** {rx['notes']}")
            
            st.subheader("Medicines")
            for i, med in enumerate(rx['medicines']):
                col1, col2 = st.columns([3, 1])
                with col1:
                    purchased_icon = "✅" if med.get('purchased') else "⬜"
                    st.write(f"{purchased_icon} **{med['name']}** - {med['dosage']}")
                    st.caption(f"Frequency: {med['frequency']} | Duration: {med['duration']}")
                with col2:
                    if not med.get('purchased'):
                        st.write("Pending")


# ============================================================================
# MEDICAL RECORDS
# ============================================================================

def render_medical_records(user, health_id):
    """Render medical records page."""
    st.title("📋 Medical Records")
    
    tab1, tab2 = st.tabs(["📜 View Records", "📤 Upload Documents"])
    
    with tab1:
        records = get_patient_medical_records(health_id)
        
        if not records:
            st.info("No medical records found.")
        else:
            for record in sorted(records, key=lambda x: x['created_at'], reverse=True):
                with st.expander(f"📋 {record['created_at'][:10]} - {record['diagnosis']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Doctor:** {record['doctor_name']}")
                        st.write(f"**Date:** {record['created_at'][:10]}")
                        st.write(f"**Symptoms:** {', '.join(record.get('symptoms', []))}")
                    with col2:
                        st.write(f"**Diagnosis:** {record['diagnosis']}")
                        st.write(f"**Treatment:** {record['treatment']}")
                    
                    if record.get('vitals'):
                        st.subheader("Vitals Recorded")
                        vitals = record['vitals']
                        cols = st.columns(4)
                        if vitals.get('bp'):
                            cols[0].metric("BP", vitals['bp'])
                        if vitals.get('pulse'):
                            cols[1].metric("Pulse", vitals['pulse'])
                        if vitals.get('temperature'):
                            cols[2].metric("Temp", f"{vitals['temperature']}°F")
                    
                    if record.get('notes'):
                        st.info(f"📝 Notes: {record['notes']}")
    
    with tab2:
        st.subheader("Upload Medical Documents")
        st.write("Upload prescriptions, lab reports, or other medical documents.")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'png', 'jpg', 'jpeg'],
            help="Supported formats: PDF, PNG, JPG"
        )
        
        if uploaded_file:
            st.success(f"File '{uploaded_file.name}' ready for processing.")
            
            col1, col2 = st.columns(2)
            with col1:
                doc_type = st.selectbox(
                    "Document Type",
                    ["Prescription", "Lab Report", "Scan/X-Ray", "Discharge Summary", "Other"]
                )
            with col2:
                doc_date = st.date_input("Document Date")
            
            if st.button("📤 Upload & Process", type="primary"):
                with st.spinner("Processing document..."):
                    # Mock OCR processing
                    ocr_result = mock_ocr_scan(uploaded_file.read())
                    
                    st.success("Document processed successfully!")
                    st.subheader("Extracted Content (OCR)")
                    st.code(ocr_result['extracted_text'])
                    st.caption(f"Confidence: {ocr_result['confidence']:.1%}")


# ============================================================================
# HEALTH TRACKING
# ============================================================================

def render_health_tracking(user, health_id):
    """Render health tracking page with charts."""
    st.title("📊 Health Tracking")
    
    tab1, tab2 = st.tabs(["📈 View Trends", "➕ Add Reading"])
    
    with tab1:
        readings = get_health_readings(health_id)
        
        if not readings:
            st.info("No health readings recorded yet. Start tracking your health metrics!")
        else:
            # BP Chart
            bp_readings = [r for r in readings if r['type'] == 'bp']
            if bp_readings:
                st.subheader("🩸 Blood Pressure")
                
                dates = []
                systolic = []
                diastolic = []
                
                for r in bp_readings:
                    dates.append(r['recorded_at'][:10])
                    try:
                        sys, dia = map(int, r['value'].split('/'))
                        systolic.append(sys)
                        diastolic.append(dia)
                    except (ValueError, AttributeError):
                        systolic.append(None)
                        diastolic.append(None)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=dates, y=systolic, mode='lines+markers', 
                                        name='Systolic', line=dict(color='#FF6B6B')))
                fig.add_trace(go.Scatter(x=dates, y=diastolic, mode='lines+markers', 
                                        name='Diastolic', line=dict(color='#4ECDC4')))
                fig.add_hline(y=120, line_dash="dash", line_color="green", 
                             annotation_text="Normal Systolic")
                fig.add_hline(y=80, line_dash="dash", line_color="blue", 
                             annotation_text="Normal Diastolic")
                fig.update_layout(title="Blood Pressure Trend", xaxis_title="Date", 
                                 yaxis_title="mmHg", height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            # Sugar Chart
            sugar_readings = [r for r in readings if r['type'] == 'sugar']
            if sugar_readings:
                st.subheader("🍬 Blood Sugar")
                
                dates = [r['recorded_at'][:10] for r in sugar_readings]
                values = [float(r['value']) for r in sugar_readings]
                
                fig = px.line(x=dates, y=values, markers=True, 
                             title="Blood Sugar Trend")
                fig.add_hline(y=100, line_dash="dash", line_color="green", 
                             annotation_text="Normal Fasting")
                fig.update_layout(xaxis_title="Date", yaxis_title="mg/dL", height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            # Data table
            st.subheader("📋 All Readings")
            df = pd.DataFrame(readings)
            df = df[['recorded_at', 'type', 'value', 'unit', 'notes']]
            df.columns = ['Date', 'Type', 'Value', 'Unit', 'Notes']
            st.dataframe(df.sort_values('Date', ascending=False), use_container_width=True)
    
    with tab2:
        st.subheader("Add New Health Reading")
        
        with st.form("add_reading"):
            reading_type = st.selectbox(
                "Reading Type",
                ["Blood Pressure", "Blood Sugar", "Weight", "Temperature", "Pulse"]
            )
            
            type_map = {
                "Blood Pressure": ("bp", "mmHg", "Enter as systolic/diastolic (e.g., 120/80)"),
                "Blood Sugar": ("sugar", "mg/dL", "Enter fasting blood sugar value"),
                "Weight": ("weight", "kg", "Enter weight in kilograms"),
                "Temperature": ("temperature", "°F", "Enter body temperature"),
                "Pulse": ("pulse", "bpm", "Enter pulse rate")
            }
            
            r_type, unit, hint = type_map[reading_type]
            
            if r_type == "bp":
                col1, col2 = st.columns(2)
                with col1:
                    systolic = st.number_input("Systolic", min_value=70, max_value=250, value=120)
                with col2:
                    diastolic = st.number_input("Diastolic", min_value=40, max_value=150, value=80)
                value = f"{systolic}/{diastolic}"
            else:
                value = st.text_input("Value", placeholder=hint)
            
            notes = st.text_input("Notes (optional)", placeholder="e.g., Fasting, After meal")
            
            if st.form_submit_button("💾 Save Reading", type="primary"):
                if value:
                    add_health_reading(health_id, r_type, value, unit, notes)
                    st.success("Reading saved successfully!")
                    st.rerun()
                else:
                    st.error("Please enter a value.")
        
        # Risk prediction
        st.markdown("---")
        st.subheader("🔮 Health Risk Assessment")
        
        if st.button("Analyze My Health Risks"):
            readings = get_health_readings(health_id)
            risks = predict_health_risks(user, readings)
            
            for risk in risks['risks']:
                level_colors = {"high": "🔴", "medium": "🟡", "low": "🟢", "info": "🔵"}
                with st.expander(f"{level_colors.get(risk['level'], '⚪')} {risk['condition']}", expanded=risk['level'] == 'high'):
                    st.write(risk['description'])
                    st.info(f"💡 Recommendation: {risk['recommendation']}")


# ============================================================================
# REMINDERS
# ============================================================================

def render_reminders(user, health_id):
    """Render medicine reminders page."""
    st.title("🔔 Medicine Reminders")
    
    tab1, tab2 = st.tabs(["📋 My Reminders", "➕ Add Reminder"])
    
    with tab1:
        reminders = get_reminders(health_id)
        
        if not reminders:
            st.info("No reminders set. Add one to stay on track with your medications!")
        else:
            for rem in reminders:
                status_icon = "🟢" if rem.get('is_active') else "⚪"
                with st.expander(f"{status_icon} {rem['medicine_name']} - {rem['frequency']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Times:** {', '.join(rem['times'])}")
                        st.write(f"**Frequency:** {rem['frequency']}")
                    with col2:
                        st.write(f"**Start:** {rem['start_date']}")
                        st.write(f"**End:** {rem['end_date']}")
    
    with tab2:
        st.subheader("Add New Reminder")
        
        with st.form("add_reminder"):
            medicine_name = st.text_input("Medicine Name")
            
            col1, col2 = st.columns(2)
            with col1:
                frequency = st.selectbox(
                    "Frequency",
                    ["Once daily", "Twice daily", "Three times daily", "Weekly"]
                )
            with col2:
                num_times = {"Once daily": 1, "Twice daily": 2, "Three times daily": 3, "Weekly": 1}
                times = []
                for i in range(num_times[frequency]):
                    t = st.time_input(f"Time {i+1}", key=f"time_{i}")
                    times.append(t.strftime("%H:%M"))
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date")
            with col2:
                end_date = st.date_input("End Date", value=datetime.now().date() + timedelta(days=30))
            
            if st.form_submit_button("➕ Add Reminder", type="primary"):
                if medicine_name:
                    add_reminder(
                        health_id,
                        medicine_name,
                        frequency,
                        times,
                        start_date.strftime("%Y-%m-%d"),
                        end_date.strftime("%Y-%m-%d")
                    )
                    st.success("Reminder added successfully!")
                    st.rerun()
                else:
                    st.error("Please enter medicine name.")


# ============================================================================
# EMERGENCY QR
# ============================================================================

def render_emergency_qr(user, health_id):
    """Render emergency QR code page."""
    st.title("🚨 Emergency QR Code")
    
    st.write("""
    This QR code contains your critical medical information for emergency situations.
    Show this to first responders or medical personnel in case of emergency.
    """)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Generate QR code
        qr_buffer = generate_emergency_qr(user)
        st.image(qr_buffer, caption="Scan for Emergency Info", width=300)
        
        # Download button
        st.download_button(
            label="📥 Download QR Code",
            data=qr_buffer.getvalue(),
            file_name=f"emergency_qr_{health_id}.png",
            mime="image/png"
        )
    
    with col2:
        st.subheader("Information Encoded:")
        st.markdown(f"""
        - **Health ID:** {health_id}
        - **Name:** {user['name']}
        - **Blood Group:** {user.get('blood_group', 'N/A')}
        - **Allergies:** {', '.join(user.get('allergies', [])) or 'None'}
        - **Emergency Contact:** {user.get('emergency_contact', 'N/A')}
        - **Phone:** {user.get('phone', 'N/A')}
        """)
        
        st.warning("⚠️ Keep this QR code accessible on your phone or print it for your wallet.")


# ============================================================================
# SYMPTOM CHECKER
# ============================================================================

def render_symptom_checker():
    """Render symptom checker page."""
    st.title("🩺 Symptom Checker")
    
    st.warning("""
    ⚕️ **Disclaimer:** This tool provides general health information only and is NOT a substitute 
    for professional medical advice, diagnosis, or treatment. Always consult a qualified 
    healthcare provider for any health concerns.
    """)
    
    symptoms_text = st.text_area(
        "Describe your symptoms",
        placeholder="E.g., I have a persistent headache for the past 3 days, mild fever, and fatigue...",
        height=150
    )
    
    if st.button("🔍 Check Symptoms", type="primary"):
        if symptoms_text:
            with st.spinner("Analyzing symptoms..."):
                result = check_symptoms(symptoms_text)
                
                st.subheader("Analysis Results")
                
                # Urgency indicator
                urgency_colors = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                st.write(f"**Urgency Level:** {urgency_colors.get(result['urgency'], '⚪')} {result['urgency'].title()}")
                
                st.info(f"💡 **Recommendation:** {result['recommendation']}")
                
                st.subheader("Possible Conditions")
                st.write("Based on your described symptoms, these conditions may be relevant:")
                for condition in result['possible_conditions']:
                    st.write(f"• {condition}")
                
                st.markdown("---")
                st.caption(result['disclaimer'])
        else:
            st.error("Please describe your symptoms.")


# ============================================================================
# FAMILY MEMBERS
# ============================================================================

def render_family_members(user, health_id):
    """Render family members management page."""
    st.title("👨‍👩‍👧 Family Members")
    
    st.write("Link family members to your account to manage their health records.")
    
    tab1, tab2 = st.tabs(["👥 Linked Members", "➕ Add Member"])
    
    with tab1:
        members = get_family_members(health_id)
        
        if not members:
            st.info("No family members linked yet.")
        else:
            for member in members:
                member_data = PATIENTS.get(member['health_id'], {})
                with st.expander(f"👤 {member_data.get('name', 'Unknown')} ({member['relationship']})"):
                    st.write(f"**Health ID:** {member['health_id']}")
                    st.write(f"**Relationship:** {member['relationship']}")
                    st.write(f"**Linked on:** {member['linked_at'][:10]}")
    
    with tab2:
        st.subheader("Link a Family Member")
        
        with st.form("link_family"):
            family_health_id = st.text_input(
                "Family Member's Health ID",
                placeholder="HID-XXXXXX"
            )
            relationship = st.selectbox(
                "Relationship",
                ["Spouse", "Parent", "Child", "Sibling", "Grandparent", "Other"]
            )
            
            if st.form_submit_button("🔗 Link Member", type="primary"):
                if family_health_id:
                    if family_health_id in PATIENTS:
                        success, message = link_family_member(health_id, family_health_id, relationship)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.error("Health ID not found. Please check and try again.")
                else:
                    st.error("Please enter the family member's Health ID.")


# ============================================================================
# CONSENT MANAGEMENT
# ============================================================================

def render_consent_management(user, health_id):
    """Render consent management page."""
    st.title("🔐 Consent Management")
    
    st.write("Control which hospitals can access your medical records.")
    
    tab1, tab2 = st.tabs(["📋 Active Consents", "➕ Grant New Consent"])
    
    with tab1:
        consents = get_patient_consents(health_id)
        
        if not consents:
            st.info("No active consents. Grant access to hospitals for better care coordination.")
        else:
            for consent in consents:
                hospital = HOSPITALS.get(consent['hospital_id'], {})
                status_icon = "🟢" if consent['is_active'] else "🔴"
                
                with st.expander(f"{status_icon} {hospital.get('name', 'Unknown Hospital')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Hospital ID:** {consent['hospital_id']}")
                        st.write(f"**Access Level:** {consent['access_level'].title()}")
                    with col2:
                        st.write(f"**Granted:** {consent['granted_at'][:10]}")
                        st.write(f"**Expires:** {consent['expires_at'][:10]}")
                    
                    if consent['is_active']:
                        if st.button("❌ Revoke Access", key=f"revoke_{consent['hospital_id']}"):
                            revoke_consent(health_id, consent['hospital_id'])
                            st.success("Access revoked.")
                            st.rerun()
    
    with tab2:
        st.subheader("Grant Access to Hospital")
        
        with st.form("grant_consent"):
            hospital_options = {h['hospital_id']: h['name'] for h in HOSPITALS.values()}
            selected_hospital = st.selectbox(
                "Select Hospital",
                list(hospital_options.keys()),
                format_func=lambda x: hospital_options[x]
            )
            
            access_level = st.selectbox(
                "Access Level",
                ["Full", "Limited", "Emergency Only"],
                help="Full: Complete access | Limited: Summary only | Emergency: Critical info only"
            )
            
            st.info("By granting access, the hospital will be able to view your medical records based on the selected access level.")
            
            if st.form_submit_button("✅ Grant Access", type="primary"):
                grant_consent(health_id, selected_hospital, access_level.lower().replace(" ", "_"))
                st.success(f"Access granted to {hospital_options[selected_hospital]}!")
                st.rerun()


# ============================================================================
# NEARBY FACILITIES
# ============================================================================

def render_nearby_facilities():
    """Render nearby hospitals and pharmacies."""
    st.title("📍 Nearby Facilities")
    
    tab1, tab2 = st.tabs(["🏥 Hospitals", "💊 Pharmacies"])
    
    with tab1:
        st.subheader("Nearby Hospitals")
        
        for hospital in NEARBY_HOSPITALS:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    emergency_badge = "🚨" if hospital['emergency'] else ""
                    st.markdown(f"**{hospital['name']}** {emergency_badge}")
                    st.caption(f"📍 {hospital['distance']} | 📞 {hospital['phone']}")
                with col2:
                    st.write(f"⭐ {hospital['rating']}")
                with col3:
                    st.button("📞 Call", key=f"call_{hospital['name']}", disabled=True)
                st.markdown("---")
    
    with tab2:
        st.subheader("Nearby Pharmacies")
        
        for pharmacy in NEARBY_PHARMACIES:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    hours_badge = "🌙 24H" if pharmacy['24_hours'] else ""
                    st.markdown(f"**{pharmacy['name']}** {hours_badge}")
                    st.caption(f"📍 {pharmacy['distance']} | 📞 {pharmacy['phone']}")
                with col2:
                    st.write(f"⭐ {pharmacy['rating']}")
                with col3:
                    st.button("📞 Call", key=f"call_{pharmacy['name']}", disabled=True)
                st.markdown("---")


# ============================================================================
# TELECONSULTATION
# ============================================================================

def render_teleconsultation(user, health_id):
    """Render teleconsultation page (placeholder UI)."""
    st.title("💬 Teleconsultation")
    
    st.info("🚧 This is a demonstration interface. In a production system, this would integrate with video calling services.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Start a Consultation")
        
        # Select doctor/hospital
        hospital_options = {h['hospital_id']: h['name'] for h in HOSPITALS.values()}
        selected_hospital = st.selectbox(
            "Select Hospital",
            list(hospital_options.keys()),
            format_func=lambda x: hospital_options[x]
        )
        
        consultation_type = st.radio(
            "Consultation Type",
            ["Video Call", "Audio Call", "Chat Only"]
        )
        
        reason = st.text_area("Reason for consultation", placeholder="Briefly describe your concern...")
        
        st.button("🎥 Start Consultation", type="primary", disabled=True)
        st.caption("Feature coming soon...")
    
    with col2:
        st.subheader("Chat Preview")
        
        # Mock chat interface
        chat_container = st.container()
        with chat_container:
            st.markdown("""
            <div style="background: #f0f2f6; padding: 10px; border-radius: 10px; margin: 5px 0;">
                <strong>Dr. Smith:</strong> Hello! How can I help you today?
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style="background: #007bff; color: white; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: right;">
                <strong>You:</strong> I've been having headaches...
            </div>
            """, unsafe_allow_html=True)
        
        message = st.text_input("Type a message...", key="chat_input")
        st.button("Send", key="send_message", disabled=True)
