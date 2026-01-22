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

st.set_page_config(
    page_title="MedTimer - Medication Management",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
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
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    if 'medication_history' not in st.session_state:
        st.session_state.medication_history = []
    if 'adherence_history' not in st.session_state:
        st.session_state.adherence_history = []
    if 'connected_patients' not in st.session_state:
        st.session_state.connected_patients = []
    if 'editing_medication' not in st.session_state:
        st.session_state.editing_medication = None
    if 'sound_enabled' not in st.session_state:
        st.session_state.sound_enabled = True
    if 'last_reminder_check' not in st.session_state:
        st.session_state.last_reminder_check = datetime.now()
    if 'celebration_triggered' not in st.session_state:
        st.session_state.celebration_triggered = False
    if 'last_adherence' not in st.session_state:
        st.session_state.last_adherence = 0
    if 'medication_actions' not in st.session_state:
        st.session_state.medication_actions = {}

# Enhanced CSS with modern styling
def inject_enhanced_css(age_category='adult'):
    """Inject modern, visually appealing CSS"""
    primary_color = get_primary_color(age_category)
    secondary_color = get_secondary_color(age_category)
    
    css = f"""
    <style>
    /* Global App Styling */
    .stApp {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        min-height: 100vh;
    }}
    
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Typography - High Contrast */
    h1, h2, h3, h4, h5, h6 {{
        font-weight: 800 !important;
        color: #ffffff !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        letter-spacing: -0.5px;
    }}
    
    p, div, span, label {{
        font-size: 16px !important;
        color: #ffffff !important;
        font-weight: 500 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }}
    
    /* Hero Section */
    .hero-section {{
        background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.1) 100%);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 40px;
        margin: 20px 0;
        border: 2px solid rgba(255,255,255,0.3);
        box-shadow: 0 20px 60px rgba(0,0,0,0.2);
    }}
    
    /* Modern Card Styling */
    .card {{
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%);
        border-radius: 20px;
        padding: 28px;
        margin: 16px 0;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        border: 1px solid rgba(255,255,255,0.5);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }}
    
    .card:hover {{
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 60px rgba(0,0,0,0.25);
    }}
    
    .card h1, .card h2, .card h3, .card h4, .card h5, .card h6,
    .card p, .card div, .card span {{
        color: #1f2937 !important;
        text-shadow: none !important;
    }}
    
    /* Stat Cards */
    .stat-card {{
        background: linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(255,255,255,0.9) 100%);
        border-radius: 24px;
        padding: 32px 24px;
        text-align: center;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        transition: all 0.4s ease;
        border: 2px solid rgba(255,255,255,0.8);
        position: relative;
        overflow: hidden;
    }}
    
    .stat-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, {primary_color}, {secondary_color});
    }}
    
    .stat-card:hover {{
        transform: translateY(-12px) scale(1.05);
        box-shadow: 0 25px 50px rgba(0,0,0,0.2);
    }}
    
    .stat-number {{
        font-size: 64px;
        font-weight: 900;
        background: linear-gradient(135deg, {primary_color}, {secondary_color});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.1;
        margin-bottom: 8px;
    }}
    
    .stat-label {{
        font-size: 18px;
        color: #4b5563 !important;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    /* Medication Cards */
    .medication-card {{
        background: linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(255,255,255,0.92) 100%);
        border-radius: 24px;
        padding: 24px;
        margin: 12px 0;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        transition: all 0.3s ease;
        border-left: 6px solid {primary_color};
        position: relative;
    }}
    
    .medication-card:hover {{
        transform: translateX(8px);
        box-shadow: 0 12px 32px rgba(0,0,0,0.18);
    }}
    
    .medication-card h1, .medication-card h2, .medication-card h3,
    .medication-card h4, .medication-card h5, .medication-card h6,
    .medication-card p, .medication-card div, .medication-card span {{
        color: #1f2937 !important;
        text-shadow: none !important;
    }}
    
    /* Status Badges */
    .status-badge {{
        display: inline-block;
        padding: 8px 20px;
        border-radius: 50px;
        font-weight: 700;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }}
    
    .status-taken {{
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white !important;
    }}
    
    .status-missed {{
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white !important;
    }}
    
    .status-upcoming {{
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white !important;
    }}
    
    .status-pending {{
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white !important;
    }}
    
    /* Button Styling */
    .stButton > button {{
        border-radius: 16px !important;
        font-weight: 700 !important;
        padding: 14px 28px !important;
        border: none !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.15) !important;
        font-size: 16px !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #ffffff !important;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-4px) !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.25) !important;
    }}
    
    /* Action Buttons */
    .action-button {{
        padding: 12px 24px;
        border-radius: 12px;
        font-weight: 700;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 4px;
    }}
    
    .take-button {{
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }}
    
    .skip-button {{
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
    }}
    
    .undo-button {{
        background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
        color: white;
    }}
    
    .action-button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.2);
    }}
    
    /* Celebration Animation */
    @keyframes balloon-float {{
        0%, 100% {{ transform: translateY(0) rotate(-2deg); }}
        50% {{ transform: translateY(-20px) rotate(2deg); }}
    }}
    
    @keyframes confetti-fall {{
        0% {{ transform: translateY(-100vh) rotate(0deg); opacity: 1; }}
        100% {{ transform: translateY(100vh) rotate(720deg); opacity: 0; }}
    }}
    
    @keyframes sparkle {{
        0%, 100% {{ transform: scale(1); opacity: 1; }}
        50% {{ transform: scale(1.5); opacity: 0.8; }}
    }}
    
    .balloon {{
        position: fixed;
        width: 60px;
        height: 80px;
        border-radius: 50% 50% 50% 50%;
        animation: balloon-float 3s ease-in-out infinite;
        z-index: 9999;
        opacity: 0.9;
    }}
    
    .confetti {{
        position: fixed;
        width: 10px;
        height: 10px;
        animation: confetti-fall 4s linear infinite;
        z-index: 9999;
    }}
    
    .celebration-container {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 9998;
        overflow: hidden;
    }}
    
    .sparkle {{
        animation: sparkle 1.5s ease-in-out infinite;
    }}
    
    /* Progress Bar */
    .progress-container {{
        background: rgba(255,255,255,0.2);
        border-radius: 12px;
        overflow: hidden;
        height: 12px;
        box-shadow: inset 0 2px 8px rgba(0,0,0,0.2);
    }}
    
    .progress-bar {{
        height: 100%;
        background: linear-gradient(90deg, {primary_color}, {secondary_color});
        border-radius: 12px;
        transition: width 0.5s ease;
        box-shadow: 0 0 20px {primary_color};
    }}
    
    /* Mascot Container */
    .mascot-container {{
        animation: float 3s ease-in-out infinite;
    }}
    
    @keyframes float {{
        0%, 100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-15px); }}
    }}
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {{
        background: rgba(255,255,255,0.15);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 8px;
        gap: 8px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 12px 24px;
        color: white !important;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {primary_color}, {secondary_color});
        color: white !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }}
    
    /* Reminder Section */
    .reminder-section {{
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.9) 100%);
        border: 3px solid {primary_color};
        border-radius: 20px;
        padding: 24px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }}
    
    .reminder-item {{
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.8) 100%);
        border-radius: 16px;
        padding: 20px;
        margin: 12px 0;
        border-left: 5px solid {primary_color};
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}
    
    /* Achievement Cards */
    .achievement-card {{
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%);
        border-radius: 20px;
        padding: 24px;
        margin: 12px 0;
        text-align: center;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        border: 3px solid #10b981;
        transition: all 0.3s ease;
    }}
    
    .achievement-card:hover {{
        transform: scale(1.05);
        box-shadow: 0 12px 36px rgba(0,0,0,0.18);
    }}
    
    /* Input Styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input {{
        background: rgba(255,255,255,0.95) !important;
        border-radius: 12px !important;
        border: 2px solid rgba(255,255,255,0.3) !important;
        color: #1f2937 !important;
        font-weight: 600 !important;
        padding: 12px 16px !important;
    }}
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {{
        border-color: {primary_color} !important;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.3) !important;
    }}
    
    /* Success Message */
    .success-message {{
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 16px 24px;
        border-radius: 16px;
        font-weight: 700;
        box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3);
        animation: slideIn 0.5s ease;
    }}
    
    @keyframes slideIn {{
        from {{ transform: translateX(-100%); opacity: 0; }}
        to {{ transform: translateX(0); opacity: 1; }}
    }}
    
    /* Colors */
    .color-indicator {{
        width: 20px;
        height: 20px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        border: 2px solid white;
    }}
    </style>
    """
    return css

# Helper functions (keeping existing ones)
def get_primary_color(age_category):
    if age_category == 'youth':
        return "#9333ea"
    elif age_category == 'adult':
        return "#22c55e"
    else:
        return "#eab308"

def get_secondary_color(age_category):
    if age_category == 'youth':
        return "#a855f7"
    elif age_category == 'adult':
        return "#16a34a"
    else:
        return "#ca8a04"

def get_age_category(age):
    if age < 18:
        return 'youth'
    elif age <= 40:
        return 'adult'
    else:
        return 'senior'

def calculate_adherence(medications):
    if not medications:
        return 0

    total_doses = 0
    taken_doses = 0

    for med in medications:
        times = med.get('reminder_times', [med.get('time')])
        total_doses += len(times)
        taken_doses += len(med.get('taken_times', []))

    return (taken_doses / total_doses * 100) if total_doses > 0 else 0

def format_time(time_str):
    try:
        time_obj = datetime.strptime(time_str, "%H:%M")
        return time_obj.strftime("%I:%M %p")
    except:
        return time_str

def get_time_of_day():
    hour = datetime.now().hour
    if hour < 12:
        return "Good Morning"
    elif hour < 18:
        return "Good Afternoon"
    else:
        return "Good Evening"

def get_medication_color_hex(color_name):
    colors = {
        'blue': '#3B82F6', 'green': '#10B981', 'purple': '#8B5CF6',
        'pink': '#EC4899', 'orange': '#F59E0B', 'red': '#EF4444',
        'yellow': '#EAB308', 'indigo': '#6366F1', 'teal': '#14B8A6', 'cyan': '#06B6D4'
    }
    return colors.get(color_name.lower(), '#3B82F6')

# Celebration functions
def trigger_celebration():
    """Trigger celebration animation for 100% adherence"""
    celebration_html = """
    <div class="celebration-container" id="celebration">
        <script>
        // Create balloons
        const balloonColors = ['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899'];
        const container = document.getElementById('celebration');
        
        for (let i = 0; i < 15; i++) {
            const balloon = document.createElement('div');
            balloon.className = 'balloon';
            balloon.style.left = Math.random() * 100 + '%';
            balloon.style.top = Math.random() * 100 + '%';
            balloon.style.background = `radial-gradient(circle at 30% 30%, white 0%, ${balloonColors[i % balloonColors.length]} 100%)`;
            balloon.style.animationDelay = Math.random() * 2 + 's';
            balloon.style.boxShadow = `0 0 20px ${balloonColors[i % balloonColors.length]}`;
            container.appendChild(balloon);
        }
        
        // Create confetti
        const confettiColors = ['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6'];
        for (let i = 0; i < 50; i++) {
            const confetti = document.createElement('div');
            confetti.className = 'confetti';
            confetti.style.left = Math.random() * 100 + '%';
            confetti.style.background = confettiColors[Math.floor(Math.random() * confettiColors.length)];
            confetti.style.animationDelay = Math.random() * 3 + 's';
            confetti.style.borderRadius = Math.random() > 0.5 ? '50%' : '0';
            container.appendChild(confetti);
        }
        
        // Play celebration sound
        const audio = new Audio('https://assets.mixkit.co/active_storage/sfx/1435/1435-preview.mp3');
        audio.volume = 0.5;
        audio.play();
        
        // Remove celebration after 8 seconds
        setTimeout(() => {
            container.remove();
        }, 8000);
        </script>
    </div>
    """
    st.markdown(celebration_html, unsafe_allow_html=True)
    st.session_state.celebration_triggered = True

def check_and_trigger_celebration(adherence):
    """Check if celebration should be triggered"""
    if adherence >= 100 and not st.session_state.celebration_triggered:
        trigger_celebration()
    elif adherence < 100:
        st.session_state.celebration_triggered = False

# Medication action handlers
def take_medication(medication_id, dose_time=None):
    """Mark medication as taken"""
    for med in st.session_state.medications:
        if med['id'] == medication_id:
            time_to_mark = dose_time if dose_time else med['time']
            if time_to_mark not in med.get('taken_times', []):
                med.setdefault('taken_times', []).append(time_to_mark)
            
            # Check if all doses are taken
            all_times = med.get('reminder_times', [med['time']])
            if set(med.get('taken_times', [])) == set(all_times):
                med['taken_today'] = True
            
            # Record action for undo
            action_id = f"take_{medication_id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            st.session_state.medication_actions[action_id] = {
                'type': 'take',
                'medication_id': medication_id,
                'time': time_to_mark,
                'timestamp': datetime.now()
            }
            
            # Check for celebration
            adherence = calculate_adherence(st.session_state.medications)
            check_and_trigger_celebration(adherence)
            
            save_user_data()
            st.rerun()
            break

