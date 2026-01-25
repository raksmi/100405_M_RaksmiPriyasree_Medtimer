
import streamlit as st
import sqlite3
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, date
import pandas as pd
import random

# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="MedTimer - Medication Management",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# DATABASE SETUP
# ============================================

def init_database():
    """Initialize SQLite database with all tables"""
    conn = sqlite3.connect('medtimer.db', check_same_thread=False)
    c = conn.cursor()
    
    # Users table
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
    
    # Diseases table
    c.execute('''CREATE TABLE IF NOT EXISTS diseases
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  name TEXT,
                  type TEXT,
                  notes TEXT,
                  FOREIGN KEY(username) REFERENCES users(username))''')
    
    # Medications table
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
    
    # Appointments table
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
    
    # Side effects table
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
    
    # Medication history table
    c.execute('''CREATE TABLE IF NOT EXISTS medication_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  medication_id INTEGER,
                  action TEXT,
                  timestamp TEXT,
                  date TEXT,
                  FOREIGN KEY(username) REFERENCES users(username))''')
    
    # Adherence history table
    c.execute('''CREATE TABLE IF NOT EXISTS adherence_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  date TEXT,
                  adherence REAL,
                  updated TEXT,
                  FOREIGN KEY(username) REFERENCES users(username))''')
    
    # Connected patients table (for caregivers)
    c.execute('''CREATE TABLE IF NOT EXISTS connected_patients
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  caregiver_username TEXT,
                  patient_username TEXT,
                  access_code TEXT,
                  connected_at TEXT,
                  FOREIGN KEY(caregiver_username) REFERENCES users(username))''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect('medtimer.db', check_same_thread=False)

# ============================================
# UTILITY FUNCTIONS
# ============================================

def get_age_category(age):
    """Determine age category based on age"""
    if age < 13:
        return 'kid'
    elif age <= 45:
        return 'adult'
    else:
        return 'senior'

def get_gradient_style(age_category):
    """Get gradient background style based on age category"""
    if age_category == 'kid':
        return "background: linear-gradient(135deg, #9333ea 0%, #ec4899 100%);"
    elif age_category == 'adult':
        return "background: linear-gradient(135deg, #ef4444 0%, #f97316 100%);"
    else:
        return "background: linear-gradient(135deg, #10b981 0%, #14b8a6 100%);"

def get_font_size(age_category):
    """Get font size based on age category"""
    if age_category == 'kid':
        return "16px"
    elif age_category == 'adult':
        return "18px"
    else:
        return "22px"

def get_primary_color(age_category):
    """Get primary color based on age category"""
    if age_category == 'kid':
        return "#9333ea"
    elif age_category == 'adult':
        return "#ef4444"
    else:
        return "#10b981"

def get_secondary_color(age_category):
    """Get secondary color based on age category"""
    if age_category == 'kid':
        return "#ec4899"
    elif age_category == 'adult':
        return "#f97316"
    else:
        return "#14b8a6"

def format_time(time_str):
    """Format time string"""
    try:
        time_obj = datetime.strptime(time_str, "%H:%M")
        return time_obj.strftime("%I:%M %p")
    except:
        return time_str

def calculate_adherence(medications):
    """Calculate medication adherence percentage"""
    if not medications:
        return 0
    taken = sum(1 for med in medications if med.get('taken_today', False))
    total = len(medications)
    return (taken / total * 100) if total > 0 else 0

def get_turtle_emoji(mood):
    """Get turtle emoji based on mood"""
    turtle_emojis = {
        'happy': '🐢😊',
        'sad': '🐢😢',
        'excited': '🐢🎉',
        'sleeping': '🐢😴',
        'thinking': '🐢🤔',
        'celebrating': '🐢🎊'
    }
    return turtle_emojis.get(mood, '🐢')

def get_severity_color(severity):
    """Get color for severity level"""
    colors = {'Mild': '#10b981', 'Moderate': '#f59e0b', 'Severe': '#ef4444'}
    return colors.get(severity, '#6b7280')

def get_severity_emoji(severity):
    """Get emoji for severity level"""
    emojis = {'Mild': '🟢', 'Moderate': '🟡', 'Severe': '🔴'}
    return emojis.get(severity, '⚪')

def get_medication_color_hex(color_name):
    """Convert color name to hex value"""
    colors = {
        'blue': '#3B82F6', 'green': '#10B981', 'purple': '#8B5CF6',
        'pink': '#EC4899', 'orange': '#F59E0B', 'red': '#EF4444',
        'yellow': '#EAB308', 'indigo': '#6366F1', 'teal': '#14B8A6', 'cyan': '#06B6D4'
    }
    return colors.get(color_name.lower(), '#3B82F6')

def format_date(date_str):
    """Format date string for display"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%B %d, %Y")
    except:
        return date_str

def days_until(date_str):
    """Calculate days until a date"""
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d")
        today = datetime.now()
        delta = target_date - today
        return delta.days
    except:
        return 0

def get_time_of_day():
    """Get current time of day greeting"""
    hour = datetime.now().hour
    if hour < 12:
        return "Good Morning"
    elif hour < 18:
        return "Good Afternoon"
    else:
        return "Good Evening"

def check_medication_conflicts(medications, new_medication):
    """Check for potential medication time conflicts"""
    conflicts = []
    new_time = new_medication.get('time', '00:00')
    for med in medications:
        med_time = med.get('time', '00:00')
        time_diff = abs(
            datetime.strptime(new_time, "%H:%M") - 
            datetime.strptime(med_time, "%H:%M")
        )
        if time_diff.total_seconds() < 1800:
            conflicts.append(med['name'])
    return conflicts

def generate_patient_code():
    """Generate a 6-digit patient access code"""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

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

# ============================================
# DATABASE FUNCTIONS
# ============================================

def save_user_data():
    """Save user data to SQLite database"""
    if not st.session_state.user_profile:
        return False
    
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        username = st.session_state.user_profile.get('username')
        
        # Update or insert user
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
        
        # Save diseases
        c.execute('DELETE FROM diseases WHERE username = ?', (username,))
        for disease in st.session_state.user_profile.get('diseases', []):
            c.execute('INSERT INTO diseases (username, name, type, notes) VALUES (?, ?, ?, ?)',
                     (username, disease.get('name'), disease.get('type'), disease.get('notes', '')))
        
        # Save medications
        c.execute('DELETE FROM medications WHERE username = ?', (username,))
        for med in st.session_state.medications:
            c.execute('''INSERT INTO medications 
                         (username, name, dosage_type, dosage_amount, frequency, time, color, instructions, taken_today, created_at)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (username, med.get('name'), med.get('dosageType'), med.get('dosageAmount'),
                      med.get('frequency'), med.get('time'), med.get('color'),
                      med.get('instructions', ''), int(med.get('taken_today', False)),
                      med.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
        
        # Save appointments
        c.execute('DELETE FROM appointments WHERE username = ?', (username,))
        for appt in st.session_state.appointments:
            c.execute('''INSERT INTO appointments 
                         (username, doctor, specialty, date, time, location, phone, notes, created_at)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (username, appt.get('doctor'), appt.get('specialty'), appt.get('date'),
                      appt.get('time'), appt.get('location', ''), appt.get('phone', ''),
                      appt.get('notes', ''), appt.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
        
        # Save side effects
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
        
        # Load user profile
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
        
        # Load diseases
        c.execute('SELECT * FROM diseases WHERE username = ?', (username,))
        diseases = c.fetchall()
        for disease in diseases:
            st.session_state.user_profile['diseases'].append({
                'id': str(disease[0]),
                'name': disease[2],
                'type': disease[3],
                'notes': disease[4]
            })
        
        # Load medications
        c.execute('SELECT * FROM medications WHERE username = ?', (username,))
        meds = c.fetchall()
        st.session_state.medications = []
        for med in meds:
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
                'created_at': med[10]
            })
        
        # Load appointments
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
        
        # Load side effects
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
        
        # Load medication history
        c.execute('SELECT * FROM medication_history WHERE username = ?', (username,))
        hist = c.fetchall()
        st.session_state.medication_history = []
        for h in hist:
            st.session_state.medication_history.append({
                'medication_id': h[2],
                'action': h[3],
                'timestamp': h[4],
                'date': h[5]
            })
        
        # Load adherence history
        c.execute('SELECT * FROM adherence_history WHERE username = ?', (username,))
        adh = c.fetchall()
        st.session_state.adherence_history = []
        for a in adh:
            st.session_state.adherence_history.append({
                'date': a[2],
                'adherence': a[3],
                'updated': a[4]
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

def update_medication_history(medication_id, action='taken'):
    """Update medication history"""
    if not st.session_state.user_profile:
        return
    
    username = st.session_state.user_profile['username']
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''INSERT INTO medication_history (username, medication_id, action, timestamp, date)
                 VALUES (?, ?, ?, ?, ?)''',
             (username, medication_id, action,
              datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
              datetime.now().strftime("%Y-%m-%d")))
    
    conn.commit()
    conn.close()

def update_adherence_history():
    """Update daily adherence history"""
    if not st.session_state.user_profile:
        return
    
    username = st.session_state.user_profile['username']
    today = datetime.now().strftime("%Y-%m-%d")
    
    if st.session_state.medications:
        taken = sum(1 for med in st.session_state.medications if med.get('taken_today', False))
        total = len(st.session_state.medications)
        adherence = (taken / total * 100) if total > 0 else 0
    else:
        adherence = 0
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Check if today's entry exists
    c.execute('SELECT id FROM adherence_history WHERE username = ? AND date = ?', (username, today))
    existing = c.fetchone()
    
    if existing:
        c.execute('UPDATE adherence_history SET adherence = ?, updated = ? WHERE id = ?',
                 (adherence, datetime.now().strftime("%H:%M:%S"), existing[0]))
    else:
        c.execute('INSERT INTO adherence_history (username, date, adherence, updated) VALUES (?, ?, ?, ?)',
                 (username, today, adherence, datetime.now().strftime("%H:%M:%S")))
    
    conn.commit()
    conn.close()

def clear_session_data():
    """Clear all session data (logout)"""
    st.session_state.user_profile = None
    st.session_state.medications = []
    st.session_state.appointments = []
    st.session_state.side_effects = []
    st.session_state.achievements = []
    st.session_state.medication_history = []
    st.session_state.adherence_history = []
    st.session_state.connected_patients = []
    st.session_state.turtle_mood = 'happy'
    st.session_state.signup_step = 1
    st.session_state.signup_data = {}

# ============================================
# CSS STYLES
# ============================================

def inject_custom_css():
    """Inject custom CSS into Streamlit app"""
    css = """
    <style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    h1 {
        font-weight: 800 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .medication-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border-left: 4px solid #667eea;
    }
    
    .medication-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
    }
    
    .stat-card {
        background: white;
        border-radius: 20px;
        padding: 30px 24px;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border-top: 4px solid #667eea;
    }
    
    .stat-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 16px 32px rgba(0,0,0,0.15);
    }
    
    .stat-number {
        font-size: 56px;
        font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.2;
        margin-bottom: 8px;
    }
    
    .stat-label {
        font-size: 16px;
        color: #6b7280;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .auth-card {
        background: white;
        border-radius: 24px;
        padding: 40px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        max-width: 500px;
        margin: 0 auto;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        border: none !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2) !important;
    }
    
    .status-taken {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 700;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
    }
    
    .status-missed {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 700;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);
    }
    
    .status-upcoming {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 700;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(245, 158, 11, 0.3);
    }
    
    .status-pending {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 700;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
    }
    
    .turtle-container {
        animation: float 3s ease-in-out infinite;
    }
    
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        border-radius: 10px !important;
    }
    
    .color-dot {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    </style>
    """
    return css

# ============================================
# CHART FUNCTIONS
# ============================================

def create_adherence_line_chart(adherence_history, age_category='adult'):
    """Create line chart showing adherence over time"""
    if not adherence_history:
        fig = go.Figure()
        fig.add_annotation(
            text="No adherence data available yet.<br>Start tracking your medications!",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="#6b7280")
        )
        fig.update_layout(height=400, xaxis=dict(visible=False), yaxis=dict(visible=False),
                         plot_bgcolor='white', paper_bgcolor='white')
        return fig
    
    sorted_history = sorted(adherence_history, key=lambda x: x['date'])
    dates = [h['date'] for h in sorted_history]
    adherence = [h['adherence'] for h in sorted_history]
    
    primary_color = get_primary_color(age_category)
    secondary_color = get_secondary_color(age_category)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=adherence, mode='lines+markers', name='Adherence',
        line=dict(color=primary_color, width=4),
        marker=dict(size=10, color=secondary_color, line=dict(width=2, color=primary_color)),
        fill='tozeroy',
        fillcolor=f'rgba({int(primary_color[1:3], 16)}, {int(primary_color[3:5], 16)}, {int(primary_color[5:7], 16)}, 0.2)'
    ))
    
    fig.add_hline(y=100, line_dash="dash", line_color="green",
                  annotation_text="100% Goal", annotation_position="right")
    
    fig.update_layout(
        title={'text': '📈 Medication Adherence Trend', 'font': {'size': 24, 'color': '#1f2937', 'family': 'Arial Black'}},
        xaxis_title='Date', yaxis_title='Adherence Rate (%)',
        yaxis=dict(range=[0, 105], ticksuffix='%'),
        height=450, plot_bgcolor='#f9fafb', paper_bgcolor='white',
        hovermode='x unified', showlegend=False, font=dict(size=14)
    )
    return fig

