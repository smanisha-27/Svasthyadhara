"""
data.py - Centralized Data Management for Healthcare Ecosystem

This module handles all data storage using Python dictionaries.
In a production system, this would connect to a real database.
"""

import json
from datetime import datetime, timedelta
import random
import string

# ============================================================================
# GLOBAL DATA STORES (In-Memory Database Simulation)
# ============================================================================

# Store all registered patients
# Key: health_id, Value: patient data dictionary
PATIENTS = {}

# Store all registered hospitals
# Key: hospital_id, Value: hospital data dictionary
HOSPITALS = {}

# Store all registered pharmacies
# Key: pharmacy_id, Value: pharmacy data dictionary
PHARMACIES = {}

# Store all appointments
# Key: appointment_id, Value: appointment data dictionary
APPOINTMENTS = {}

# Store all prescriptions
# Key: prescription_id, Value: prescription data dictionary
PRESCRIPTIONS = {}

# Store all medical records/consultations
# Key: record_id, Value: medical record dictionary
MEDICAL_RECORDS = {}

# Store all uploaded files/reports
# Key: file_id, Value: file metadata dictionary
UPLOADED_FILES = {}

# Store consent records (patient approvals for hospital access)
# Key: (patient_health_id, hospital_id), Value: consent data
CONSENTS = {}

# Store health tracking data (BP, sugar, etc.)
# Key: health_id, Value: list of health readings
HEALTH_TRACKING = {}

# Store medicine reminders
# Key: health_id, Value: list of reminders
REMINDERS = {}

# Store family links
# Key: health_id, Value: list of linked family member health_ids
FAMILY_LINKS = {}

# ============================================================================
# ID GENERATORS
# ============================================================================

def generate_health_id():
    """
    Generate a unique Health ID for patients.
    Format: HID-XXXXXX (6 alphanumeric characters)
    """
    while True:
        # Generate random 6-character alphanumeric string
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        health_id = f"HID-{random_part}"
        # Ensure uniqueness
        if health_id not in PATIENTS:
            return health_id


def generate_hospital_id():
    """
    Generate a unique Hospital ID.
    Format: HOSP-XXXX (4 alphanumeric characters)
    """
    while True:
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        hospital_id = f"HOSP-{random_part}"
        if hospital_id not in HOSPITALS:
            return hospital_id


def generate_pharmacy_id():
    """
    Generate a unique Pharmacy ID.
    Format: PHAR-XXXX (4 alphanumeric characters)
    """
    while True:
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        pharmacy_id = f"PHAR-{random_part}"
        if pharmacy_id not in PHARMACIES:
            return pharmacy_id


def generate_appointment_id():
    """Generate unique appointment ID."""
    return f"APT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}"


def generate_prescription_id():
    """Generate unique prescription ID."""
    return f"RX-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}"


def generate_record_id():
    """Generate unique medical record ID."""
    return f"MR-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}"


# ============================================================================
# PATIENT DATA OPERATIONS
# ============================================================================

def register_patient(name, email, password, phone, dob, blood_group, allergies="", emergency_contact=""):
    """
    Register a new patient in the system.
    
    Args:
        name: Patient's full name
        email: Email address (used for login)
        password: Account password
        phone: Contact number
        dob: Date of birth
        blood_group: Blood group (A+, B-, etc.)
        allergies: Known allergies (comma-separated)
        emergency_contact: Emergency contact number
    
    Returns:
        tuple: (success: bool, health_id or error_message: str)
    """
    # Check if email already exists
    for patient in PATIENTS.values():
        if patient['email'] == email:
            return False, "Email already registered"
    
    # Generate unique Health ID
    health_id = generate_health_id()
    
    # Create patient record
    PATIENTS[health_id] = {
        'health_id': health_id,
        'name': name,
        'email': email,
        'password': password,  # In production, this should be hashed!
        'phone': phone,
        'dob': dob,
        'blood_group': blood_group,
        'allergies': [a.strip() for a in allergies.split(',') if a.strip()],
        'emergency_contact': emergency_contact,
        'registered_at': datetime.now().isoformat(),
        'insurance_info': {},
        'medical_conditions': [],
        'current_medications': []
    }
    
    # Initialize empty health tracking for this patient
    HEALTH_TRACKING[health_id] = []
    REMINDERS[health_id] = []
    FAMILY_LINKS[health_id] = []
    
    return True, health_id


