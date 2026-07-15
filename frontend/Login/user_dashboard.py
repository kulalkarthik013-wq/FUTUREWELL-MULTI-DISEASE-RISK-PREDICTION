import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from PIL import Image
from code.DiseaseModel import DiseaseModel
from code.helper import prepare_symptoms_array
import joblib
from streamlit_login_auth_ui.widgets import __login__
from streamlit_option_menu import option_menu  # Make sure this is imported
from logger import log_diabetes_result, load_diabetes_results
from logger import log_heart_disease_result, load_heart_disease_results
from logger import log_parkison_result, load_parkison_results
from logger import log_liver_result, load_liver_results
from logger import log_lung_cancer_result, load_lung_cancer_results
from logger import log_chronic_kidney_result, load_chronic_kidney_results
import json
from logger import log_login_event_json
import os
from fpdf import FPDF
from datetime import datetime
from dotenv import load_dotenv
from logger import grant_access, has_access, list_access_users
from user_trans import translations
import streamlit as st
import streamlit as st

import streamlit as st
from datetime import datetime
import base64
from logger import load_appointments,save_appointments
import streamlit as st
import json
import os
# Import your JSON helper functions
from chat_store import (
    authenticate_doctor,
    assign_patient_to_doctor,
    get_conversation,
    save_patient_message,
    save_patient_media,
    save_doctor_reply,
    get_all_patients_for_doctor,
)

from fpdf import FPDF
import streamlit as st
import uuid
from fpdf import FPDF
import qrcode
from io import BytesIO

def get_base64_image(uploaded_file):
    if uploaded_file is not None:
        data = uploaded_file.read()
        return base64.b64encode(data).decode("utf-8")
    return None



def generate_qr_code(appointment_id: str):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(appointment_id)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


DOCTORS_FILE = r"D:\proj\frontend\data\chat_data.json"

def load_doctors():
    if not os.path.exists(DOCTORS_FILE):
        with open(DOCTORS_FILE, "w") as f:
            json.dump({"doctors": ["Dr. Smith", "Dr. Patel", "Dr. Rao"]}, f, indent=4)
    with open(DOCTORS_FILE, "r") as f:
        data = json.load(f)
        return data.get("doctors", [])

