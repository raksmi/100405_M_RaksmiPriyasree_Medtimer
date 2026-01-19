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
    
    c.execute('''CREATE TABLE IF NOT EXISTS connected_patients
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  caregiver_username TEXT,
                  patient_username TEXT,
                  access_code TEXT,
                  connected_at TEXT,
                  FOREIGN KEY(caregiver_username) REFERENCES users(username))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS reminders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  medication_id INTEGER,
                  reminder_time TEXT,
                  acknowledged INTEGER DEFAULT 0,
                  created_at TEXT,
                  FOREIGN KEY(username) REFERENCES users(username))''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect('medtimer.db', check_same_thread=False)


def get_age_category(age):
    """Determine age category based on age"""
    if age < 18:
        return 'youth'
    elif age <= 40:
        return 'adult'
    else:
        return 'senior'

def get_gradient_style(age_category):
    """Get gradient background style based on age category"""
    if age_category == 'youth':
        return "background: linear-gradient(135deg, #9333ea 0%, #a855f7 50%, #c084fc 100%);"
    elif age_category == 'adult':
        return "background: linear-gradient(135deg, #22c55e 0%, #16a34a 50%, #15803d 100%);"
    else:
        return "background: linear-gradient(135deg, #eab308 0%, #ca8a04 50%, #a16207 100%);"

def get_font_size(age_category):
    """Get font size based on age category"""
    if age_category == 'youth':
        return "16px"
    elif age_category == 'adult':
        return "18px"
    else:
        return "22px"

def get_primary_color(age_category):
    """Get primary color based on age category"""
    if age_category == 'youth':
        return "#9333ea"
    elif age_category == 'adult':
        return "#22c55e"
    else:
        return "#eab308"

def get_secondary_color(age_category):
    """Get secondary color based on age category"""
    if age_category == 'youth':
        return "#a855f7"
    elif age_category == 'adult':
        return "#16a34a"
    else:
        return "#ca8a04"

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

def play_reminder_sound():
    """Play reminder sound using HTML audio with better sound quality"""
    audio_html = """
    <audio id="reminderSound" autoplay loop>
        <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
    </audio>
    <script>
        var audio = document.getElementById('reminderSound');
        audio.volume = 0.7;
        audio.play().catch(function(error) {
            console.log('Audio play failed:', error);
        });
        
        // Auto-stop after 10 seconds
        setTimeout(function() {
            audio.pause();
            audio.currentTime = 0;
        }, 10000);
    </script>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

def play_notification_sound():
    """Play notification sound for reminders"""
    audio_html = """
    <audio id="notificationSound" autoplay>
        <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
    </audio>
    <script>
        var audio = document.getElementById('notificationSound');
        audio.volume = 0.6;
        audio.play().catch(function(error) {
            console.log('Audio play failed:', error);
        });
    </script>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

def categorize_medications_by_status(medications):
    """Categorize medications into missed, upcoming, and taken"""
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    
    missed = []
    upcoming = []
    taken = []
    
    for med in medications:
        # Get all times for this medication (reminder_times or just time)
        med_times = med.get('reminder_times', [])
        if not med_times:
            med_times = [med.get('time', '00:00')]
        
        # Track if any dose is taken for this medication
        med_taken_times = med.get('taken_times', [])
        all_doses_taken = len(med_taken_times) == len(med_times) and len(med_times) > 0
        
        for time_slot in med_times:
            if time_slot in med_taken_times:
                # This specific dose was taken - add to taken list
                if not any(m['id'] == med['id'] and m['time'] == time_slot for m in taken):
                    taken.append({
                        'id': med['id'],
                        'name': med['name'],
                        'time': time_slot,
                        'dosageAmount': med['dosageAmount'],
                        'color': med.get('color', 'blue')
                    })
            elif time_slot < current_time:
                # Dose is past time and not taken - missed
                if not any(m['id'] == med['id'] and m['time'] == time_slot for m in missed):
                    missed.append({
                        'id': med['id'],
                        'name': med['name'],
                        'time': time_slot,
                        'dosageAmount': med['dosageAmount'],
                        'color': med.get('color', 'blue')
                    })
            else:
                # Dose is in the future - upcoming
                if not any(m['id'] == med['id'] and m['time'] == time_slot for m in upcoming):
                    upcoming.append({
                        'id': med['id'],
                        'name': med['name'],
                        'time': time_slot,
                        'dosageAmount': med['dosageAmount'],
                        'color': med.get('color', 'blue')
                    })
    
    # Sort by time
    missed.sort(key=lambda x: x['time'])
    upcoming.sort(key=lambda x: x['time'])
    taken.sort(key=lambda x: x['time'])
    
    return missed, upcoming, taken

def get_mascot_message(adherence, time_of_day):
    """Get mascot message based on adherence and time of day"""
    if adherence >= 90:
        messages = {
            'morning': [
                "🌟 You're a medication superstar! Keep shining!",
                "☀️ Amazing start to the day! 90%+ adherence!",
                "🏆 Perfect score so far! You're crushing it!"
            ],
            'afternoon': [
                "🌟 Still going strong! You're unstoppable!",
                "💪 Your dedication is inspiring!",
                "🏆 Champion status maintained all day!"
            ],
            'evening': [
                "🌟 What a perfect day! You're amazing!",
                "🎉 Congratulations on near-perfect adherence!",
                "⭐ You've mastered your medication routine!"
            ]
        }
    elif adherence >= 70:
        messages = {
            'morning': [
                "👍 Good start today! Let's keep it up!",
                "💪 You're doing great! Keep going!",
                "🌅 Nice start! Stay on track!"
            ],
            'afternoon': [
                "👍 Still doing well! Almost there!",
                "💪 Good progress! You can do it!",
                "🌤 Staying strong! Keep focused!"
            ],
            'evening': [
                "👍 Good effort today! Tomorrow will be even better!",
                "💪 Solid work! Rest well!",
                "🌙 Nice job! You're improving!"
            ]
        }
    elif adherence >= 50:
        messages = {
            'morning': [
                "🤔 Let's focus on today's medications!",
                "📝 Every pill counts! Let's try to take all!",
                "📋 Review your schedule and stay mindful!"
            ],
            'afternoon': [
                "🤔 Keep trying! You've got this!",
                "📝 Stay focused on your health goals!",
                "📋 Don't forget your afternoon doses!"
            ],
            'evening': [
                "🤔 Tomorrow is a new day! Let's plan better!",
                "📝 Reflect and prepare for a better day!",
                "📋 Let's organize your schedule for tomorrow!"
            ]
        }
    else:
        messages = {
            'morning': [
                "⚠️ Let's make today better than yesterday!",
                "💪 Start fresh! You can improve!",
                "🏆 Focus on one medication at a time!"
            ],
            'afternoon': [
                "⚠️ Don't give up! Every dose matters!",
                "💪 Small steps lead to big changes!",
                "🏆 Stay committed to your health!"
            ],
            'evening': [
                "⚠️ Tomorrow is a fresh start! Let's plan!",
                "💪 I believe in you! Try again tomorrow!",
                "🏆 Let's set a goal for tomorrow!"
            ]
        }
    
    import random
    return random.choice(messages.get(time_of_day, messages['morning']))

def update_mascot_mood(adherence):
    """Update mascot mood based on adherence"""
    if adherence >= 90:
        st.session_state.turtle_mood = 'excited'
    elif adherence >= 70:
        st.session_state.turtle_mood = 'happy'
    elif adherence >= 50:
        st.session_state.turtle_mood = 'neutral'
    else:
        st.session_state.turtle_mood = 'worried'

def check_upcoming_reminders(upcoming_meds):
    """Check for upcoming medications and show reminders"""
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    
    for med in upcoming_meds[:3]: 
        med_time = datetime.strptime(med['time'], "%H:%M")
        time_diff = (med_time - now).total_seconds() / 60 
        
        if 0 < time_diff <= 30:
            st.warning(f"⏰ **Upcoming Reminder:** {med['name']} ({med['dosageAmount']}) at {med['time']} - Take in {int(time_diff)} minutes!")
            return True
    return False

def check_due_medications(medications):
    """Check for medications that are due now and trigger reminders"""
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    
    due_medications = []
    for med in medications:
        # Get all times for this medication
        med_times = med.get('reminder_times', [])
        if not med_times:
            med_times = [med.get('time', '00:00')]
        
        for med_time in med_times:
            med_datetime = datetime.strptime(med_time, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day
            )
            time_diff = abs((now - med_datetime).total_seconds() / 60)
            
            # Check if time is within 5 minutes of now and not already taken
            if time_diff <= 5 and med_time not in med.get('taken_times', []):
                if med not in due_medications:
                    due_medications.append(med)
        
    return due_medications

def calculate_adherence(medications):
    """Calculate medication adherence percentage (dose-based)"""
    if not medications:
        return 0

    total_doses = 0
    taken_doses = 0

    for med in medications:
        # Get all times for this medication
        times = med.get('reminder_times', [])
        if not times:
            times = [med.get('time', '00:00')]
        
        total_doses += len(times)
        taken_doses += len(med.get('taken_times', []))

    return (taken_doses / total_doses * 100) if total_doses > 0 else 0


def get_mascot_image(mood):
    mascot_images = {
        'happy': r"C:\Users\tnvxx\OneDrive\Desktop\sucess.png",
        'excited': r"C:\Users\tnvxx\OneDrive\Desktop\sucess.png",
        'neutral': '🐢',
        'worried': '🐢'
    }
    return mascot_images.get(mood, '🐢')

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
    if 'editing_medication' not in st.session_state:
        st.session_state.editing_medication = None
    if 'sound_enabled' not in st.session_state:
        st.session_state.sound_enabled = True
    if 'last_reminder_check' not in st.session_state:
        st.session_state.last_reminder_check = datetime.now()

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
        
        c.execute('DELETE FROM diseases WHERE username = ?', (username,))
        for disease in st.session_state.user_profile.get('diseases', []):
            c.execute('INSERT INTO diseases (username, name, type, notes) VALUES (?, ?, ?, ?)',
                     (username, disease.get('name'), disease.get('type'), disease.get('notes', '')))
        
        c.execute('DELETE FROM medications WHERE username = ?', (username,))
        for med in st.session_state.medications:
            # Serialize taken_times list to JSON string
            taken_times_json = json.dumps(med.get('taken_times', []))
            c.execute('''INSERT INTO medications 
                         (username, name, dosage_type, dosage_amount, frequency, time, color, instructions, taken_today, taken_times, created_at)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (username, med.get('name'), med.get('dosageType'), med.get('dosageAmount'),
                      med.get('frequency'), med.get('time'), med.get('color'),
                      med.get('instructions', ''), int(med.get('taken_today', False)),
                      taken_times_json,
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
        
        c.execute('SELECT * FROM diseases WHERE username = ?', (username,))
        diseases = c.fetchall()
        for disease in diseases:
            st.session_state.user_profile['diseases'].append({
                'id': str(disease[0]),
                'name': disease[2],
                'type': disease[3],
                'notes': disease[4]
            })
        
        c.execute('SELECT * FROM medications WHERE username = ?', (username,))
        meds = c.fetchall()
        st.session_state.medications = []
        for med in meds:
            # Deserialize taken_times from JSON string
            taken_times = []
            if med[11]:  # If taken_times column exists and has data
                try:
                    taken_times = json.loads(med[11])
                except:
                    taken_times = []
            
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
                'created_at': med[10]
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
    
    # Calculate adherence based on doses taken
    adherence = calculate_adherence(st.session_state.medications)
    
    conn = get_db_connection()
    c = conn.cursor()
    
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
    st.session_state.editing_medication = None

def inject_custom_css(age_category='adult'):
    """Inject custom CSS into Streamlit app with age-based styling"""
    primary_color = get_primary_color(age_category)
    secondary_color = get_secondary_color(age_category)
    font_size = get_font_size(age_category)
    background_style = get_gradient_style(age_category)
    
    css = f"""
    <style>
    .stApp {{
        {background_style}
    }}
    
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    h1, h2, h3, h4, h5, h6 {{
        font-weight: 800 !important;
        color: #ffffff !important;
    }}
    
    p, div, span, label {{
        font-size: {font_size} !important;
        color: #ffffff !important;
    }}
    
    h1 {{ font-size: calc({font_size} * 2.5) !important; }}
    h2 {{ font-size: calc({font_size} * 2) !important; }}
    h3 {{ font-size: calc({font_size} * 1.5) !important; }}
    
    .medication-card {{
        background: white;
        border-radius: 16px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border-left: 4px solid {primary_color};
    }}
    
    .medication-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
    }}
    
    .medication-card p, .medication-card div, .medication-card span {{
        color: #1f2937 !important;
    }}
    
    .stat-card {{
        background: white;
        border-radius: 20px;
        padding: 30px 24px;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border-top: 4px solid {primary_color};
    }}
    
    .stat-card:hover {{
        transform: translateY(-8px);
        box-shadow: 0 16px 32px rgba(0,0,0,0.15);
    }}
    
    .stat-card p, .stat-card div, .stat-card span {{
        color: #1f2937 !important;
    }}
    
    .mascot-message-text {{
        color: #000000 !important;
    }}
    
    .stat-number {{
        font-size: 56px;
        font-weight: 900;
        color: #ffffff !important;
        line-height: 1.2;
        margin-bottom: 8px;
    }}
    
    .stat-label {{
        font-size: {font_size};
        color: #edf0f2 !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .auth-card {{
        background: black;
        border-radius: 24px;
        padding: 40px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        max-width: 500px;
        margin: 0 auto;
        border: 1px solid rgba(255,255,255,0.2);
    }}
    
    .auth-card p, .auth-card div, .auth-card span, .auth-card label {{
        color: #ffffff !important;
    }}
    
    .stButton > button {{
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        border: none !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        font-size: {font_size} !important;
        color: #ffffff !important;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2) !important;
    }}
    
    .status-taken {{
        background: linear-gradient(135deg, #10b981, #059669);
        color: white !important;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: {font_size};
        font-weight: 700;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
    }}
    
    .status-missed {{
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white !important;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: {font_size};
        font-weight: 700;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);
    }}
    
    .status-upcoming {{
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white !important;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: {font_size};
        font-weight: 700;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(245, 158, 11, 0.3);
    }}
    
    .status-pending {{
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white !important;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: {font_size};
        font-weight: 700;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
    }}
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input {{
        color: #f2f4f7 !important;
    }}
    
    @keyframes float {{
        0%, 100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-20px); }}
    }}
    
    .turtle-container {{
        animation: float 3s ease-in-out infinite;
    }}
    
    .stProgress > div > div > div {{
        background: linear-gradient(90deg, {primary_color} 0%, {secondary_color} 100%) !important;
        border-radius: 10px !important;
    }}
    
    .color-dot {{
        width: 16px;
        height: 16px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }}
    
    /* Fix for white text in cards */
    .stMarkdown {{
        color: #ffffff !important;
    }}
    
    .stMarkdown strong {{
        color: #1f2937 !important;
    }}
    
    /* Reminder section styling */
    .reminder-section {{
        background: linear-gradient(135deg, #fff7ed, #ffedd5);
        border: 2px solid #f59e0b;
        border-radius: 16px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
    }}
    
    .reminder-item {{
        background: white;
        border-radius: 12px;
        padding: 16px;
        margin: 10px 0;
        border-left: 4px solid #f59e0b;
    }}
    
    /* Date Time Display */
    .datetime-display {{
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }}
    
    .datetime-time {{
        font-size: 48px;
        font-weight: 900;
        color: #ffffff;
        margin: 0;
    }}
    
    .datetime-date {{
        font-size: 20px;
        color: rgba(255, 255, 255, 0.9);
        margin-top: 8px;
    }}
    </style>
    """
    return css

def create_adherence_line_chart(adherence_history, age_category='adult'):
    """Create line chart showing adherence over time"""
    if not adherence_history:
        fig = go.Figure()
        fig.add_annotation(
            text="No adherence data available yet.<br>Start tracking your medications!",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="#1f2937")
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

def dashboard_overview_tab(age_category):
    """Dashboard overview with stats and today's schedule"""
    # Add date and time display at the top
    now = datetime.now()
    time_str = now.strftime("%I:%M:%S %p")
    date_str = now.strftime("%A, %B %d, %Y")
    
    st.markdown(f"""
    <div class='datetime-display'>
        <div class='datetime-time'>{time_str}</div>
        <div class='datetime-date'>{date_str}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Greeting
    greeting = get_time_of_day()
    user_name = st.session_state.user_profile.get('name', 'Friend')
    st.markdown(f"<h2 style='color: #ffffff;'>{greeting}, {user_name}! 👋</h2>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Categorize medications
    missed, upcoming, taken = categorize_medications_by_status(st.session_state.medications)
    due_meds = check_due_medications(st.session_state.medications)
    
    # Calculate stats
    total_meds = len(st.session_state.medications)
    taken_today_count = len(taken)
    total_appointments = len(st.session_state.appointments)
    adherence = calculate_adherence(st.session_state.medications)
    
    # Update mascot mood
    update_mascot_mood(adherence)
    
    # Stats cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-number'>{total_meds}</div>
            <div class='stat-label'>Total Meds</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-number'>{taken_today_count}</div>
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
        adherence_color = "#10b981" if adherence >= 70 else "#f59e0b" if adherence >= 50 else "#ef4444"
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-number' style='background: linear-gradient(135deg, {adherence_color}, {adherence_color}88);'>{adherence:.0f}%</div>
            <div class='stat-label'>Adherence</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Mascot message
    time_of_day = get_time_of_day().lower().replace('👋 ', '')
    mascot_message = get_mascot_message(adherence, time_of_day)
    mascot_color = get_mascot_text_color(st.session_state.turtle_mood)
    mascot_img = get_mascot_image(st.session_state.turtle_mood)
    st.markdown(
    f"""
    <div style="
        background: #f0f0f0;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.12);
        text-align: center;
    ">
        <img src="{mascot_img}" width="90" style="margin-bottom:10px;">
        <p style="font-size:18px; color:#000000 !important;">
            {mascot_message}
        </p>
    </div>
    """,
    unsafe_allow_html=True
    )
    
    # Sound toggle
    col_sound_left, col_sound_right = st.columns([4, 1])
    with col_sound_right:
        if st.button("🔊" if st.session_state.sound_enabled else "🔇", use_container_width=True):
            st.session_state.sound_enabled = not st.session_state.sound_enabled
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Due medications section
    st.markdown("<h3 style='color: #ffffff;'>⏰ Due Now</h3>", unsafe_allow_html=True)
    
    due_meds = check_due_medications(st.session_state.medications)
    if due_meds:
        if st.session_state.sound_enabled:
            play_reminder_sound()
        
        for med in due_meds:
            st.markdown(
                f"""
                <div class='reminder-item'>
                    <strong>🔔 REMINDER NOW:</strong>
                    {med['name']} ({med['dosageAmount']}) at {format_time(med['time'])}
                </div>
                """,
                unsafe_allow_html=True
            )
            
            if st.button(
                "✓ Take Now",
                key=f"take_due_{med['id']}_{med['time']}",
                use_container_width=True):
                dose_time = med['time']
                for m in st.session_state.medications:
                    if m['id'] == med['id']:
                        if dose_time not in m.get('taken_times', []):
                            m['taken_times'].append(dose_time)
                        
                        # Mark medicine fully taken only if all doses done
                        all_times = m.get('reminder_times', [m.get('time')])
                        if set(m['taken_times']) == set(all_times):
                            m['taken_today'] = True
                        
                        update_medication_history(med['id'], 'taken')
                        update_adherence_history()
                        save_user_data()
                        st.rerun()
    else:
        st.success("🎉 No medications due right now!")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Missed medications section
    if missed:
        st.markdown("<h3 style='color: #ffffff;'>❌ Missed Medications</h3>", unsafe_allow_html=True)
        for med in missed[:5]:
            st.markdown(
                f"""
                <div class='reminder-item' style='border-left-color: #ef4444;'>
                    <strong>⚠️ Missed:</strong> {med['name']} ({med['dosageAmount']}) at {format_time(med['time'])}
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button(
                "✓ Take Now",
                key=f"take_missed_{med['id']}_{med['time']}",
                use_container_width=True):
                for m in st.session_state.medications:
                    if m['id'] == med['id']:
                        if med['time'] not in m.get('taken_times', []):
                            m['taken_times'].append(med['time'])
                        
                        all_times = m.get('reminder_times', [m.get('time')])
                        if set(m['taken_times']) == set(all_times):
                            m['taken_today'] = True
                        
                        update_medication_history(med['id'], 'taken')
                        update_adherence_history()
                        save_user_data()
                        st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Upcoming medications section
    st.markdown("<h3 style='color: #ffffff;'>📅 Upcoming Medications</h3>", unsafe_allow_html=True)
    
    if upcoming:
        upcoming_count = 0
        for med in upcoming[:5]: 
            med_time = datetime.strptime(med['time'], "%H:%M")
            now = datetime.now()
            time_diff = (med_time - now).total_seconds() / 60
            
            if time_diff > 0:
                st.markdown(f"""
                <div class='reminder-item' style='border-left-color: #3b82f6;'>
                    <strong>🕐 In {int(time_diff)} minutes:</strong> {med['name']} ({med['dosageAmount']}) at {format_time(med['time'])}
                </div>
                """,
                unsafe_allow_html=True
                )
                upcoming_count += 1
    else:
        st.info("No upcoming medications scheduled.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Taken medications section
    if taken:
        st.markdown("<h3 style='color: #ffffff;'>✅ Taken Today</h3>", unsafe_allow_html=True)
        for med in taken[:10]:
            st.markdown(
                f"""
                <div class='reminder-item' style='border-left-color: #10b981;'>
                    <strong>✓ Taken:</strong> {med['name']} ({med['dosageAmount']}) at {format_time(med['time'])}
                </div>
                """,
                unsafe_allow_html=True
            )

# Main app logic
def main():
    # Initialize database and session state
    init_database()
    initialize_session_state()
    
    # Get age category for styling
    if st.session_state.user_profile:
        age = st.session_state.user_profile.get('age', 25)
        age_category = get_age_category(age)
    else:
        age_category = 'adult'
    
    # Inject custom CSS
    st.markdown(inject_custom_css(age_category), unsafe_allow_html=True)
    
    # Page routing
    if st.session_state.page == 'patient_dashboard':
        dashboard_overview_tab(age_category)
    else:
        st.markdown("<h1 style='color: white; text-align: center;'>Welcome to MedTimer!</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: white; text-align: center;'>Please log in to access your dashboard.</p>", unsafe_allow_html=True)

if __name__ == '__main__':
    main()
