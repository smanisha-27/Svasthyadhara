"""
pages/hospital.py - Hospital Dashboard and Features

Hospital portal including:
- Patient search by Health ID
- Add consultation details
- Manage appointments
- Create prescriptions
- Doctor dashboard
"""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

from data import (
    PATIENTS, HOSPITALS,
    get_hospital, get_patient,
    get_hospital_appointments, update_appointment,
    get_patient_medical_records, create_medical_record,
    get_patient_prescriptions, create_prescription,
    check_consent
)

from auth import get_current_user, get_current_user_id, logout


def render_hospital_dashboard():
    """
    Main function to render the complete hospital dashboard.
    """
    user = get_current_user()
    hospital_id = get_current_user_id()
    
    if not user:
        st.error("Session expired. Please login again.")
        return
    
    # Sidebar navigation
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/hospital-2.png", width=80)
        st.markdown(f"### 🏥 {user['name']}")
        st.markdown(f"**ID:** `{hospital_id}`")
        st.markdown("---")
        
        menu_options = [
            ("🏠 Dashboard", "dashboard"),
            ("🔍 Search Patient", "search"),
            ("📅 Appointments", "appointments"),
            ("📋 Add Consultation", "consultation"),
            ("💊 Create Prescription", "prescription"),
            ("👨‍⚕️ Doctor Panel", "doctors"),
            ("📊 Analytics", "analytics"),
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
        render_hospital_home(user, hospital_id)
    elif page == "search":
        render_patient_search(hospital_id)
    elif page == "appointments":
        render_hospital_appointments(hospital_id)
    elif page == "consultation":
        render_add_consultation(hospital_id)
    elif page == "prescription":
        render_create_prescription(hospital_id)
    elif page == "doctors":
        render_doctor_panel(user, hospital_id)
    elif page == "analytics":
        render_hospital_analytics(hospital_id)


# ============================================================================
# DASHBOARD HOME
# ============================================================================

def render_hospital_home(user, hospital_id):
    """Render hospital dashboard home page."""
    st.title("🏥 Hospital Dashboard")
    st.markdown(f"Welcome, **{user['name']}**!")
    
    # Quick Stats
    appointments = get_hospital_appointments(hospital_id)
    today = datetime.now().strftime("%Y-%m-%d")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        today_apts = len([a for a in appointments if a['appointment_date'] == today])
        st.metric("📅 Today's Appointments", today_apts)
    
    with col2:
        pending = len([a for a in appointments if a['status'] == 'scheduled'])
        st.metric("⏳ Pending Appointments", pending)
    
    with col3:
        completed = len([a for a in appointments if a['status'] == 'completed'])
        st.metric("✅ Completed", completed)
    
    with col4:
        st.metric("🏥 Departments", len(user.get('specializations', [])))
    
    st.markdown("---")
    
    # Today's Appointments
    st.subheader("📋 Today's Schedule")
    
    today_appointments = [a for a in appointments if a['appointment_date'] == today]
    
    if not today_appointments:
        st.info("No appointments scheduled for today.")
    else:
        for apt in sorted(today_appointments, key=lambda x: x['appointment_time']):
            patient = PATIENTS.get(apt['patient_health_id'], {})
            status_colors = {"scheduled": "🟡", "completed": "🟢", "cancelled": "🔴"}
            
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            with col1:
                st.write(f"**{apt['appointment_time']}**")
                st.caption(apt['department'])
            with col2:
                st.write(f"👤 {patient.get('name', 'Unknown')}")
                st.caption(f"ID: {apt['patient_health_id']}")
            with col3:
                st.write(apt['reason'][:50] + "..." if len(apt['reason']) > 50 else apt['reason'])
            with col4:
                st.write(f"{status_colors.get(apt['status'], '⚪')} {apt['status'].title()}")
            
            st.markdown("---")
    
    # Quick Actions
    st.subheader("⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Search Patient", use_container_width=True):
            st.session_state.current_page = 'search'
            st.rerun()
    
    with col2:
        if st.button("📋 New Consultation", use_container_width=True):
            st.session_state.current_page = 'consultation'
            st.rerun()
    
    with col3:
        if st.button("💊 New Prescription", use_container_width=True):
            st.session_state.current_page = 'prescription'
            st.rerun()


# ============================================================================
# PATIENT SEARCH
# ============================================================================

def render_patient_search(hospital_id):
    """Render patient search page."""
    st.title("🔍 Search Patient")
    
    search_query = st.text_input(
        "Enter Patient Health ID",
        placeholder="HID-XXXXXX"
    )
    
    if st.button("🔍 Search", type="primary") or search_query:
        if search_query:
            patient = get_patient(search_query.upper())
            
            if patient:
                # Check consent
                consent = check_consent(patient['health_id'], hospital_id)
                
                st.success(f"Patient found: **{patient['name']}**")
                
                if consent:
                    st.info(f"✅ You have **{consent}** access to this patient's records.")
                    
                    # Display patient info
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📋 Patient Information")
                        st.write(f"**Health ID:** {patient['health_id']}")
                        st.write(f"**Name:** {patient['name']}")
                        st.write(f"**Blood Group:** {patient.get('blood_group', 'N/A')}")
                        st.write(f"**Phone:** {patient.get('phone', 'N/A')}")
                        
                        allergies = patient.get('allergies', [])
                        if allergies:
                            st.warning(f"⚠️ **Allergies:** {', '.join(allergies)}")
                    
                    with col2:
                        st.subheader("📊 Quick Stats")
                        
                        records = get_patient_medical_records(patient['health_id'])
                        prescriptions = get_patient_prescriptions(patient['health_id'])
                        
                        st.metric("Medical Records", len(records))
                        st.metric("Prescriptions", len(prescriptions))
                    
                    # Medical history
                    st.markdown("---")
                    st.subheader("📜 Medical History")
                    
                    if records:
                        for record in sorted(records, key=lambda x: x['created_at'], reverse=True)[:5]:
                            with st.expander(f"📋 {record['created_at'][:10]} - {record['diagnosis']}"):
                                st.write(f"**Doctor:** {record['doctor_name']}")
                                st.write(f"**Symptoms:** {', '.join(record.get('symptoms', []))}")
                                st.write(f"**Diagnosis:** {record['diagnosis']}")
                                st.write(f"**Treatment:** {record['treatment']}")
                    else:
                        st.info("No medical records found.")
                    
                    # Quick action buttons
                    st.markdown("---")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📋 Add Consultation", use_container_width=True):
                            st.session_state.selected_patient = patient['health_id']
                            st.session_state.current_page = 'consultation'
                            st.rerun()
                    with col2:
                        if st.button("💊 Create Prescription", use_container_width=True):
                            st.session_state.selected_patient = patient['health_id']
                            st.session_state.current_page = 'prescription'
                            st.rerun()
                else:
                    st.warning("⚠️ You don't have consent to access this patient's full records.")
                    st.write(f"**Name:** {patient['name']}")
                    st.write(f"**Health ID:** {patient['health_id']}")
                    st.info("The patient needs to grant your hospital access through their consent settings.")
            else:
                st.error("Patient not found. Please check the Health ID.")


# ============================================================================
# APPOINTMENTS MANAGEMENT
# ============================================================================

def render_hospital_appointments(hospital_id):
    """Render hospital appointments management."""
    st.title("📅 Appointments Management")
    
    appointments = get_hospital_appointments(hospital_id)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Status", ["All", "Scheduled", "Completed", "Cancelled"])
    with col2:
        date_filter = st.date_input("Date", value=datetime.now().date())
    with col3:
        dept_filter = st.selectbox("Department", ["All"] + get_hospital(hospital_id).get('specializations', []))
    
    # Apply filters
    filtered = appointments
    if status_filter != "All":
        filtered = [a for a in filtered if a['status'] == status_filter.lower()]
    if date_filter:
        date_str = date_filter.strftime("%Y-%m-%d")
        filtered = [a for a in filtered if a['appointment_date'] == date_str]
    if dept_filter != "All":
        filtered = [a for a in filtered if a['department'] == dept_filter]
    
    st.markdown("---")
    
    if not filtered:
        st.info("No appointments match your filters.")
    else:
        for apt in sorted(filtered, key=lambda x: (x['appointment_date'], x['appointment_time'])):
            patient = PATIENTS.get(apt['patient_health_id'], {})
            status_colors = {"scheduled": "🟡", "completed": "🟢", "cancelled": "🔴"}
            
            with st.expander(f"{status_colors.get(apt['status'], '⚪')} {apt['appointment_date']} {apt['appointment_time']} - {patient.get('name', 'Unknown')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Appointment ID:** {apt['appointment_id']}")
                    st.write(f"**Patient:** {patient.get('name', 'Unknown')}")
                    st.write(f"**Health ID:** {apt['patient_health_id']}")
                    st.write(f"**Department:** {apt['department']}")
                with col2:
                    st.write(f"**Doctor:** {apt['doctor_name']}")
                    st.write(f"**Reason:** {apt['reason']}")
                    st.write(f"**Status:** {apt['status'].title()}")
                
                if apt['status'] == 'scheduled':
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("✅ Mark Complete", key=f"complete_{apt['appointment_id']}"):
                            update_appointment(apt['appointment_id'], {'status': 'completed'})
                            st.success("Appointment marked as completed.")
                            st.rerun()
                    with col2:
                        if st.button("❌ Cancel", key=f"cancel_{apt['appointment_id']}"):
                            update_appointment(apt['appointment_id'], {'status': 'cancelled'})
                            st.success("Appointment cancelled.")
                            st.rerun()
                    with col3:
                        if st.button("📋 Add Notes", key=f"notes_{apt['appointment_id']}"):
                            st.session_state.selected_patient = apt['patient_health_id']
                            st.session_state.current_page = 'consultation'
                            st.rerun()


# ============================================================================
# ADD CONSULTATION
# ============================================================================

def render_add_consultation(hospital_id):
    """Render add consultation page."""
    st.title("📋 Add Consultation Details")
    
    hospital = get_hospital(hospital_id)
    
    with st.form("consultation_form"):
        # Patient selection
        patient_id = st.text_input(
            "Patient Health ID *",
            value=st.session_state.get('selected_patient', ''),
            placeholder="HID-XXXXXX"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            doctor_name = st.text_input("Doctor Name *", placeholder="Dr. ")
            department = st.selectbox(
                "Department *",
                hospital.get('specializations', ['General Medicine'])
            )
        with col2:
            consultation_date = st.date_input("Consultation Date", value=datetime.now().date())
        
        st.subheader("Clinical Details")
        
        symptoms = st.text_area(
            "Symptoms *",
            placeholder="List the patient's symptoms (one per line or comma-separated)"
        )
        
        diagnosis = st.text_input("Diagnosis *", placeholder="Primary diagnosis")
        
        treatment = st.text_area(
            "Treatment Plan *",
            placeholder="Describe the treatment plan"
        )
        
        notes = st.text_area(
            "Additional Notes",
            placeholder="Any additional observations or instructions"
        )
        
        st.subheader("Vitals (Optional)")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            bp = st.text_input("Blood Pressure", placeholder="120/80")
        with col2:
            pulse = st.text_input("Pulse Rate", placeholder="72")
        with col3:
            temp = st.text_input("Temperature (°F)", placeholder="98.6")
        with col4:
            weight = st.text_input("Weight (kg)", placeholder="70")
        
        col1, col2 = st.columns(2)
        with col1:
            follow_up = st.checkbox("Schedule Follow-up")
        with col2:
            if follow_up:
                follow_up_date = st.date_input(
                    "Follow-up Date",
                    value=datetime.now().date() + timedelta(days=7)
                )
        
        submitted = st.form_submit_button("💾 Save Consultation", type="primary")
        
        if submitted:
            # Validate required fields
            if not all([patient_id, doctor_name, symptoms, diagnosis, treatment]):
                st.error("Please fill in all required fields (*)")
            else:
                # Check if patient exists
                patient = get_patient(patient_id.upper())
                if not patient:
                    st.error("Patient not found. Please check the Health ID.")
                else:
                    # Check consent
                    consent = check_consent(patient['health_id'], hospital_id)
                    
                    if not consent:
                        st.warning("⚠️ No consent from patient. Consultation will be recorded but access may be limited.")
                    
                    # Create vitals dict
                    vitals = {}
                    if bp:
                        vitals['bp'] = bp
                    if pulse:
                        vitals['pulse'] = pulse
                    if temp:
                        vitals['temperature'] = temp
                    if weight:
                        vitals['weight'] = weight
                    
                    # Parse symptoms
                    symptom_list = [s.strip() for s in symptoms.replace('\n', ',').split(',') if s.strip()]
                    
                    # Create medical record
                    record_id = create_medical_record(
                        patient_health_id=patient['health_id'],
                        hospital_id=hospital_id,
                        doctor_name=doctor_name,
                        symptoms=symptom_list,
                        diagnosis=diagnosis,
                        treatment=treatment,
                        notes=notes,
                        vitals=vitals
                    )
                    
                    st.success(f"✅ Consultation recorded successfully! Record ID: {record_id}")
                    
                    # Clear selected patient
                    if 'selected_patient' in st.session_state:
                        del st.session_state.selected_patient


# ============================================================================
# CREATE PRESCRIPTION
# ============================================================================

def render_create_prescription(hospital_id):
    """Render create prescription page."""
    st.title("💊 Create Prescription")
    
    hospital = get_hospital(hospital_id)
    
    # Patient info
    patient_id = st.text_input(
        "Patient Health ID *",
        value=st.session_state.get('selected_patient', ''),
        placeholder="HID-XXXXXX"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        doctor_name = st.text_input("Doctor Name *", placeholder="Dr. ")
    with col2:
        diagnosis = st.text_input("Diagnosis *")
    
    st.markdown("---")
    st.subheader("Medicines")
    
    # Dynamic medicine list
    if 'medicine_list' not in st.session_state:
        st.session_state.medicine_list = [{}]
    
    medicines_to_add = []
    
    for i, med in enumerate(st.session_state.medicine_list):
        st.markdown(f"**Medicine {i + 1}**")
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        with col1:
            name = st.text_input("Name", key=f"med_name_{i}", placeholder="Medicine name")
        with col2:
            dosage = st.text_input("Dosage", key=f"med_dosage_{i}", placeholder="e.g., 500mg")
        with col3:
            frequency = st.selectbox(
                "Frequency",
                ["Once daily", "Twice daily", "Three times daily", "As needed", "Weekly"],
                key=f"med_freq_{i}"
            )
        with col4:
            duration = st.text_input("Duration", key=f"med_dur_{i}", placeholder="e.g., 7 days")
        
        if name:
            medicines_to_add.append({
                'name': name,
                'dosage': dosage,
                'frequency': frequency,
                'duration': duration,
                'purchased': False
            })
        
        st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Add Another Medicine"):
            st.session_state.medicine_list.append({})
            st.rerun()
    with col2:
        if len(st.session_state.medicine_list) > 1:
            if st.button("➖ Remove Last"):
                st.session_state.medicine_list.pop()
                st.rerun()
    
    notes = st.text_area("Additional Notes", placeholder="Instructions, warnings, etc.")
    
    if st.button("💾 Save Prescription", type="primary"):
        if not all([patient_id, doctor_name, diagnosis]):
            st.error("Please fill in all required fields.")
        elif not medicines_to_add:
            st.error("Please add at least one medicine.")
        else:
            patient = get_patient(patient_id.upper())
            if not patient:
                st.error("Patient not found.")
            else:
                prescription_id = create_prescription(
                    patient_health_id=patient['health_id'],
                    hospital_id=hospital_id,
                    doctor_name=doctor_name,
                    medicines=medicines_to_add,
                    diagnosis=diagnosis,
                    notes=notes
                )
                
                st.success(f"✅ Prescription created! ID: {prescription_id}")
                st.session_state.medicine_list = [{}]
                
                if 'selected_patient' in st.session_state:
                    del st.session_state.selected_patient


# ============================================================================
# DOCTOR PANEL
# ============================================================================

def render_doctor_panel(user, hospital_id):
    """Render doctor management panel."""
    st.title("👨‍⚕️ Doctor Panel")
    
    st.write("Manage doctors and their schedules.")
    
    # Mock doctor list
    doctors = [
        {"name": "Dr. Emily Chen", "department": "Cardiology", "status": "Available"},
        {"name": "Dr. James Wilson", "department": "Orthopedics", "status": "In Consultation"},
        {"name": "Dr. Sarah Miller", "department": "Pediatrics", "status": "Available"},
        {"name": "Dr. Robert Brown", "department": "Neurology", "status": "Off Duty"},
    ]
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Doctor List")
        
        for doc in doctors:
            status_colors = {"Available": "🟢", "In Consultation": "🟡", "Off Duty": "🔴"}
            
            with st.container():
                col_a, col_b, col_c = st.columns([2, 2, 1])
                with col_a:
                    st.write(f"**{doc['name']}**")
                with col_b:
                    st.write(doc['department'])
                with col_c:
                    st.write(f"{status_colors.get(doc['status'], '⚪')} {doc['status']}")
                st.markdown("---")
    
    with col2:
        st.subheader("Quick Stats")
        st.metric("Total Doctors", len(doctors))
        st.metric("Available", len([d for d in doctors if d['status'] == 'Available']))
        st.metric("Departments", len(user.get('specializations', [])))


# ============================================================================
# ANALYTICS
# ============================================================================

def render_hospital_analytics(hospital_id):
    """Render hospital analytics page."""
    st.title("📊 Analytics Dashboard")
    
    appointments = get_hospital_appointments(hospital_id)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Appointments", len(appointments))
    with col2:
        completed = len([a for a in appointments if a['status'] == 'completed'])
        st.metric("Completed", completed)
    with col3:
        cancelled = len([a for a in appointments if a['status'] == 'cancelled'])
        st.metric("Cancelled", cancelled)
    with col4:
        completion_rate = (completed / len(appointments) * 100) if appointments else 0
        st.metric("Completion Rate", f"{completion_rate:.1f}%")
    
    st.markdown("---")
    
    if appointments:
        # Department distribution
        st.subheader("Appointments by Department")
        dept_counts = {}
        for apt in appointments:
            dept = apt.get('department', 'Unknown')
            dept_counts[dept] = dept_counts.get(dept, 0) + 1
        
        import plotly.express as px
        fig = px.pie(
            values=list(dept_counts.values()),
            names=list(dept_counts.keys()),
            title="Department Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Status distribution
        st.subheader("Appointment Status")
        status_counts = {}
        for apt in appointments:
            status = apt.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        fig = px.bar(
            x=list(status_counts.keys()),
            y=list(status_counts.values()),
            title="Status Distribution",
            color=list(status_counts.keys())
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for analytics.")