def create_medication_pie_chart(medications, age_category='adult'):
    """Create pie chart showing medications by type"""
    if not medications:
        fig = go.Figure()
        fig.add_annotation(
            text="No medications added yet.<br>Add your first medication!",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="#6b7280")
        )
        fig.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='white')
        return fig
    
    type_counts = {}
    for med in medications:
        med_type = med.get('dosageType', 'other').capitalize()
        type_counts[med_type] = type_counts.get(med_type, 0) + 1
    
    labels = list(type_counts.keys())
    values = list(type_counts.values())
    colors = ['#3B82F6', '#10B981', '#8B5CF6', '#EC4899', '#F59E0B', '#EF4444']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=0.4,
        marker=dict(colors=colors, line=dict(color='white', width=3)),
        textinfo='label+percent', textfont=dict(size=16, color='white', family='Arial Black'),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title={'text': '💊 Medications by Type', 'font': {'size': 24, 'color': '#1f2937', 'family': 'Arial Black'}},
        height=450, paper_bgcolor='white', showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    return fig

def create_daily_schedule_bar_chart(medications, age_category='adult'):
    """Create bar chart showing medication schedule throughout the day"""
    if not medications:
        fig = go.Figure()
        fig.add_annotation(
            text="No medications scheduled.<br>Add medications to see your daily schedule!",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="#6b7280")
        )
        fig.update_layout(height=400, xaxis=dict(visible=False), yaxis=dict(visible=False),
                         plot_bgcolor='white', paper_bgcolor='white')
        return fig
    
    hour_counts = {}
    colors_by_hour = {}
    
    for med in medications:
        time_str = med.get('time', '00:00')
        try:
            hour = int(time_str.split(':')[0])
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
            color = get_medication_color_hex(med.get('color', 'blue'))
            if hour not in colors_by_hour:
                colors_by_hour[hour] = color
        except:
            pass
    
    hours = sorted(hour_counts.keys())
    counts = [hour_counts[h] for h in hours]
    labels = [f"{h:02d}:00" for h in hours]
    colors = [colors_by_hour.get(h, '#3B82F6') for h in hours]
    
    fig = go.Figure(data=[
        go.Bar(x=labels, y=counts, marker=dict(color=colors, line=dict(color='white', width=2)),
               text=counts, textposition='outside', textfont=dict(size=14, color='#1f2937', family='Arial Black'))
    ])
    
    fig.update_layout(
        title={'text': '🕐 Daily Medication Schedule', 'font': {'size': 24, 'color': '#1f2937', 'family': 'Arial Black'}},
        xaxis_title='Time of Day', yaxis_title='Number of Medications',
        height=450, plot_bgcolor='#f9fafb', paper_bgcolor='white',
        showlegend=False, font=dict(size=14)
    )
    return fig