def skip_medication(medication_id, dose_time=None):
    """Skip a medication dose"""
    for med in st.session_state.medications:
        if med['id'] == medication_id:
            time_to_skip = dose_time if dose_time else med['time']
            
            # Record action for undo
            action_id = f"skip_{medication_id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            st.session_state.medication_actions[action_id] = {
                'type': 'skip',
                'medication_id': medication_id,
                'time': time_to_skip,
                'timestamp': datetime.now()
            }
            
            save_user_data()
            st.rerun()
            break

def undo_last_action():
    """Undo the last medication action"""
    if not st.session_state.medication_actions:
        st.warning("No actions to undo")
        return
    
    # Get the most recent action
    action_id = max(st.session_state.medication_actions.keys())
    action = st.session_state.medication_actions[action_id]
    
    # Undo the action
    if action['type'] == 'take':
        for med in st.session_state.medications:
            if med['id'] == action['medication_id']:
                if action['time'] in med.get('taken_times', []):
                    med['taken_times'].remove(action['time'])
                    med['taken_today'] = False
                break
    elif action['type'] == 'skip':
        # For skip, we might want to restore the medication to pending
        # This is a simplified version
        pass
    
    # Remove the action
    del st.session_state.medication_actions[action_id]
    save_user_data()
    st.rerun()

