import streamlit as st
import sqlite3
from groq import Groq
from datetime import datetime
import pandas as pd
import plotly.express as px

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

# Custom CSS for Professional Look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .stTextInput>div>div>input { border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🦷 DentalCare AI - Smart Clinic Management")
st.markdown("""
    <div style="
        background: linear-gradient(90deg, #1e3c72, #2a5298);
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    ">
        <h1 style="font-size:45px; margin-bottom:10px;">
            🦷 DentalCare AI Pro
        </h1>
        <p style="font-size:20px; opacity:0.9;">
            Smart AI-Powered Clinic Management & Virtual Dental Assistant
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Sidebar Menu
menu = ["🏠 Dashboard", "💬 AI Dental Assistant", "📅 Book Appointment", "📋 View All Records"]
choice = st.sidebar.selectbox("Navigation Menu", menu)

# --- HOME DASHBOARD ---
if choice == "🏠 Dashboard":
    st.subheader("📊 Smart Clinic Dashboard")
# Date Filter
selected_date = st.date_input("📅 Select Date to View Appointments", datetime.today())

# Fetch Data
df = pd.read_sql_query("SELECT * FROM appointments", conn)

# Convert date column
df["date"] = pd.to_datetime(df["date"])

# Filter Data
filtered_df = df[df["date"] == pd.to_datetime(selected_date)]
    # Fetch Data

df = pd.read_sql_query("SELECT * FROM appointments", conn)

total_appts = len(df)
today_date = datetime.today().strftime("%Y-%m-%d")
today_appts = len(df[df["date"] == today_date])
emergency_cases = len(df[df["reason"] == "Emergency Pain"])

    # KPI CARDS
col1, col2, col3 = st.columns(3)

col1.markdown(f"""
        <div style="background:linear-gradient(90deg,#4facfe,#00f2fe);
                    padding:20px;border-radius:15px;color:white;text-align:center">
            <h3>Total Appointments</h3>
            <h1>{total_appts}</h1>
        </div>
    """, unsafe_allow_html=True)

col2.markdown(f"""
        <div style="background:linear-gradient(90deg,#43e97b,#38f9d7);
                    padding:20px;border-radius:15px;color:white;text-align:center">
            <h3>Today's Appointments</h3>
            <h1>{today_appts}</h1>
        </div>
    """, unsafe_allow_html=True)

col3.markdown(f"""
        <div style="background:linear-gradient(90deg,#fa709a,#fee140);
                    padding:20px;border-radius:15px;color:white;text-align:center">
            <h3>Emergency Cases</h3>
            <h1>{emergency_cases}</h1>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

    # GRAPH SECTION
if not df.empty:
        reason_count = df["reason"].value_counts().reset_index()
        reason_count.columns = ["Reason", "Count"]

        fig = px.bar(reason_count, x="Reason", y="Count",
                     title="📈 Appointment Distribution",
                     text_auto=True)

        st.plotly_chart(fig, use_container_width=True)
else:
        st.info("No appointment data available to show charts.")
    
        st.info("💡 *Tip:* Use the sidebar to navigate between AI Chat and Booking system.")
    
    # Dental Education Image
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Tooth_section_international.svg/1024px-Tooth_section_international.svg.png", 
             caption="Understand your Tooth Structure: Enamel, Dentin & Pulp", width=500)

# --- AI ASSISTANT ---

if choice == "💬 AI Dental Assistant":

   st.subheader("💬 Chat with AI Dentist Assistant")
   st.write("Ask anything about tooth pain, hygiene, or braces.")
    
user_msg = st.text_area("Type your concern here...", placeholder="Example: My gums are bleeding, what should I do?")
    
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

if choice == "📞 AI Calling Agent":

    st.subheader("📞 AI Calling Assistant")

    phone = st.text_input("Enter Patient Phone Number")

    message = st.text_area("AI Message",
    value="Hello, this is DentalCare AI reminding you about your dental appointment.")

    if st.button("Start AI Call Simulation"):

        if phone:

            with st.spinner("AI is preparing the call..."):

                ai_response = get_dental_ai_response(message)

                st.success("📞 Call Simulation Started")

                st.write("Patient Number:", phone)

                st.write("AI Message:")

                st.info(ai_response)

        else:

            st.warning("Enter phone number first.")