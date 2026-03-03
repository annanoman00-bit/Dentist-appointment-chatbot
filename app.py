import streamlit as st
import sqlite3
from groq import Groq
from datetime import datetime
import pandas as pd

# ---------------------------------------------------------
# 🔑 CONFIGURATION & API SETUP
# ---------------------------------------------------------
GROQ_API_KEY = "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"
MODEL_NAME = "llama-3.3-70b-versatile"

client_groq = Groq(api_key=GROQ_API_KEY)

# Database Connection (Automatic Create)
conn = sqlite3.connect('dentist_clinic.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS appointments 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, phone TEXT, date TEXT, time TEXT, reason TEXT, status TEXT)''')
conn.commit()

# ---------------------------------------------------------
# 🧠 BACKEND FUNCTIONS
# ---------------------------------------------------------

def get_dental_ai_response(user_query):
    """Groq AI se professional dental advice lene ke liye"""
    system_instruction = (
        "You are a highly professional Senior Dentist Assistant. "
        "Provide accurate, polite, and helpful dental advice. "
        "Always suggest booking an appointment for physical exams."
    )
    try:
        response = client_groq.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_query}
            ],
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ AI Error: {str(e)}"

def save_appointment(name, phone, date, time, reason):
    """Database mein appointment save karne ke liye"""
    try:
        cursor.execute("INSERT INTO appointments (name, phone, date, time, reason, status) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, phone, str(date), time, reason, "Confirmed"))
        conn.commit()
        return True
    except:
        return False

# ---------------------------------------------------------
# 🎨 PROFESSIONAL UI (STREAMLIT)
# ---------------------------------------------------------
st.set_page_config(page_title="DentalCare AI Pro", page_icon="🦷", layout="wide")

st.markdown("""
<style>

/* Background Gradient */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #e3f2fd, #ffffff);
}

/* Main Card Style */
.block-container {
    padding: 2rem 2rem 2rem 2rem;
    border-radius: 15px;
    background: rgba(255,255,255,0.85);
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #007bff, #0056b3);
}

[data-testid="stSidebar"] * {
    color: white !important;
}

/* Button Styling */
.stButton>button {
    background: linear-gradient(90deg, #007bff, #00c6ff);
    color: white;
    border: none;
    border-radius: 10px;
    height: 3em;
    font-weight: bold;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
}

/* Input Fields */
.stTextInput>div>div>input, 
.stTextArea textarea, 
.stSelectbox>div>div {
    border-radius: 10px !important;
    border: 1px solid #ced4da !important;
}

/* Section Headers */
h1, h2, h3 {
    color: #003366;
    font-weight: 700;
}

</style>
""", unsafe_allow_html=True)

# 🔥 NEW UI CODE END
#  Custom CSS for Professional Look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .stTextInput>div>div>input { border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🦷 DentalCare AI - Smart Clinic Management")
st.markdown("---")

# Sidebar Menu
menu = ["🏠 Dashboard", "💬 AI Dental Assistant", "📅 Book Appointment", "📋 View All Records"]
choice = st.sidebar.selectbox("Navigation Menu", menu)

# --- HOME DASHBOARD ---
if choice == "🏠 Dashboard":
    st.subheader("Welcome to Your Smart Clinic")
    col1, col2, col3 = st.columns(3)
    
    total_appts = cursor.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]
    
    col1.metric("Total Appointments", total_appts)
    col2.metric("Clinic Status", "Open")
    col3.metric("AI Status", "Online (Llama 3.3)")
    
    st.info("💡 *Tip:* Use the sidebar to navigate between AI Chat and Booking system.")
    
    # Dental Education Image
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Tooth_section_international.svg/1024px-Tooth_section_international.svg.png", 
             caption="Understand your Tooth Structure: Enamel, Dentin & Pulp", width=500)

# --- AI ASSISTANT ---
elif choice == "💬 AI Dental Assistant":
    st.subheader("💬 Chat with AI Dentist Assistant")
    st.write("Ask anything about tooth pain, hygiene, or braces.")
    
    user_msg = st.text_area("Type your concern here...",placeholder="Example: My gums are bleeding, what should I do?")
    
    if st.button("Ask AI"):
        if user_msg:
            with st.spinner("AI is analyzing your query..."):
                advice = get_dental_ai_response(user_msg)
                st.markdown(f"### 🤖 AI Response:\n{advice}")
        else:
            st.warning("Please enter a question.")

# --- BOOKING SYSTEM ---
elif choice == "📅 Book Appointment":
    st.subheader("📅 Schedule a New Appointment")
    
    with st.form("appt_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Patient Full Name*")
            phone = st.text_input("Contact Number*")
            appt_date = st.date_input("Preferred Date", min_value=datetime.today())
        with c2:
            appt_time = st.selectbox("Preferred Time Slot", ["10:00 AM", "11:00 AM", "12:00 PM", "02:00 PM", "04:00 PM", "06:00 PM"])
            reason = st.selectbox("Reason for Visit", ["Routine Checkup", "Emergency Pain", "Teeth Whitening", "Braces Adjustment", "Cleaning"])
            
        submitted = st.form_submit_button("Confirm & Save Appointment")
        
        if submitted:
            if name and phone:
                if save_appointment(name, phone, appt_date, appt_time, reason):
                    st.success(f"✅ Success! Appointment for *{name}* has been saved in the database.")
                    st.balloons()
                else:
                    st.error("Database error occurred.")
            else:
                st.error("Please fill all required (*) fields.")

# --- RECORDS VIEW ---
elif choice == "📋 View All Records":
    st.subheader("📋 Clinic Records")
    query = "SELECT id, name, phone, date, time, reason, status FROM appointments ORDER BY id DESC"
    df = pd.read_sql_query(query, conn)
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        # Option to clear records
        if st.sidebar.button("Clear All Records"):
            cursor.execute("DELETE FROM appointments")
            conn.commit()
            st.rerun()
    else:
        st.write("No appointments found in the database.")

st.sidebar.markdown("---")
st.sidebar.write("Developed for Dental Professionals 🦷")                                                                                                                                                                                         