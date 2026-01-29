# 💊 MedTimer - Advanced Medication Management System

**Your Comprehensive Medication Management Companion**


## 📋 Table of Contents

-   [🎯 Overview](#-overview)
-   [✨ Features](#-features)
-   [📖 Usage](#-usage)
-   [👥 User Types](#-user-types)
-   [🎨 Customization](#-customization)
-   [📊 Analytics](#-analytics)
-   [🔒 Credits](#-credits)


* * *

## 🎯 Overview

**MedTimer** is a sophisticated, feature-rich medication management application designed to help patients and caregivers track medications, appointments, side effects, and health metrics. Built with Streamlit and SQLite, it provides a beautiful, intuitive interface with real-time notifications, comprehensive analytics, and gamification elements to encourage adherence.


Live demo link: https://100405mraksmipriyasreemedtimer-wwrplznergmeukuahbjhpx.streamlit.app/


### Key Highlights:

-   🎨 **Age-Adaptive Interface**: Custom themes based on user age (Youth, Adult, Senior)
-   📱 **Font size** : Font size changes based on your age
-   ⏰ **Real-Time Reminders**: Automated medication reminders with sound notifications
-   📊 **Advanced Analytics**: Visual charts and trends for medication adherence
-   🤝 **Dual User Support**: Both patients and caregivers can manage medications.. (coming up)
-   📱 **Responsive Design**: Beautiful, mobile-friendly interface
-   🔄 **Undo Functionality**: Easily undo medication actions
-   🎉 **Celebration Effects**: Special animations for perfect adherence

Photos and Flow link: https://drive.google.com/drive/folders/1w-nhn8XTzIXfWgVUTafC9dqBy2XRgb6U?usp=sharing
* * *

## ✨ Features

### 📊 Dashboard Features

#### 🕐 **Real-Time Date & Time Display**

-   Always-visible current date, time, and day of week
-   Beautiful frosted glass effect with modern styling
-   Auto-updates every time you interact with the app

#### 📈 **Medication Status Tracking**

-   **Missed Medications**: Red indicators for doses you've missed
-   **Upcoming Medications**: Yellow indicators for doses coming up
-   **Taken Medications**: Green indicators for completed doses
-   Real-time categorization with automatic status updates

#### 🎯 **Adherence Tracking**

-   **Percentage Calculation**: Real-time adherence percentage
-   **Dose-Based Tracking**: Accurate tracking of each individual dose
-   **Automatic Updates**: Adherence updates immediately when you take/undo medications
-   **100% Celebration**: Special gold shimmer effect when you achieve perfect adherence
-   **Visual Progress Bar**: Color-coded progress indicator

#### 🐢 **Intelligent Mascot**

-   **Mood Changes**: Mascot expression changes based on adherence
    -    Excited (90%+ adherence)
    -   😊 Happy (70-89% adherence)
    -   😐 Neutral (50-69% adherence)
    -   😟 Worried (below 50% adherence)
-   **Motivational Messages**: Context-aware messages based on time of day and adherence
-   **Visual Feedback**: Animated mascot with floating effects

#### 📊 **Statistics Cards**

-   **Total Doses**: Number of scheduled medication doses for today
-   **Doses Taken**: Number of doses you've completed
-   **Appointments**: Count of scheduled doctor appointments
-   **Adherence Rate**: Your current adherence percentage

### 💊 Medication Management

#### ➕ **Add Medications**

-   **Comprehensive Details**: Name, dosage amount, dosage type
-   **Flexible Scheduling**:
    -   Once daily, Twice daily, Three times daily
    -   Every 4, 6, 8, 12 hours
    -   As needed, Weekly, Monthly
-   **Multiple Doses**: Support for medications taken multiple times per day
-   **Custom Times**: Set specific times for each dose
-   **Color Coding**: Assign colors to medications for visual identification
-   **Instructions**: Add special instructions or notes
-   **Conflict Detection**: Warns if medications are scheduled too close together

#### ✏️ **Edit Medications**

-   Modify all medication details
-   Update dosage, frequency, and times
-   Change color indicators
-   Edit or add instructions

#### 🗑️ **Delete Medications**

-   Remove medications from your list
-   Preserves history

#### ✓ **Take Medication**

-   One-click dose marking
-   Sound notification confirmation
-   Automatic adherence update
-   Timestamped tracking

#### ↩️ **Undo Dose**

-   Undo mistaken dose markings
-   Reverts adherence calculation
-   Preserves action history
-   Quick and easy reversal

#### ✕ **Skip Dose**

-   Mark doses as intentionally skipped
-   Logged in medication history
-   Doesn't affect adherence negatively

### 📅 Appointment Management

#### ➕ **Schedule Appointments**

-   Doctor name and specialty
-   Date and time selection
-   Location and contact information
-   Notes for the visit

#### 📋 **Appointment List**

-   **Upcoming**: Future appointments with countdown
-   **Past**: Historical appointment records
-   **Today**: Special highlighting for today's appointments
-   Color-coded status indicators

#### 🗑️ **Cancel Appointments**

-   Easy removal of scheduled appointments
-   Maintains history

### ⚠️ Side Effects Tracking

#### 📝 **Report Side Effects**

-   Select which medication caused the effect
-   Severity level (Mild, Moderate, Severe)
-   Type of side effect (Nausea, Dizziness, Headache, etc.)
-   Date occurred
-   Detailed description

#### 📊 **Side Effects Dashboard**

-   **Severity Statistics**: Counts by severity level
-   **Medication Breakdown**: See which medications cause issues
-   **Timeline**: View side effects over time
-   **Filtering**: Filter by severity level
-   **Sorting**: Sort by date, severity, or recency

### 🏆 Achievement System

#### 🎯 **Gamification Badges**

-   **First Step**: Created your MedTimer account
-   **Medicine Cabinet**: Added your first medication
-   **Med Master**: Added 5 or more medications
-   **Perfect Day**: Took all medications on time
-   **Health Tracker**: Scheduled 3 doctor appointments
-   **Appointment Keeper**: Scheduled your first appointment
-   **Week Warrior**: Maintained 7-day adherence streak
-   **Health Advocate**: Reported a side effect
-   **Turtle's Best Friend**: Made your turtle companion happy
-   **Consistency King/Queen**: Achieved 100% adherence rate

#### 📊 **Progress Tracking**

-   Visual progress bar
-   Percentage completion
-   Achievement count
-   Locked/earned status indicators

### 📤 Reports & Exports

#### 📄 **Generate Reports**

-   **Complete Health Report**: Comprehensive overview of everything
-   **Medication History**: Detailed medication tracking
-   **Adherence Report**: Adherence trends and statistics
-   **Appointment Summary**: All your appointments
-   **Side Effects Log**: Complete side effects record
-   **Monthly Summary**: Monthly health overview

#### 📊 **Export Formats**

-   **PDF**: Professional reports with formatting and tables
-   **Text**: Simple text reports
-   **CSV**: Spreadsheet-compatible format for analysis
-   **Detailed**: Comprehensive reports with all information

#### 📅 **Date Range Selection**

-   Custom date ranges for reports
-   Default 30-day range
-   Flexible reporting periods

### 📈 Analytics & Insights

#### 📊 **Visual Charts**

-   **Adherence Trend Line**: Track adherence over time
-   **Medication Type Pie Chart**: Distribution by medication type
-   **Daily Schedule Bar Chart**: Visualize medication times throughout the day
-   **Side Effects Bar Chart**: Breakdown by severity
-   **Weekly Heatmap**: Medication patterns by day and time

#### 📉 **Data Insights**

-   Identify patterns in medication adherence
-   Spot problematic time slots
-   Track side effect trends
-   Monitor appointment compliance

### 🎨 Interface Features

#### 🌈 **Age-Adaptive Themes**

-   **Youth (<18)**: Purple gradient theme, 16px font
-   **Adult (18-40)**: Green gradient theme, 18px font
-   **Senior (40+)**: Yellow/Gold gradient theme, 22px font

#### ✨ **Visual Effects**

-   **Frosted Glass**: Modern glass-morphism effects
-   **Gradient Backgrounds**: Beautiful color transitions
-   **Card Hover Effects**: Interactive feedback
-   **Smooth Transitions**: Animated state changes
-   **100% Adherence Celebration**: Gold shimmer and pulsing effects
-   **Floating Mascot**: Animated turtle companion

#### 📱 **Responsive Design**

-   Mobile-friendly interface
-   Adaptive layouts
-   Touch-optimized buttons
-   Readable fonts and colors

### 🎵 **Sound Notifications**

#### 🔔 **Reminder Sounds**

-   **Due Now**: Immediate alert for medications due
-   **Upcoming**: 30-minute advance warning
-   **Confirmation**: Sound when taking medication
-   **Toggle On/Off**: Control sound preferences

### 🤝 Caregiver Features (coming up)

#### 👥 **Patient Management**

-   Connect to multiple patients
-   View patient medications and adherence
-   Monitor appointment schedules
-   Track side effects

#### 🔗 **Connection System**

-   6-digit access codes
-   Secure patient linking
-   Easy connection process
-   Manage connected patients

#### 📊 **Caregiver Dashboard**

-   Overview of all patients
-   Average adherence tracking
-   Total medications count
-   Alert system

### 🔐 Security & Privacy

#### 💾 **Data Storage**

-   **Local SQLite Database**: All data stored locally
-   **Secure Session Management**: Safe user sessions
-   **Privacy First**: No data sent to external servers

#### 🔒 **Authentication**

-   Username/password login
-   Optional email verification
-   Secure password handling
-   Session management

### 📚 Health Conditions

#### 🏥 **Disease Tracking**

-   Add health conditions/diseases
-   Categorize by type (Chronic, Acute, Preventive)
-   Add notes and details
-   Track multiple conditions


### First-Time Setup

1.  **Select Account Type**: Choose between "Patient" or "Caregiver"
2.  **Sign Up**: Create your account with:
    -   Username
    -   Full Name
    -   Age
    -   Password
    -   Optional: Email address
3.  **Add Health Conditions**: (Optional) Add any health conditions you have
4.  **Add Medications**: (Optional) Add your medications with scheduling details
5.  **Start Tracking**: Your dashboard is ready!

### Daily Workflow

1.  **Check Dashboard**: See today's date, time, and medication status
2.  **Take Medications**: Click "✓ Take" when you take your medication
3.  **View Reminders**: Receive alerts for upcoming and due medications
4.  **Track Adherence**: Watch your adherence percentage update in real-time
5.  **Undo if Needed**: Use "↩️ Undo" if you make a mistake
6.  **Review Analytics**: Check the Analytics tab for trends and insights
7.  **Generate Reports**: Export reports when needed

### Managing Medications

#### Adding a New Medication

1.  Go to the "💊 Medications" tab
2.  Click "➕ Add New Medication"
3.  Fill in:
    -   Medication Name
    -   Dosage Type (Pill, Liquid, Injection, Other)
    -   Dosage Amount (e.g., 500mg)
    -   Frequency (e.g., Twice daily)
    -   Set specific times for each dose
    -   Choose a color indicator
    -   Add instructions (optional)
4.  Click "Add Medication"

#### Taking a Medication

1.  Go to the Dashboard
2.  Find the medication you want to take
3.  Click "✓ Take" button
4.  Listen for confirmation sound
5.  Watch adherence update automatically

#### Undoing a Dose

1.  Go to the Dashboard
2.  Find the medication you want to undo
3.  Click "↩️ Undo" button
4.  The dose will be removed from taken history
5.  Adherence will recalculate

### Scheduling Appointments

1.  Go to the "👨‍⚕️ Appointments" tab
2.  Click "➕ Schedule New Appointment"
3.  Fill in:
    -   Doctor's name
    -   Specialty (optional)
    -   Date and time
    -   Location (optional)
    -   Contact phone (optional)
    -   Notes (optional)
4.  Click "Schedule Appointment"

### Reporting Side Effects

1.  Go to the "⚠️ Side Effects" tab
2.  Click "➕ Report New Side Effect"
3.  Fill in:
    -   Which medication caused it
    -   Severity level (Mild, Moderate, Severe)
    -   Type of side effect
    -   Date it occurred
    -   Detailed description
4.  Click "Report Side Effect"
5.  For severe effects, you'll be prompted to contact your doctor

### Generating Reports

1.  Go to the "📥 Reports" tab
2.  Select the type of report you want
3.  Choose the date range
4.  Select the format (PDF, Text, CSV, Detailed)
5.  Click "📄 Generate Report"
6.  Download the generated report

### Viewing Analytics

1.  Go to the "📈 Analytics" tab
2.  Explore the various charts:
    -   Adherence Trend over time
    -   Medications by type
    -   Daily schedule visualization
    -   Side effects breakdown
    -   Weekly patterns

### Caregiver Usage

#### Connecting to a Patient

1.  Log in as Caregiver
2.  Go to the "🔗 Connect" tab
3.  Enter the patient's 6-digit access code
4.  Click "🔗 Connect"

#### Monitoring Patients (coming up)

1.  Go to the "👥 My Patients" tab
2.  View all connected patients
3.  Check their medication adherence
4.  Review their appointments
5.  Track their side effects

* * *

## 👥 User Types

### 👤 Patient Dashboard

**Features Available:**

-   ✅ All medication management features
-   ✅ Appointment scheduling
-   ✅ Side effects reporting
-   ✅ Achievement tracking
-   ✅ Personal analytics
-   ✅ Report generation
-   ✅ Real-time reminders
-   ✅ Adherence tracking

**Ideal For:**

-   Individuals managing their own medications
-   People who need medication reminders
-   Patients tracking health conditions
-   Anyone wanting to improve medication adherence

### 🤝 Caregiver Dashboard (coming up for real time)

**Features Available:**

-   ✅ Connect to multiple patients
-   ✅ Monitor patient medications
-   ✅ Track patient adherence
-   ✅ View patient appointments
-   ✅ Review side effects
-   ✅ Generate patient reports
-   ✅ Manage patient connections

**Ideal For:**

-   Family members caring for loved ones
-   Professional caregivers
-   Nurses and healthcare workers
-   Home health aides
-   Anyone managing medications for others

* * *

## 🎨 Customization

### Age-Based Themes

The application automatically adjusts its theme based on the user's age:

#### Youth Theme (Ages < 18)

-   **Colors**: Purple gradient (#9333ea → #a855f7 → #c084fc)
-   **Font Size**: 16px (optimized for younger users)
-   **Design**: Vibrant and engaging

#### Adult Theme (Ages 18-40)

-   **Colors**: Green gradient (#22c55e → #16a34a → #15803d)
-   **Font Size**: 18px (standard readability)
-   **Design**: Clean and professional

#### Senior Theme (Ages 40+)

-   **Colors**: Yellow/Gold gradient (#eab308 → #ca8a04 → #a16207)
-   **Font Size**: 22px (large, easy to read)
-   **Design**: High contrast, clear visibility

### Medication Colors

Assign colors to medications for visual organization:

-   🔵 Blue
-   🟢 Green
-   🟣 Purple
-   🩷 Pink
-   🟠 Orange
-   🔴 Red
-   🟡 Yellow
-   🟦 Indigo

### Sound Preferences

Toggle sound notifications on/off:

-   **On**: Receive audible reminders and confirmations
-   **Off**: Silent notifications only

* * *

## 📊 Analytics

### Adherence Metrics

**How Adherence is Calculated:**

```
Adherence % = (Total Doses Taken / Total Doses Scheduled) × 100
```

**Note**: Upcoming doses are not penalized in the calculation.

### Adherence Levels

-   🌟 **Excellent (90%+)**: Perfect or near-perfect adherence
-   👍 **Good (70-89%)**: Consistent medication taking
-   🤔 **Fair (50-69%)**: Room for improvement
-   ⚠️ **Poor (below 50%)**: Needs attention and support

### Visualizations

1.  **Adherence Trend Line**
    -   Shows adherence over time
    -   Identifies patterns and trends
    -   100% goal line for reference
2.  **Medication Type Distribution**
    -   Pie chart of medication types
    -   Visual breakdown by dosage form
3.  **Daily Schedule**
    -   Bar chart of medication times
    -   Identify busy/quiet periods
4.  **Side Effects Analysis**
    -   Bar chart by severity
    -   Track problematic medications
5.  **Weekly Heatmap**
    -   Heat map of medication patterns
    -   Day and time breakdown


## 📊 Statistics

-   **Total Lines of Code**: 3,000+
-   **Features**: 50+
-   **User Types**: 2 (Patient, Caregiver)
-   **Age Categories**: 3 (Youth, Adult, Senior)
-   **Achievement Badges**: 10
-   **Report Formats**: 4 (PDF, Text, CSV, Detailed)
-   **Chart Types**: 5
-   **Medication Frequencies**: 10
-   **Color Options**: 8

* * *

🔗 Integration Details
📌 Database Integration (SQLite)

Auto-initializes on first run

Tables include:

users

medications

appointments

side_effects

medication_history

adherence_history

connected_patients

All user data is locally stored and persistent

📊 Visualization Integration

Plotly charts used for:

Adherence trends

Medication distribution

Daily schedule

Side-effect severity

Charts dynamically update based on user data

🔔 Reminder & Notification Integration

HTML-based audio reminders

Triggered when medication time is within ±5 minutes

Optional sound toggle for accessibility

📄 Report Generation Integration

PDF reports generated using ReportLab

Includes:

Patient profile

Medication list

Appointments

Side effects

Downloadable directly from the app

🔐 Authentication Integration

Username + Password login

Optional email-based demo verification

Caregiver ↔ Patient linking using 6-digit access codes

## Testing:

Tested by: Friend





## 🎯 Credits
Created by: M.Raksmi Priyasree (ID: 1000405)

Class: Artificial Intelligence: Python programming – Year 1

Mentor: Syed Ali Beema.S

School: Jain Vidyalaya IB world school, Madurai

## NOTE: App's timing is different according to the streamlit's configuration


[⬆ Back to Top](#-medtimer---advanced-medication-management-system)
