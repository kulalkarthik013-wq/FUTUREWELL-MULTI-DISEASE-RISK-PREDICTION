import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from streamlit_login_auth_ui.widgets import __login__
from logger import (
    log_diabetes_result, load_diabetes_results,
    log_heart_disease_result, load_heart_disease_results,
    log_parkison_result, load_parkison_results,
    log_liver_result, load_liver_results,
    log_lung_cancer_result, load_lung_cancer_results,
    log_chronic_kidney_result, load_chronic_kidney_results,
    log_login_event_json,load_manual_access_json,save_manual_access_json,save_feedback_json,load_feedback_json,load_auth_json
)
import json
import os
from datetime import datetime
from admin_trans import translations
import base64

from chat_store import (
    authenticate_doctor,
    assign_patient_to_doctor,
    get_conversation,
    save_patient_message,
    save_patient_media,
    save_doctor_reply,
    get_all_patients_for_doctor,
    clear_patient_chat
)
from logger import load_appointments,save_appointments
import streamlit as st
import json
import os

DOCTORS_FILE = r"D:\proj\frontend\data\chat_data.json"
APPOINTMENTS_FILE = r"D:\proj\frontend\appointments.json"

# ------------------ Helpers ------------------
def load_doctors():
    if not os.path.exists(DOCTORS_FILE):
        return []
    with open(DOCTORS_FILE, "r") as f:
        data = json.load(f)
        return data.get("doctors", [])

def load_appointments():
    if not os.path.exists(APPOINTMENTS_FILE):
        return {}
    with open(APPOINTMENTS_FILE, "r") as f:
        return json.load(f)

