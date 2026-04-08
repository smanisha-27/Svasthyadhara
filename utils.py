"""
utils.py - Utility Functions for Healthcare Ecosystem

Contains helper functions for QR code generation, symptom checking,
drug interactions, and other utilities.
"""

import qrcode
from io import BytesIO
import base64
from datetime import datetime
import random

# ============================================================================
# QR CODE GENERATION
# ============================================================================

def generate_qr_code(data):
    """
    Generate a QR code image from data.
    
    Args:
        data: String data to encode in QR code
    
    Returns:
        BytesIO object containing the QR code image
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to bytes
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return img_buffer


def generate_emergency_qr(patient_data):
    """
    Generate an emergency QR code containing critical patient information.
    
    Args:
        patient_data: Dictionary containing patient information
    
    Returns:
        BytesIO object containing the QR code image
    """
    # Create emergency info string
    emergency_info = f"""
EMERGENCY MEDICAL INFO
======================
Health ID: {patient_data.get('health_id', 'N/A')}
Name: {patient_data.get('name', 'N/A')}
Blood Group: {patient_data.get('blood_group', 'N/A')}
Allergies: {', '.join(patient_data.get('allergies', [])) or 'None'}
Emergency Contact: {patient_data.get('emergency_contact', 'N/A')}
Phone: {patient_data.get('phone', 'N/A')}
    """.strip()
    
    return generate_qr_code(emergency_info)


# ============================================================================
# SYMPTOM CHECKER (Mock AI Logic)
# ============================================================================

# Symptom database with possible conditions
SYMPTOM_CONDITIONS = {
    "headache": ["Tension headache", "Migraine", "Dehydration", "Eye strain"],
    "fever": ["Viral infection", "Flu", "COVID-19", "Bacterial infection"],
    "cough": ["Common cold", "Bronchitis", "Allergies", "COVID-19"],
    "chest pain": ["Muscle strain", "Acid reflux", "Anxiety", "Heart condition (seek immediate care)"],
    "fatigue": ["Lack of sleep", "Anemia", "Thyroid issues", "Depression"],
    "nausea": ["Food poisoning", "Gastritis", "Motion sickness", "Pregnancy"],
    "dizziness": ["Low blood pressure", "Inner ear issue", "Dehydration", "Anemia"],
    "shortness of breath": ["Anxiety", "Asthma", "Heart condition", "COVID-19"],
    "back pain": ["Muscle strain", "Poor posture", "Herniated disc", "Kidney issues"],
    "joint pain": ["Arthritis", "Injury", "Gout", "Viral infection"],
    "sore throat": ["Common cold", "Strep throat", "Allergies", "Acid reflux"],
    "stomach pain": ["Indigestion", "Gastritis", "Food poisoning", "Appendicitis"],
    "runny nose": ["Common cold", "Allergies", "Sinusitis", "Flu"],
    "skin rash": ["Allergic reaction", "Eczema", "Contact dermatitis", "Viral infection"],
}

SEVERITY_KEYWORDS = {
    "severe": 3,
    "intense": 3,
    "unbearable": 3,
    "mild": 1,
    "slight": 1,
    "moderate": 2,
    "persistent": 2,
    "chronic": 2,
}


def check_symptoms(symptoms_text):
    """
    Analyze symptoms and provide possible conditions.
    This is a MOCK function - not real medical advice!
    
    Args:
        symptoms_text: Text describing symptoms
    
    Returns:
        Dictionary with possible conditions and recommendations
    """
    symptoms_lower = symptoms_text.lower()
    found_conditions = set()
    severity = 1  # Default mild
    
    # Check for severity keywords
    for keyword, level in SEVERITY_KEYWORDS.items():
        if keyword in symptoms_lower:
            severity = max(severity, level)
    
    # Find matching conditions
    for symptom, conditions in SYMPTOM_CONDITIONS.items():
        if symptom in symptoms_lower:
            found_conditions.update(conditions)
    
    # Generate recommendation based on severity
    if severity >= 3 or "chest pain" in symptoms_lower or "shortness of breath" in symptoms_lower:
        recommendation = "⚠️ URGENT: Please seek immediate medical attention or visit the emergency room."
        urgency = "high"
    elif severity == 2 or len(found_conditions) >= 3:
        recommendation = "We recommend scheduling an appointment with a doctor within 24-48 hours."
        urgency = "medium"
    else:
        recommendation = "Monitor your symptoms. If they persist for more than 3 days, consult a doctor."
        urgency = "low"
    
    if not found_conditions:
        found_conditions = {"Unable to determine - please consult a healthcare provider"}
    
    return {
        "possible_conditions": list(found_conditions),
        "severity_level": severity,
        "urgency": urgency,
        "recommendation": recommendation,
        "disclaimer": "⚕️ This is not a medical diagnosis. Please consult a qualified healthcare provider for proper evaluation."
    }


# ============================================================================
# DRUG INTERACTION CHECKER (Mock Logic)
# ============================================================================

# Known drug interactions (simplified mock data)
DRUG_INTERACTIONS = {
    ("aspirin", "warfarin"): {
        "severity": "high",
        "description": "Increased risk of bleeding when aspirin is combined with warfarin."
    },
    ("aspirin", "ibuprofen"): {
        "severity": "medium",
        "description": "Both are NSAIDs and may increase stomach bleeding risk."
    },
    ("lisinopril", "potassium"): {
        "severity": "medium",
        "description": "May cause dangerously high potassium levels."
    },
    ("metformin", "alcohol"): {
        "severity": "high",
        "description": "Increased risk of lactic acidosis."
    },
    ("simvastatin", "grapefruit"): {
        "severity": "medium",
        "description": "Grapefruit can increase statin levels in blood."
    },
    ("blood thinner", "aspirin"): {
        "severity": "high",
        "description": "Combined use significantly increases bleeding risk."
    },
}


def check_drug_interactions(medicines):
    """
    Check for potential drug interactions between medicines.
    This is a MOCK function - always consult a pharmacist!
    
    Args:
        medicines: List of medicine names
    
    Returns:
        List of found interactions
    """
    interactions = []
    medicines_lower = [m.lower() for m in medicines]
    
    # Check all pairs
    for i, med1 in enumerate(medicines_lower):
        for med2 in medicines_lower[i+1:]:
            # Check both orderings
            for drug1, drug2 in [(med1, med2), (med2, med1)]:
                # Check for exact match
                key = (drug1, drug2)
                if key in DRUG_INTERACTIONS:
                    interactions.append({
                        "drug1": med1.title(),
                        "drug2": med2.title(),
                        **DRUG_INTERACTIONS[key]
                    })
                    break
                # Check for partial match (e.g., "aspirin 100mg" matches "aspirin")
                for (d1, d2), info in DRUG_INTERACTIONS.items():
                    if (d1 in drug1 or drug1 in d1) and (d2 in drug2 or drug2 in d2):
                        interactions.append({
                            "drug1": med1.title(),
                            "drug2": med2.title(),
                            **info
                        })
                        break
    
    return interactions


# ============================================================================
# RISK PREDICTION (Mock Logic)
# ============================================================================

def predict_health_risks(patient_data, health_readings):
    """
    Predict potential health risks based on patient data and readings.
    This is a MOCK function for demonstration only!
    
    Args:
        patient_data: Patient information dictionary
        health_readings: List of health tracking readings
    
    Returns:
        Dictionary with risk assessments
    """
    risks = []
    
    # Check BP readings
    bp_readings = [r for r in health_readings if r['type'] == 'bp']
    if bp_readings:
        latest_bp = bp_readings[-1]['value']
        try:
            systolic, diastolic = map(int, latest_bp.split('/'))
            if systolic >= 140 or diastolic >= 90:
                risks.append({
                    "condition": "Hypertension Risk",
                    "level": "high" if systolic >= 160 else "medium",
                    "description": f"Your recent BP reading ({latest_bp}) indicates elevated blood pressure.",
                    "recommendation": "Consider lifestyle changes and consult your doctor."
                })
        except (ValueError, AttributeError):
            pass
    
    # Check sugar readings
    sugar_readings = [r for r in health_readings if r['type'] == 'sugar']
    if sugar_readings:
        try:
            latest_sugar = float(sugar_readings[-1]['value'])
            if latest_sugar >= 126:
                risks.append({
                    "condition": "Diabetes Risk",
                    "level": "high" if latest_sugar >= 200 else "medium",
                    "description": f"Your fasting blood sugar ({latest_sugar} mg/dL) is elevated.",
                    "recommendation": "Schedule a glucose tolerance test with your doctor."
                })
        except (ValueError, TypeError):
            pass
    
    # Check age-related risks
    if patient_data.get('dob'):
        try:
            birth_year = int(patient_data['dob'].split('-')[0])
            age = datetime.now().year - birth_year
            if age >= 45:
                risks.append({
                    "condition": "Age-Related Screening",
                    "level": "low",
                    "description": "Based on your age, regular health screenings are recommended.",
                    "recommendation": "Schedule annual checkups including cardiac and cancer screenings."
                })
        except (ValueError, IndexError):
            pass
    
    # Check allergies
    if patient_data.get('allergies'):
        risks.append({
            "condition": "Allergy Alert",
            "level": "info",
            "description": f"Known allergies: {', '.join(patient_data['allergies'])}",
            "recommendation": "Always inform healthcare providers about these allergies."
        })
    
    if not risks:
        risks.append({
            "condition": "General Health",
            "level": "low",
            "description": "No significant risk factors identified based on available data.",
            "recommendation": "Continue maintaining a healthy lifestyle!"
        })
    
    return {"risks": risks, "assessed_at": datetime.now().isoformat()}


# ============================================================================
# OCR MOCK FUNCTION
# ============================================================================

def mock_ocr_scan(file_bytes):
    """
    Mock OCR function that returns dummy extracted text.
    In production, this would use actual OCR libraries like Tesseract.
    
    Args:
        file_bytes: Uploaded file bytes
    
    Returns:
        Dictionary with extracted text
    """
    # Simulate OCR processing
    mock_extracted_text = """
    PRESCRIPTION
    ============
    
    Patient Name: [Extracted from image]
    Date: [Current Date]
    
    Medications:
    1. Amoxicillin 500mg - Take twice daily for 7 days
    2. Paracetamol 650mg - Take as needed for fever
    3. Vitamin D3 60000 IU - Once weekly
    
    Diagnosis: Upper Respiratory Tract Infection
    
    Follow-up: After 1 week
    
    Doctor's Signature: [Detected]
    Hospital Stamp: [Detected]
    
    ---
    Note: This is mock OCR output for demonstration.
    """
    
    return {
        "success": True,
        "extracted_text": mock_extracted_text.strip(),
        "confidence": random.uniform(0.85, 0.98),
        "processed_at": datetime.now().isoformat()
    }


# ============================================================================
# MEDICINE ADHERENCE CALCULATOR
# ============================================================================

def calculate_adherence(prescriptions):
    """
    Calculate medicine adherence percentage based on purchased medicines.
    
    Args:
        prescriptions: List of prescription dictionaries
    
    Returns:
        Dictionary with adherence statistics
    """
    total_medicines = 0
    purchased_medicines = 0
    
    for rx in prescriptions:
        if rx.get('status') == 'active':
            for medicine in rx.get('medicines', []):
                total_medicines += 1
                if medicine.get('purchased', False):
                    purchased_medicines += 1
    
    adherence_rate = (purchased_medicines / total_medicines * 100) if total_medicines > 0 else 100
    
    return {
        "total_medicines": total_medicines,
        "purchased": purchased_medicines,
        "pending": total_medicines - purchased_medicines,
        "adherence_rate": round(adherence_rate, 1),
        "status": "good" if adherence_rate >= 80 else "needs_attention" if adherence_rate >= 50 else "poor"
    }


# ============================================================================
# TRANSLATION MOCK (Multi-language Support)
# ============================================================================

TRANSLATIONS = {
    "es": {  # Spanish
        "welcome": "Bienvenido",
        "dashboard": "Panel de Control",
        "appointments": "Citas",
        "prescriptions": "Recetas",
        "profile": "Perfil",
        "logout": "Cerrar Sesión",
        "health_id": "ID de Salud",
    },
    "hi": {  # Hindi
        "welcome": "स्वागत है",
        "dashboard": "डैशबोर्ड",
        "appointments": "अपॉइंटमेंट",
        "prescriptions": "नुस्खे",
        "profile": "प्रोफ़ाइल",
        "logout": "लॉग आउट",
        "health_id": "स्वास्थ्य आईडी",
    },
    "fr": {  # French
        "welcome": "Bienvenue",
        "dashboard": "Tableau de Bord",
        "appointments": "Rendez-vous",
        "prescriptions": "Ordonnances",
        "profile": "Profil",
        "logout": "Déconnexion",
        "health_id": "ID Santé",
    }
}


def translate(text, language="en"):
    """
    Mock translation function.
    
    Args:
        text: Text key to translate
        language: Target language code
    
    Returns:
        Translated text or original if not found
    """
    if language == "en":
        return text.replace("_", " ").title()
    
    lang_dict = TRANSLATIONS.get(language, {})
    return lang_dict.get(text.lower(), text.replace("_", " ").title())


# ============================================================================
# SMART ALERTS
# ============================================================================

def generate_smart_alerts(patient_data, appointments, prescriptions, health_readings):
    """
    Generate smart alerts and reminders for a patient.
    
    Args:
        patient_data: Patient information
        appointments: Patient's appointments
        prescriptions: Patient's prescriptions
        health_readings: Patient's health readings
    
    Returns:
        List of alert dictionaries
    """
    alerts = []
    now = datetime.now()
    
    # Check upcoming appointments
    for apt in appointments:
        if apt.get('status') == 'scheduled':
            apt_date = datetime.strptime(apt['appointment_date'], "%Y-%m-%d")
            days_until = (apt_date - now).days
            if 0 <= days_until <= 3:
                alerts.append({
                    "type": "appointment",
                    "priority": "high" if days_until == 0 else "medium",
                    "title": "Upcoming Appointment",
                    "message": f"You have an appointment with {apt['doctor_name']} on {apt['appointment_date']} at {apt['appointment_time']}",
                    "action": "View appointment details"
                })
    
    # Check pending prescriptions
    for rx in prescriptions:
        if rx.get('status') == 'active':
            pending_meds = [m for m in rx.get('medicines', []) if not m.get('purchased')]
            if pending_meds:
                alerts.append({
                    "type": "prescription",
                    "priority": "medium",
                    "title": "Pending Medicines",
                    "message": f"You have {len(pending_meds)} medicine(s) to purchase from prescription {rx['prescription_id']}",
                    "action": "View prescription"
                })
    
    # Check health readings
    bp_readings = [r for r in health_readings if r['type'] == 'bp']
    if bp_readings:
        latest = bp_readings[-1]
        try:
            systolic, diastolic = map(int, latest['value'].split('/'))
            if systolic >= 140 or diastolic >= 90:
                alerts.append({
                    "type": "health",
                    "priority": "high",
                    "title": "High Blood Pressure Alert",
                    "message": f"Your recent BP reading ({latest['value']}) is above normal range.",
                    "action": "Track your BP and consult a doctor"
                })
        except (ValueError, AttributeError):
            pass
    
    # Check for missing health data
    if not health_readings or len(health_readings) < 3:
        alerts.append({
            "type": "reminder",
            "priority": "low",
            "title": "Track Your Health",
            "message": "Regular health tracking helps monitor your wellbeing. Consider logging your BP and sugar levels.",
            "action": "Go to Health Tracking"
        })
    
    return alerts