def create_side_effects_bar_chart(side_effects):
    """Create bar chart showing side effects by severity"""
    if not side_effects:
        fig = go.Figure()
        fig.add_annotation(
            text="No side effects reported.<br>Great job! Keep it up!",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="#10b981")
        )
        fig.update_layout(height=400, xaxis=dict(visible=False), yaxis=dict(visible=False),
                         plot_bgcolor='white', paper_bgcolor='white')
        return fig
    
    severity_counts = {'Mild': 0, 'Moderate': 0, 'Severe': 0}
    for effect in side_effects:
        severity = effect.get('severity', 'Mild')
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    severities = ['Mild', 'Moderate', 'Severe']
    counts = [severity_counts[s] for s in severities]
    colors = ['#10b981', '#f59e0b', '#ef4444']
    
    fig = go.Figure(data=[
        go.Bar(x=severities, y=counts, marker=dict(color=colors, line=dict(color='white', width=2)),
               text=counts, textposition='outside', textfont=dict(size=16, color='#1f2937', family='Arial Black'))
    ])
    
    fig.update_layout(
        title={'text': '⚠️ Side Effects by Severity', 'font': {'size': 24, 'color': '#1f2937', 'family': 'Arial Black'}},
        xaxis_title='Severity Level', yaxis_title='Number of Reports',
        height=450, plot_bgcolor='#f9fafb', paper_bgcolor='white',
        showlegend=False, font=dict(size=14)
    )
    return fig

def create_medication_status_donut(medications):
    """Create donut chart showing taken vs pending medications"""
    if not medications:
        fig = go.Figure()
        fig.add_annotation(
            text="No medications to track.<br>Add medications to see status!",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="#6b7280")
        )
        fig.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='white')
        return fig
    
    taken = sum(1 for med in medications if med.get('taken_today', False))
    pending = len(medications) - taken
    
    labels = ['Taken ✅', 'Pending ⏰']
    values = [taken, pending]
    colors = ['#10b981', '#f59e0b']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=0.5,
        marker=dict(colors=colors, line=dict(color='white', width=4)),
        textinfo='label+value', textfont=dict(size=18, color='white', family='Arial Black'),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.add_annotation(
        text=f"{(taken/len(medications)*100):.0f}%<br>Complete",
        x=0.5, y=0.5, font=dict(size=24, color='#1f2937', family='Arial Black'),
        showarrow=False
    )
    
    fig.update_layout(
        title={'text': '📊 Today\'s Progress', 'font': {'size': 24, 'color': '#1f2937', 'family': 'Arial Black'}},
        height=450, paper_bgcolor='white', showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
    )
    return fig

def create_weekly_heatmap(medication_history):
    """Create heatmap showing medication adherence by day and time"""
    if not medication_history:
        fig = go.Figure()
        fig.add_annotation(
            text="No medication history yet.<br>Start taking your medications to see patterns!",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="#6b7280")
        )
        fig.update_layout(height=400, xaxis=dict(visible=False), yaxis=dict(visible=False),
                         plot_bgcolor='white', paper_bgcolor='white')
        return fig
    
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    hours = [f"{h:02d}:00" for h in range(0, 24, 3)]
    data = [[random.randint(0, 3) for _ in hours] for _ in days]
    
    fig = go.Figure(data=go.Heatmap(
        z=data, x=hours, y=days,
        colorscale=[[0, '#f3f4f6'], [0.33, '#fef3c7'], [0.66, '#a7f3d0'], [1, '#10b981']],
        showscale=True, colorbar=dict(title='Medications<br>Taken'),
        hovertemplate='Day: %{y}<br>Time: %{x}<br>Medications: %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        title={'text': '📅 Weekly Medication Heatmap', 'font': {'size': 24, 'color': '#1f2937', 'family': 'Arial Black'}},
        xaxis_title='Time of Day', yaxis_title='Day of Week',
        height=400, plot_bgcolor='white', paper_bgcolor='white', font=dict(size=14)
    )
    return fig

# ============================================
# AUTHENTICATION PAGES
# ============================================

def account_type_selection_page():
    """Landing page for selecting account type"""
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>🏥 Welcome to MedTimer</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 20px; color: #fff; margin-bottom: 50px;'>Your Comprehensive Medication Management Solution</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; margin-bottom: 30px;'>Choose Account Type</h2>", unsafe_allow_html=True)
        
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
        
        st.markdown("</div>", unsafe_allow_html=True)

def patient_login_page():
    """Patient login page"""
    if st.button("← Back"):
        st.session_state.page = 'account_type_selection'
        st.rerun()
    
    st.markdown("<h1 style='text-align: center; margin-top: 20px;'>💊 Patient Login</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔒 Password", "📧 Email"])
        
        with tab1:
            st.markdown("### Username & Password Login")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("✨ Sign In", use_container_width=True):
                if username and password:
                    if load_user_data(username):
                        st.success(f"Welcome back, {st.session_state.user_profile['name']}!")
                        st.session_state.page = 'patient_dashboard'
                        st.rerun()
                    else:
                        st.error("User not found. Please sign up first!")
                else:
                    st.warning("Please enter username and password")
        
        with tab2:
            st.markdown("### Email Verification Login")
            email = st.text_input("Email Address", key="login_email")
            
            if st.button("Send Login Code", use_container_width=True):
                if email:
                    st.info(f"Demo: Verification code '123456' sent to {email}")
                    
            code = st.text_input("Enter 6-Digit Code", max_chars=6, key="verification_code")
            
            if st.button("Verify & Login", use_container_width=True):
                if code == "123456":
                    st.success("Login successful!")
                    st.session_state.page = 'patient_dashboard'
                    st.rerun()
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        if st.button("Don't have an account? Sign Up", use_container_width=True):
            st.session_state.page = 'patient_signup'
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

def caregiver_login_page():
    """Caregiver login page"""
    if st.button("← Back"):
        st.session_state.page = 'account_type_selection'
        st.rerun()
    
    st.markdown("<h1 style='text-align: center; margin-top: 20px;'>🤝 Caregiver Login</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div class='auth-card' style='border: 3px solid #10b981;'>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔒 Password", "🔑 Patient Code"])
        
        with tab1:
            st.markdown("### Username & Password")
            username = st.text_input("Caregiver Username", key="caregiver_username")
            password = st.text_input("Password", type="password", key="caregiver_password")
            
            if st.button("🚀 Sign In", use_container_width=True):
                if username and password:
                    if load_user_data(username):
                        st.success(f"Welcome back, {st.session_state.user_profile['name']}!")
                        st.session_state.page = 'caregiver_dashboard'
                        st.rerun()
                    else:
                        st.error("Caregiver not found. Please sign up first!")
                else:
                    st.warning("Please enter username and password")
        
        with tab2:
            st.markdown("### Connect to Patient")
            caregiver_username = st.text_input("Your Username", key="connect_username")
            patient_code = st.text_input("Patient Access Code", max_chars=6, key="patient_code")
            
            if st.button("🔗 Connect", use_container_width=True):
                if caregiver_username and patient_code:
                    st.info(f"Demo: Connecting {caregiver_username} to patient with code {patient_code}")
                    if load_user_data(caregiver_username):
                        st.session_state.page = 'caregiver_dashboard'
                        st.rerun()
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        if st.button("Don't have an account? Sign Up", use_container_width=True):
            st.session_state.page = 'caregiver_signup'
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================
# SIGNUP PAGES
# ============================================