def get_patient(health_id):
    """Get patient data by Health ID."""
    return PATIENTS.get(health_id)


def get_patient_by_email(email):
    """Get patient data by email address."""
    for patient in PATIENTS.values():
        if patient['email'] == email:
            return patient
    return None


def update_patient(health_id, updates):
    """Update patient information."""
    if health_id in PATIENTS:
        PATIENTS[health_id].update(updates)
        return True
    return False


# ============================================================================
# HOSPITAL DATA OPERATIONS
# ============================================================================

def register_hospital(name, email, password, address, phone, specializations):
    """
    Register a new hospital in the system.
    
    Args:
        name: Hospital name
        email: Hospital email (used for login)
        password: Account password
        address: Physical address
        phone: Contact number
        specializations: List of medical specializations
    
    Returns:
        tuple: (success: bool, hospital_id or error_message: str)
    """
    # Check if email already exists
    for hospital in HOSPITALS.values():
        if hospital['email'] == email:
            return False, "Email already registered"
    
    hospital_id = generate_hospital_id()
    
    HOSPITALS[hospital_id] = {
        'hospital_id': hospital_id,
        'name': name,
        'email': email,
        'password': password,
        'address': address,
        'phone': phone,
        'specializations': specializations,
        'registered_at': datetime.now().isoformat(),
        'doctors': [],  # List of doctor names/IDs
        'departments': []
    }
    
    return True, hospital_id


def get_hospital(hospital_id):
    """Get hospital data by Hospital ID."""
    return HOSPITALS.get(hospital_id)


def get_hospital_by_email(email):
    """Get hospital data by email address."""
    for hospital in HOSPITALS.values():
        if hospital['email'] == email:
            return hospital
    return None


# ============================================================================
# PHARMACY DATA OPERATIONS
# ============================================================================

def register_pharmacy(name, email, password, address, phone, license_number):
    """
    Register a new pharmacy in the system.
    """
    # Check if email already exists
    for pharmacy in PHARMACIES.values():
        if pharmacy['email'] == email:
            return False, "Email already registered"
    
    pharmacy_id = generate_pharmacy_id()
    
    PHARMACIES[pharmacy_id] = {
        'pharmacy_id': pharmacy_id,
        'name': name,
        'email': email,
        'password': password,
        'address': address,
        'phone': phone,
        'license_number': license_number,
        'registered_at': datetime.now().isoformat()
    }
    
    return True, pharmacy_id


def get_pharmacy(pharmacy_id):
    """Get pharmacy data by Pharmacy ID."""
    return PHARMACIES.get(pharmacy_id)


def get_pharmacy_by_email(email):
    """Get pharmacy data by email address."""
    for pharmacy in PHARMACIES.values():
        if pharmacy['email'] == email:
            return pharmacy
    return None


# ============================================================================
# APPOINTMENT OPERATIONS
# ============================================================================

def create_appointment(patient_health_id, hospital_id, doctor_name, department, 
                       appointment_date, appointment_time, reason):
    """
    Create a new appointment.
    """
    appointment_id = generate_appointment_id()
    
    APPOINTMENTS[appointment_id] = {
        'appointment_id': appointment_id,
        'patient_health_id': patient_health_id,
        'hospital_id': hospital_id,
        'doctor_name': doctor_name,
        'department': department,
        'appointment_date': appointment_date,
        'appointment_time': appointment_time,
        'reason': reason,
        'status': 'scheduled',  # scheduled, completed, cancelled
        'created_at': datetime.now().isoformat(),
        'notes': ''
    }
    
    return appointment_id


def get_patient_appointments(health_id):
    """Get all appointments for a patient."""
    return [apt for apt in APPOINTMENTS.values() 
            if apt['patient_health_id'] == health_id]


def get_hospital_appointments(hospital_id):
    """Get all appointments for a hospital."""
    return [apt for apt in APPOINTMENTS.values() 
            if apt['hospital_id'] == hospital_id]


def update_appointment(appointment_id, updates):
    """Update appointment details."""
    if appointment_id in APPOINTMENTS:
        APPOINTMENTS[appointment_id].update(updates)
        return True
    return False