def save_appointments(data):
    with open(APPOINTMENTS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def authenticate_doctor(username, password):
    doctors = load_doctors()
    for doc in doctors:
        if doc["username"] == username and doc["password"] == password:
            return doc
    return None

# ------------------ Doctor Dashboard ------------------
def show_doc_app(username):
    st.title("Appointment Requests")
    if "doctor_display" not in st.session_state:
        st.session_state["doctor_display"] = None

    # 🔹 Login check
    if not st.session_state.get("doctor_logged_in"):
        st.subheader("Doctor Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            doc = authenticate_doctor(username, password)
            if doc:
                st.session_state["doctor_logged_in"] = True
                st.session_state["doctor_username"] = doc["name"]
                st.session_state["doctor_specialty"] = doc["specialty"]
                st.session_state["doctor_display"] = f"{doc['name']} ({doc['specialty']})"
                st.success(f"Login successful ✅ Welcome {doc['name']} ({doc['specialty']})")
                st.rerun()
            else:
                st.error("Invalid credentials ❌")
        return

    # 🔹 Dashboard after login
    doctor_display = st.session_state["doctor_display"]
    st.markdown(f"## Welcome, {doctor_display}")

    appointments = load_appointments()
    found = False

    col1, col2 = st.columns([20, 2])  # wide left, narrow right
    with col1:
        st.subheader("📋 Your Appointment Requests")
    with col2:
        if st.button(" Logout", key="logout_button"):
            st.session_state["doctor_logged_in"] = False
            st.session_state["doctor_username"] = None
            st.session_state["doctor_specialty"] = None
            st.session_state["doctor_display"] = None
            st.rerun()


    found = False

    for appt_id, appt in appointments.items():
        if appt["doctor"] == doctor_display:
            found = True

            # ✅ Use a container for each appointment card
            with st.container():
                st.markdown(
                    f"""
                    <div style="
                        background-color:#f9f9f9;
                        border:1px solid #ddd;
                        border-radius:10px;
                        padding:15px;
                        margin-bottom:10px;
                    ">
                        <h4 style="margin:0; color:#333;">🆔 {appt_id}</h4>
                        <p style="margin:5px 0;">👤 Patient: <b>{appt['patient']}</b></p>
                        <p style="margin:5px 0;">📅 Date: {appt['date']} | ⏰ Time: {appt['time']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if appt["status"] == "Pending":
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button("✅ Approve", key=f"approve_{appt_id}"):
                            appt["status"] = "Approved"
                            save_appointments(appointments)
                            st.success(f"Appointment {appt_id} approved!")
                            st.rerun()
                    with col2:
                        if st.button("❌ Reject", key=f"reject_{appt_id}"):
                            appt["status"] = "Rejected"
                            save_appointments(appointments)
                            st.warning(f"Appointment {appt_id} rejected.")
                            st.rerun()
                else:
                    if appt["status"] == "Approved":
                        st.markdown(
                            "<div style='background-color:#d4edda; color:#155724; "
                            "padding:8px; border-radius:5px; display:inline-block;'>✔ Approved</div>",
                            unsafe_allow_html=True
                        )
                    elif appt["status"] == "Rejected":
                        st.markdown(
                            "<div style='background-color:#f8d7da; color:#721c24; "
                            "padding:8px; border-radius:5px; display:inline-block;'>✘ Rejected</div>",
                            unsafe_allow_html=True
                        )

    if not found:
        st.info("No appointments assigned to you yet.")

    
# -------------------------------
# Doctor UI
# -------------------------------

def show_doctor_ui(label):
    st.title("👨‍⚕️ Doctor Dashboard")

    if not st.session_state.get("doctor_logged_in"):
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if authenticate_doctor(username, password):
                st.session_state["doctor_logged_in"] = True
                st.session_state["doctor_username"] = username
                st.success("Login successful ✅")
                st.rerun()
            else:
                st.error("Invalid credentials ❌")
        return

    st.markdown(f"## Welcome, {st.session_state['doctor_username']}")



    patients = get_all_patients_for_doctor(st.session_state["doctor_username"])
    if not patients:
        st.info("No patients assigned yet.")
        return

    patient = st.selectbox("Select patient:", patients)
    st.subheader(f"Conversation with {patient}")



    history = get_conversation(patient)

    st.markdown("<div style='background-color:#f9f9f9; padding:15px; border-radius:10px;'>", unsafe_allow_html=True)

    for msg in history:
        who = "👤 Patient" if msg["sender"] == "patient" else f"🩺 Doctor ({msg['doctor']})"
        align = "right" if msg["sender"] == "patient" else "left"
        bg_color = "#DCF8C6" if msg["sender"] == "patient" else "#E6E6FA"

        if msg.get("message"):
            st.markdown(
                f"""
                <div style='text-align:{align}; margin:10px;'>
                    <div style='background-color:{bg_color}; padding:10px 15px; border-radius:15px; 
                                display:inline-block; max-width:70%; box-shadow:0 1px 3px rgba(0,0,0,0.1);'>
                        <b>{who}</b><br>{msg['message']}
                    </div><br>
                    <small style='color:gray;'>{msg['timestamp']}</small>
                </div>
                """,
                unsafe_allow_html=True
            )

        elif msg.get("media"):
            if msg["media"].endswith((".png", ".jpg", ".jpeg")):
                # Inline image bubble
                st.markdown(
                    f"""
                    <div style='text-align:{align}; margin:10px;'>
                        <div style='background-color:{bg_color}; padding:10px; border-radius:15px; 
                                    display:inline-block; max-width:70%;'>
                            <b>{who}</b><br>
                        </div><br>
                        <img src="file:///{msg['media']}" width="250"><br>
                        <small style='color:gray;'>{msg['timestamp']}</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            elif msg["media"].endswith(".pdf"):
                # Inline PDF preview
                with open(msg["media"], "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                pdf_display = f"""
                    <div style='text-align:{align}; margin:10px;'>
                        <div style='background-color:{bg_color}; padding:10px; border-radius:15px; 
                                    display:inline-block; max-width:70%;'>
                            <b>{who}</b><br>
                        </div><br>
                        <iframe src="data:application/pdf;base64,{base64_pdf}" width="600" height="400"></iframe><br>
                        <small style='color:gray;'>{msg['timestamp']}</small>
                    </div>
                """
                st.markdown(pdf_display, unsafe_allow_html=True)

            else:
                # Generic file link bubble
                st.markdown(
                    f"""
                    <div style='text-align:{align}; margin:10px;'>
                        <div style='background-color:{bg_color}; padding:10px 15px; border-radius:15px; 
                                    display:inline-block; max-width:70%;'>
                            <b>{who}</b><br>📎 <a href="{msg['media']}" target="_blank">View File</a>
                        </div><br>
                        <small style='color:gray;'>{msg['timestamp']}</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    reply = st.text_input("Reply to patient:")

    # Two columns: one for reply, one for logout
    reply_col, logout_col = st.columns([3, 1])

    with reply_col:
        if st.button("Send Reply"):
            save_doctor_reply(st.session_state["doctor_username"], patient, reply)
            st.success("Reply sent ✅")
            st.rerun()

    with logout_col:
        if st.button("Clear Chat"):
            clear_patient_chat(patient)
            st.success("Chat history cleared ✅")
            st.rerun()


def show_doc_dashboard(username, role="Doctor"):
    # 🔹 Role bar at the top

    with st.sidebar:
        lang_choice = st.sidebar.selectbox("Select Language", ["English", "Kannada", "Hindi"])
        labels = translations[lang_choice]
        st.markdown(f"""
            <div style='background-color:#ff8800; padding:10px; border-radius:8px; 
                        text-align:center; color:white; font-size:18px; font-weight:bold;'>
                <span style="filter: invert(1);">👤</span>
                Logged in as: {username} | Role: {role}
            </div>
            """, unsafe_allow_html=True)
        selected = option_menu(
            labels["doctor_dashboard"],
            [
                labels["home"],
                labels["test_dashboards"],
                labels["patient_chat"],
                "Appointment Requests"
            ],

             icons=[
                "house",          # Home
                "bar-chart-line", # Dashboards
                "chat-dots",
                "calendar-check"   # User Profile
            ],
            default_index=0,
            orientation="vertical"
    )

    # Dashboards
    if selected == labels["test_dashboards"]:
        st.title(labels["test_dashboards"])

        # Custom CSS for blue-white tab design
        st.markdown("""
            <style>
            div[data-testid="stTabs"] button {
                font-weight: bold;
                color: #0072ff;
                background: rgba(255,255,255,0.6);
                border: 2px solid #0072ff;
                border-radius: 10px;
                margin: 0px;
                padding: 8px 30px;
            }
            div[data-testid="stTabs"] button:hover {
                background: rgba(255,255,255,0.8);
                color: #0056cc;
            }
            div[data-testid="stTabs"] button:focus {
                background: #0072ff;
                color: white;
            }
            </style>
        """, unsafe_allow_html=True)

        # Create tabs with translated labels
        tabs = st.tabs([
            labels["diabetes_dashboard"],
            labels["heart_dashboard"],
            labels["parkinson_dashboard"],
            labels["liver_dashboard"],
            labels["lung_dashboard"],
            labels["kidney_dashboard"]
        ])

        # Example placeholders
        def render_dashboard(df, title):
            st.subheader(title)
            if not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.info(labels.get("no_results", "No test results found yet."))

        # Render each tab with translated titles
        with tabs[0]:
            render_dashboard(load_diabetes_results(), labels.get("diabetes_history", "Diabetes Test History"))

        with tabs[1]:
            render_dashboard(load_heart_disease_results(), labels.get("heart_history", "Heart Disease Test History"))

        with tabs[2]:
            render_dashboard(load_parkison_results(), labels.get("parkinson_history", "Parkinson Test History"))

        with tabs[3]:
            render_dashboard(load_liver_results(), labels.get("liver_history", "Liver Disease Test History"))

        with tabs[4]:
            render_dashboard(load_lung_cancer_results(), labels.get("lung_history", "Lung Cancer Test History"))

        with tabs[5]:
            render_dashboard(load_chronic_kidney_results(), labels.get("kidney_history", "Chronic Kidney Test History"))

                            
    if selected == labels["patient_chat"]:
                    show_doctor_ui(labels)
    if selected == "Appointment Requests":
            show_doc_app(username)  # or a filtered appointment view
                

    if selected == "Home":
        st.markdown("<h1 style='color:#000000;'>Doctor Home</h1>", unsafe_allow_html=True)

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
                .card {
                    background: rgba(255, 255, 255, 0.15);
                    backdrop-filter: blur(10px);
                    border-radius: 12px;
                    padding: 1.5rem;
                    margin-top: 1rem;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                    border: 1px solid rgba(255,255,255,0.3);
                }
                .card-title {
                    font-size: 1.4rem;
                    font-weight: 700;
                    background: linear-gradient(90deg, #ff7eb3, #ff758c);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    margin-bottom: 0.8rem;
                }
                .card-text {
                    font-size: 1rem;
                    color: #000000;
                    line-height: 1.6;
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
        st.markdown("<h2 class='gradient-text section'>How It Works</h2>", unsafe_allow_html=True)
        steps = [
            "Login securely with your doctor credentials",
            "View and manage appointment requests",
            "Approve or reject patient bookings",
            "Access patient chat and communication tools"
        ]
        for i, step in enumerate(steps, 1):
            st.markdown(f"<div class='step'>{i}) <strong>{step}</strong></div>", unsafe_allow_html=True)

        # Appointment Section
        st.markdown("""
            <div class="card">
                <div class="card-title">Appointments</div>
                <div class="card-text">Manage patient appointment requests, approve or reject them, and view schedules.</div>
            </div>
        """, unsafe_allow_html=True)

        # 🔹 About Section
        st.markdown("<h2 class='gradient-text section'>About</h2>", unsafe_allow_html=True)
        st.markdown("""
            <div class="card">
                <div class="card-title">About This Dashboard</div>
                <div class="card-text">
                    The Doctor Dashboard is designed to simplify hospital workflows. 
                    Doctors can securely log in, manage appointments, and communicate with patients through integrated chat. 
                    This platform ensures efficiency, transparency, and trust in patient care.
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Privacy Section
        st.markdown("<h2 class='gradient-text section'>Privacy</h2>", unsafe_allow_html=True)
        st.success("All patient data is handled securely and confidentially.")

        # FAQ Section
        st.markdown("<h2 class='gradient-text section'>FAQ</h2>", unsafe_allow_html=True)
        with st.expander("Common Questions"):
            faq = {
                "How do I approve an appointment?": "Go to Appointment Requests and click Approve.",
                "Can I reject a booking?": "Yes, use the Reject button in Appointment Requests.",
                "How does patient chat work?": "You can communicate with patients directly through the chat module."
            }
            for q, a in faq.items():
                st.markdown(f"**{q}**")
                st.write(a)

        # Disclaimer
        st.markdown("<h2 class='gradient-text section'>Disclaimer</h2>", unsafe_allow_html=True)
        st.info("This dashboard is for authorized doctors only. Unauthorized access is prohibited.")

        # Footer
        st.markdown("<div class='footer'>Doctor Dashboard © 2025</div>", unsafe_allow_html=True)