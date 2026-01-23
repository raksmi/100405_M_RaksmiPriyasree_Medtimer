import streamlit as st
import sqlite3
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, date
import pandas as pd
import random
import base64
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import time

# ==================== CONFIGURATION ====================
st.set_page_config(
    page_title="MedTimer Pro - Medication Management",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== DATABASE FUNCTIONS ====================
def init_database():
    """Initialize SQLite database with all tables"""
    conn = sqlite3.connect('medtimer.db', check_same_thread=False)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY,
                  name TEXT,
                  age INTEGER,
                  email TEXT,
                  password TEXT,
                  user_type TEXT,
                  phone TEXT,
                  relationship TEXT,
                  experience TEXT,
                  notes TEXT,
                  created_at TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS diseases
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  name TEXT,
                  type TEXT,
                  notes TEXT,
                  FOREIGN KEY(username) REFERENCES users(username))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS medications
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  name TEXT,
                  dosage_type TEXT,
                  dosage_amount TEXT,
                  frequency TEXT,
                  time TEXT,
                  color TEXT,
                  instructions TEXT,
                  taken_today INTEGER,
                  taken_times TEXT,
                  reminder_times TEXT,
                  created_at TEXT,
                  FOREIGN KEY(username) REFERENCES users(username))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS appointments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  doctor TEXT,
                  specialty TEXT,
                  date TEXT,
                  time TEXT,
                  location TEXT,
                  phone TEXT,
                  notes TEXT,
                  created_at TEXT,
                  FOREIGN KEY(username) REFERENCES users(username))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS side_effects
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  medication TEXT,
                  severity TEXT,
                  type TEXT,
                  description TEXT,
                  date TEXT,
                  reported_at TEXT,
                  FOREIGN KEY(username) REFERENCES users(username))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS medication_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  medication_id INTEGER,
                  action TEXT,
                  timestamp TEXT,
                  date TEXT,
                  FOREIGN KEY(username) REFERENCES users(username))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS adherence_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  date TEXT,
                  adherence REAL,
                  updated TEXT,
                  FOREIGN KEY(username) REFERENCES users(username))''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect('medtimer.db', check_same_thread=False)

# ==================== UTILITY FUNCTIONS ====================
def get_age_category(age):
    """Determine age category based on age"""
    if age < 18:
        return 'youth'
    elif age <= 40:
        return 'adult'
    else:
        return 'senior'

def get_primary_color(age_category):
    """Get primary color based on age category"""
    if age_category == 'youth':
        return "#8B5CF6"  # Purple
    elif age_category == 'adult':
        return "#10B981"  # Green
    else:
        return "#F59E0B"  # Amber

def get_secondary_color(age_category):
    """Get secondary color based on age category"""
    if age_category == 'youth':
        return "#A78BFA"
    elif age_category == 'adult':
        return "#34D399"
    else:
        return "#FBBF24"

def get_gradient_colors(age_category):
    """Get gradient colors based on age category"""
    if age_category == 'youth':
        return {
            'primary': '#8B5CF6',
            'secondary': '#A78BFA',
            'accent': '#C4B5FD',
            'gradient': 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #9333ea 100%)'
        }
    elif age_category == 'adult':
        return {
            'primary': '#10B981',
            'secondary': '#34D399',
            'accent': '#6EE7B7',
            'gradient': 'linear-gradient(135deg, #11998e 0%, #38ef7d 50%, #10b981 100%)'
        }
    else:
        return {
            'primary': '#F59E0B',
            'secondary': '#FBBF24',
            'accent': '#FCD34D',
            'gradient': 'linear-gradient(135deg, #f093fb 0%, #f5576c 50%, #f59e0b 100%)'
        }

def format_time(time_str):
    """Format time string"""
    try:
        time_obj = datetime.strptime(time_str, "%H:%M")
        return time_obj.strftime("%I:%M %p")
    except:
        return time_str

def get_custom_medication_times(frequency):
    """Get default custom medication times based on frequency"""
    frequency_map = {
        'once-daily': ['09:00'],
        'twice-daily': ['08:00', '20:00'],
        'three-times-daily': ['08:00', '13:00', '20:00'],
        'every-4-hours': ['08:00', '12:00', '16:00', '20:00'],
        'every-6-hours': ['06:00', '12:00', '18:00', '00:00'],
        'every-8-hours': ['08:00', '16:00', '00:00'],
        'every-12-hours': ['08:00', '20:00'],
        'as-needed': ['09:00'],
        'weekly': ['09:00'],
        'monthly': ['09:00']
    }
    return frequency_map.get(frequency, ['09:00'])

def get_time_of_day():
    """Get current time of day greeting"""
    hour = datetime.now().hour
    if hour < 12:
        return "Good Morning"
    elif hour < 18:
        return "Good Afternoon"
    else:
        return "Good Evening"

