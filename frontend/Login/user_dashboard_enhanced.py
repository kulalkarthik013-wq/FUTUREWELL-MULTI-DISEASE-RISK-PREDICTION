# Enhanced User Dashboard Features
import streamlit as st
import json
import os
from datetime import datetime
import base64
from logger import load_auth_json, load_appointments, save_appointments
from chat_store import get_conversation, save_patient_message, save_patient_media

# ==================== PROFILE MANAGEMENT ====================
def show_enhanced_profile(username):
    st.markdown("""<style>
    .profile-card{background:rgba(255,255,255,0.9);backdrop-filter:blur(10px);padding:25px;border-radius:15px;margin:15px 0;box-shadow:0 8px 20px rgba(0,0,0,0.15)}
    .status-active{background:#10b981;color:white;padding:5px 15px;border-radius:20px;font-weight:bold}
    .status-suspended{background:#ef4444;color:white;padding:5px 15px;border-radius:20px;font-weight:bold}
    </style>""", unsafe_allow_html=True)
    
    st.markdown("<h1 style='color:#0072ff'>👤 My Profile</h1>", unsafe_allow_html=True)
    
    auth_data = load_auth_json()
    user_info = next((u for u in auth_data if u["username"] == username), None)
    
    if user_info:
        try:
            with open("user_status.json", "r") as f:
                user_status = json.load(f)
        except:
            user_status = {}
        
        try:
            with open("subscriptions.json", "r") as f:
                subs = json.load(f)
        except:
            subs = {}
        
        status = user_status.get(username, {}).get("status", "Active")
        status_class = "status-active" if status == "Active" else "status-suspended"
        
        st.markdown(f"<div class='profile-card'><h2>{user_info['name']}</h2><span class='{status_class}'>{status}</span></div>", unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["📝 Edit Profile", "🔐 Change Password", "💳 Subscription"])
        
        with tab1:
            st.subheader("Edit Your Information")
            new_name = st.text_input("Name", value=user_info.get("name", ""))
            new_email = st.text_input("Email", value=user_info.get("email", ""))
            new_phone = st.text_input("Phone", value=user_info.get("phone", ""))
            
            uploaded_pic = st.file_uploader("Upload Profile Picture", type=["png", "jpg", "jpeg"])
            if uploaded_pic:
                st.image(uploaded_pic, width=150)
                img_data = base64.b64encode(uploaded_pic.read()).decode()
                user_info["profile_pic"] = img_data
            
            if st.button("💾 Save Changes", use_container_width=True):
                for u in auth_data:
                    if u["username"] == username:
                        u["name"] = new_name
                        u["email"] = new_email
                        u["phone"] = new_phone
                        if uploaded_pic:
                            u["profile_pic"] = img_data
                with open("_secret_auth_.json", "w") as f:
                    json.dump(auth_data, f, indent=4)
                st.success("✅ Profile updated!")
                st.rerun()
        
        with tab2:
            st.subheader("Change Password")
            current_pwd = st.text_input("Current Password", type="password")
            new_pwd = st.text_input("New Password", type="password")
            confirm_pwd = st.text_input("Confirm New Password", type="password")
            
            if st.button("🔄 Update Password", use_container_width=True):
                if new_pwd == confirm_pwd and new_pwd:
                    if current_pwd == user_info.get("password"):
                        for u in auth_data:
                            if u["username"] == username:
                                u["password"] = new_pwd
                        with open("_secret_auth_.json", "w") as f:
                            json.dump(auth_data, f, indent=4)
                        st.success("✅ Password updated!")
                    else:
                        st.error("❌ Current password incorrect")
                else:
                    st.error("❌ Passwords don't match")
        
        with tab3:
            st.subheader("Subscription Status")
            if username in subs:
                sub = subs[username]
                st.metric("💰 Amount Paid", f"${sub.get('amount', 0)}")
                st.metric("📅 Expiry Date", sub.get('expiry', 'N/A'))
                st.metric("🔄 Auto-Renew", "Yes" if sub.get('auto_renew') else "No")
                if sub.get('active'):
                    st.success("✅ Active Subscription")
                else:
                    st.error("❌ Subscription Expired")
            else:
                st.info("No active subscription")