# ============================================================================
# PRESCRIPTION OPERATIONS
# ============================================================================

def create_prescription(patient_health_id, hospital_id, doctor_name, medicines, 
                        diagnosis, notes=""):
    """
    Create a new prescription.
    
    Args:
        patient_health_id: Patient's Health ID
        hospital_id: Hospital ID
        doctor_name: Prescribing doctor's name
        medicines: List of medicine dictionaries with name, dosage, frequency, duration
        diagnosis: Medical diagnosis
        notes: Additional notes
    """
    prescription_id = generate_prescription_id()
    
    PRESCRIPTIONS[prescription_id] = {
        'prescription_id': prescription_id,
        'patient_health_id': patient_health_id,
        'hospital_id': hospital_id,
        'doctor_name': doctor_name,
        'medicines': medicines,  # List of {name, dosage, frequency, duration, purchased}
        'diagnosis': diagnosis,
        'notes': notes,
        'created_at': datetime.now().isoformat(),
        'status': 'active',  # active, completed, cancelled
        'pharmacy_id': None,  # Filled when purchased
        'purchase_date': None,
        'bill_amount': None
    }
    
    return prescription_id


def get_patient_prescriptions(health_id):
    """Get all prescriptions for a patient."""
    return [rx for rx in PRESCRIPTIONS.values() 
            if rx['patient_health_id'] == health_id]


def get_prescription(prescription_id):
    """Get prescription by ID."""
    return PRESCRIPTIONS.get(prescription_id)


def update_prescription(prescription_id, updates):
    """Update prescription details."""
    if prescription_id in PRESCRIPTIONS:
        PRESCRIPTIONS[prescription_id].update(updates)
        return True
    return False


# ============================================================================
# MEDICAL RECORD OPERATIONS
# ============================================================================

def create_medical_record(patient_health_id, hospital_id, doctor_name, 
                          symptoms, diagnosis, treatment, notes="", vitals=None):
    """
    Create a new medical record/consultation entry.
    """
    record_id = generate_record_id()
    
    MEDICAL_RECORDS[record_id] = {
        'record_id': record_id,
        'patient_health_id': patient_health_id,
        'hospital_id': hospital_id,
        'doctor_name': doctor_name,
        'symptoms': symptoms,
        'diagnosis': diagnosis,
        'treatment': treatment,
        'notes': notes,
        'vitals': vitals or {},  # BP, temperature, pulse, etc.
        'created_at': datetime.now().isoformat(),
        'follow_up_date': None
    }
    
    return record_id


def get_patient_medical_records(health_id):
    """Get all medical records for a patient."""
    return [rec for rec in MEDICAL_RECORDS.values() 
            if rec['patient_health_id'] == health_id]


# ============================================================================
# CONSENT OPERATIONS
# ============================================================================

def grant_consent(patient_health_id, hospital_id, access_level="full"):
    """
    Grant a hospital access to patient's medical data.
    
    Args:
        patient_health_id: Patient's Health ID
        hospital_id: Hospital requesting access
        access_level: Level of access (full, limited, emergency_only)
    """
    key = (patient_health_id, hospital_id)
    CONSENTS[key] = {
        'patient_health_id': patient_health_id,
        'hospital_id': hospital_id,
        'access_level': access_level,
        'granted_at': datetime.now().isoformat(),
        'expires_at': (datetime.now() + timedelta(days=365)).isoformat(),
        'is_active': True
    }
    return True


def revoke_consent(patient_health_id, hospital_id):
    """Revoke hospital's access to patient data."""
    key = (patient_health_id, hospital_id)
    if key in CONSENTS:
        CONSENTS[key]['is_active'] = False
        return True
    return False


def check_consent(patient_health_id, hospital_id):
    """Check if hospital has active consent to access patient data."""
    key = (patient_health_id, hospital_id)
    consent = CONSENTS.get(key)
    if consent and consent['is_active']:
        return consent['access_level']
    return None


def get_patient_consents(health_id):
    """Get all consents granted by a patient."""
    return [c for c in CONSENTS.values() 
            if c['patient_health_id'] == health_id]


# ============================================================================
# HEALTH TRACKING OPERATIONS
# ============================================================================