# Save and Load functions (simplified)
def save_user_data():
    """Save user data to SQLite database"""
    if not st.session_state.user_profile:
        return False
    
    try:
        conn = sqlite3.connect('medtimer.db', check_same_thread=False)
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
            c.execute('''INSERT INTO medications 
                         (username, name, dosage_type, dosage_amount, frequency, time, color, instructions, taken_today, created_at)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (username, med.get('name'), med.get('dosageType'), med.get('dosageAmount'),
                      med.get('frequency'), med.get('time'), med.get('color'),
                      med.get('instructions', ''), int(med.get('taken_today', False)),
                      med.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        return False

def init_database():
    """Initialize SQLite database"""
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
                  created_at TEXT,
                  FOREIGN KEY(username) REFERENCES users(username))''')
    
    conn.commit()
    conn.close()

# Enhanced Dashboard Page
def enhanced_dashboard_page():
    """Enhanced dashboard with modern UI"""
    if not st.session_state.user_profile:
        st.session_state.page = 'account_type_selection'
        st.rerun()
        return
    
    age = st.session_state.user_profile.get('age', 25)
    age_category = get_age_category(age)
    greeting = get_time_of_day()
    
    # Inject enhanced CSS
    st.markdown(inject_enhanced_css(age_category), unsafe_allow_html=True)
    
    # Hero Section
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="hero-section">
            <h1 style="font-size: 48px; margin-bottom: 12px;">👋 {greeting}, {st.session_state.user_profile['name']}!</h1>
            <p style="font-size: 20px; margin: 0; opacity: 0.9;">Ready to crush your medication goals today? 💪</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Quick stats
        total_meds = len(st.session_state.medications)
        adherence = calculate_adherence(st.session_state.medications)
        
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{adherence:.0f}%</div>
            <div class="stat-label">Today's Adherence</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            save_user_data()
            st.session_state.user_profile = None
            st.session_state.page = 'account_type_selection'
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Action Buttons
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("↩️ Undo Last Action", use_container_width=True):
            undo_last_action()
    
    # Stats Row
    st.markdown("<h2 style='color: #ffffff; text-align: center; margin: 30px 0;'>📊 Today's Overview</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    taken_today = sum(1 for med in st.session_state.medications if med.get('taken_today', False))
    pending = len(st.session_state.medications) - taken_today
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{len(st.session_state.medications)}</div>
            <div class="stat-label">Total Meds</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number" style="background: linear-gradient(135deg, #10b981, #059669);">{taken_today}</div>
            <div class="stat-label">Taken</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number" style="background: linear-gradient(135deg, #f59e0b, #d97706);">{pending}</div>
            <div class="stat-label">Pending</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number" style="background: linear-gradient(135deg, #8b5cf6, #7c3aed);">{len(st.session_state.appointments)}</div>
            <div class="stat-label">Appointments</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Medication Schedule Section
    st.markdown("<h2 style='color: #ffffff; text-align: center; margin: 30px 0;'>💊 Today's Medication Schedule</h2>", unsafe_allow_html=True)
    
    # Categorize medications
    current_time = datetime.now().strftime("%H:%M")
    
    due_meds = []
    upcoming_meds = []
    taken_meds = []
    missed_meds = []
    
    for med in st.session_state.medications:
        med_times = med.get('reminder_times', [med.get('time', '00:00')])
        
        for dose_time in med_times:
            if dose_time in med.get('taken_times', []):
                continue
            
            time_diff = (datetime.strptime(dose_time, "%H:%M") - datetime.now()).total_seconds() / 60
            
            if abs(time_diff) <= 5:
                due_meds.append({
                    'id': med['id'],
                    'name': med['name'],
                    'time': dose_time,
                    'dosageAmount': med['dosageAmount'],
                    'color': med.get('color', 'blue')
                })
            elif time_diff > 0 and time_diff <= 30:
                upcoming_meds.append({
                    'id': med['id'],
                    'name': med['name'],
                    'time': dose_time,
                    'dosageAmount': med['dosageAmount'],
                    'color': med.get('color', 'blue')
                })
            elif time_diff < 0:
                missed_meds.append({
                    'id': med['id'],
                    'name': med['name'],
                    'time': dose_time,
                    'dosageAmount': med['dosageAmount'],
                    'color': med.get('color', 'blue')
                })
        
        if med.get('taken_today', False):
            taken_meds.append(med)
    
    # Due Medications (with sound)
    if due_meds:
        if st.session_state.sound_enabled:
            st.markdown("""
            <audio autoplay>
                <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
            </audio>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="reminder-section">
            <h2 style="color: #ef4444; text-align: center; margin-bottom: 20px;">🔔 TIME TO TAKE MEDICATION!</h2>
        </div>
        """, unsafe_allow_html=True)
        
        for med in due_meds:
            color_hex = get_medication_color_hex(med.get('color', 'blue'))
            st.markdown(f"""
            <div class="medication-card" style="border-left-color: #ef4444; border-width: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h3 style="font-size: 28px; margin-bottom: 8px;">{med['name']}</h3>
                        <p style="font-size: 18px; margin: 4px 0;"><strong>Dosage:</strong> {med['dosageAmount']}</p>
                        <p style="font-size: 18px; margin: 4px 0;"><strong>Time:</strong> {format_time(med['time'])}</p>
                    </div>
                    <div style="text-align: right;">
                        <span class="status-badge status-missed">DUE NOW</span>
                    </div>
                </div>
                <div style="margin-top: 20px; display: flex; gap: 10px;">
                    <button class="action-button take-button" onclick="document.querySelector('[data-testid=&quot;stButton&quot;]').click();">
                        ✅ Take Now
                    </button>
                    <button class="action-button skip-button">
                        ⏭️ Skip
                    </button>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Streamlit buttons for functionality
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✅ Take {med['name']}", key=f"take_due_{med['id']}_{med['time']}"):
                    take_medication(med['id'], med['time'])
            with col2:
                if st.button(f"⏭️ Skip {med['name']}", key=f"skip_due_{med['id']}_{med['time']}"):
                    skip_medication(med['id'], med['time'])
    
    # Upcoming Medications
    if upcoming_meds:
        st.markdown(f"""
        <div class="reminder-section" style="border-color: #f59e0b;">
            <h3 style="color: #f59e0b; text-align: center; margin-bottom: 20px;">⏰ Upcoming (Next 30 Minutes)</h3>
        </div>
        """, unsafe_allow_html=True)
        
        for med in upcoming_meds:
            color_hex = get_medication_color_hex(med.get('color', 'blue'))
            time_diff = (datetime.strptime(med['time'], "%H:%M") - datetime.now()).total_seconds() / 60
            
            st.markdown(f"""
            <div class="medication-card" style="border-left-color: {color_hex};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h3 style="font-size: 24px; margin-bottom: 8px;">{med['name']}</h3>
                        <p style="font-size: 16px; margin: 4px 0;"><strong>Dosage:</strong> {med['dosageAmount']}</p>
                        <p style="font-size: 16px; margin: 4px 0;"><strong>Time:</strong> {format_time(med['time'])}</p>
                        <p style="font-size: 16px; margin: 4px 0;"><strong>In:</strong> {int(time_diff)} minutes</p>
                    </div>
                    <div style="text-align: right;">
                        <span class="status-badge status-upcoming">UPCOMING</span>
                    </div>
                </div>
                <div style="margin-top: 16px; display: flex; gap: 10px;">
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✅ Take {med['name']}", key=f"take_upcoming_{med['id']}_{med['time']}"):
                    take_medication(med['id'], med['time'])
            with col2:
                if st.button(f"⏭️ Skip {med['name']}", key=f"skip_upcoming_{med['id']}_{med['time']}"):
                    skip_medication(med['id'], med['time'])
    
    # Missed Medications
    if missed_meds:
        st.markdown(f"""
        <div class="reminder-section" style="border-color: #ef4444;">
            <h3 style="color: #ef4444; text-align: center; margin-bottom: 20px;">❌ Missed Medications</h3>
        </div>
        """, unsafe_allow_html=True)
        
        for med in missed_meds:
            color_hex = get_medication_color_hex(med.get('color', 'blue'))
            st.markdown(f"""
            <div class="medication-card" style="border-left-color: #ef4444;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h3 style="font-size: 24px; margin-bottom: 8px;">{med['name']}</h3>
                        <p style="font-size: 16px; margin: 4px 0;"><strong>Dosage:</strong> {med['dosageAmount']}</p>
                        <p style="font-size: 16px; margin: 4px 0;"><strong>Was due at:</strong> {format_time(med['time'])}</p>
                    </div>
                    <div style="text-align: right;">
                        <span class="status-badge status-missed">MISSED</span>
                    </div>
                </div>
                <div style="margin-top: 16px; display: flex; gap: 10px;">
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✅ Take Now {med['name']}", key=f"take_missed_{med['id']}_{med['time']}"):
                    take_medication(med['id'], med['time'])
            with col2:
                if st.button(f"⏭️ Skip {med['name']}", key=f"skip_missed_{med['id']}_{med['time']}"):
                    skip_medication(med['id'], med['time'])
    
    # Taken Medications
    if taken_meds:
        st.markdown(f"""
        <div class="reminder-section" style="border-color: #10b981;">
            <h3 style="color: #10b981; text-align: center; margin-bottom: 20px;">✅ Completed Today</h3>
        </div>
        """, unsafe_allow_html=True)
        
        for med in taken_meds:
            color_hex = get_medication_color_hex(med.get('color', 'blue'))
            st.markdown(f"""
            <div class="medication-card" style="border-left-color: #10b981;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h3 style="font-size: 24px; margin-bottom: 8px;">{med['name']}</h3>
                        <p style="font-size: 16px; margin: 4px 0;"><strong>Dosage:</strong> {med['dosageAmount']}</p>
                        <p style="font-size: 16px; margin: 4px 0;"><strong>Status:</strong> All doses taken</p>
                    </div>
                    <div style="text-align: right;">
                        <span class="status-badge status-taken">TAKEN ✅</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Progress Section
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="card">
        <h3 style="text-align: center; margin-bottom: 20px;">🎯 Today's Progress</h3>
        <div class="progress-container">
            <div class="progress-bar" style="width: {adherence}%;"></div>
        </div>
        <p style="text-align: center; margin-top: 16px; font-size: 20px; font-weight: 700;">
            {adherence:.0f}% Complete
        </p>
    </div>
    """, unsafe_allow_html=True)

# Landing Page
def landing_page():
    """Modern landing page"""
    st.markdown(inject_enhanced_css('adult'), unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; padding: 60px 20px;">
        <h1 style="font-size: 72px; margin-bottom: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
            🏥 MedTimer
        </h1>
        <p style="font-size: 28px; margin-bottom: 40px; opacity: 0.9;">
            Your Personal Medication Management Companion
        </p>
        
        <div style="max-width: 600px; margin: 0 auto;">
            <div class="card">
                <h2 style="text-align: center; margin-bottom: 30px;">Choose Your Account Type</h2>
                <div style="display: flex; gap: 20px; justify-content: center;">
                    <div style="flex: 1; text-align: center; padding: 30px; background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%); 
                         border-radius: 20px; border: 2px solid rgba(255,255,255,0.3); cursor: pointer; transition: all 0.3s ease;"
                         onmouseover="this.style.transform='scale(1.05)'; this.style.boxShadow='0 20px 40px rgba(0,0,0,0.2)';"
                         onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='none';">
                        <div style="font-size: 64px; margin-bottom: 16px;">👤</div>
                        <h3 style="margin-bottom: 8px;">Patient</h3>
                        <p style="font-size: 14px;">Manage your medications</p>
                    </div>
                    
                    <div style="flex: 1; text-align: center; padding: 30px; background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%); 
                         border-radius: 20px; border: 2px solid rgba(255,255,255,0.3); cursor: pointer; transition: all 0.3s ease;"
                         onmouseover="this.style.transform='scale(1.05)'; this.style.boxShadow='0 20px 40px rgba(0,0,0,0.2)';"
                         onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='none';">
                        <div style="font-size: 64px; margin-bottom: 16px;">🤝</div>
                        <h3 style="margin-bottom: 8px;">Caregiver</h3>
                        <p style="font-size: 14px;">Support loved ones</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("👤 Patient Account", use_container_width=True):
                st.session_state.page = 'patient_login'
                st.rerun()
        with col_b:
            if st.button("🤝 Caregiver Account", use_container_width=True):
                st.session_state.page = 'caregiver_login'
                st.rerun()

# Main App
def main():
    """Main application"""
    init_database()
    initialize_session_state()
    
    page = st.session_state.page
    
    if page == 'account_type_selection':
        landing_page()
    elif page == 'patient_login':
        # Simple login for demo
        st.markdown(inject_enhanced_css('adult'), unsafe_allow_html=True)
        st.markdown("""
        <div style="max-width: 500px; margin: 60px auto; padding: 40px; background: rgba(255,255,255,0.95); 
             border-radius: 24px; box-shadow: 0 20px 60px rgba(0,0,0,0.2);">
            <h2 style="text-align: center; margin-bottom: 30px;">🔐 Patient Login</h2>
        </div>
        """, unsafe_allow_html=True)
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✨ Sign In", use_container_width=True):
                if username and password:
                    st.session_state.user_profile = {
                        'name': username,
                        'username': username,
                        'age': 25,
                        'userType': 'patient',
                        'diseases': []
                    }
                    st.session_state.page = 'dashboard'
                    st.rerun()
            if st.button("← Back", use_container_width=True):
                st.session_state.page = 'account_type_selection'
                st.rerun()
    elif page == 'dashboard':
        enhanced_dashboard_page()
    else:
        landing_page()

if __name__ == "__main__":
    main()