# ==================== APPOINTMENT BOOKING ====================
def show_appointment_booking(username):
    st.markdown("<h1 style='color:#0072ff'>📅 My Appointments</h1>", unsafe_allow_html=True)
    
    appointments = load_appointments()
    user_appointments = {k: v for k, v in appointments.items() if v.get('patient') == username}
    
    tab1, tab2 = st.tabs(["📋 My Appointments", "➕ Book New"])
    
    with tab1:
        if user_appointments:
            for appt_id, appt in user_appointments.items():
                status_color = "#10b981" if appt['status'] == 'Confirmed' else "#f59e0b" if appt['status'] == 'Pending' else "#ef4444"
                st.markdown(f"""<div style='background:rgba(255,255,255,0.9);padding:20px;border-radius:15px;margin:10px 0;border-left:5px solid {status_color}'>
                <h3>🩺 Dr. {appt['doctor']}</h3>
                <p>📅 {appt['date']} | 🕒 {appt['time']}</p>
                <p>Status: <b>{appt['status']}</b></p>
                </div>""", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("❌ Cancel", key=f"cancel_{appt_id}"):
                        appointments[appt_id]['status'] = 'Cancelled'
                        save_appointments(appointments)
                        st.success("Appointment cancelled")
                        st.rerun()
                with col2:
                    new_date = st.date_input("Reschedule", key=f"date_{appt_id}")
                    if st.button("🔄 Reschedule", key=f"resched_{appt_id}"):
                        appointments[appt_id]['date'] = str(new_date)
                        save_appointments(appointments)
                        st.success("Appointment rescheduled")
                        st.rerun()
        else:
            st.info("No appointments yet")
    
    with tab2:
        st.subheader("Book New Appointment")
        doctors = ["Dr. Smith", "Dr. Patel", "Dr. Kumar"]
        doctor = st.selectbox("Select Doctor", doctors)
        date = st.date_input("Select Date")
        time = st.time_input("Select Time")
        
        if st.button("📅 Book Appointment", use_container_width=True):
            import uuid
            appt_id = f"APT-{uuid.uuid4().hex[:8].upper()}"
            appointments[appt_id] = {
                "appointment_id": appt_id,
                "patient": username,
                "doctor": doctor,
                "date": str(date),
                "time": str(time),
                "status": "Pending",
                "fee": 50
            }
            save_appointments(appointments)
            st.success("✅ Appointment booked!")
            st.rerun()

# ==================== DOCTOR CHAT ====================
def show_modern_chat(username):
    st.markdown("""<style>
    .chat-container{background:linear-gradient(135deg,#667eea,#764ba2);padding:25px;border-radius:20px;box-shadow:0 10px 30px rgba(0,0,0,0.3)}
    .chat-window{background:#fff;border-radius:15px;padding:20px;max-height:500px;overflow-y:auto;box-shadow:inset 0 2px 10px rgba(0,0,0,0.05)}
    .msg-patient{background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:15px 20px;border-radius:20px 20px 5px 20px;margin:10px 0;max-width:70%;float:right;clear:both;box-shadow:0 4px 10px rgba(102,126,234,0.3)}
    .msg-doctor{background:linear-gradient(135deg,#f093fb,#f5576c);color:white;padding:15px 20px;border-radius:20px 20px 20px 5px;margin:10px 0;max-width:70%;float:left;clear:both;box-shadow:0 4px 10px rgba(245,87,108,0.3)}
    .clearfix::after{content:"";display:table;clear:both}
    </style>""", unsafe_allow_html=True)
    
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    st.markdown("<h1 style='color:white;text-align:center'>💬 Chat with Doctor</h1>", unsafe_allow_html=True)
    
    history = get_conversation(username)
    
    st.markdown("<div class='chat-window'>", unsafe_allow_html=True)
    for msg in history:
        if msg.get("message"):
            who = "👤 You" if msg["sender"] == "patient" else f"🩺 Dr. {msg.get('doctor', 'Doctor')}"
            msg_class = "msg-patient" if msg["sender"] == "patient" else "msg-doctor"
            st.markdown(f"<div class='clearfix'><div class='{msg_class}'><b>{who}</b><br>{msg['message']}<br><small style='opacity:0.8'>{msg['timestamp']}</small></div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("### ✍️ Send Message")
    message = st.text_area("Type your message", key="user_msg")
    uploaded_file = st.file_uploader("📎 Attach File", type=["png", "jpg", "pdf"])
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📨 Send Message", use_container_width=True):
            if message:
                save_patient_message(username, message)
                st.success("✅ Sent!")
                st.rerun()
    with col2:
        if st.button("📎 Send File", use_container_width=True):
            if uploaded_file:
                save_patient_media(username, uploaded_file)
                st.success("✅ File sent!")
                st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