def patient_signup_page():
    """Multi-step patient signup page"""
    if st.button("← Back"):
        if st.session_state.signup_step > 1:
            st.session_state.signup_step -= 1
            st.rerun()
        else:
            st.session_state.page = 'patient_login'
            st.session_state.signup_step = 1
            st.session_state.signup_data = {}
            st.rerun()
    
    st.markdown("<h1 style='text-align: center;'>📝 Create Patient Account</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
        
        progress = st.session_state.signup_step / 5
        st.progress(progress)
        st.markdown(f"<p style='text-align: center;'>Step {st.session_state.signup_step} of 5</p>", unsafe_allow_html=True)
        
        if st.session_state.signup_step == 1:
            st.markdown("### 👤 Basic Information")
            name = st.text_input("Full Name", value=st.session_state.signup_data.get('name', ''))
            username = st.text_input("Username", value=st.session_state.signup_data.get('username', ''))
            age = st.number_input("Age", min_value=1, max_value=120, value=st.session_state.signup_data.get('age', 25))
            password = st.text_input("Password", type="password", value=st.session_state.signup_data.get('password', ''))
            
            if st.button("Continue →", use_container_width=True):
                if name and username and password:
                    if user_exists(username):
                        st.error("Username already exists! Please choose another.")
                    else:
                        st.session_state.signup_data['name'] = name
                        st.session_state.signup_data['username'] = username
                        st.session_state.signup_data['age'] = age
                        st.session_state.signup_data['password'] = password
                        st.session_state.signup_step = 2
                        st.rerun()
                else:
                    st.warning("Please fill all required fields")
        
        elif st.session_state.signup_step == 2:
            st.markdown("### 📧 Email Verification (Optional)")
            st.info("Get medication reminders via email. You can skip this step.")
            
            email = st.text_input("Email Address (optional)", value=st.session_state.signup_data.get('email', ''))
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Skip", use_container_width=True):
                    st.session_state.signup_data['email'] = ''
                    st.session_state.signup_step = 3
                    st.rerun()
            
            with col_b:
                if st.button("Continue →", use_container_width=True):
                    st.session_state.signup_data['email'] = email
                    st.session_state.signup_step = 3
                    st.rerun()
        
        elif st.session_state.signup_step == 3:
            st.markdown("### 🏥 Your Health Conditions")
            
            if 'diseases' not in st.session_state.signup_data:
                st.session_state.signup_data['diseases'] = []
            
            disease_name = st.text_input("Disease/Condition Name", key="disease_name_input")
            disease_type = st.selectbox("Type", ["Chronic", "Acute", "Preventive", "Other"], key="disease_type_select")
            disease_notes = st.text_area("Notes (optional)", key="disease_notes_input")
            
            if st.button("➕ Add Disease"):
                if disease_name:
                    st.session_state.signup_data['diseases'].append({
                        'id': str(len(st.session_state.signup_data['diseases']) + 1),
                        'name': disease_name,
                        'type': disease_type.lower(),
                        'notes': disease_notes
                    })
                    st.rerun()
            
            if st.session_state.signup_data['diseases']:
                st.markdown("**Added Conditions:**")
                for i, disease in enumerate(st.session_state.signup_data['diseases']):
                    col_a, col_b = st.columns([4, 1])
                    with col_a:
                        st.markdown(f"- {disease['name']} ({disease['type']})")
                    with col_b:
                        if st.button("🗑️", key=f"del_disease_{i}"):
                            st.session_state.signup_data['diseases'].pop(i)
                            st.rerun()
            
            if st.button("Continue →", use_container_width=True, key="continue_from_diseases"):
                st.session_state.signup_step = 4
                st.rerun()
        
        elif st.session_state.signup_step == 4:
            st.markdown("### 💊 Your Medications")
            
            if 'medications' not in st.session_state.signup_data:
                st.session_state.signup_data['medications'] = []
            
            med_name = st.text_input("Medication Name", key="med_name_input")
            col_a, col_b = st.columns(2)
            with col_a:
                dosage_type = st.selectbox("Type", ["Pill", "Liquid", "Injection", "Other"], key="dosage_type_select")
            with col_b:
                dosage_amount = st.text_input("Dosage", placeholder="e.g., 500mg", key="dosage_amount_input")
            
            frequency = st.selectbox("Frequency", [
                "Once daily", "Twice daily", "Three times daily", 
                "Every 4 hours", "Every 6 hours", "Every 8 hours",
                "Every 12 hours", "As needed", "Weekly", "Monthly"
            ], key="frequency_select")
            
            time = st.time_input("Time", value=datetime.strptime("09:00", "%H:%M").time(), key="time_input")
            color = st.selectbox("Color", ["Blue", "Green", "Purple", "Pink", "Orange", "Red", "Yellow", "Indigo"], key="color_select")
            
            if st.button("➕ Add Medication"):
                if med_name and dosage_amount:
                    st.session_state.signup_data['medications'].append({
                        'id': len(st.session_state.signup_data['medications']) + 1,
                        'name': med_name,
                        'dosageType': dosage_type.lower(),
                        'dosageAmount': dosage_amount,
                        'frequency': frequency.lower().replace(' ', '-'),
                        'time': time.strftime("%H:%M"),
                        'color': color.lower(),
                        'taken_today': False
                    })
                    st.rerun()
            
            if st.session_state.signup_data['medications']:
                st.markdown("**Added Medications:**")
                for i, med in enumerate(st.session_state.signup_data['medications']):
                    col_a, col_b = st.columns([4, 1])
                    with col_a:
                        st.markdown(f"- {med['name']} ({med['dosageAmount']}) at {med['time']}")
                    with col_b:
                        if st.button("🗑️", key=f"del_med_{i}"):
                            st.session_state.signup_data['medications'].pop(i)
                            st.rerun()
            
            col_skip, col_cont = st.columns(2)
            with col_skip:
                if st.button("Skip", use_container_width=True, key="skip_medications"):
                    st.session_state.signup_step = 5
                    st.rerun()
            with col_cont:
                if st.button("Continue →", use_container_width=True, key="continue_from_medications"):
                    st.session_state.signup_step = 5
                    st.rerun()
        
        elif st.session_state.signup_step == 5:
            st.markdown("### ✅ Review Your Information")
            
            st.markdown(f"**Name:** {st.session_state.signup_data.get('name')}")
            st.markdown(f"**Username:** {st.session_state.signup_data.get('username')}")
            st.markdown(f"**Age:** {st.session_state.signup_data.get('age')}")
            
            if st.session_state.signup_data.get('email'):
                st.markdown(f"**Email:** {st.session_state.signup_data.get('email')}")
            
            st.markdown(f"**Diseases:** {len(st.session_state.signup_data.get('diseases', []))}")
            st.markdown(f"**Medications:** {len(st.session_state.signup_data.get('medications', []))}")
            
            if st.button("🎉 Complete Registration", use_container_width=True):
                st.session_state.user_profile = {
                    'name': st.session_state.signup_data.get('name'),
                    'username': st.session_state.signup_data.get('username'),
                    'age': st.session_state.signup_data.get('age'),
                    'email': st.session_state.signup_data.get('email', ''),
                    'password': st.session_state.signup_data.get('password'),
                    'userType': 'patient',
                    'diseases': st.session_state.signup_data.get('diseases', []),
                }
                
                st.session_state.medications = st.session_state.signup_data.get('medications', [])
                save_user_data()
                
                st.session_state.signup_step = 1
                st.session_state.signup_data = {}
                
                st.success("Registration complete! Welcome to MedTimer!")
                st.session_state.page = 'patient_dashboard'
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

def caregiver_signup_page():
    """Caregiver signup page"""
    if st.button("← Back"):
        st.session_state.page = 'caregiver_login'
        st.rerun()
    
    st.markdown("<h1 style='text-align: center;'>🤝 Caregiver Registration</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div class='auth-card' style='border: 3px solid #10b981;'>", unsafe_allow_html=True)
        
        st.markdown("### Step 1: Basic Information")
        name = st.text_input("Full Name", key="cg_name")
        username = st.text_input("Username", key="cg_username")
        phone = st.text_input("Phone Number (optional)", key="cg_phone")
        password = st.text_input("Password", type="password", key="cg_password")
        
        st.markdown("### Step 2: Professional Details")
        relationship = st.selectbox("Your Role", [
            "Family Member", "Professional Caregiver", "Nurse",
            "Home Health Aide", "Friend", "Other"
        ], key="cg_relationship")
        
        experience = st.selectbox("Caregiving Experience", [
            "New to caregiving", "Less than 1 year", "1-3 years",
            "3-5 years", "5+ years"
        ], key="cg_experience")
        
        notes = st.text_area("Additional Notes (optional)", key="cg_notes")
        
        if st.button("✅ Complete Registration", use_container_width=True):
            if name and username and password and relationship and experience:
                if user_exists(username):
                    st.error("Username already exists! Please choose another.")
                else:
                    st.session_state.user_profile = {
                        'name': name,
                        'username': username,
                        'phone': phone,
                        'password': password,
                        'relationship': relationship,
                        'experience': experience,
                        'notes': notes,
                        'userType': 'caregiver',
                        'age': 30,
                        'diseases': [],
                    }
                    save_user_data()
                    st.success("Registration complete!")
                    st.session_state.page = 'caregiver_dashboard'
                    st.rerun()
            else:
                st.warning("Please fill all required fields")
        
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================
# PATIENT DASHBOARD
# ============================================

def patient_dashboard_page():
    """Main patient dashboard with tabs"""
    if not st.session_state.user_profile:
        st.session_state.page = 'patient_login'
        st.rerun()
        return
    
    age = st.session_state.user_profile.get('age', 25)
    age_category = get_age_category(age)
    greeting = get_time_of_day()
    
    col1, col2, col3 = st.columns([2, 4, 2])
    
    with col1:
        st.markdown(f"<h2>👋 {greeting}, {st.session_state.user_profile['name']}</h2>", unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"<div class='turtle-container'><p style='text-align: center; font-size: 48px;'>{get_turtle_emoji(st.session_state.turtle_mood)}</p></div>", unsafe_allow_html=True)
    
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            save_user_data()
            clear_session_data()
            st.session_state.page = 'account_type_selection'
            st.rerun()
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Dashboard", "💊 Medications", "👨‍⚕️ Appointments",
        "⚠️ Side Effects", "🏆 Achievements", "📥 Reports", "📈 Analytics"
    ])
    
    with tab1:
        dashboard_overview_tab(age_category)
    
    with tab2:
        medications_tab()
    
    with tab3:
        appointments_tab()
    
    with tab4:
        side_effects_tab()
    
    with tab5:
        achievements_tab()
    
    with tab6:
        reports_tab()
    
    with tab7:
        analytics_tab(age_category)