# ==================== FIXED: Medication Categorization ====================
def categorize_medications_by_status(medications):
    """
    FIXED: Properly categorize medications into missed, upcoming, and taken
    This function now correctly handles medications with multiple doses
    """
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    
    missed = []
    upcoming = []
    taken = []
    
    for med in medications:
        # Ensure taken_times exists
        if 'taken_times' not in med or not isinstance(med['taken_times'], list):
            med['taken_times'] = []
        
        # Get all dose times for this medication
        reminder_times_json = med.get('reminder_times', '[]')
        if isinstance(reminder_times_json, str):
            try:
                reminder_times = json.loads(reminder_times_json) if reminder_times_json else []
            except:
                reminder_times = []
        else:
            reminder_times = reminder_times_json
        
        # If no reminder_times, use the main time
        if not reminder_times:
            reminder_times = [med.get('time', '00:00')]
        
        # Process each dose time
        all_doses_taken = True
        has_missed = False
        
        for dose_time in reminder_times:
            if dose_time in med['taken_times']:
                continue  # This dose already taken
            
            all_doses_taken = False
            
            if dose_time < current_time:
                # Dose time has passed - it's missed
                has_missed = True
                if not any(m['id'] == med['id'] and m['time'] == dose_time for m in missed):
                    missed.append({
                        'id': med['id'],
                        'name': med['name'],
                        'time': dose_time,
                        'dosageAmount': med['dosageAmount'],
                        'color': med.get('color', 'blue')
                    })
            elif dose_time > current_time:
                # Dose time is in the future - it's upcoming
                if not any(m['id'] == med['id'] and m['time'] == dose_time for m in upcoming):
                    upcoming.append({
                        'id': med['id'],
                        'name': med['name'],
                        'time': dose_time,
                        'dosageAmount': med['dosageAmount'],
                        'color': med.get('color', 'blue')
                    })
        
        # Add medication to taken list if all doses are taken
        if all_doses_taken:
            taken.append(med)
    
    # Sort by time
    missed.sort(key=lambda x: x['time'])
    upcoming.sort(key=lambda x: x['time'])
    
    return missed, upcoming, taken

def calculate_adherence(medications):
    """Calculate medication adherence percentage (dose-based)"""
    if not medications:
        return 0

    total_doses = 0        
    taken_doses = 0        

    for med in medications:
        # Ensure taken_times exists and is a list
        if 'taken_times' not in med or not isinstance(med['taken_times'], list):
            med['taken_times'] = []
        
        # Get reminder times
        reminder_times_json = med.get('reminder_times', '[]')
        if isinstance(reminder_times_json, str):
            try:
                reminder_times = json.loads(reminder_times_json) if reminder_times_json else []
            except:
                reminder_times = []
        else:
            reminder_times = reminder_times_json
        
        # If no reminder_times, use main time
        if not reminder_times:
            reminder_times = [med.get('time', '00:00')]
        
        total_doses += len(reminder_times)
        taken_doses += len(med['taken_times'])

    return (taken_doses / total_doses * 100) if total_doses > 0 else 0

def get_medication_color_hex(color_name):
    """Convert color name to hex value"""
    colors = {
        'blue': '#3B82F6', 'green': '#10B981', 'purple': '#8B5CF6',
        'pink': '#EC4899', 'orange': '#F59E0B', 'red': '#EF4444',
        'yellow': '#EAB308', 'indigo': '#6366F1', 'teal': '#14B8A6', 'cyan': '#06B6D4'
    }
    return colors.get(color_name.lower(), '#3B82F6')

# ==================== SESSION STATE ====================
def initialize_session_state():
    """Initialize all session state variables"""
    if 'page' not in st.session_state:
        st.session_state.page = 'account_type_selection'
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = None
    if 'medications' not in st.session_state:
        st.session_state.medications = []
    if 'appointments' not in st.session_state:
        st.session_state.appointments = []
    if 'side_effects' not in st.session_state:
        st.session_state.side_effects = []
    if 'turtle_mood' not in st.session_state:
        st.session_state.turtle_mood = 'happy'
    if 'achievements' not in st.session_state:
        st.session_state.achievements = []
    if 'signup_step' not in st.session_state:
        st.session_state.signup_step = 1
    if 'signup_data' not in st.session_state:
        st.session_state.signup_data = {}
    if 'editing_medication' not in st.session_state:
        st.session_state.editing_medication = None
    if 'sound_enabled' not in st.session_state:
        st.session_state.sound_enabled = True
    if 'button_counter' not in st.session_state:
        st.session_state.button_counter = 0
    if 'undo_stack' not in st.session_state:
        st.session_state.undo_stack = []
    if 'checklist_filter' not in st.session_state:
        st.session_state.checklist_filter = 'all'
    if 'medication_history' not in st.session_state:
        st.session_state.medication_history = []
    if 'adherence_history' not in st.session_state:
        st.session_state.adherence_history = []