def add_health_reading(health_id, reading_type, value, unit, notes=""):
    """
    Add a health tracking reading (BP, sugar, weight, etc.)
    
    Args:
        health_id: Patient's Health ID
        reading_type: Type of reading (bp, sugar, weight, temperature, pulse)
        value: Reading value (can be string for BP like "120/80")
        unit: Unit of measurement
        notes: Optional notes
    """
    if health_id not in HEALTH_TRACKING:
        HEALTH_TRACKING[health_id] = []
    
    reading = {
        'type': reading_type,
        'value': value,
        'unit': unit,
        'notes': notes,
        'recorded_at': datetime.now().isoformat()
    }
    
    HEALTH_TRACKING[health_id].append(reading)
    return True


def get_health_readings(health_id, reading_type=None):
    """Get health readings for a patient, optionally filtered by type."""
    readings = HEALTH_TRACKING.get(health_id, [])
    if reading_type:
        return [r for r in readings if r['type'] == reading_type]
    return readings


# ============================================================================
# REMINDER OPERATIONS
# ============================================================================

def add_reminder(health_id, medicine_name, frequency, times, start_date, end_date):
    """
    Add a medicine reminder for a patient.
    """
    if health_id not in REMINDERS:
        REMINDERS[health_id] = []
    
    reminder = {
        'id': f"REM-{random.randint(1000, 9999)}",
        'medicine_name': medicine_name,
        'frequency': frequency,  # daily, twice_daily, weekly, etc.
        'times': times,  # List of times like ["08:00", "20:00"]
        'start_date': start_date,
        'end_date': end_date,
        'is_active': True,
        'created_at': datetime.now().isoformat()
    }
    
    REMINDERS[health_id].append(reminder)
    return reminder['id']


def get_reminders(health_id):
    """Get all reminders for a patient."""
    return REMINDERS.get(health_id, [])


# ============================================================================
# FAMILY LINKING OPERATIONS
# ============================================================================

def link_family_member(primary_health_id, family_member_health_id, relationship):
    """
    Link a family member to a patient's account.
    """
    if primary_health_id not in FAMILY_LINKS:
        FAMILY_LINKS[primary_health_id] = []
    
    # Check if already linked
    for link in FAMILY_LINKS[primary_health_id]:
        if link['health_id'] == family_member_health_id:
            return False, "Family member already linked"
    
    FAMILY_LINKS[primary_health_id].append({
        'health_id': family_member_health_id,
        'relationship': relationship,
        'linked_at': datetime.now().isoformat()
    })
    
    return True, "Family member linked successfully"


def get_family_members(health_id):
    """Get all linked family members for a patient."""
    return FAMILY_LINKS.get(health_id, [])


# ============================================================================
# DUMMY DATA INITIALIZATION
# ============================================================================

