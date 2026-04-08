"""
app.py - Healthcare Ecosystem Main Application

This is the main entry point for the Healthcare Ecosystem web application.
Run this file with: streamlit run app.py

The application provides:
- Patient portal for managing health records
- Hospital portal for patient management
- Pharmacy portal for prescription fulfillment
"""

import streamlit as st

# Import authentication and session management
from auth import (
    init_session_state, is_authenticated, get_current_user_type,
    login, logout, handle_patient_registration,
    handle_hospital_registration, handle_pharmacy_registration
)

# Import data initialization
from data import initialize_dummy_data

# Import dashboard pages
from pages.patient import render_patient_dashboard
from pages.hospital import render_hospital_dashboard
from pages.pharmacy import render_pharmacy_dashboard


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Svasthyadhara",
    page_icon="🏥 Svasthyadhara",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================
# CUSTOM CSS
# ============================================================================

def load_custom_css():
    """Load custom CSS for better styling."""
    st.markdown("""
    <style>
        /* Main container padding */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Metric cards */
        [data-testid="metric-container"] {
            background-color: #f0f2f6;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Buttons */
        .stButton > button {
            border-radius: 8px;
            font-weight: 500;
        }
        
        /* Expanders */
        .streamlit-expanderHeader {
            font-weight: 600;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #f8f9fa;
        }
        
        /* Forms */
        [data-testid="stForm"] {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* Info boxes */
        .stAlert {
            border-radius: 8px;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            padding: 10px 20px;
        }
    </style>
    """, unsafe_allow_html=True)


# ============================================================================
# LOGIN/REGISTRATION PAGE
# ============================================================================

def render_login_page():
    """Render the login and registration page."""
    
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h1>🏥 Svasthyadhara</h1>
        <p style="font-size: 1.2em; color: #666;">
            Connecting Patients, Hospitals, and Pharmacies
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Login/Register tabs
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        render_login_form()
    
    with tab2:
        render_registration_form()
    
    # Demo credentials info
    st.markdown("---")
    with st.expander("📋 Demo Credentials"):
        st.markdown("""
        **Patient Login:**
        - Email: `john@example.com`
        - Password: `password123`
        
        **Hospital Login:**
        - Email: `city@hospital.com`
        - Password: `hospital123`
        
        **Pharmacy Login:**
        - Email: `medplus@pharmacy.com`
        - Password: `pharmacy123`
        """)


def render_login_form():
    """Render the login form."""
    st.subheader("Welcome Back!")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        user_type = st.selectbox(
            "Login as:",
            ["Patient", "Hospital", "Pharmacy"],
            key="login_user_type"
        )
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password")
            
            submitted = st.form_submit_button("🔐 Login", type="primary", use_container_width=True)
            
            if submitted:
                if email and password:
                    success, message = login(email, password, user_type.lower())
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please enter both email and password.")


def render_registration_form():
    """Render the registration forms for different user types."""
    st.subheader("Create an Account")
    
    user_type = st.selectbox(
        "Register as:",
        ["Patient", "Hospital", "Pharmacy"],
        key="register_user_type"
    )
    
    if user_type == "Patient":
        render_patient_registration()
    elif user_type == "Hospital":
        render_hospital_registration()
    else:
        render_pharmacy_registration()


def render_patient_registration():
    """Render patient registration form."""
    with st.form("patient_registration"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name *")
            email = st.text_input("Email *")
            password = st.text_input("Password *", type="password")
            phone = st.text_input("Phone Number *")
        
        with col2:
            dob = st.date_input("Date of Birth *")
            blood_group = st.selectbox(
                "Blood Group *",
                ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
            )
            emergency_contact = st.text_input("Emergency Contact")
            allergies = st.text_input("Known Allergies (comma-separated)")
        
        st.markdown("---")
        
        submitted = st.form_submit_button("📝 Register", type="primary", use_container_width=True)
        
        if submitted:
            form_data = {
                'name': name,
                'email': email,
                'password': password,
                'phone': phone,
                'dob': dob.strftime("%Y-%m-%d"),
                'blood_group': blood_group,
                'emergency_contact': emergency_contact,
                'allergies': allergies
            }
            
            success, message = handle_patient_registration(form_data)
            if success:
                st.success(message)
                st.info("Please login with your credentials.")
            else:
                st.error(message)


def render_hospital_registration():
    """Render hospital registration form."""
    with st.form("hospital_registration"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Hospital Name *")
            email = st.text_input("Email *")
            password = st.text_input("Password *", type="password")
        
        with col2:
            phone = st.text_input("Phone Number *")
            address = st.text_area("Address *")
        
        specializations = st.text_input(
            "Specializations (comma-separated) *",
            placeholder="Cardiology, Orthopedics, Pediatrics"
        )
        
        submitted = st.form_submit_button("📝 Register Hospital", type="primary", use_container_width=True)
        
        if submitted:
            form_data = {
                'name': name,
                'email': email,
                'password': password,
                'phone': phone,
                'address': address,
                'specializations': specializations
            }
            
            success, message = handle_hospital_registration(form_data)
            if success:
                st.success(message)
                st.info("Please login with your credentials.")
            else:
                st.error(message)


def render_pharmacy_registration():
    """Render pharmacy registration form."""
    with st.form("pharmacy_registration"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Pharmacy Name *")
            email = st.text_input("Email *")
            password = st.text_input("Password *", type="password")
        
        with col2:
            phone = st.text_input("Phone Number *")
            license_number = st.text_input("License Number *")
        
        address = st.text_area("Address *")
        
        submitted = st.form_submit_button("📝 Register Pharmacy", type="primary", use_container_width=True)
        
        if submitted:
            form_data = {
                'name': name,
                'email': email,
                'password': password,
                'phone': phone,
                'address': address,
                'license_number': license_number
            }
            
            success, message = handle_pharmacy_registration(form_data)
            if success:
                st.success(message)
                st.info("Please login with your credentials.")
            else:
                st.error(message)


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point."""
    
    # Load custom CSS
    load_custom_css()
    
    # Initialize session state
    init_session_state()
    
    # Initialize dummy data (only runs once)
    initialize_dummy_data()
    
    # Check authentication status
    if is_authenticated():
        # Route to appropriate dashboard based on user type
        user_type = get_current_user_type()
        
        if user_type == 'patient':
            render_patient_dashboard()
        elif user_type == 'hospital':
            render_hospital_dashboard()
        elif user_type == 'pharmacy':
            render_pharmacy_dashboard()
        else:
            st.error("Unknown user type. Please login again.")
            logout()
            st.rerun()
    else:
        # Show login/registration page
        render_login_page()


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    main()
