"""
auth.py - Authentication and Session Management

Handles user authentication, session state, and role-based access control.
"""

import streamlit as st
from data import (
    get_patient_by_email, get_hospital_by_email, get_pharmacy_by_email,
    register_patient, register_hospital, register_pharmacy
)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session_state():
    """
    Initialize all required session state variables.
    Call this at the start of the app.
    """
    # Authentication state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'user_type' not in st.session_state:
        st.session_state.user_type = None  # 'patient', 'hospital', 'pharmacy'
    
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None  # health_id, hospital_id, or pharmacy_id
    
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None  # Full user data dictionary
    
    # UI state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'dashboard'
    
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    
    # Temporary states for multi-step processes
    if 'selected_appointment' not in st.session_state:
        st.session_state.selected_appointment = None
    
    if 'selected_prescription' not in st.session_state:
        st.session_state.selected_prescription = None


# ============================================================================
# AUTHENTICATION FUNCTIONS
# ============================================================================

def login(email, password, user_type):
    """
    Authenticate a user and create a session.
    
    Args:
        email: User's email address
        password: User's password
        user_type: Type of user ('patient', 'hospital', 'pharmacy')
    
    Returns:
        tuple: (success: bool, message: str)
    """
    user = None
    user_id = None
    
    if user_type == 'patient':
        user = get_patient_by_email(email)
        if user:
            user_id = user['health_id']
    elif user_type == 'hospital':
        user = get_hospital_by_email(email)
        if user:
            user_id = user['hospital_id']
    elif user_type == 'pharmacy':
        user = get_pharmacy_by_email(email)
        if user:
            user_id = user['pharmacy_id']
    
    if not user:
        return False, "Email not found. Please register first."
    
    # In production, use proper password hashing comparison!
    if user.get('password') != password:
        return False, "Incorrect password."
    
    # Set session state
    st.session_state.authenticated = True
    st.session_state.user_type = user_type
    st.session_state.user_id = user_id
    st.session_state.user_data = user
    st.session_state.current_page = 'dashboard'
    
    return True, f"Welcome back, {user.get('name', 'User')}!"


def logout():
    """
    Clear session and log out user.
    """
    st.session_state.authenticated = False
    st.session_state.user_type = None
    st.session_state.user_id = None
    st.session_state.user_data = None
    st.session_state.current_page = 'dashboard'
    st.session_state.selected_appointment = None
    st.session_state.selected_prescription = None


def is_authenticated():
    """Check if user is currently authenticated."""
    return st.session_state.get('authenticated', False)


def get_current_user():
    """Get current user's data."""
    return st.session_state.get('user_data')


def get_current_user_type():
    """Get current user's type."""
    return st.session_state.get('user_type')


def get_current_user_id():
    """Get current user's ID."""
    return st.session_state.get('user_id')


# ============================================================================
# REGISTRATION HANDLERS
# ============================================================================

def handle_patient_registration(form_data):
    """
    Handle patient registration form submission.
    
    Args:
        form_data: Dictionary with registration form fields
    
    Returns:
        tuple: (success: bool, message: str)
    """
    required_fields = ['name', 'email', 'password', 'phone', 'dob', 'blood_group']
    
    # Validate required fields
    for field in required_fields:
        if not form_data.get(field):
            return False, f"Please fill in the {field.replace('_', ' ')} field."
    
    # Validate email format (basic)
    if '@' not in form_data['email']:
        return False, "Please enter a valid email address."
    
    # Validate password length
    if len(form_data['password']) < 6:
        return False, "Password must be at least 6 characters long."
    
    # Register patient
    success, result = register_patient(
        name=form_data['name'],
        email=form_data['email'],
        password=form_data['password'],
        phone=form_data['phone'],
        dob=form_data['dob'],
        blood_group=form_data['blood_group'],
        allergies=form_data.get('allergies', ''),
        emergency_contact=form_data.get('emergency_contact', '')
    )
    
    if success:
        return True, f"Registration successful! Your Health ID is: **{result}**"
    else:
        return False, result


def handle_hospital_registration(form_data):
    """Handle hospital registration form submission."""
    required_fields = ['name', 'email', 'password', 'address', 'phone']
    
    for field in required_fields:
        if not form_data.get(field):
            return False, f"Please fill in the {field.replace('_', ' ')} field."
    
    if '@' not in form_data['email']:
        return False, "Please enter a valid email address."
    
    if len(form_data['password']) < 6:
        return False, "Password must be at least 6 characters long."
    
    specializations = form_data.get('specializations', '').split(',')
    specializations = [s.strip() for s in specializations if s.strip()]
    
    success, result = register_hospital(
        name=form_data['name'],
        email=form_data['email'],
        password=form_data['password'],
        address=form_data['address'],
        phone=form_data['phone'],
        specializations=specializations
    )
    
    if success:
        return True, f"Registration successful! Your Hospital ID is: **{result}**"
    else:
        return False, result


def handle_pharmacy_registration(form_data):
    """Handle pharmacy registration form submission."""
    required_fields = ['name', 'email', 'password', 'address', 'phone', 'license_number']
    
    for field in required_fields:
        if not form_data.get(field):
            return False, f"Please fill in the {field.replace('_', ' ')} field."
    
    if '@' not in form_data['email']:
        return False, "Please enter a valid email address."
    
    if len(form_data['password']) < 6:
        return False, "Password must be at least 6 characters long."
    
    success, result = register_pharmacy(
        name=form_data['name'],
        email=form_data['email'],
        password=form_data['password'],
        address=form_data['address'],
        phone=form_data['phone'],
        license_number=form_data['license_number']
    )
    
    if success:
        return True, f"Registration successful! Your Pharmacy ID is: **{result}**"
    else:
        return False, result


# ============================================================================
# ROLE-BASED ACCESS HELPERS
# ============================================================================

def require_auth(allowed_types=None):
    """
    Decorator/helper to require authentication.
    
    Args:
        allowed_types: List of allowed user types, or None for any
    
    Returns:
        bool: True if access allowed, False otherwise
    """
    if not is_authenticated():
        return False
    
    if allowed_types and get_current_user_type() not in allowed_types:
        return False
    
    return True


def get_user_display_name():
    """Get a display-friendly name for the current user."""
    user = get_current_user()
    if not user:
        return "Guest"
    return user.get('name', 'User')