# ==================== MODERN CSS ====================
def inject_modern_css(age_category='adult'):
    """Inject modern, stunning CSS into Streamlit app"""
    colors = get_gradient_colors(age_category)
    primary = colors['primary']
    secondary = colors['secondary']
    accent = colors['accent']
    gradient = colors['gradient']
    
    css = f"""
    <style>
    /* Global Styles */
    .stApp {{
        background: {gradient};
        min-height: 100vh;
    }}
    
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Glassmorphism Effect */
    .glass-card {{
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }}
    
    .glass-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }}
    
    /* Stat Cards */
    .stat-card {{
        background: rgba(255, 255, 255, 0.95);
        border-radius: 24px;
        padding: 32px 24px;
        text-align: center;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border-top: 5px solid {primary};
        position: relative;
        overflow: hidden;
    }}
    
    .stat-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, {primary}22, transparent);
        opacity: 0;
        transition: opacity 0.3s ease;
    }}
    
    .stat-card:hover {{
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
    }}
    
    .stat-card:hover::before {{
        opacity: 1;
    }}
    
    .stat-number {{
        font-size: 64px;
        font-weight: 900;
        background: linear-gradient(135deg, {primary}, {secondary});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.2;
        margin-bottom: 8px;
        position: relative;
        z-index: 1;
    }}
    
    .stat-label {{
        font-size: 14px;
        color: #6B7280;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        position: relative;
        z-index: 1;
    }}
    
    /* Medication Cards */
    .medication-card {{
        background: white;
        border-radius: 20px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
        border-left: 6px solid {primary};
        position: relative;
        overflow: hidden;
    }}
    
    .medication-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, {primary}, {secondary});
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }}
    
    .medication-card:hover {{
        transform: translateY(-8px);
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
    }}
    
    .medication-card:hover::before {{
        transform: scaleX(1);
    }}
    
    /* Checklist Items */
    .checklist-item {{
        background: white;
        border-radius: 16px;
        padding: 20px;
        margin: 12px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
        border-left: 6px solid;
        display: flex;
        align-items: center;
        gap: 16px;
    }}
    
    .checklist-item.taken {{
        border-left-color: #10B981;
        background: linear-gradient(135deg, #ECFDF5, white);
    }}
    
    .checklist-item.missed {{
        border-left-color: #EF4444;
        background: linear-gradient(135deg, #FEF2F2, white);
    }}
    
    .checklist-item.upcoming {{
        border-left-color: #F59E0B;
        background: linear-gradient(135deg, #FFFBEB, white);
    }}
    
    .checklist-checkbox {{
        width: 28px;
        height: 28px;
        border: 3px solid;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
    }}
    
    .checklist-checkbox.checked {{
        background-color: #10B981;
        border-color: #10B981;
        color: white;
    }}
    
    .checklist-checkbox.missed {{
        background-color: #EF4444;
        border-color: #EF4444;
        color: white;
    }}
    
    .checklist-checkbox.upcoming {{
        background-color: #F59E0B;
        border-color: #F59E0B;
        color: white;
    }}
    
    /* Button Styles */
    .stButton > button {{
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 14px 28px !important;
        border: none !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        font-size: 16px !important;
        position: relative;
        overflow: hidden;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2) !important;
    }}
    
    .stButton > button:active {{
        transform: translateY(0) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    }}
    
    /* Filter Buttons */
    .filter-btn {{
        background: white;
        color: #6B7280;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: 2px solid transparent;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }}
    
    .filter-btn.active {{
        background: linear-gradient(135deg, {primary}, {secondary});
        color: white;
        border-color: {primary};
        box-shadow: 0 4px 16px rgba({int(primary[1:3], 16)}, {int(primary[3:5], 16)}, {int(primary[5:7], 16)}, 0.4);
    }}
    
    .filter-btn:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }}
    
    /* Status Badges */
    .status-badge {{
        display: inline-block;
        padding: 8px 20px;
        border-radius: 25px;
        font-weight: 700;
        font-size: 14px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
    }}
    
    .status-badge.taken {{
        background: linear-gradient(135deg, #10B981, #059669);
        color: white;
    }}
    
    .status-badge.missed {{
        background: linear-gradient(135deg, #EF4444, #DC2626);
        color: white;
    }}
    
    .status-badge.upcoming {{
        background: linear-gradient(135deg, #F59E0B, #D97706);
        color: white;
    }}
    
    .status-badge.pending {{
        background: linear-gradient(135deg, #3B82F6, #2563EB);
        color: white;
    }}
    
    /* Animations */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    @keyframes pulse {{
        0%, 100% {{ transform: scale(1); }}
        50% {{ transform: scale(1.05); }}
    }}
    
    @keyframes float {{
        0%, 100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-10px); }}
    }}
    
    .animate-fade-in {{
        animation: fadeIn 0.6s ease-out forwards;
    }}
    
    .animate-pulse {{
        animation: pulse 2s infinite;
    }}
    
    .animate-float {{
        animation: float 3s ease-in-out infinite;
    }}
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {{
        font-weight: 800 !important;
        color: white !important;
    }}
    
    p, div, span, label {{
        color: white !important;
    }}
    
    .medication-card p, 
    .medication-card div, 
    .medication-card span {{
        color: #1F2937 !important;
    }}
    
    .stat-card p, 
    .stat-card div, 
    .stat-card span {{
        color: #1F2937 !important;
    }}
    
    /* Progress Bar */
    .stProgress > div > div > div {{
        background: linear-gradient(90deg, {primary} 0%, {secondary} 100%) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba({int(primary[1:3], 16)}, {int(primary[3:5], 16)}, {int(primary[5:7], 16)}, 0.4) !important;
    }}
    
    /* Icons */
    .med-icon {{
        width: 60px;
        height: 60px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }}
    
    /* Toast Notifications */
    .stAlert {{
        border-radius: 16px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        animation: fadeIn 0.4s ease-out;
    }}
    
    /* Time Display */
    .time-display {{
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 20px 40px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }}
    
    /* Mascot Container */
    .mascot-container {{
        animation: float 4s ease-in-out infinite;
    }}
    
    /* Section Headers */
    .section-header {{
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
    }}
    
    .section-header h3 {{
        font-size: 28px;
        margin: 0;
        background: linear-gradient(135deg, white, rgba(255, 255, 255, 0.8));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    .section-header .icon {{
        font-size: 32px;
        animation: pulse 2s infinite;
    }}
    </style>
    """
    return css