def initialize_dummy_data():
    """
    Initialize the system with dummy data for testing.
    Call this once when the app starts.
    """
    # Check if data already exists
    if PATIENTS:
        return
    
    # Create dummy patients
    register_patient(
        name="John Smith",
        email="john@example.com",
        password="password123",
        phone="555-0101",
        dob="1985-03-15",
        blood_group="A+",
        allergies="Penicillin, Peanuts",
        emergency_contact="555-0102"
    )
    
    register_patient(
        name="Sarah Johnson",
        email="sarah@example.com",
        password="password123",
        phone="555-0201",
        dob="1990-07-22",
        blood_group="O-",
        allergies="None",
        emergency_contact="555-0202"
    )
    
    # Create dummy hospitals
    register_hospital(
        name="City General Hospital",
        email="city@hospital.com",
        password="hospital123",
        address="123 Medical Center Drive, Downtown",
        phone="555-1000",
        specializations=["Cardiology", "Orthopedics", "Neurology", "Pediatrics", "Emergency"]
    )
    
    register_hospital(
        name="Sunrise Medical Center",
        email="sunrise@hospital.com",
        password="hospital123",
        address="456 Health Avenue, Westside",
        phone="555-2000",
        specializations=["General Medicine", "Dermatology", "Gynecology", "ENT"]
    )
    
    # Create dummy pharmacies
    register_pharmacy(
        name="MedPlus Pharmacy",
        email="medplus@pharmacy.com",
        password="pharmacy123",
        address="789 Wellness Street",
        phone="555-3000",
        license_number="PH-2024-001"
    )
    
    register_pharmacy(
        name="HealthFirst Drugstore",
        email="healthfirst@pharmacy.com",
        password="pharmacy123",
        address="321 Care Lane",
        phone="555-4000",
        license_number="PH-2024-002"
    )
    
    # Get the first patient's health ID for creating sample data
    first_patient_id = list(PATIENTS.keys())[0]
    first_hospital_id = list(HOSPITALS.keys())[0]
    
    # Create sample appointments
    create_appointment(
        patient_health_id=first_patient_id,
        hospital_id=first_hospital_id,
        doctor_name="Dr. Emily Chen",
        department="Cardiology",
        appointment_date=(datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
        appointment_time="10:00 AM",
        reason="Annual heart checkup"
    )
    
    # Create sample prescription
    create_prescription(
        patient_health_id=first_patient_id,
        hospital_id=first_hospital_id,
        doctor_name="Dr. Emily Chen",
        medicines=[
            {"name": "Aspirin", "dosage": "100mg", "frequency": "Once daily", 
             "duration": "30 days", "purchased": False},
            {"name": "Lisinopril", "dosage": "10mg", "frequency": "Once daily", 
             "duration": "30 days", "purchased": False}
        ],
        diagnosis="Mild hypertension",
        notes="Monitor blood pressure weekly"
    )
    
    # Create sample medical record
    create_medical_record(
        patient_health_id=first_patient_id,
        hospital_id=first_hospital_id,
        doctor_name="Dr. Emily Chen",
        symptoms=["Occasional chest discomfort", "Mild fatigue"],
        diagnosis="Mild hypertension, Stage 1",
        treatment="Lifestyle modifications, medication",
        notes="Advised to reduce sodium intake and exercise regularly",
        vitals={"bp": "140/90", "pulse": "78", "temperature": "98.6"}
    )
    
    # Add sample health readings
    for i in range(7):
        date_offset = timedelta(days=i)
        # Simulate BP readings
        systolic = 120 + random.randint(-10, 20)
        diastolic = 80 + random.randint(-5, 10)
        
        reading = {
            'type': 'bp',
            'value': f"{systolic}/{diastolic}",
            'unit': 'mmHg',
            'notes': '',
            'recorded_at': (datetime.now() - date_offset).isoformat()
        }
        if first_patient_id not in HEALTH_TRACKING:
            HEALTH_TRACKING[first_patient_id] = []
        HEALTH_TRACKING[first_patient_id].append(reading)
        
        # Simulate sugar readings
        sugar = 100 + random.randint(-10, 30)
        sugar_reading = {
            'type': 'sugar',
            'value': str(sugar),
            'unit': 'mg/dL',
            'notes': 'Fasting',
            'recorded_at': (datetime.now() - date_offset).isoformat()
        }
        HEALTH_TRACKING[first_patient_id].append(sugar_reading)
    
    # Grant consent
    grant_consent(first_patient_id, first_hospital_id, "full")
    
    print("Dummy data initialized successfully!")


# ============================================================================
# NEARBY FACILITIES (DUMMY DATA)
# ============================================================================

NEARBY_HOSPITALS = [
    {"name": "City General Hospital", "distance": "0.5 km", "phone": "555-1000", 
     "emergency": True, "rating": 4.5},
    {"name": "Sunrise Medical Center", "distance": "1.2 km", "phone": "555-2000", 
     "emergency": True, "rating": 4.2},
    {"name": "Community Health Clinic", "distance": "2.0 km", "phone": "555-5000", 
     "emergency": False, "rating": 4.0},
    {"name": "St. Mary's Hospital", "distance": "3.5 km", "phone": "555-6000", 
     "emergency": True, "rating": 4.7},
]

NEARBY_PHARMACIES = [
    {"name": "MedPlus Pharmacy", "distance": "0.3 km", "phone": "555-3000", 
     "24_hours": True, "rating": 4.3},
    {"name": "HealthFirst Drugstore", "distance": "0.8 km", "phone": "555-4000", 
     "24_hours": False, "rating": 4.1},
    {"name": "Apollo Pharmacy", "distance": "1.5 km", "phone": "555-7000", 
     "24_hours": True, "rating": 4.4},
]