def show_app_dashboard(username):
    st.markdown("""<style>.appt-card{background:rgba(255,255,255,0.9);backdrop-filter:blur(10px);padding:20px;border-radius:15px;margin:10px 0;box-shadow:0 8px 20px rgba(0,0,0,0.15)}</style>""", unsafe_allow_html=True)
    st.markdown("<h1 style='color:#0072ff'>📅 Doctor Appointments</h1>", unsafe_allow_html=True)

    appointments = load_appointments()
    user_appointments = {k: v for k, v in appointments.items() if v.get('patient') == username}
    
    tab1, tab2 = st.tabs(["📋 My Appointments", "➕ Book New"])
    
    with tab1:
        if user_appointments:
            for appt_id, appt in user_appointments.items():
                status_color = "#10b981" if appt['status'] == 'Confirmed' else "#f59e0b" if appt['status'] == 'Pending' else "#ef4444"
                st.markdown(f"<div class='appt-card' style='border-left:5px solid {status_color}'><h4 style='color:#0072ff'>🩺 Dr. {appt['doctor']}</h4><p style='color:#333'>📅 {appt['date']} | 🕒 {appt['time']} | Status: <b>{appt['status']}</b></p></div>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("❌ Cancel", key=f"cancel_{appt_id}"):
                        appointments[appt_id]['status'] = 'Cancelled'
                        save_appointments(appointments)
                        st.success("Cancelled")
                        st.rerun()
                with col2:
                    new_date = st.date_input("Reschedule", key=f"date_{appt_id}")
                    if st.button("🔄 Reschedule", key=f"resched_{appt_id}"):
                        appointments[appt_id]['date'] = str(new_date)
                        save_appointments(appointments)
                        st.success("Rescheduled")
                        st.rerun()
        else:
            st.info("No appointments")
    
    with tab2:
        st.subheader("Book an Appointment")

    doctors = load_doctors()
    states = sorted(set([doc["state"] for doc in doctors]))
    state = st.selectbox("Choose State", states, key="state_select")

    # Step 2: Select City (filtered by state)
    cities = sorted(set([doc["city"] for doc in doctors if doc["state"] == state]))
    city = st.selectbox("Choose City", cities, key="city_select")

    # Step 3: Select Place/Location (filtered by city)
    places = sorted(set([doc["location"] for doc in doctors if doc["city"] == city]))
    place = st.selectbox("Choose Place", places, key="place_select")

    # Step 4: Select Doctor (filtered by place)
    filtered_doctors = [doc for doc in doctors if doc["location"] == place]
    doctor_options = [f"{doc['name']} ({doc['specialty']})" for doc in filtered_doctors]
    doctor = st.selectbox("Choose Doctor", doctor_options, key="doctor_select")


    date = st.date_input("Select Date", key="date_select")

    # ✅ Doctor timings: 10 AM – 7 PM with 15-min slots
    time_options = [
        "10:00 AM", "10:15 AM", "10:30 AM", "10:45 AM",
        "11:00 AM", "11:15 AM", "11:30 AM", "11:45 AM",
        "12:00 PM", "12:15 PM", "12:30 PM", "12:45 PM",
        # Skip 01:00 PM – 02:00 PM (Lunch break)
        "02:00 PM", "02:15 PM", "02:30 PM", "02:45 PM",
        "03:00 PM", "03:15 PM", "03:30 PM", "03:45 PM",
        # Skip 04:00 PM – 04:30 PM (Evening break)
        "04:30 PM", "04:45 PM",
        "05:00 PM", "05:15 PM", "05:30 PM", "05:45 PM",
        "06:00 PM", "06:15 PM", "06:30 PM", "06:45 PM",
        "07:00 PM"
    ]

    selected_time = st.selectbox("Select Time", time_options, key="time_select")

    if st.button("Book Appointment", key="book_button"):
        appointment_id = f"APT-{uuid.uuid4().hex[:8].upper()}"  # ✅ random unique ID

        appointments[appointment_id] = {
            "appointment_id": appointment_id,
            "patient": username,
            "doctor": doctor,
            "state": state,
            "city": city,
            "location": place,
            "date": str(date),
            "time": selected_time,
            "status": "Pending"
        }

        save_appointments(appointments)
        st.success("Appointment request submitted!")

    st.subheader("Your Appointments")
    for idx, appt in enumerate(appointments.values()):
        if appt["patient"] == username:
            st.write(
                f"Doctor: {appt['doctor']} | Location: {appt.get('location','N/A')} | "
                f"Date: {appt['date']} | Time: {appt['time']} | Status: {appt['status']}"
            )
        
            if appt["status"] == "Approved":
                qr_bytes = generate_qr_code(appt["appointment_id"])
                st.image(qr_bytes, caption=f"QR for {appt['appointment_id']}")
                st.download_button(
                    label="📲 Download QR Code",
                    data=qr_bytes,
                    file_name=f"{appt['appointment_id']}.png",
                    mime="image/png",
                    key=f"qr_{idx}"
                )

                



# -------------------------------
# Patient UI
# -------------------------------
def show_health_analytics(username):
    st.markdown("""<style>.analytics-card{background:rgba(255,255,255,0.9);backdrop-filter:blur(10px);padding:20px;border-radius:15px;margin:10px 0;box-shadow:0 8px 20px rgba(0,0,0,0.15)}</style>""", unsafe_allow_html=True)
    st.markdown("<h1 style='color:#0072ff'>📈 My Health Analytics</h1>", unsafe_allow_html=True)
    
    from logger import (load_diabetes_results, load_heart_disease_results, load_parkison_results,
                        load_liver_results, load_lung_cancer_results, load_chronic_kidney_results)
    
    # Load all test results
    all_tests = {
        "Diabetes": load_diabetes_results(),
        "Heart Disease": load_heart_disease_results(),
        "Parkinson": load_parkison_results(),
        "Liver Disease": load_liver_results(),
        "Lung Cancer": load_lung_cancer_results(),
        "Chronic Kidney": load_chronic_kidney_results()
    }
    
    # Filter user's tests
    user_tests = {}
    for disease, df in all_tests.items():
        if not df.empty:
            if 'Name' in df.columns:
                user_df = df[df['Name'].str.lower() == username.lower()]
                if not user_df.empty:
                    user_tests[disease] = user_df
            elif 'Username' in df.columns:
                user_df = df[df['Username'].str.lower() == username.lower()]
                if not user_df.empty:
                    user_tests[disease] = user_df
    
    if not user_tests:
        st.info("No test results found. Take a test to see your analytics!")
        return
    
    # Dashboard Metrics
    col1, col2, col3, col4 = st.columns(4)
    total_tests = sum(len(df) for df in user_tests.values())
    positive_tests = sum(df['Result'].str.contains('Disease|Diabetic|Cancer|Parkinson', case=False, na=False).sum() for df in user_tests.values())
    negative_tests = total_tests - positive_tests
    risk_score = int((positive_tests / total_tests * 100)) if total_tests > 0 else 0
    
    col1.metric("📊 Total Tests", total_tests)
    col2.metric("✅ Negative", negative_tests)
    col3.metric("⚠️ Positive", positive_tests)
    col4.metric("🎯 Risk Score", f"{risk_score}%")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Progress Charts", "📋 Test History", "📄 Download Report"])
    
    with tab1:
        st.subheader("Test Results Over Time")
        for disease, df in user_tests.items():
            if 'Timestamp' in df.columns:
                df['Date'] = pd.to_datetime(df['Timestamp'], errors='coerce')
                df = df.sort_values('Date')
                st.markdown(f"### {disease}")
                st.line_chart(df.set_index('Date')['Result'].apply(lambda x: 1 if 'Disease' in str(x) or 'Diabetic' in str(x) else 0))
        
        st.subheader("Test Distribution")
        test_counts = {disease: len(df) for disease, df in user_tests.items()}
        st.bar_chart(test_counts)
    
    with tab2:
        st.subheader("Complete Test History")
        for disease, df in user_tests.items():
            with st.expander(f"{disease} ({len(df)} tests)"):
                st.dataframe(df, use_container_width=True)
                
                # Comparison with previous test
                if len(df) > 1:
                    latest = df.iloc[-1]
                    previous = df.iloc[-2]
                    st.markdown("**Comparison with Previous Test:**")
                    col1, col2 = st.columns(2)
                    col1.info(f"Previous: {previous['Result']}")
                    col2.success(f"Latest: {latest['Result']}")
    
    with tab3:
        st.subheader("Download Health Report")
        
        # Generate comprehensive report
        report_text = f"HEALTH REPORT - {username}\n"
        report_text += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report_text += f"SUMMARY\n"
        report_text += f"Total Tests: {total_tests}\n"
        report_text += f"Positive Results: {positive_tests}\n"
        report_text += f"Negative Results: {negative_tests}\n"
        report_text += f"Risk Score: {risk_score}%\n\n"
        
        for disease, df in user_tests.items():
            report_text += f"\n{disease.upper()}\n"
            report_text += f"Tests Taken: {len(df)}\n"
            if not df.empty:
                latest = df.iloc[-1]
                report_text += f"Latest Result: {latest['Result']}\n"
                report_text += f"Date: {latest['Timestamp']}\n"
        
        st.download_button(
            "📥 Download Full Report (TXT)",
            report_text,
            f"health_report_{username}.txt",
            "text/plain",
            use_container_width=True
        )
        
        # CSV Export
        combined_df = pd.concat([df.assign(Disease=disease) for disease, df in user_tests.items()], ignore_index=True)
        st.download_button(
            "📥 Download Data (CSV)",
            combined_df.to_csv(index=False),
            f"health_data_{username}.csv",
            "text/csv",
            use_container_width=True
        )

def show_patient_ui(username):
    st.markdown("""<style>
    .chat-container{background:rgba(255,255,255,0.85);backdrop-filter:blur(10px);padding:25px;border-radius:20px;box-shadow:0 10px 30px rgba(0,0,0,0.2)}
    .chat-window{background:rgba(255,255,255,0.95);border-radius:15px;padding:20px;max-height:500px;overflow-y:auto}
    .msg-patient{background:rgba(0,114,255,0.9);color:white;padding:15px 20px;border-radius:20px 20px 5px 20px;margin:10px 0;max-width:70%;float:right;clear:both}
    .msg-doctor{background:rgba(102,126,234,0.9);color:white;padding:15px 20px;border-radius:20px 20px 20px 5px;margin:10px 0;max-width:70%;float:left;clear:both}
    .clearfix::after{content:"";display:table;clear:both}
    </style>""", unsafe_allow_html=True)
    
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    st.markdown("<h1 style='color:#0072ff;text-align:center'>💬 Chat with Doctor</h1>", unsafe_allow_html=True)

    patient_name = st.text_input("Enter your name:")
    specialty = st.selectbox("Doctor Type:", ["Orthopaedist", "Cardiologist","Neurologist","Dermatologist","Medicine","Gynecologist","Pediatrician","ENT Specialist","Psychiatrist", "General Surgeon","Oncologist","Endocrinologist"])

    if st.button("Assign Doctor"):
        doctor = assign_patient_to_doctor(patient_name, specialty)
        if doctor:
            st.session_state["patient_username"] = patient_name
            st.session_state["doctor_username"] = doctor["username"]
            st.session_state["doctor_specialty"] = doctor["specialty"]
            st.success(f"Assigned to {doctor['name']} ({doctor['specialty']})")
        else:
            st.error("No doctor available")

    if "patient_username" in st.session_state:
        history = get_conversation(st.session_state["patient_username"])
        st.markdown("<div class='chat-window'>", unsafe_allow_html=True)

        for msg in history:
            who = "👤 You" if msg["sender"] == "patient" else f"🩺 Dr. {msg.get('doctor', 'Doctor')}"
            msg_class = "msg-patient" if msg["sender"] == "patient" else "msg-doctor"
            
            if msg.get("message"):
                st.markdown(f"<div class='clearfix'><div class='{msg_class}'><b>{who}</b><br>{msg['message']}<br><small style='opacity:0.8'>{msg['timestamp']}</small></div></div>", unsafe_allow_html=True)
            elif msg.get("media"):
                if msg["media"].endswith((".png", ".jpg", ".jpeg")):
                    st.image(msg["media"], caption=f"{who} — {msg['timestamp']}", width=250)
                elif msg["media"].endswith(".pdf"):
                    with open(msg["media"], "rb") as f:
                        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="600" height="400"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)
                    st.caption(f"{who} — {msg['timestamp']}")
                else:
                    st.markdown(f"<div class='clearfix'><div class='{msg_class}'><b>{who}</b><br>📎 <a href='{msg['media']}' target='_blank' style='color:white'>View File</a><br><small style='opacity:0.8'>{msg['timestamp']}</small></div></div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.divider()
        st.markdown("### ✍️ Send a message")

        user_message = st.text_area(
            "Type your message here...",
            placeholder="Write your question or update for the doctor...",
            height=100
        )
        uploaded_file = st.file_uploader("📎 Attach prescription or image", type=["png","jpg","jpeg","pdf"])
        if st.button(" Send"):
            if user_message.strip():
                save_patient_message(st.session_state["patient_username"], user_message.strip())
                st.success("Message sent ✅")
                st.rerun()
            elif uploaded_file is not None:
                save_patient_media(st.session_state["patient_username"], uploaded_file)
                st.success("File sent ✅")
                st.rerun()
            else:
                st.warning("Please type a message or attach a file before sending.")

                


def save_feedback_json(username, comment, file_path="feedback.json"):
    feedback_entry = {
        "username": username,
        "comment": comment,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Load existing feedback
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
    else:
        data = []

    # Append new entry
    data.append(feedback_entry)

    # Save back to file
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4) 


def load_feedback_json(file_path="feedback.json"):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            st.error("⚠️ Feedback file is corrupted.")
            return []
    return []  




class CertificatePDF(FPDF):
    def header(self):
        # Add full-page background (A4 size in mm)
        self.image('background4.jpg', x=0, y=0, w=210, h=297)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Times', 'I', 10)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, 'AlphaGroup©2025', 0, 0, 'C')

def generate_diabetes_certificate(name, result_text, inputs):
    pdf = CertificatePDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Times", 'B', 24)
    pdf.set_text_color(255, 0, 0)  # Red
    pdf.ln(10)
    pdf.cell(0, 12, "FUTURE WELL", ln=True, align='C')

    pdf.set_font("Times", 'B', 18)
    pdf.set_text_color(0, 0, 0)  # Black
    pdf.ln(5)
    pdf.cell(0, 10, "DISEASE PREDICTION CERTIFICATE", ln=True, align='C')
    pdf.ln(10)

    # Personal Info
    pdf.set_font("Times", size=14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Name: {name}", ln=True)
    pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.cell(0, 10, f"Result: {result_text}", ln=True)
    pdf.ln(10)

    # Input Summary
    pdf.set_font("Times", 'B', 14)
    pdf.set_fill_color(224, 247, 250)
    pdf.cell(0, 10, "Input Summary", ln=True)
    pdf.ln(5)

    pdf.set_font("Times", size=12)

    # Convert dictionary to list of tuples
    input_items = list(inputs.items())

    # Split into two columns
    half = len(input_items) // 2 + len(input_items) % 2
    left_column = input_items[:half]
    right_column = input_items[half:]

    # Print side-by-side
    for i in range(half):
        if i < len(left_column):
            key, value = left_column[i]
            pdf.cell(90, 10, f"{key}: {value}", border=0)
        if i < len(right_column):
            key, value = right_column[i]
            pdf.cell(90, 10, f"{key}: {value}", border=0)
        pdf.ln(10)

    # Disclaimer
    pdf.set_font("Times", 'I', 11)
    pdf.set_text_color(150, 0, 0)
    pdf.multi_cell(0, 10, "Disclaimer: This certificate is generated based on model prediction and is not a medical diagnosis.")

    # ✅ Convert bytearray → bytes
    return bytes(pdf.output(dest='S'))




def save_user_data(user_data, filename="_secret_auth_.json"):
    """Save updated user data back into the JSON file."""
    with open(filename, "w") as f:
        json.dump(user_data, f, indent=4)

def get_user_email(username, filename="_secret_auth_.json"):
    """Fetch email for a given username from JSON file."""
    with open(filename, "r") as f:
        authorized_users_data = json.load(f)

    for user in authorized_users_data:
        if user["username"] == username:
            return user.get("email", "Not available")
    return "Not available"

def load_manual_access_json():
    try:
        with open("manual_access.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def show_user_dashboard(username, role="User"):
    manual_access = manual_access = load_manual_access_json()

    

    if username in manual_access:
            st.session_state["is_subscribed"] = manual_access[username]
    else:
            st.session_state["is_subscribed"] = False


    


    with st.sidebar:
        lang_choice = st.sidebar.selectbox("Select Language", ["English", "Kannada", "Hindi"])
        labels = translations[lang_choice]

        # Handle profile picture upload
        if "profile_pic" not in st.session_state:
            st.session_state["profile_pic"] = None


        # Convert to base64 for inline display
        img_base64 = get_base64_image(st.session_state["profile_pic"])
        if img_base64:
            img_tag = f"data:image/png;base64,{img_base64}"
        else:
            img_tag = "https://cdn-icons-png.flaticon.com/512/149/149071.png"  # default avatar

        # 🔹 Role bar with profile picture inline
        st.markdown(f"""
            <div style='background-color:#0072ff; padding:10px; border-radius:8px;
                        text-align:center; color:white; font-size:18px; font-weight:bold;
                        display:flex; align-items:center; justify-content:center; gap:10px;'>
                <img src="{img_tag}" style="width:35px; height:35px; border-radius:50%; border:2px solid white;" />
                Logged in as: {username} | Role: {role}
            </div>
            """, unsafe_allow_html=True)

        # 🔹 Profile expander with Edit Profile
        with st.expander("View Profile"):
            from logger import load_auth_json
            auth_data = load_auth_json()
            user_info = next((u for u in auth_data if u["username"] == username), None)
            
            uploaded_pic = st.file_uploader("Upload/Update Profile Picture", type=["png", "jpg", "jpeg"])
            if uploaded_pic is not None:
                st.session_state["profile_pic"] = uploaded_pic
            if st.session_state["profile_pic"]:
                st.image(st.session_state["profile_pic"], width=120, caption=f"{username}'s Profile Picture")
            else:
                st.image("https://cdn-icons-png.flaticon.com/512/149/149071.png", width=120, caption="Default Avatar")

            st.write(f"**Username:** {username}")
            st.write(f"**Role:** {role}")
            email = get_user_email(username)
            st.write(f"**Email:** {email}")
            
            st.markdown("---")
            st.subheader("📝 Edit Profile")
            
            tab1, tab2, tab3 = st.tabs(["👤 Profile Info", "🔐 Change Password", "💳 Subscription"])
            
            with tab1:
                if 'edit_mode' not in st.session_state:
                    st.session_state['edit_mode'] = False
                
                if not st.session_state['edit_mode']:
                    st.text_input("Name", value=user_info.get("name", "") if user_info else "", disabled=True)
                    st.text_input("Email", value=user_info.get("email", "") if user_info else "", disabled=True)
                    st.text_input("Phone", value=user_info.get("phone", "") if user_info else "", disabled=True)
                    if st.button("✏️ Edit", use_container_width=True):
                        st.session_state['edit_mode'] = True
                        st.rerun()
                else:
                    new_name = st.text_input("Name", value=user_info.get("name", "") if user_info else "")
                    new_email = st.text_input("Email", value=user_info.get("email", "") if user_info else "")
                    new_phone = st.text_input("Phone", value=user_info.get("phone", "") if user_info else "")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Save", use_container_width=True):
                            for u in auth_data:
                                if u["username"] == username:
                                    u["name"] = new_name
                                    u["email"] = new_email
                                    u["phone"] = new_phone
                            with open("_secret_auth_.json", "w") as f:
                                json.dump(auth_data, f, indent=4)
                            st.session_state['edit_mode'] = False
                            st.success("✅ Profile updated!")
                            st.rerun()
                    with col2:
                        if st.button("❌ Cancel", use_container_width=True):
                            st.session_state['edit_mode'] = False
                            st.rerun()
            
            with tab2:
                from argon2 import PasswordHasher
                ph = PasswordHasher()
                
                current_pwd = st.text_input("Current Password", type="password")
                new_pwd = st.text_input("New Password", type="password")
                confirm_pwd = st.text_input("Confirm Password", type="password")
                
                if st.button("🔄 Update Password", use_container_width=True):
                    if not current_pwd or not new_pwd or not confirm_pwd:
                        st.error("❌ All fields are required")
                    elif new_pwd != confirm_pwd:
                        st.error("❌ New passwords don't match")
                    else:
                        try:
                            ph.verify(user_info.get("password"), current_pwd)
                            for u in auth_data:
                                if u["username"] == username:
                                    u["password"] = ph.hash(new_pwd)
                            with open("_secret_auth_.json", "w") as f:
                                json.dump(auth_data, f, indent=4)
                            st.success("✅ Password updated!")
                        except:
                            st.error("❌ Current password is incorrect")
            
            with tab3:
                if st.session_state.get("is_subscribed", False):
                    st.success("✅ Subscribed")
                    try:
                        with open("subscriptions.json", "r") as f:
                            subs = json.load(f)
                        if username in subs:
                            sub = subs[username]
                            st.metric("💰 Amount", f"${sub.get('amount', 0)}")
                            st.metric("📅 Expiry", sub.get('expiry', 'N/A'))
                    except:
                        pass
                else:
                    st.warning("❌ Not Subscribed")
                    if st.button("Buy Subscription", key="buy_sub_button", use_container_width=True):
                        img = Image.open("D:/proj/frontend/pay.jpg")
                        st.image(img, caption=f"Scan to pay ₹{129} to buy Monthly & ₹{699} to buy Yearly Subscription")
                        st.caption("To enable your subscription, please send the payment screenshot and your username/email ID for verification on WhatsApp (+91 6363796651).")

                        

       




        selected = option_menu(
        labels["title"],   # menu title
        [
            labels["home"], 
            labels["disease_prediction"], 
            "Diabetes Prediction",
            "Heart Disease Prediction",
            "Parkinson Prediction",
            "Liver Disease Prediction",
            "Lung Cancer Prediction",
            "Chronic Kidney Prediction",
            labels["doctor_chat"],
            "Doctor Appointment",
            labels["contact"]
        ],
        icons=["house", "bar-chart-line", "activity", "heart", "person",
            "shield-plus", "wind", "file-medical","chat-dots","calendar-check","telephone"],
        default_index=0,
        orientation="vertical"
    )


    if selected == labels["home"]:
        st.markdown(f"<h1 style='color:#000000;'>{labels['home_title']}</h1>", unsafe_allow_html=True)

        


        # Custom CSS
        st.markdown("""
            <style>
                h1, h2 {
                    font-family: 'Segoe UI', sans-serif;
                }
                .gradient-text {
                    background: linear-gradient(to right, #0072ff, #00c6ff);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }
                .section {
                    margin-top: 2rem;
                    margin-bottom: 1rem;
                }
                .step {
                    font-size: 16px;
                    margin-bottom: 0.5rem;
                }
                .footer {
                    text-align: center;
                    color: gray;
                    font-size: 14px;
                    margin-top: 3rem;
                }
                hr {
                    border: none;
                    height: 1px;
                    background: #ddd;
                }
            </style>
        """, unsafe_allow_html=True)

    

        # How it works
        st.markdown(f"<h2 class='gradient-text section'>{labels['how_it_works']}</h2>", unsafe_allow_html=True)
        for i, step in enumerate(labels["steps"], 1):
            st.markdown(f"<div class='step'>{i}) <strong>{step}</strong></div>", unsafe_allow_html=True)



        # --- About Subscription Section ---
        st.markdown(
            """
            <style>
            .sub-card {
                background: rgba(255, 255, 255, 0.15);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                padding: 1.5rem;
                margin-top: 2rem;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                border: 1px solid rgba(255,255,255,0.3);
            }
            .sub-title {
                font-size: 1.4rem;
                font-weight: 700;
                background: linear-gradient(90deg, #ff7eb3, #ff758c);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 0.8rem;
            }
            .sub-text {
                font-size: 1rem;
                color: #000000;
                line-height: 1.6;
            }
          
            .sub-btn {
                display: inline-block;
                margin-top: 1rem;
                padding: 0.6rem 1.2rem;
                background: #FFFFFF;   /* simple dark color */
                color: white;
                border-radius: 6px;
                text-decoration: none;
                font-weight: 600;
                transition: background 0.3s ease;
            }
            .sub-btn:hover {
                background: #F3F3F3;   /* lighter shade on hover */
            }
            </style>
            """,
            unsafe_allow_html=True
        )

       

        st.markdown(f"""
            <div class="sub-card">
                <div class="sub-title">{labels['subscription_title']}</div>
                <div class="sub-text">{labels['subscription_text']}</div>
            </div>
        """, unsafe_allow_html=True)



        if st.button(labels["view_plans"] if "view_plans" in labels else "View Plans"):
            st.markdown(f"### {labels['subscription_title']}")
            st.info(labels["subscription_plan_info"])

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"### {labels['monthly_plan']}")
                for feature in labels["subscription_features"]:
                    st.markdown(f"- {feature}")

            with col2:
                st.markdown(f"### {labels['yearly_plan']}")
                for feature in labels["subscription_features"]:
                    st.markdown(f"- {feature}")

                

           # About section
        st.markdown(f"<h2 class='gradient-text section'>{labels['about_title']}</h2>", unsafe_allow_html=True)
        st.markdown(f"##### {labels['about_text']}")

        # Privacy
        st.markdown(f"<h2 class='gradient-text section'>{labels['privacy_title']}</h2>", unsafe_allow_html=True)
        st.success(labels["privacy_text"])

        # FAQ
        st.markdown(f"<h2 class='gradient-text section'>{labels['faq_title']}</h2>", unsafe_allow_html=True)
        with st.expander(labels["expander_title"]):
            for q, a in labels["faq"].items():
                st.markdown(f"**{q}**")
                st.write(a)

        # Disclaimer
        st.markdown(f"<h2 class='gradient-text section'>{labels['disclaimer_title']}</h2>", unsafe_allow_html=True)
        st.info(labels["disclaimer_text"])



                        

                    



    elif selected == labels["contact"]:   # use translated menu label

        # Title
        st.markdown(
            f"<h1 style='color:#000000;'>{labels['contact_title']}</h1>",
            unsafe_allow_html=True
        )

        # Description
        st.markdown(labels["contact_description"])

        # Feedback form
        st.markdown('<div class="feedback-box">', unsafe_allow_html=True)
        st.markdown(f"<div class='feedback-title'>{labels['feedback_title']}</div>", unsafe_allow_html=True)

        with st.form("feedback_form"):
            username = st.text_input(labels["name_label"])
            comment = st.text_area(labels["comment_label"])
            submitted = st.form_submit_button(labels["submit_button"])
        if submitted and username and comment:
            save_feedback_json(username, comment)
            st.success(labels["success_message"])
        st.markdown('</div>', unsafe_allow_html=True)

        # Support Info
        st.markdown(f"### {labels['support_options']}")
        st.markdown(f"""
        - {labels['email']}
        - {labels['whatsapp']}
        - {labels['phone']}
        """)

        # Custom CSS (unchanged)
        st.markdown("""
            <style>
            /* White gradient slider track */
            .stSlider > div[data-baseweb="slider"] > div > div {
                background: linear-gradient(to right, #ffffff, #e0e0e0);
                height: 6px;
                border-radius: 3px;
            }

            /* Slider thumb styling */
            .stSlider span[role="slider"] {
                background-color: #cccccc !important;
                border: 2px solid #ffffff;
                height: 20px;
                width: 20px;
                border-radius: 50%;
            }
            </style>
        """, unsafe_allow_html=True)

                

        st.markdown("""
                    <style>
                    /* White gradient slider track */
                    .stSlider > div[data-baseweb="slider"] > div > div {
                        background: linear-gradient(to right, #ffffff, #e0e0e0);  /* White to light gray */
                        height: 6px;
                        border-radius: 3px;
                    }

                    /* Slider thumb styling */
                    .stSlider span[role="slider"] {
                        background-color: #cccccc !important;  /* Light gray thumb */
                        border: 2px solid #ffffff;
                        height: 20px;
                        width: 20px;
                        border-radius: 50%;
                    }
                    </style>
                """, unsafe_allow_html=True)


        
    

    elif selected == labels["disease_prediction"]:   # use translated menu label
        # Create disease class and load ML model
        disease_model = DiseaseModel()
        disease_model.load_xgboost('model/xgboost_model.json')

        # Title
        st.write(f"# {labels['disease_title']}")

        # Symptoms input
        symptoms = st.multiselect(labels["symptom_prompt"], options=disease_model.all_symptoms)
        X = prepare_symptoms_array(symptoms)

        # Trigger XGBoost model
        if st.button(labels["predict_button"]):
            prediction, prob = disease_model.predict(X)
            st.write(f"## {labels['disease_title']}: {prediction} ({prob*100:.2f}% probability)")

            # Tabs
            tab1, tab2 = st.tabs([labels["description_tab"], labels["precautions_tab"]])

            with tab1:
                st.write(disease_model.describe_predicted_disease())

            with tab2:
                precautions = disease_model.predicted_disease_precautions()
                for i, precaution in enumerate(precautions[:4], 1):
                    st.write(f"{i}. {precaution}")

    else:
        if st.session_state["is_subscribed"]:
            st.success(f"Welcome to {selected} module (subscriber only).")




            # Diabetes prediction page
            if selected == 'Diabetes Prediction':  # pagetitle
                        st.title("Diabetes Disease Prediction")
                        diabetes_model = joblib.load("models/diabetes_model.sav")
                # columns
                # no inputs from the user
                        name = st.text_input("Name:")
                        col1, col2, col3 = st.columns(3)
                        with col2:
                            gender_labels = ["Male", "Female"]
                            gender_index = st.selectbox("Gender", list(range(len(gender_labels))), format_func=lambda x: gender_labels[x])
                            sex = 1 if gender_labels[gender_index] == "Male" else 0
                            selected_gender = gender_labels[gender_index]
            
                        with col1:

                            Age =st.slider("Enter your age", 1, 100, 25)

                        with col2:
                            Glucose = st.slider("Glucose Level (mg/dL)", min_value=50, max_value=200, value=120, step=1)

                        with col3:
                            BloodPressure = st.slider("Blood Pressure (mmHg)", min_value=40, max_value=140, value=80, step=1)

                        with col1:
                            SkinThickness = st.slider("Skin Thickness (mm)", min_value=0, max_value=100, value=20, step=1)

                        with col2:
                            Insulin = st.slider("Insulin Level (μU/mL)", min_value=0, max_value=900, value=80, step=5)

                        with col3:
                            BMI = st.slider("BMI", min_value=10.0, max_value=60.0, value=25.0, step=0.1)

                        with col1:
                            DiabetesPedigreefunction = st.slider("Diabetes Pedigree Function", min_value=0.0, max_value=2.5, value=0.5, step=0.01)

                        with col3: Pregnancies = st.slider("Number of Pregnancies", min_value=0, max_value=20, value=2, step=1)

                # code for prediction
                        diabetes_dig = ''

                # button
                        if st.button("Diabetes test result"):
                            diabetes_prediction=[[]]
                            diabetes_prediction = diabetes_model.predict(
                                [[Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreefunction, Age]])

                    # after the prediction is done if the value in the list at index is 0 is 1 then the person is diabetic
                            if diabetes_prediction[0] == 1:
                                diabetes_dig = "we are really sorry to say but it seems like you are Diabetic."
                                image = Image.open('positive.jpg')
                                st.image(image, caption='')
                            else:
                                diabetes_dig = 'Congratulation,You are not diabetic'
                                image = Image.open('negative.jpg')
                                st.image(image, caption='')
                            st.success(name+' , ' + diabetes_dig)
                            inputs = {
                            "Age": Age,
                            "Sex": selected_gender,    
                            "Pregnancies": Pregnancies,
                            "Glucose": Glucose,
                            "BloodPressure": BloodPressure,
                            "SkinThickness": SkinThickness,
                            "Insulin": Insulin,
                            "BMI": BMI,
                            "DiabetesPedigreeFunction": DiabetesPedigreefunction
                            
                            }
                            log_diabetes_result(name, diabetes_prediction[0], inputs)
                            pdf_bytes = generate_diabetes_certificate(name, diabetes_dig, inputs)
                            st.download_button(label="📄 Download Certificate", data=pdf_bytes, file_name="Diabetes_Certificate.pdf", mime="application/pdf")


                    



            # Heart prediction page
            elif selected == 'Heart Disease Prediction':
                        st.title("Heart Disease Prediction")
                        heart_model = joblib.load("models/heart_disease_model.sav")

                        name = st.text_input("Name:")
                        col1, col2, col3 = st.columns(3)

                        # Age
                        with col1:
                            age = st.slider("Age", min_value=1, max_value=120, value=45)

                        # Gender
                        with col2:
                            gender_labels = ["Male", "Female"]
                            gender_index = st.selectbox("Gender", list(range(len(gender_labels))), format_func=lambda x: gender_labels[x])
                            sex = 1 if gender_labels[gender_index] == "Male" else 0
                            selected_gender = gender_labels[gender_index]

                        # Chest Pain Type
                        with col3:
                            cp_labels = ["Typical Angina", "Atypical Angina", "Non-anginal Pain", "Asymptomatic"]
                            cp_index = st.selectbox("Chest Pain Type", list(range(len(cp_labels))), format_func=lambda x: cp_labels[x])
                            cp = cp_index
                            cp_label = cp_labels[cp_index]

                        # Resting Blood Pressure
                        with col1:
                            trestbps = st.slider("Resting Blood Pressure (mmHg)", min_value=80, max_value=200, value=120)

                        # Serum Cholesterol
                        with col2:
                            chol = st.slider("Serum Cholesterol (mg/dL)", min_value=100, max_value=400, value=200)

                        # Resting ECG
                        with col3:
                            restecg_labels = ["Normal", "ST-T wave abnormality", "Left ventricular hypertrophy"]
                            restecg_index = st.selectbox("Resting ECG", list(range(len(restecg_labels))), format_func=lambda x: restecg_labels[x])
                            restecg = restecg_index
                            restecg_label = restecg_labels[restecg_index]

                        # Max Heart Rate Achieved
                        with col1:
                            thalach = st.slider("Max Heart Rate Achieved", min_value=60, max_value=220, value=150)

                        # ST Depression (Oldpeak)
                        with col2:
                            oldpeak = st.slider("ST Depression (Oldpeak)", min_value=0.0, max_value=6.0, value=1.0, step=0.1)

                        # Peak Exercise ST Segment
                        with col3:
                            slope_labels = ["Upsloping", "Flat", "Downsloping"]
                            slope_index = st.selectbox("Peak Exercise ST Segment", list(range(len(slope_labels))), format_func=lambda x: slope_labels[x])
                            slope = slope_index
                            slope_label = slope_labels[slope_index]

                        # Major Vessels Colored by Fluoroscopy
                        with col1:
                            ca = st.slider("Major Vessels Colored by Fluoroscopy", min_value=0, max_value=3, value=0)

                        # Thalassemia
                        with col2:
                            thal_labels = ["Normal", "Fixed Defect", "Reversible Defect"]
                            thal_index = st.selectbox("Thalassemia", list(range(len(thal_labels))), format_func=lambda x: thal_labels[x])
                            thal = thal_index
                            thal_label = thal_labels[thal_index]

                        # Exercise Induced Angina
                        with col3:
                            exang = 1 if st.checkbox("Exercise Induced Angina") else 0

                        # Fasting Blood Sugar
                        with col1:
                            fbs = 1 if st.checkbox("Fasting Blood Sugar > 120 mg/dL") else 0

                        # Prediction
                        heart_dig = ''
                        if st.button("Heart Test Result"):
                            heart_prediction = heart_model.predict([[age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]])
                            result = heart_prediction[0]

                            if result == 1:
                                heart_dig = "We are really sorry to say, but it seems like you have Heart Disease."
                                image = Image.open("positive.jpg")
                                st.image(image)
                                st.error(f"{name} ({selected_gender}), {heart_dig}")
                            else:
                                heart_dig = "Congratulations, you don't have Heart Disease."
                                image = Image.open("negative.jpg")
                                st.image(image)
                                st.success(f"{name} ({selected_gender}), {heart_dig}")

                            # Log inputs with readable labels
                            inputs = {
                                
                                "Age": age,
                                "Sex": selected_gender,
                                "ChestPainType": cp_label,
                                "RestingBP": trestbps,
                                "Cholesterol": chol,
                                "FastingBS": "Yes" if fbs == 1 else "No",
                                "RestingECG": restecg_label,
                                "MaxHR": thalach,
                                "ExerciseAngina": "Yes" if exang == 1 else "No",
                                "Oldpeak": oldpeak,
                                "Slope": slope_label,
                                "CA": ca,
                                "Thal": thal_label
                            }

                            log_heart_disease_result(name, result, inputs)
                            pdf_bytes = generate_diabetes_certificate(name, heart_dig, inputs)
                            st.download_button(label="📄 Download Certificate", data=pdf_bytes, file_name="Heart_Certificate.pdf", mime="application/pdf")







            elif selected == 'Parkinson Prediction':
                        st.title("Parkison prediction")
                        parkinson_model = joblib.load("models/parkinsons_model.sav")
            # parameters
            #    name	MDVP:Fo(Hz)	MDVP:Fhi(Hz)	MDVP:Flo(Hz)	MDVP:Jitter(%)	MDVP:Jitter(Abs)	MDVP:RAP	MDVP:PPQ	Jitter:DDP	MDVP:Shimmer	MDVP:Shimmer(dB)	Shimmer:APQ3	Shimmer:APQ5	MDVP:APQ	Shimmer:DDA	NHR	HNR	status	RPDE	DFA	spread1	spread2	D2	PPE
            # change the variables according to the dataset used in the model
                        name = st.text_input("Name:")
                        col1, col2, col3 = st.columns(3)
                        with col1:

                            age =st.slider("Enter your age", 1, 100, 25)

                        with col2:
                            gender_labels = ["Male", "Female"]
                            gender_index = st.selectbox("Gender", list(range(len(gender_labels))), format_func=lambda x: gender_labels[x])
                            sex = 1 if gender_labels[gender_index] == "Male" else 0
                            selected_gender = gender_labels[gender_index]    

                        with col1:
                            MDVP = st.slider("MDVP:Fo (Hz)", min_value=60.0, max_value=300.0, value=150.0, step=1.0)

                        with col2:
                            MDVPFIZ = st.slider("MDVP:Fhi (Hz)", min_value=100.0, max_value=600.0, value=250.0, step=1.0)

                        with col3:
                            MDVPFLO = st.slider("MDVP:Flo (Hz)", min_value=60.0, max_value=300.0, value=100.0, step=1.0)

                        with col1:
                            MDVPJITTER = st.slider("MDVP:Jitter (%)", min_value=0.0, max_value=1.0, value=0.01, step=0.001)

                        with col2:
                            MDVPJitterAbs = st.slider("MDVP:Jitter (Abs)", min_value=0.0, max_value=0.02, value=0.005, step=0.0001)

                        with col3:
                            MDVPRAP = st.slider("MDVP:RAP", min_value=0.0, max_value=0.05, value=0.01, step=0.001)

                        with col2:
                            MDVPPPQ = st.slider("MDVP:PPQ", min_value=0.0, max_value=0.05, value=0.01, step=0.001)

                        with col3:
                            JitterDDP = st.slider("Jitter:DDP", min_value=0.0, max_value=0.1, value=0.02, step=0.001)

                        with col1:
                            MDVPShimmer = st.slider("MDVP:Shimmer", min_value=0.0, max_value=0.2, value=0.05, step=0.001)

                        with col2:
                            MDVPShimmer_dB = st.slider("MDVP:Shimmer (dB)", min_value=0.0, max_value=3.0, value=1.0, step=0.1)

                        with col3:
                            Shimmer_APQ3 = st.slider("Shimmer:APQ3", min_value=0.0, max_value=0.1, value=0.02, step=0.001)

                        with col1:
                            ShimmerAPQ5 = st.slider("Shimmer:APQ5", min_value=0.0, max_value=0.1, value=0.02, step=0.001)

                        with col2:
                            MDVP_APQ = st.slider("MDVP:APQ", min_value=0.0, max_value=0.2, value=0.05, step=0.001)

                        with col3:
                            ShimmerDDA = st.slider("Shimmer:DDA", min_value=0.0, max_value=0.2, value=0.05, step=0.001)

                        with col1:
                            NHR = st.slider("NHR", min_value=0.0, max_value=0.5, value=0.05, step=0.01)

                        with col2:
                            HNR = st.slider("HNR", min_value=0.0, max_value=50.0, value=20.0, step=1.0)

                        with col2:
                            RPDE = st.slider("RPDE", min_value=0.0, max_value=1.0, value=0.5, step=0.01)

                        with col3:
                            DFA = st.slider("DFA", min_value=0.0, max_value=1.0, value=0.7, step=0.01)

                        with col1:
                            spread1 = st.slider("Spread1", min_value=-10.0, max_value=0.0, value=-4.0, step=0.1)

                        with col1:
                            spread2 = st.slider("Spread2", min_value=0.0, max_value=1.0, value=0.3, step=0.01)

                        with col3:
                            D2 = st.slider("D2", min_value=1.0, max_value=3.0, value=2.0, step=0.01)

                        with col1:
                            PPE = st.slider("PPE", min_value=0.0, max_value=1.0, value=0.3, step=0.01)

                # code for prediction
                        parkinson_dig = ''
                
                # button
                        if st.button("Parkinson test result"):
                            parkinson_prediction=[[]]
                    # change the parameters according to the model
                            parkinson_prediction = parkinson_model.predict([[MDVP, MDVPFIZ, MDVPFLO, MDVPJITTER, MDVPJitterAbs, MDVPRAP, MDVPPPQ, JitterDDP, MDVPShimmer,MDVPShimmer_dB, Shimmer_APQ3, ShimmerAPQ5, MDVP_APQ, ShimmerDDA, NHR, HNR,  RPDE, DFA, spread1, spread2, D2, PPE]])

                            if parkinson_prediction[0] == 1:
                                parkinson_dig = 'we are really sorry to say but it seems like you have Parkinson disease'
                                image = Image.open('positive.jpg')
                                st.image(image, caption='')
                            else:
                                parkinson_dig = "Congratulation , You don't have Parkinson disease"
                                image = Image.open('negative.jpg')
                                st.image(image, caption='')
                            st.success(name+' , ' + parkinson_dig)
                            inputs = {
                            "Age": age,
                            "Sex": selected_gender,
                            "MDVP:Fo(Hz)": MDVP,
                            "MDVP:Fhi(Hz)": MDVPFIZ,
                            "MDVP:Flo(Hz)": MDVPFLO,
                            "MDVP:Jitter(%)": MDVPJITTER,
                            "MDVP:Jitter(Abs)": MDVPJitterAbs,
                            "MDVP:RAP": MDVPRAP,
                            "MDVP:PPQ": MDVPPPQ,
                            "Jitter:DDP": JitterDDP,
                            "MDVP:Shimmer": MDVPShimmer,
                            "MDVP:Shimmer(dB)": MDVPShimmer_dB,
                            "Shimmer:APQ3": Shimmer_APQ3,
                            "Shimmer:APQ5": ShimmerAPQ5,
                            "MDVP:APQ": MDVP_APQ,
                            "Shimmer:DDA": ShimmerDDA,
                            "NHR": NHR,
                            "HNR": HNR,
                            "RPDE": RPDE,
                            "DFA": DFA,
                            "spread1": spread1,
                            "spread2": spread2,
                            "D2": D2,
                            "PPE": PPE
                            }
                            log_parkison_result(name, parkinson_prediction[0], inputs)
                            pdf_bytes = generate_diabetes_certificate(name, parkinson_dig, inputs)
                            st.download_button(label="📄 Download Certificate", data=pdf_bytes, file_name="Parksion_certificate.pdf", mime="application/pdf")




            # Lung Cancer prediction page
            elif selected == 'Lung Cancer Prediction':
                        st.title("Lung Cancer Prediction")
                        lung_cancer_model = joblib.load('models/lung_cancer_model.sav')
                                        # Load the dataset
                        lung_cancer_data = pd.read_csv('data/lung_cancer.csv')

                        # Convert 'M' to 0 and 'F' to 1 in the 'GENDER' column
                        lung_cancer_data['GENDER'] = lung_cancer_data['GENDER'].map({'M': 'Male', 'F': 'Female'})

                # Columns
                # No inputs from the user
                        name = st.text_input("Name:")
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            gender = st.selectbox("Gender:", lung_cancer_data['GENDER'].unique())
                        with col2:
                            age = st.slider("Enter your age", 1, 100, 25)
                        with col3:
                            smoking = st.selectbox("Smoking:", ['NO', 'YES'])
                        with col1:
                            yellow_fingers = st.selectbox("Yellow Fingers:", ['NO', 'YES'])

                        with col2:
                            anxiety = st.selectbox("Anxiety:", ['NO', 'YES'])
                        with col3:
                            peer_pressure = st.selectbox("Peer Pressure:", ['NO', 'YES'])
                        with col1:
                            chronic_disease = st.selectbox("Chronic Disease:", ['NO', 'YES'])

                        with col2:
                            fatigue = st.selectbox("Fatigue:", ['NO', 'YES'])
                        with col3:
                            allergy = st.selectbox("Allergy:", ['NO', 'YES'])
                        with col1:
                            wheezing = st.selectbox("Wheezing:", ['NO', 'YES'])

                        with col2:
                            alcohol_consuming = st.selectbox("Alcohol Consuming:", ['NO', 'YES'])
                        with col3:
                            coughing = st.selectbox("Coughing:", ['NO', 'YES'])
                        with col1:
                            shortness_of_breath = st.selectbox("Shortness of Breath:", ['NO', 'YES'])

                        with col2:
                            swallowing_difficulty = st.selectbox("Swallowing Difficulty:", ['NO', 'YES'])
                        with col3:
                            chest_pain = st.selectbox("Chest Pain:", ['NO', 'YES'])

                # Code for prediction
                        cancer_result = ''

                # Button
                        if st.button("Predict Lung Cancer"):
                    # Create a DataFrame with user inputs
                            user_data = pd.DataFrame({
                                'GENDER': [gender],
                                'AGE': [age],
                                'SMOKING': [smoking],
                                'YELLOW_FINGERS': [yellow_fingers],
                                'ANXIETY': [anxiety],
                                'PEER_PRESSURE': [peer_pressure],
                                'CHRONICDISEASE': [chronic_disease],
                                'FATIGUE': [fatigue],
                                'ALLERGY': [allergy],
                                'WHEEZING': [wheezing],
                                'ALCOHOLCONSUMING': [alcohol_consuming],
                                'COUGHING': [coughing],
                                'SHORTNESSOFBREATH': [shortness_of_breath],
                                'SWALLOWINGDIFFICULTY': [swallowing_difficulty],
                                'CHESTPAIN': [chest_pain]
                            })

                    # Map string values to numeric
                            user_data.replace({'NO': 1, 'YES': 2}, inplace=True)
                    # Strip leading and trailing whitespaces from column names
                            user_data.columns = user_data.columns.str.strip()

                    # Convert columns to numeric where necessary
                            numeric_columns = ['AGE', 'FATIGUE', 'ALLERGY', 'ALCOHOLCONSUMING', 'COUGHING', 'SHORTNESSOFBREATH']
                            user_data[numeric_columns] = user_data[numeric_columns].apply(pd.to_numeric, errors='coerce')

                    # Perform prediction
                            cancer_prediction = lung_cancer_model.predict(user_data)

                    # Display result
                            if cancer_prediction[0] == 'YES':
                                cancer_result = "The model predicts that there is a risk of Lung Cancer."
                                image = Image.open('positive.jpg')
                                st.image(image, caption='')
                            else:
                                cancer_result = "The model predicts no significant risk of Lung Cancer."
                                image = Image.open('negative.jpg')
                                st.image(image, caption='')
            
                            st.success(name + ', ' + cancer_result)
                            inputs = {
                                'GENDER': gender,
                                'AGE': age,
                                'SMOKING': smoking,
                                'YELLOW_FINGERS': yellow_fingers,
                                'ANXIETY': anxiety,
                                'PEER_PRESSURE': peer_pressure,
                                'CHRONICDISEASE': chronic_disease,
                                'FATIGUE': fatigue,
                                'ALLERGY': allergy,
                                'WHEEZING': wheezing,
                                'ALCOHOLCONSUMING': alcohol_consuming,
                                'COUGHING': coughing,
                                'SHORTNESSOFBREATH': shortness_of_breath,
                                'SWALLOWINGDIFFICULTY': swallowing_difficulty,
                                'CHESTPAIN': chest_pain
                            }
                            log_lung_cancer_result(name, cancer_prediction[0], inputs)
                            pdf_bytes = generate_diabetes_certificate(name, cancer_result, inputs)
                            st.download_button(label="📄 Download Certificate", data=pdf_bytes, file_name="Lung_Cancer_certificate.pdf", mime="application/pdf")



            # Liver prediction page
            elif selected == 'Liver Disease Prediction':
                        st.title("Liver Disease Prediction")
                        liver_model = joblib.load('models/liver_model.sav')

                        name = st.text_input("Name:")
                        col1, col2, col3 = st.columns(3)

                        # Gender
                        with col1:
                            gender_labels = ["Male", "Female"]
                            gender_index = st.selectbox("Gender", list(range(len(gender_labels))), format_func=lambda x: gender_labels[x])
                            Sex = 0 if gender_labels[gender_index] == "Male" else 1
                            selected_gender = gender_labels[gender_index]

                        # Age
                        with col2:
                            age = st.slider("Age", min_value=1, max_value=100, value=45)

                        # Total Bilirubin
                        with col3:
                            Total_Bilirubin = st.slider("Total Bilirubin (mg/dL)", min_value=0.0, max_value=10.0, value=1.0, step=0.1)

                        # Direct Bilirubin
                        with col1:
                            Direct_Bilirubin = st.slider("Direct Bilirubin (mg/dL)", min_value=0.0, max_value=5.0, value=0.5, step=0.1)

                        # Alkaline Phosphotase
                        with col2:
                            Alkaline_Phosphotase = st.slider("Alkaline Phosphotase (IU/L)", min_value=50, max_value=300, value=120)

                        # Alamine Aminotransferase (ALT)
                        with col3:
                            Alamine_Aminotransferase = st.slider("Alamine Aminotransferase (ALT)", min_value=10, max_value=200, value=45)

                        # Aspartate Aminotransferase (AST)
                        with col1:
                            Aspartate_Aminotransferase = st.slider("Aspartate Aminotransferase (AST)", min_value=10, max_value=200, value=50)

                        # Total Proteins
                        with col2:
                            Total_Protiens = st.slider("Total Proteins (g/dL)", min_value=4.0, max_value=10.0, value=7.0, step=0.1)

                        # Albumin
                        with col3:
                            Albumin = st.slider("Albumin (g/dL)", min_value=2.0, max_value=6.0, value=4.0, step=0.1)

                        # Albumin/Globulin Ratio
                        with col1:
                            Albumin_and_Globulin_Ratio = st.slider("Albumin/Globulin Ratio", min_value=0.0, max_value=2.5, value=1.0, step=0.1)

                        # Prediction
                        liver_dig = ''
                        if st.button("Liver Test Result"):
                            liver_prediction = liver_model.predict([[Sex, age, Total_Bilirubin, Direct_Bilirubin, Alkaline_Phosphotase,
                                                                    Alamine_Aminotransferase, Aspartate_Aminotransferase,
                                                                    Total_Protiens, Albumin, Albumin_and_Globulin_Ratio]])
                            result = liver_prediction[0]

                            if result == 1:
                                image = Image.open('positive.jpg')
                                st.image(image)
                                liver_dig = "We are really sorry to say, but it seems like you have liver disease."
                                st.error(f"{name} ({selected_gender}), {liver_dig}")
                            else:
                                image = Image.open('negative.jpg')
                                st.image(image)
                                liver_dig = "Congratulations, you don't have liver disease."
                                st.success(f"{name} ({selected_gender}), {liver_dig}")

                            # Log inputs with readable labels
                            inputs = {
                                "Sex": selected_gender,
                                "Age": age,
                                "Total_Bilirubin": Total_Bilirubin,
                                "Direct_Bilirubin": Direct_Bilirubin,
                                "Alkaline_Phosphotase": Alkaline_Phosphotase,
                                "Alamine_Aminotransferase": Alamine_Aminotransferase,
                                "Aspartate_Aminotransferase": Aspartate_Aminotransferase,
                                "Total_Protiens": Total_Protiens,
                                "Albumin": Albumin,
                                "Albumin_and_Globulin_Ratio": Albumin_and_Globulin_Ratio
                            }

                            log_liver_result(name, result, inputs)
                            pdf_bytes = generate_diabetes_certificate(name, liver_dig, inputs)
                            st.download_button(label="📄 Download Certificate", data=pdf_bytes, file_name="Liver_Diabetes_Certificate.pdf", mime="application/pdf")

            # Chronic Kidney Disease Prediction Page
                

            elif selected == 'Chronic Kidney Prediction':
                        st.title(" Chronic Kidney Disease Prediction")
                        chronic_disease_model = joblib.load('models/chronic_model.sav')

                        name = st.text_input("Name:")

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            AGE = st.slider("Age", 1, 100, 25)
                        with col2:
                            BP = st.slider("Blood Pressure", 50, 200, 120)
                        with col3:
                            SPECIFIC_GRAVITY= st.slider("Specific Gravity", 1.0, 1.05, 1.02)

                        with col1:
                            ALBUMIN = st.slider("Albumin", 0, 5, 0)
                        with col2:
                            SUGAR = st.slider("Sugar", 0, 5, 0)

                        # Categorical inputs (store original and encoded)
                        original_inputs = {}
                        encoded_inputs = {}

                        def dual_input(label, options, encoding_map, col):
                            with col:
                                val = st.selectbox(label, options)
                                original_inputs[label] = val
                                encoded_inputs[label] = encoding_map[val]

                        dual_input("Red Blood Cells", ["Normal", "Abnormal"], {"Normal": 1, "Abnormal": 0}, col3)
                        dual_input("Pus Cells", ["Normal", "Abnormal"], {"Normal": 1, "Abnormal": 0}, col1)
                        dual_input("Pus Cell Clumps", ["Present", "Not Present"], {"Present": 1, "Not Present": 0}, col2)
                        dual_input("Bacteria", ["Present", "Not Present"], {"Present": 1, "Not Present": 0}, col3)

                        with col1:
                            BLOOD_GLUCOSE_RANDOM = st.slider("Blood Glucose Random", 50, 200, 120)
                        with col2:
                            BLOOD_UREA = st.slider("Blood Urea", 10, 200, 60)
                        with col3:
                            SERIUM_CERATININE = st.slider("Serum Creatinine", 0, 10, 3)

                        with col1:
                            SODIUM = st.slider("Sodium", 100, 200, 140)
                        with col2:
                            POTASSIUM = st.slider("Potassium", 2, 7, 4)
                        with col3:
                            HEMOGLOBIN = st.slider("Hemoglobin", 3, 17, 12)

                        with col1:
                            PACKED_CELL_VOLUME = st.slider("Packed Cell Volume", 20, 60, 40)
                        with col2:
                            WHITE_BLOOD_CELL_COUNT = st.slider("White Blood Cell Count", 2000, 20000, 10000)
                        with col3:
                            RED_BLOOD_CELL_COUNT = st.slider("Red Blood Cell Count", 2, 8, 4)

                        dual_input("Hypertension", ["Yes", "No"], {"Yes": 1, "No": 0}, col1)
                        dual_input("Diabetes Mellitus", ["Yes", "No"], {"Yes": 1, "No": 0}, col2)
                        dual_input("Coronary Artery Disease", ["Yes", "No"], {"Yes": 1, "No": 0}, col3)
                        dual_input("Appetite", ["Good", "Poor"], {"Good": 1, "Poor": 0}, col1)
                        dual_input("Pedal Edema", ["Yes", "No"], {"Yes": 1, "No": 0}, col2)
                        dual_input("Anemia", ["Yes", "No"], {"Yes": 1, "No": 0}, col3)

                        if st.button(" Predict Chronic Kidney Disease"):
                            user_input = pd.DataFrame({
                                'age': [AGE], 'bp': [BP], 'sg': [SPECIFIC_GRAVITY], 'al': [ALBUMIN], 'su': [SUGAR],
                                'rbc': [encoded_inputs["Red Blood Cells"]],
                                'pc': [encoded_inputs["Pus Cells"]],
                                'pcc': [encoded_inputs["Pus Cell Clumps"]],
                                'ba': [encoded_inputs["Bacteria"]],
                                'bgr': [BLOOD_GLUCOSE_RANDOM], 'bu': [BLOOD_UREA], 'sc': [SERIUM_CERATININE], 'sod': [SODIUM], 'pot': [POTASSIUM],
                                'hemo': [HEMOGLOBIN], 'pcv': [PACKED_CELL_VOLUME], 'wc': [WHITE_BLOOD_CELL_COUNT], 'rc': [RED_BLOOD_CELL_COUNT],
                                'htn': [encoded_inputs["Hypertension"]],
                                'dm': [encoded_inputs["Diabetes Mellitus"]],
                                'cad': [encoded_inputs["Coronary Artery Disease"]],
                                'appet': [encoded_inputs["Appetite"]],
                                'pe': [encoded_inputs["Pedal Edema"]],
                                'ane': [encoded_inputs["Anemia"]]
                            })

                            with st.spinner("Analyzing your health data..."):
                                kidney_prediction = chronic_disease_model.predict(user_input)

                            if kidney_prediction[0] == 1:
                                image = Image.open('positive.jpg')
                                st.image(image, caption='')
                                kidney_prediction_dig = "we are really sorry to say but it seems like you have kidney disease."
                            else:
                                image = Image.open('negative.jpg')
                                st.image(image, caption='')
                                kidney_prediction_dig = "Congratulations, you don't have kidney disease."

                            st.success(name + ', ' + kidney_prediction_dig)

                            # Merge all inputs for logging
                            inputs = {
                                'AGE': AGE, 'BP': BP, 'SPECIFIC_GRAVITY': SPECIFIC_GRAVITY, 'ALBUMIN': ALBUMIN, 'SUGAR': SUGAR,
                                'BLOOD_GLUCOSE_RANDOM': BLOOD_GLUCOSE_RANDOM, 'BLOOD_UREA': BLOOD_UREA, 'SERIUM_CERATININE': SERIUM_CERATININE, 'SODIUM': SODIUM, 'POTASSIUM': POTASSIUM,
                                'HEMOGLOBIN': HEMOGLOBIN, 'PACKED_CELL_VOLUME': PACKED_CELL_VOLUME, 'WHITE_BLOOD_CELL_COUNT': WHITE_BLOOD_CELL_COUNT, 'RED_BLOOD_CELL_COUNT': RED_BLOOD_CELL_COUNT
                            }
                            inputs.update(original_inputs)  # Add original categorical labels

                            log_chronic_kidney_result(name, kidney_prediction[0], inputs)
                            pdf_bytes = generate_diabetes_certificate(name, kidney_prediction_dig, inputs)
                            st.download_button(label="📄 Download Certificate", data=pdf_bytes, file_name="Kidney_Disease_Certificate.pdf", mime="application/pdf")

                          
            elif selected ==labels["doctor_chat"]:
                show_patient_ui(username)
            elif selected == "Doctor Appointment":
                show_app_dashboard(username)



        else:
            st.error("Buy Subscription to access the module.")
            
               

# Example usage
grant_access("bharathraj0")


print(list_access_users())  # ['bharathraj0', 'guest123']
    
load_dotenv()
COURIER_API_KEY = os.getenv("COURIER_API_KEY")