# ==================== DATA FUNCTIONS ====================
def save_user_data():
    """Save user data to SQLite database"""
    if not st.session_state.user_profile:
        return False
    
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        username = st.session_state.user_profile.get('username')
        
        c.execute('''INSERT OR REPLACE INTO users 
                     (username, name, age, email, password, user_type, phone, relationship, experience, notes, created_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (username,
                   st.session_state.user_profile.get('name'),
                   st.session_state.user_profile.get('age'),
                   st.session_state.user_profile.get('email', ''),
                   st.session_state.user_profile.get('password', ''),
                   st.session_state.user_profile.get('userType'),
                   st.session_state.user_profile.get('phone', ''),
                   st.session_state.user_profile.get('relationship', ''),
                   st.session_state.user_profile.get('experience', ''),
                   st.session_state.user_profile.get('notes', ''),
                   datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        c.execute('DELETE FROM medications WHERE username = ?', (username,))
        for med in st.session_state.medications:
            # Ensure taken_times exists and is properly formatted
            if 'taken_times' not in med:
                med['taken_times'] = []
            
            # Convert taken_times to JSON for storage
            taken_times_json = json.dumps(med['taken_times'])
            
            # Convert reminder_times to JSON for storage
            reminder_times = med.get('reminder_times', [])
            reminder_times_json = json.dumps(reminder_times) if reminder_times else '[]'
                
            c.execute('''INSERT INTO medications 
                         (username, name, dosage_type, dosage_amount, frequency, time, color, instructions, taken_today, taken_times, reminder_times, created_at)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (username, med.get('name'), med.get('dosageType'), med.get('dosageAmount'),
                      med.get('frequency'), med.get('time'), med.get('color'),
                      med.get('instructions', ''), int(med.get('taken_today', False)),
                      taken_times_json, reminder_times_json,
                      med.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
        
        c.execute('DELETE FROM appointments WHERE username = ?', (username,))
        for appt in st.session_state.appointments:
            c.execute('''INSERT INTO appointments 
                         (username, doctor, specialty, date, time, location, phone, notes, created_at)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (username, appt.get('doctor'), appt.get('specialty'), appt.get('date'),
                      appt.get('time'), appt.get('location', ''), appt.get('phone', ''),
                      appt.get('notes', ''), appt.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
        
        c.execute('DELETE FROM side_effects WHERE username = ?', (username,))
        for effect in st.session_state.side_effects:
            c.execute('''INSERT INTO side_effects 
                         (username, medication, severity, type, description, date, reported_at)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                     (username, effect.get('medication'), effect.get('severity'),
                      effect.get('type', ''), effect.get('description'),
                      effect.get('date'), effect.get('reported_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

def load_user_data(username):
    """Load user data from SQLite database"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        
        if not user:
            conn.close()
            return False
        
        st.session_state.user_profile = {
            'username': user[0],
            'name': user[1],
            'age': user[2],
            'email': user[3],
            'password': user[4],
            'userType': user[5],
            'phone': user[6],
            'relationship': user[7],
            'experience': user[8],
            'notes': user[9],
            'diseases': []
        }
        
        c.execute('SELECT * FROM medications WHERE username = ?', (username,))
        meds = c.fetchall()
        st.session_state.medications = []
        for med in meds:
            # Parse taken_times from JSON
            taken_times = []
            try:
                if med[11]:  # taken_times column
                    taken_times = json.loads(med[11])
            except:
                pass
            
            # Parse reminder_times from JSON
            reminder_times = []
            try:
                if med[12]:  # reminder_times column
                    reminder_times = json.loads(med[12])
            except:
                pass
            
            st.session_state.medications.append({
                'id': med[0],
                'name': med[2],
                'dosageType': med[3],
                'dosageAmount': med[4],
                'frequency': med[5],
                'time': med[6],
                'color': med[7],
                'instructions': med[8],
                'taken_today': bool(med[9]),
                'taken_times': taken_times,
                'reminder_times': reminder_times,
                'created_at': med[13]
            })
        
        c.execute('SELECT * FROM appointments WHERE username = ?', (username,))
        appts = c.fetchall()
        st.session_state.appointments = []
        for appt in appts:
            st.session_state.appointments.append({
                'id': appt[0],
                'doctor': appt[2],
                'specialty': appt[3],
                'date': appt[4],
                'time': appt[5],
                'location': appt[6],
                'phone': appt[7],
                'notes': appt[8],
                'created_at': appt[9]
            })
        
        c.execute('SELECT * FROM side_effects WHERE username = ?', (username,))
        effects = c.fetchall()
        st.session_state.side_effects = []
        for effect in effects:
            st.session_state.side_effects.append({
                'id': effect[0],
                'medication': effect[2],
                'severity': effect[3],
                'type': effect[4],
                'description': effect[5],
                'date': effect[6],
                'reported_at': effect[7]
            })
        
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return False

def user_exists(username):
    """Check if user exists"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT username FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    conn.close()
    return result is not None

def save_state_to_undo_stack(action_type="medication_change"):
    """Save current state to undo stack"""
    if len(st.session_state.undo_stack) >= 10:
        st.session_state.undo_stack.pop(0)
    
    state_snapshot = {
        'action_type': action_type,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'medications': [med.copy() for med in st.session_state.medications]
    }
    st.session_state.undo_stack.append(state_snapshot)

def undo_last_action():
    """Undo the last action"""
    if not st.session_state.undo_stack:
        return False
    
    previous_state = st.session_state.undo_stack.pop()
    st.session_state.medications = previous_state['medications']
    save_user_data()
    return True

def clear_session_data():
    """Clear all session data (logout)"""
    st.session_state.user_profile = None
    st.session_state.medications = []
    st.session_state.appointments = []
    st.session_state.side_effects = []
    st.session_state.achievements = []
    st.session_state.medication_history = []
    st.session_state.adherence_history = []
    st.session_state.turtle_mood = 'happy'
    st.session_state.signup_step = 1
    st.session_state.signup_data = {}
    st.session_state.editing_medication = None
    st.session_state.undo_stack = []
    st.session_state.checklist_filter = 'all'

# ==================== PAGES ====================
def account_type_selection_page():
    """Landing page for selecting account type"""
    st.markdown("""
    <div style="text-align: center; padding: 60px 20px;">
        <h1 style="font-size: 48px; margin-bottom: 20px;">🏥 MedTimer Pro</h1>
        <p style="font-size: 24px; margin-bottom: 60px; opacity: 0.9;">
            Your Comprehensive Medication Management Solution
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("👤 Patient", key="patient_btn", use_container_width=True):
                st.session_state.account_type = 'patient'
                st.session_state.page = 'patient_login'
                st.rerun()
        
        with col_b:
            if st.button("🤝 Caregiver", key="caregiver_btn", use_container_width=True):
                st.session_state.account_type = 'caregiver'
                st.session_state.page = 'caregiver_login'
                st.rerun()

def patient_login_page():
    """Patient login page"""
    if st.button("← Back", key="login_back"):
        st.session_state.page = 'account_type_selection'
        st.rerun()
    
    st.markdown("""
    <h1 style="text-align: center; margin-top: 40px;">💊 Patient Login</h1>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(20px); 
                    border-radius: 24px; padding: 40px; border: 1px solid rgba(255, 255, 255, 0.2);">
        """, unsafe_allow_html=True)
        
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        col_login, col_signup = st.columns(2)
        with col_login:
            if st.button("✨ Sign In", key="signin_btn", use_container_width=True):
                if username and password:
                    if load_user_data(username):
                        st.success(f"Welcome back, {st.session_state.user_profile['name']}!")
                        st.session_state.page = 'patient_dashboard'
                        st.rerun()
                    else:
                        st.error("User not found. Please sign up first!")
                else:
                    st.warning("Please enter username and password")
        
        with col_signup:
            if st.button("Sign Up", key="goto_signup_btn", use_container_width=True):
                st.session_state.page = 'patient_signup'
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

def patient_signup_page():
    """Patient signup page"""
    if st.button("← Back", key="signup_back"):
        st.session_state.page = 'patient_login'
        st.session_state.signup_step = 1
        st.session_state.signup_data = {}
        st.rerun()
    
    st.markdown("""
    <h1 style="text-align: center; color: white;">📝 Create Patient Account</h1>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(20px); 
                    border-radius: 24px; padding: 40px; border: 1px solid rgba(255, 255, 255, 0.2);">
        """, unsafe_allow_html=True)
        
        username = st.text_input("Username", key="signup_username")
        name = st.text_input("Full Name", key="signup_name")
        age = st.number_input("Age", min_value=1, max_value=120, value=25, key="signup_age")
        password = st.text_input("Password", type="password", key="signup_password")
        
        if st.button("🎉 Create Account", key="complete_signup_btn", use_container_width=True):
            if name and username and password:
                if user_exists(username):
                    st.error("Username already exists! Please choose another.")
                else:
                    st.session_state.user_profile = {
                        'name': name,
                        'username': username,
                        'age': age,
                        'email': '',
                        'password': password,
                        'userType': 'patient',
                        'diseases': [],
                    }
                    
                    save_user_data()
                    st.success("Registration complete! Welcome to MedTimer Pro!")
                    st.session_state.page = 'patient_dashboard'
                    st.rerun()
            else:
                st.warning("Please fill all required fields")
        
        st.markdown("</div>", unsafe_allow_html=True)

# ==================== DASHBOARD ====================
def patient_dashboard_page():
    """Main patient dashboard with modern design"""
    if not st.session_state.user_profile:
        st.session_state.page = 'patient_login'
        st.rerun()
        return
    
    age = st.session_state.user_profile.get('age', 25)
    age_category = get_age_category(age)
    greeting = get_time_of_day()
    
    st.markdown(inject_modern_css(age_category), unsafe_allow_html=True)
    
    # Header
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="section-header">
            <span class="icon">👋</span>
            <h2>{greeting}, {st.session_state.user_profile['name']}!</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Time display
        now = datetime.now()
        current_date = now.strftime("%A, %B %d, %Y")
        current_time = now.strftime("%I:%M %p")
        
        st.markdown(f"""
        <div class="time-display animate-fade-in">
            <h3 style="margin: 0; font-size: 20px;">📅 {current_date}</h3>
            <p style="margin: 5px 0 0 0; font-size: 16px; opacity: 0.9;">🕐 {current_time}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("🚪 Logout", key="dashboard_logout", use_container_width=True):
            save_user_data()
            clear_session_data()
            st.session_state.page = 'account_type_selection'
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Stats row
    missed, upcoming, taken = categorize_medications_by_status(st.session_state.medications)
    adherence = calculate_adherence(st.session_state.medications)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_meds = len(st.session_state.medications)
        st.markdown(f"""
        <div class="stat-card animate-fade-in" style="animation-delay: 0.1s;">
            <div class="stat-number">{total_meds}</div>
            <div class="stat-label">Medications</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        taken_today = len(taken)
        st.markdown(f"""
        <div class="stat-card animate-fade-in" style="animation-delay: 0.2s;">
            <div class="stat-number">{taken_today}</div>
            <div class="stat-label">Taken Today</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        missed_count = len(missed)
        st.markdown(f"""
        <div class="stat-card animate-fade-in" style="animation-delay: 0.3s;">
            <div class="stat-number">{missed_count}</div>
            <div class="stat-label">Missed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        adherence_color = "#10B981" if adherence >= 70 else "#F59E0B" if adherence >= 50 else "#EF4444"
        st.markdown(f"""
        <div class="stat-card animate-fade-in" style="animation-delay: 0.4s;">
            <div class="stat-number" style="background: linear-gradient(135deg, {adherence_color}, {adherence_color}88);">
                {adherence:.0f}%
            </div>
            <div class="stat-label">Adherence</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Medication Checklist Section
    st.markdown("""
    <div class="section-header">
        <span class="icon">✅</span>
        <h3>Today's Medication Checklist</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Filter buttons
    col_filter1, col_filter2, col_filter3, col_filter4, col_filter5 = st.columns(5)
    
    with col_filter1:
        if st.button("📋 All", key="filter_all", use_container_width=True):
            st.session_state.checklist_filter = 'all'
            st.rerun()
    
    with col_filter2:
        if st.button("🟢 Taken", key="filter_taken", use_container_width=True):
            st.session_state.checklist_filter = 'taken'
            st.rerun()
    
    with col_filter3:
        if st.button("🟡 Upcoming", key="filter_upcoming", use_container_width=True):
            st.session_state.checklist_filter = 'upcoming'
            st.rerun()
    
    with col_filter4:
        if st.button("🔴 Missed", key="filter_missed", use_container_width=True):
            st.session_state.checklist_filter = 'missed'
            st.rerun()
    
    with col_filter5:
        if st.button("➕ Add", key="add_med_shortcut", use_container_width=True):
            st.session_state.editing_medication = "new"
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Display medications based on filter
    if st.session_state.checklist_filter == 'all' or st.session_state.checklist_filter == 'taken':
        if taken:
            st.markdown(f"""
            <div class="section-header">
                <span class="icon">🟢</span>
                <h4 style="color: #10B981;">TAKEN ({len(taken)})</h4>
            </div>
            """, unsafe_allow_html=True)
            
            for med in taken:
                color_hex = get_medication_color_hex(med.get('color', 'blue'))
                times = med.get('reminder_times', [med.get('time', '00:00')])
                times_str = ', '.join([format_time(t) for t in times])
                
                st.markdown(f"""
                <div class="checklist-item taken animate-fade-in">
                    <div class="checklist-checkbox checked">✓</div>
                    <div style="flex: 1;">
                        <strong style="font-size: 18px;">{med['name']}</strong>
                        <div style="margin-top: 4px;">
                            <span style="color: #6B7280;">{med['dosageAmount']}</span>
                            <span style="color: #9CA3AF; margin: 0 8px;">|</span>
                            <span style="color: #6B7280;">{times_str}</span>
                        </div>
                    </div>
                    <div class="med-icon" style="background: {color_hex}20; color: {color_hex};">💊</div>
                </div>
                """, unsafe_allow_html=True)
    
    if st.session_state.checklist_filter == 'all' or st.session_state.checklist_filter == 'upcoming':
        if upcoming:
            st.markdown(f"""
            <div class="section-header">
                <span class="icon">🟡</span>
                <h4 style="color: #F59E0B;">UPCOMING ({len(upcoming)})</h4>
            </div>
            """, unsafe_allow_html=True)
            
            for med in upcoming:
                color_hex = get_medication_color_hex(med.get('color', 'blue'))
                med_time = datetime.strptime(med['time'], "%H:%M")
                now = datetime.now()
                time_diff = (med_time - now).total_seconds() / 60
                
                col_med, col_btn = st.columns([4, 1])
                
                with col_med:
                    st.markdown(f"""
                    <div class="checklist-item upcoming animate-fade-in">
                        <div class="checklist-checkbox upcoming">⏰</div>
                        <div style="flex: 1;">
                            <strong style="font-size: 18px;">{med['name']}</strong>
                            <div style="margin-top: 4px;">
                                <span style="color: #6B7280;">{med['dosageAmount']}</span>
                                <span style="color: #9CA3AF; margin: 0 8px;">|</span>
                                <span style="color: #6B7280;">{format_time(med['time'])}</span>
                            </div>
                        </div>
                        <div>
                            <span style="color: #F59E0B; font-weight: 700; font-size: 14px;">
                                In {int(time_diff)} min
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_btn:
                    st.session_state.button_counter += 1
                    if st.button("📌 Take", key=f"take_upcoming_{med['id']}_{med['time']}_{st.session_state.button_counter}", use_container_width=True):
                        save_state_to_undo_stack("take_now")
                        
                        # FIXED: Properly update medication status
                        for m in st.session_state.medications:
                            if m['id'] == med['id']:
                                # Ensure taken_times exists
                                if 'taken_times' not in m or not isinstance(m['taken_times'], list):
                                    m['taken_times'] = []
                                
                                # Add this dose time to taken_times
                                if med['time'] not in m['taken_times']:
                                    m['taken_times'].append(med['time'])
                                
                                # Update taken_today if all doses are taken
                                reminder_times = m.get('reminder_times', [])
                                if not reminder_times:
                                    reminder_times = [m.get('time', '00:00')]
                                
                                if set(m['taken_times']) == set(reminder_times):
                                    m['taken_today'] = True
                                
                                break
                        
                        save_user_data()
                        st.success(f"✓ {med['name']} marked as taken!")
                        st.rerun()
    
    if st.session_state.checklist_filter == 'all' or st.session_state.checklist_filter == 'missed':
        if missed:
            st.markdown(f"""
            <div class="section-header">
                <span class="icon">🔴</span>
                <h4 style="color: #EF4444;">MISSED ({len(missed)})</h4>
            </div>
            """, unsafe_allow_html=True)
            
            for med in missed:
                color_hex = get_medication_color_hex(med.get('color', 'blue'))
                
                col_med, col_btn = st.columns([4, 1])
                
                with col_med:
                    st.markdown(f"""
                    <div class="checklist-item missed animate-fade-in">
                        <div class="checklist-checkbox missed">⚠️</div>
                        <div style="flex: 1;">
                            <strong style="font-size: 18px;">{med['name']}</strong>
                            <div style="margin-top: 4px;">
                                <span style="color: #6B7280;">{med['dosageAmount']}</span>
                                <span style="color: #9CA3AF; margin: 0 8px;">|</span>
                                <span style="color: #6B7280;">{format_time(med['time'])}</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_btn:
                    st.session_state.button_counter += 1
                    if st.button("📌 Take", key=f"take_missed_{med['id']}_{med['time']}_{st.session_state.button_counter}", use_container_width=True):
                        save_state_to_undo_stack("take_late")
                        
                        # FIXED: Properly update medication status
                        for m in st.session_state.medications:
                            if m['id'] == med['id']:
                                # Ensure taken_times exists
                                if 'taken_times' not in m or not isinstance(m['taken_times'], list):
                                    m['taken_times'] = []
                                
                                # Add this dose time to taken_times
                                if med['time'] not in m['taken_times']:
                                    m['taken_times'].append(med['time'])
                                
                                # Update taken_today if all doses are taken
                                reminder_times = m.get('reminder_times', [])
                                if not reminder_times:
                                    reminder_times = [m.get('time', '00:00')]
                                
                                if set(m['taken_times']) == set(reminder_times):
                                    m['taken_today'] = True
                                
                                break
                        
                        save_user_data()
                        st.success(f"✓ {med['name']} marked as taken!")
                        st.rerun()
        else:
            if st.session_state.checklist_filter == 'missed':
                st.success("🎉 No missed medications! Great job!")
    
    # Add Medication Modal
    if st.session_state.editing_medication == "new":
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="medication-card">
            <h3>➕ Add New Medication</h3>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("add_medication_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_med_name = st.text_input("Medication Name", key="new_med_name")
                new_dosage_type = st.selectbox("Type", ["pill", "liquid", "injection", "other"], key="new_dosage_type")
                new_dosage_amount = st.text_input("Dosage Amount", key="new_dosage_amount")
            
            with col2:
                new_frequency = st.selectbox("Frequency", [
                    "once-daily", "twice-daily", "three-times-daily",
                    "every-4-hours", "every-6-hours", "every-8-hours",
                    "every-12-hours", "as-needed", "weekly", "monthly"
                ], key="new_frequency")
                
                default_times = get_custom_medication_times(new_frequency)
                reminder_times_input = []
                
                for i, default_time in enumerate(default_times):
                    time_input = st.time_input(f"Time {i+1}", value=datetime.strptime(default_time, "%H:%M").time(), key=f"new_time_{i}")
                    reminder_times_input.append(time_input.strftime("%H:%M"))
            
            new_color = st.selectbox("Color", ["Blue", "Green", "Purple", "Pink", "Orange", "Red", "Yellow", "Indigo"], key="new_color")
            
            col_add, col_cancel = st.columns(2)
            with col_add:
                if st.form_submit_button("Add Medication", use_container_width=True):
                    if new_med_name and new_dosage_amount:
                        save_state_to_undo_stack("add_medication")
                        new_med = {
                            'id': len(st.session_state.medications) + 1,
                            'name': new_med_name,
                            'dosageType': new_dosage_type,
                            'dosageAmount': new_dosage_amount,
                            'frequency': new_frequency,
                            'time': reminder_times_input[0] if reminder_times_input else '09:00',
                            'color': new_color.lower(),
                            'instructions': '',
                            'taken_today': False,
                            'taken_times': [],
                            'reminder_times': reminder_times_input if len(reminder_times_input) > 1 else [],
                            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        st.session_state.medications.append(new_med)
                        save_user_data()
                        st.success(f"✅ Added {new_med_name}!")
                        st.session_state.editing_medication = None
                        st.rerun()
                    else:
                        st.warning("Please fill in medication name and dosage")
            
            with col_cancel:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.editing_medication = None
                    st.rerun()
    
    # Undo button
    if st.session_state.undo_stack:
        st.markdown("<br>", unsafe_allow_html=True)
        col_undo_left, col_undo_right = st.columns([8, 1])
        with col_undo_right:
            if st.button("↩️ Undo", key="undo_btn", use_container_width=True, help=f"Undo last action"):
                if undo_last_action():
                    st.success("Undo successful!")
                    st.rerun()
                else:
                    st.error("Nothing to undo")

# ==================== MAIN ROUTER ====================
def main():
    """Main application router"""
    
    init_database()
    initialize_session_state()
    
    page = st.session_state.page
    
    if page == 'account_type_selection':
        account_type_selection_page()
    elif page == 'patient_login':
        patient_login_page()
    elif page == 'patient_signup':
        patient_signup_page()
    elif page == 'patient_dashboard':
        patient_dashboard_page()
    else:
        account_type_selection_page()

if __name__ == "__main__":
    main()