def dashboard_overview_tab(age_category):
    """Dashboard overview with stats and today's schedule"""
    st.markdown("### 📊 Your Health Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_meds = len(st.session_state.medications)
    taken_today = sum(1 for med in st.session_state.medications if med.get('taken_today', False))
    total_appointments = len(st.session_state.appointments)
    adherence = calculate_adherence(st.session_state.medications)
    
    with col1:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-number'>{total_meds}</div>
            <div class='stat-label'>Medications</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-number'>{taken_today}</div>
            <div class='stat-label'>Taken Today</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-number'>{total_appointments}</div>
            <div class='stat-label'>Appointments</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-number'>{adherence:.0f}%</div>
            <div class='stat-label'>Adherence</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_medication_status_donut(st.session_state.medications), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_medication_pie_chart(st.session_state.medications, age_category), use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📅 Today's Medication Schedule")
    
    if st.session_state.medications:
        sorted_meds = sorted(st.session_state.medications, key=lambda x: x.get('time', '00:00'))
        
        for med in sorted_meds:
            col_a, col_b, col_c, col_d, col_e = st.columns([3, 2, 2, 2, 1])
            
            with col_a:
                color_hex = get_medication_color_hex(med.get('color', 'blue'))
                st.markdown(
                    f"<div style='display: flex; align-items: center;'>"
                    f"<div class='color-dot' style='background-color: {color_hex};'></div>"
                    f"<strong>{med['name']}</strong> ({med['dosageAmount']})"
                    f"</div>",
                    unsafe_allow_html=True
                )
            
            with col_b:
                st.markdown(f"🕐 {format_time(med.get('time', 'N/A'))}")
            
            with col_c:
                st.markdown(f"📦 {med.get('dosageType', 'pill').capitalize()}")
            
            with col_d:
                if med.get('taken_today', False):
                    st.markdown('<span class="status-taken">✅ Taken</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="status-pending">⏰ Pending</span>', unsafe_allow_html=True)
            
            with col_e:
                if not med.get('taken_today', False):
                    if st.button("✓", key=f"take_{med['id']}"):
                        med['taken_today'] = True
                        st.session_state.turtle_mood = 'excited'
                        update_medication_history(med['id'], 'taken')
                        update_adherence_history()
                        save_user_data()
                        st.rerun()
            
            st.markdown("<hr style='margin: 8px 0; opacity: 0.2;'>", unsafe_allow_html=True)
    else:
        st.info("No medications scheduled. Add medications in the Medications tab.")

def analytics_tab(age_category):
    """Analytics tab with comprehensive graphs"""
    st.markdown("### 📈 Medication Analytics & Insights")
    
    st.markdown("#### Adherence Trend")
    st.plotly_chart(
        create_adherence_line_chart(st.session_state.get('adherence_history', []), age_category),
        use_container_width=True
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_daily_schedule_bar_chart(st.session_state.medications, age_category), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_side_effects_bar_chart(st.session_state.side_effects), use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("#### Weekly Medication Pattern")
    st.plotly_chart(create_weekly_heatmap(st.session_state.get('medication_history', [])), use_container_width=True)

# ============================================
# FEATURE TABS
# ============================================

def medications_tab():
    """Medications tab content"""
    st.markdown("### 💊 Your Medications")
    
    with st.expander("➕ Add New Medication", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            new_med_name = st.text_input("Medication Name", key="new_med_name")
            new_dosage_type = st.selectbox("Type", ["pill", "liquid", "injection", "other"], key="new_dosage_type")
            new_dosage_amount = st.text_input("Dosage Amount (e.g., 500mg)", key="new_dosage_amount")
            new_instructions = st.text_area("Instructions (optional)", key="new_instructions")
        
        with col2:
            new_frequency = st.selectbox("Frequency", [
                "once-daily", "twice-daily", "three-times-daily",
                "every-4-hours", "every-6-hours", "every-8-hours",
                "every-12-hours", "as-needed", "weekly", "monthly"
            ], key="new_frequency")
            new_time = st.time_input("Time", key="new_time")
            new_color = st.selectbox("Color Indicator", [
                "Blue", "Green", "Purple", "Pink", "Orange", "Red", "Yellow", "Indigo"
            ], key="new_color")
        
        if st.button("Add Medication", use_container_width=True, key="add_med_btn"):
            if new_med_name and new_dosage_amount:
                new_med = {
                    'id': len(st.session_state.medications) + 1,
                    'name': new_med_name,
                    'dosageType': new_dosage_type,
                    'dosageAmount': new_dosage_amount,
                    'frequency': new_frequency,
                    'time': new_time.strftime("%H:%M"),
                    'color': new_color.lower(),
                    'instructions': new_instructions,
                    'taken_today': False,
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                conflicts = check_medication_conflicts(st.session_state.medications, new_med)
                if conflicts:
                    st.warning(f"⚠️ Time conflict detected with: {', '.join(conflicts)}. Medications are scheduled close together.")
                
                st.session_state.medications.append(new_med)
                save_user_data()
                st.success(f"Added {new_med_name}!")
                st.rerun()
            else:
                st.warning("Please fill in medication name and dosage")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        sort_by = st.selectbox("Sort by", ["Time", "Name", "Type", "Status"], key="sort_meds")
    with col2:
        filter_by = st.selectbox("Filter by", ["All", "Taken", "Pending"], key="filter_meds")
    
    sorted_meds = st.session_state.medications.copy()
    
    if sort_by == "Time":
        sorted_meds.sort(key=lambda x: x.get('time', '00:00'))
    elif sort_by == "Name":
        sorted_meds.sort(key=lambda x: x.get('name', ''))
    elif sort_by == "Type":
        sorted_meds.sort(key=lambda x: x.get('dosageType', ''))
    elif sort_by == "Status":
        sorted_meds.sort(key=lambda x: x.get('taken_today', False), reverse=True)
    
    if filter_by == "Taken":
        sorted_meds = [m for m in sorted_meds if m.get('taken_today', False)]
    elif filter_by == "Pending":
        sorted_meds = [m for m in sorted_meds if not m.get('taken_today', False)]
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if sorted_meds:
        for med in sorted_meds:
            color_hex = get_medication_color_hex(med.get('color', 'blue'))
            
            st.markdown(f"<div class='medication-card' style='border-left-color: {color_hex};'>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([4, 2, 1])
            
            with col1:
                st.markdown(f"### {med['name']}")
                st.markdown(f"**Dosage:** {med['dosageAmount']} | **Type:** {med['dosageType'].capitalize()}")
                st.markdown(f"**Time:** {med['time']} | **Frequency:** {med['frequency'].replace('-', ' ').title()}")
                if med.get('instructions'):
                    st.markdown(f"**Instructions:** {med['instructions']}")
            
            with col2:
                status = "Taken ✅" if med.get('taken_today', False) else "Pending ⏰"
                st.markdown(f"**Status:** {status}")
                st.markdown(
                    f"<div style='width: 40px; height: 40px; background-color: {color_hex}; "
                    f"border-radius: 50%; margin-top: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);'></div>",
                    unsafe_allow_html=True
                )
            
            with col3:
                if st.button("🗑️", key=f"delete_{med['id']}", help="Delete"):
                    st.session_state.medications = [m for m in st.session_state.medications if m['id'] != med['id']]
                    save_user_data()
                    st.rerun()
                
                if not med.get('taken_today', False):
                    if st.button("✓ Take", key=f"take_med_{med['id']}", use_container_width=True):
                        med['taken_today'] = True
                        update_medication_history(med['id'], 'taken')
                        update_adherence_history()
                        save_user_data()
                        st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("No medications found. Add your first medication above!")

def appointments_tab():
    """Appointments tab content"""
    st.markdown("### 👨‍⚕️ Doctor Appointments")
    
    with st.expander("➕ Schedule New Appointment", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            appt_doctor = st.text_input("Doctor Name", key="appt_doctor")
            appt_specialty = st.text_input("Specialty", key="appt_specialty", placeholder="e.g., Cardiologist")
            appt_date = st.date_input("Date", key="appt_date", min_value=date.today())
        
        with col2:
            appt_time = st.time_input("Time", key="appt_time")
            appt_location = st.text_input("Location", key="appt_location", placeholder="Hospital/Clinic name")
            appt_phone = st.text_input("Contact Phone (optional)", key="appt_phone")
        
        appt_notes = st.text_area("Notes (optional)", key="appt_notes", placeholder="Reason for visit, things to discuss, etc.")
        
        if st.button("Schedule Appointment", use_container_width=True, key="add_appt_btn"):
            if appt_doctor and appt_date:
                new_appt = {
                    'id': len(st.session_state.appointments) + 1,
                    'doctor': appt_doctor,
                    'specialty': appt_specialty,
                    'date': appt_date.strftime("%Y-%m-%d"),
                    'time': appt_time.strftime("%H:%M"),
                    'location': appt_location,
                    'phone': appt_phone,
                    'notes': appt_notes,
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                st.session_state.appointments.append(new_appt)
                save_user_data()
                st.success(f"Appointment with Dr. {appt_doctor} scheduled!")
                st.rerun()
            else:
                st.warning("Please fill in doctor name and date")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    filter_option = st.selectbox("Filter", ["All Appointments", "Upcoming", "Past"], key="filter_appointments")
    
    today = date.today().strftime("%Y-%m-%d")
    filtered_appts = st.session_state.appointments.copy()
    
    if filter_option == "Upcoming":
        filtered_appts = [a for a in filtered_appts if a['date'] >= today]
    elif filter_option == "Past":
        filtered_appts = [a for a in filtered_appts if a['date'] < today]
    
    filtered_appts.sort(key=lambda x: x['date'])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if filtered_appts:
        for appt in filtered_appts:
            days = days_until(appt['date'])
            
            if days < 0:
                card_style = "border-left: 4px solid #6b7280;"
                status_badge = '<span class="status-missed">Past</span>'
            elif days == 0:
                card_style = "border-left: 4px solid #ef4444;"
                status_badge = '<span class="status-missed">Today!</span>'
            elif days <= 7:
                card_style = "border-left: 4px solid #f59e0b;"
                status_badge = '<span class="status-upcoming">Soon</span>'
            else:
                card_style = "border-left: 4px solid #10b981;"
                status_badge = '<span class="status-taken">Scheduled</span>'
            
            st.markdown(f"<div class='medication-card' style='{card_style}'>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([4, 2, 1])
            
            with col1:
                st.markdown(f"### 👨‍⚕️ Dr. {appt['doctor']}")
                if appt.get('specialty'):
                    st.markdown(f"**Specialty:** {appt['specialty']}")
                st.markdown(f"**Date:** {format_date(appt['date'])} ({days} days)" if days >= 0 else f"**Date:** {format_date(appt['date'])} (past)")
                st.markdown(f"**Time:** {appt['time']}")
                if appt.get('location'):
                    st.markdown(f"**Location:** {appt['location']}")
                if appt.get('phone'):
                    st.markdown(f"**Contact:** {appt['phone']}")
                if appt.get('notes'):
                    st.markdown(f"**Notes:** {appt['notes']}")
            
            with col2:
                st.markdown(f"**Status:** {status_badge}", unsafe_allow_html=True)
                if days >= 0:
                    if days == 0:
                        st.markdown("### 🔔")
                        st.markdown("**Appointment Today!**")
                    elif days == 1:
                        st.markdown("### ⏰")
                        st.markdown("**Tomorrow**")
                    else:
                        st.markdown(f"### 📅")
                        st.markdown(f"**In {days} days**")
            
            with col3:
                if st.button("🗑️", key=f"delete_appt_{appt['id']}", help="Cancel"):
                    st.session_state.appointments = [a for a in st.session_state.appointments if a['id'] != appt['id']]
                    save_user_data()
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("No appointments found.")

def side_effects_tab():
    """Side effects tab content"""
    st.markdown("### ⚠️ Report & Track Side Effects")
    
    with st.expander("➕ Report New Side Effect", expanded=False):
        if not st.session_state.medications:
            st.warning("Please add medications first before reporting side effects.")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                effect_med = st.selectbox("Medication", [m['name'] for m in st.session_state.medications], key="effect_med")
                effect_severity = st.select_slider("Severity Level", options=["Mild", "Moderate", "Severe"], key="effect_severity")
            
            with col2:
                effect_type = st.selectbox("Type of Side Effect",
                    ["Nausea", "Dizziness", "Headache", "Fatigue", "Rash", "Pain", "Other"],
                    key="effect_type")
                effect_date = st.date_input("Date Occurred", key="effect_date")
            
            effect_description = st.text_area("Description", key="effect_description",
                placeholder="Describe the side effect in detail...")
            
            if effect_severity == "Severe":
                st.error("⚠️ Severe side effects should be reported to your doctor immediately!")
            elif effect_severity == "Moderate":
                st.warning("⚠️ Consider consulting your doctor about this side effect.")
            
            if st.button("Report Side Effect", use_container_width=True, key="report_effect_btn"):
                if effect_description:
                    new_effect = {
                        'id': len(st.session_state.side_effects) + 1,
                        'medication': effect_med,
                        'severity': effect_severity,
                        'type': effect_type,
                        'description': effect_description,
                        'date': effect_date.strftime("%Y-%m-%d"),
                        'reported_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    st.session_state.side_effects.append(new_effect)
                    save_user_data()
                    st.success("Side effect reported successfully!")
                    
                    if effect_severity == "Severe":
                        st.error("🚨 Please contact your doctor as soon as possible!")
                    
                    st.rerun()
                else:
                    st.warning("Please provide a description of the side effect")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        severity_filter = st.selectbox("Filter by Severity", ["All", "Mild", "Moderate", "Severe"], key="severity_filter")
    with col2:
        sort_option = st.selectbox("Sort by", ["Most Recent", "Oldest First", "Severity"], key="sort_effects")
    
    filtered_effects = st.session_state.side_effects.copy()
    
    if severity_filter != "All":
        filtered_effects = [e for e in filtered_effects if e.get('severity') == severity_filter]
    
    if sort_option == "Most Recent":
        filtered_effects.sort(key=lambda x: x.get('date', ''), reverse=True)
    elif sort_option == "Oldest First":
        filtered_effects.sort(key=lambda x: x.get('date', ''))
    elif sort_option == "Severity":
        severity_order = {'Severe': 3, 'Moderate': 2, 'Mild': 1}
        filtered_effects.sort(key=lambda x: severity_order.get(x.get('severity', 'Mild'), 0), reverse=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.side_effects:
        col1, col2, col3, col4 = st.columns(4)
        total = len(st.session_state.side_effects)
        mild = sum(1 for e in st.session_state.side_effects if e.get('severity') == 'Mild')
        moderate = sum(1 for e in st.session_state.side_effects if e.get('severity') == 'Moderate')
        severe = sum(1 for e in st.session_state.side_effects if e.get('severity') == 'Severe')
        
        with col1:
            st.metric("Total Reports", total)
        with col2:
            st.metric("Mild", mild)
        with col3:
            st.metric("Moderate", moderate)
        with col4:
            st.metric("Severe", severe)
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    if filtered_effects:
        for effect in filtered_effects:
            severity = effect.get('severity', 'Mild')
            severity_color = get_severity_color(severity)
            severity_emoji = get_severity_emoji(severity)
            
            st.markdown(f"<div class='medication-card' style='border-left: 4px solid {severity_color};'>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([4, 2, 1])
            
            with col1:
                st.markdown(f"### {severity_emoji} {effect['medication']}")
                st.markdown(f"**Type:** {effect.get('type', 'Not specified')}")
                st.markdown(f"**Severity:** {severity}")
                st.markdown(f"**Date:** {effect['date']}")
                st.markdown(f"**Description:** {effect['description']}")
            
            with col2:
                st.markdown(f"""
                <div style='text-align: center; padding: 16px; background-color: {severity_color}20; 
                            border-radius: 12px; margin-top: 10px;'>
                    <div style='font-size: 48px;'>{severity_emoji}</div>
                    <div style='font-weight: 700; color: {severity_color};'>{severity}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                if st.button("🗑️", key=f"delete_effect_{effect['id']}", help="Remove"):
                    st.session_state.side_effects = [e for e in st.session_state.side_effects if e['id'] != effect['id']]
                    save_user_data()
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        if severity_filter != "All":
            st.info(f"No {severity_filter.lower()} side effects reported. That's good!")
        else:
            st.success("No side effects reported. Great job! 🎉")

def achievements_tab():
    """Achievements tab content"""
    st.markdown("### 🏆 Your Achievements & Badges")
    
    achievements_list = [
        {'id': 'first_step', 'name': 'First Step', 'description': 'Created your MedTimer account',
         'icon': '🎯', 'earned': True, 'category': 'Getting Started'},
        {'id': 'first_medication', 'name': 'Medicine Cabinet', 'description': 'Added your first medication',
         'icon': '💊', 'earned': len(st.session_state.medications) >= 1, 'category': 'Medications'},
        {'id': 'med_master', 'name': 'Med Master', 'description': 'Added 5 or more medications',
         'icon': '🎓', 'earned': len(st.session_state.medications) >= 5, 'category': 'Medications'},
        {'id': 'perfect_day', 'name': 'Perfect Day', 'description': 'Took all medications on time today',
         'icon': '⭐', 'earned': all(m.get('taken_today', False) for m in st.session_state.medications) if st.session_state.medications else False,
         'category': 'Adherence'},
        {'id': 'health_tracker', 'name': 'Health Tracker', 'description': 'Scheduled 3 doctor appointments',
         'icon': '📅', 'earned': len(st.session_state.appointments) >= 3, 'category': 'Appointments'},
        {'id': 'appointment_keeper', 'name': 'Appointment Keeper', 'description': 'Scheduled your first appointment',
         'icon': '👨‍⚕️', 'earned': len(st.session_state.appointments) >= 1, 'category': 'Appointments'},
        {'id': 'week_warrior', 'name': 'Week Warrior', 'description': 'Maintained 7 day adherence streak',
         'icon': '🔥', 'earned': False, 'category': 'Streaks'},
        {'id': 'side_effect_reporter', 'name': 'Health Advocate', 'description': 'Reported a side effect',
         'icon': '⚠️', 'earned': len(st.session_state.side_effects) >= 1, 'category': 'Health Monitoring'},
        {'id': 'turtle_friend', 'name': 'Turtle\'s Best Friend', 'description': 'Made your turtle companion happy',
         'icon': '🐢', 'earned': st.session_state.turtle_mood in ['happy', 'excited', 'celebrating'], 'category': 'Fun'},
        {'id': 'consistency_king', 'name': 'Consistency King/Queen', 'description': 'Achieve 100% adherence rate',
         'icon': '👑', 'earned': all(m.get('taken_today', False) for m in st.session_state.medications) and len(st.session_state.medications) > 0,
         'category': 'Adherence'}
    ]
    
    earned_count = sum(1 for a in achievements_list if a['earned'])
    total_count = len(achievements_list)
    progress_pct = (earned_count / total_count * 100) if total_count > 0 else 0
    
    st.markdown(f"""
    <div style='text-align: center; padding: 24px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 16px; color: white; margin-bottom: 24px;'>
        <h2 style='color: white; margin: 0;'>🎯 {earned_count} / {total_count} Achievements Unlocked</h2>
        <p style='font-size: 18px; margin-top: 8px;'>{progress_pct:.0f}% Complete</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.progress(progress_pct / 100)
    st.markdown("<br>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    
    for i, achievement in enumerate(achievements_list):
        col = cols[i % 3]
        
        with col:
            if achievement['earned']:
                opacity = "1.0"
                border_color = "#10b981"
                bg_gradient = "linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%)"
                status = '<span style="color: #10b981; font-weight: 700;">✅ Earned</span>'
            else:
                opacity = "0.6"
                border_color = "#e5e7eb"
                bg_gradient = "linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%)"
                status = '<span style="color: #6b7280; font-weight: 600;">🔒 Locked</span>'
            
            st.markdown(f"""
            <div style='text-align: center; padding: 20px; background: {bg_gradient}; 
                        border-radius: 16px; margin: 10px 0; opacity: {opacity}; 
                        border: 3px solid {border_color}; transition: all 0.3s ease;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.1);'>
                <div style='font-size: 56px; margin-bottom: 12px;'>{achievement['icon']}</div>
                <h3 style='margin: 8px 0; color: #1f2937;'>{achievement['name']}</h3>
                <p style='font-size: 14px; color: #6b7280; margin: 8px 0;'>{achievement['description']}</p>
                <div style='margin-top: 12px;'>{status}</div>
            </div>
            """, unsafe_allow_html=True)

def reports_tab():
    """Reports tab content"""
    st.markdown("### 📥 Generate & Download Health Reports")
    
    report_type = st.selectbox("Report Type", [
        "Complete Health Report",
        "Medication History",
        "Adherence Report",
        "Appointment Summary",
        "Side Effects Log",
        "Monthly Summary"
    ])
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=date.today() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", value=date.today())
    
    report_format = st.radio("Format", ["Text", "CSV", "Detailed"], horizontal=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("📄 Generate Report", use_container_width=True):
        profile = st.session_state.user_profile
        
        report = f"""
{'=' * 70}
MEDTIMER HEALTH REPORT
{'=' * 70}

Patient: {profile['name']}
Username: {profile['username']}
Age: {profile['age']}
Report Type: {report_type}
Date Range: {start_date} to {end_date}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'=' * 70}

MEDICATIONS ({len(st.session_state.medications)})
{'-' * 70}

"""
        
        if report_format == "CSV":
            report += "Name,Dosage,Type,Frequency,Time,Status\n"
            for med in st.session_state.medications:
                status = "Taken" if med.get('taken_today', False) else "Pending"
                report += f"{med['name']},{med['dosageAmount']},{med['dosageType']},{med['frequency']},{med['time']},{status}\n"
        else:
            for i, med in enumerate(st.session_state.medications, 1):
                status = "✅ Taken" if med.get('taken_today', False) else "⏰ Pending"
                report += f"""
{i}. {med['name']}
   - Dosage: {med['dosageAmount']}
   - Type: {med['dosageType'].capitalize()}
   - Frequency: {med['frequency'].replace('-', ' ').title()}
   - Time: {med['time']}
   - Status: {status}

"""
        
        report += f"""
APPOINTMENTS ({len(st.session_state.appointments)})
{'-' * 70}

"""
        
        for i, appt in enumerate(st.session_state.appointments, 1):
            report += f"""
{i}. Dr. {appt['doctor']}
   - Specialty: {appt.get('specialty', 'N/A')}
   - Date: {appt['date']}
   - Time: {appt['time']}
   - Location: {appt.get('location', 'N/A')}

"""
        
        report += f"""
SIDE EFFECTS LOG ({len(st.session_state.side_effects)})
{'-' * 70}

"""
        
        for i, effect in enumerate(st.session_state.side_effects, 1):
            report += f"""
{i}. {effect['medication']} - {effect['severity']}
   - Type: {effect.get('type', 'N/A')}
   - Date: {effect['date']}
   - Description: {effect['description']}

"""
        
        report += f"""
{'=' * 70}
End of Report
Generated by MedTimer - Your Medication Management Companion
{'=' * 70}
"""
        
        st.markdown("### 📄 Report Preview")
        st.text_area("Preview", report, height=300, key="report_preview")
        
        file_extension = "txt" if report_format != "CSV" else "csv"
        filename = f"medtimer_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_extension}"
        
        st.download_button(
            label="⬇️ Download Report",
            data=report,
            file_name=filename,
            mime="text/plain" if report_format != "CSV" else "text/csv",
            use_container_width=True
        )
        
        st.success("Report generated successfully!")

# ============================================
# CAREGIVER DASHBOARD
# ============================================

def caregiver_dashboard_page():
    """Main caregiver dashboard"""
    if not st.session_state.user_profile:
        st.session_state.page = 'caregiver_login'
        st.rerun()
        return
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown(f"<h1>🤝 Caregiver Dashboard - {st.session_state.user_profile['name']}</h1>", unsafe_allow_html=True)
    
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            save_user_data()
            clear_session_data()
            st.session_state.page = 'account_type_selection'
            st.rerun()
    
    tab1, tab2, tab3, tab4 = st.tabs(["👥 My Patients", "📊 Overview", "🔗 Connect", "⚙️ Settings"])
    
    with tab1:
        st.markdown("### 👥 Connected Patients")
        
        if 'connected_patients' not in st.session_state:
            st.session_state.connected_patients = []
        
        if st.session_state.connected_patients:
            for patient in st.session_state.connected_patients:
                st.markdown("<div class='medication-card' style='border-left: 4px solid #10b981;'>", unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"### 👤 {patient['name']}")
                    st.markdown(f"**Age:** {patient['age']}")
                    st.markdown(f"**Access Code:** {patient['access_code']}")
                    st.markdown(f"**Last Contact:** {patient.get('last_contact', 'N/A')}")
                
                with col2:
                    st.metric("Medications", patient.get('medications', 0))
                    st.metric("Adherence", f"{patient.get('adherence', 0)}%")
                
                with col3:
                    if st.button("🗑️ Disconnect", key=f"disconnect_patient_{patient['id']}", use_container_width=True):
                        st.session_state.connected_patients = [p for p in st.session_state.connected_patients if p['id'] != patient['id']]
                        save_user_data()
                        st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.info("You haven't connected to any patients yet. Use the Connect tab to link with a patient using their access code.")
            
            if st.button("➕ Add Demo Patient", use_container_width=True):
                demo_patient = {
                    'id': 1,
                    'name': 'Demo Patient',
                    'age': 65,
                    'access_code': '123456',
                    'medications': 5,
                    'adherence': 85,
                    'last_contact': 'Today'
                }
                st.session_state.connected_patients.append(demo_patient)
                save_user_data()
                st.rerun()
    
    with tab2:
        st.markdown("### 📊 Overall Statistics")
        
        total_patients = len(st.session_state.connected_patients)
        total_medications = sum(p.get('medications', 0) for p in st.session_state.connected_patients)
        avg_adherence = sum(p.get('adherence', 0) for p in st.session_state.connected_patients) / total_patients if total_patients > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-number'>{total_patients}</div>
                <div class='stat-label'>Patients</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-number'>{total_medications}</div>
                <div class='stat-label'>Total Medications</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-number'>{avg_adherence:.0f}%</div>
                <div class='stat-label'>Avg Adherence</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class='stat-card'>
                <div class='stat-number'>0</div>
                <div class='stat-label'>Alerts</div>
            </div>
            """, unsafe_allow_html=True)
        
        if total_patients > 0:
            st.markdown("<br>", unsafe_allow_html=True)
            st.info("Connect to patients to see detailed overview statistics.")
        else:
            st.info("Connect to patients to see overview statistics.")
    
    with tab3:
        st.markdown("### 🔗 Connect to Patient")
        
        st.info("Ask your patient for their 6-digit access code to connect and monitor their medication adherence.")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            patient_code = st.text_input("Patient Access Code", max_chars=6, key="patient_connect_code")
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔗 Connect", use_container_width=True):
                if patient_code and len(patient_code) == 6:
                    st.success(f"Successfully connected to patient with code: {patient_code}")
                    st.info("In a full implementation, this would fetch and link patient data.")
                else:
                    st.warning("Please enter a valid 6-digit code")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("### 🔑 Your Caregiver Access Code")
        
        if 'caregiver_code' not in st.session_state:
            st.session_state.caregiver_code = generate_patient_code()
        
        st.code(st.session_state.caregiver_code, language=None)
        st.caption("Share this code with patients who want to connect with you.")
    
    with tab4:
        st.markdown("### ⚙️ Profile Settings")
        
        profile = st.session_state.user_profile
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Name:** {profile['name']}")
            st.markdown(f"**Username:** {profile['username']}")
            st.markdown(f"**Role:** {profile.get('relationship', 'N/A')}")
        
        with col2:
            st.markdown(f"**Experience:** {profile.get('experience', 'N/A')}")
            st.markdown(f"**Phone:** {profile.get('phone', 'Not provided')}")
        
        if profile.get('notes'):
            st.markdown(f"**Notes:** {profile['notes']}")

# ============================================
# MAIN APPLICATION
# ============================================

def main():
    """Main application router"""
    
    # Initialize database
    init_database()
    
    # Initialize session state
    initialize_session_state()
    
    # Inject CSS
    st.markdown(inject_custom_css(), unsafe_allow_html=True)
    
    # Route to appropriate page
    page = st.session_state.page
    
    if page == 'account_type_selection':
        account_type_selection_page()
    elif page == 'patient_login':
        patient_login_page()
    elif page == 'patient_signup':
        patient_signup_page()
    elif page == 'patient_dashboard':
        patient_dashboard_page()
    elif page == 'caregiver_login':
        caregiver_login_page()
    elif page == 'caregiver_signup':
        caregiver_signup_page()
    elif page == 'caregiver_dashboard':
        caregiver_dashboard_page()
    else:
        account_type_selection_page()

if __name__ == "__main__":
    main()

