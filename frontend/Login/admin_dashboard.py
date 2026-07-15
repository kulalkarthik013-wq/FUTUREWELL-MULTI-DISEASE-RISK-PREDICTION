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
import platform

from chat_store import (
    authenticate_doctor,
    assign_patient_to_doctor,
    get_conversation,
    save_patient_message,
    save_patient_media,
    save_doctor_reply,
    get_all_patients_for_doctor,
    clear_patient_chat,get_all_doctors,save_admin_reply
)
from logger import load_appointments, save_appointments

def show_admin_app(username):
    st.markdown("""<style>.appt-card{background:rgba(255,255,255,0.85);backdrop-filter:blur(10px);padding:20px;border-radius:15px;color:#333;margin:15px 0;box-shadow:0 8px 20px rgba(0,0,0,0.15)}.appt-pending{border-left:5px solid #f59e0b}.appt-confirmed{border-left:5px solid #10b981}.appt-cancelled{border-left:5px solid #ef4444}.appt-noshow{border-left:5px solid #6b7280}.revenue-card{background:rgba(255,255,255,0.1);backdrop-filter:blur(10px);padding:15px;border-radius:10px;margin:10px 0}</style>""", unsafe_allow_html=True)
    st.markdown("<h1 style='color:#0072ff;font-size:42px;font-weight:bold'>📅 Appointment Management</h1>", unsafe_allow_html=True)
    
    appointments = load_appointments()
    
    if appointments:
        total_revenue = sum(appt.get('fee', 0) for appt in appointments.values())
        confirmed = sum(1 for a in appointments.values() if a['status'] == 'Confirmed')
        pending = sum(1 for a in appointments.values() if a['status'] == 'Pending')
        no_shows = sum(1 for a in appointments.values() if a.get('no_show', False))
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 Revenue", f"${total_revenue}")
        col2.metric("✅ Confirmed", confirmed)
        col3.metric("⏳ Pending", pending)
        col4.metric("❌ No-Shows", no_shows)
        
        st.markdown("---")
        
        for appt_id, appt in appointments.items():
            status_class = f"appt-{appt['status'].lower()}" if appt['status'] != 'No-Show' else "appt-noshow"
            no_show_badge = " 🚫 NO-SHOW" if appt.get('no_show', False) else ""
            fee = appt.get('fee', 0)
            
            st.markdown(f"<div class='appt-card {status_class}'><h3 style='color:#0072ff'>👤 {appt['patient']} → 🩺 Dr. {appt['doctor']}{no_show_badge}</h3><p style='color:#333'>📅 {appt['date']} | 🕒 {appt['time']} | 💵 ${fee} | Status: <b>{appt['status']}</b></p></div>", unsafe_allow_html=True)
            
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                if st.button("✅ Confirm", key=f"conf_{appt_id}"):
                    appointments[appt_id]['status'] = 'Confirmed'
                    save_appointments(appointments)
                    st.rerun()
            with col2:
                if st.button("❌ Cancel", key=f"canc_{appt_id}"):
                    appointments[appt_id]['status'] = 'Cancelled'
                    save_appointments(appointments)
                    st.rerun()
            with col3:
                if st.button("🚫 No-Show", key=f"noshow_{appt_id}"):
                    appointments[appt_id]['no_show'] = True
                    appointments[appt_id]['status'] = 'No-Show'
                    save_appointments(appointments)
                    st.rerun()
            with col4:
                if st.button("📧 Reminder", key=f"remind_{appt_id}"):
                    st.success(f"✅ Reminder sent to {appt['patient']}!")
            with col5:
                new_fee = st.number_input("Fee", value=fee, key=f"fee_{appt_id}", min_value=0)
                if new_fee != fee:
                    appointments[appt_id]['fee'] = new_fee
                    save_appointments(appointments)
                    st.rerun()
    else:
        st.info("📅 No appointments scheduled yet.")

def show_admin_convo(username):
    st.markdown("""<style>.chat-msg{padding:12px;border-radius:12px;margin:8px 0;box-shadow:0 2px 5px rgba(0,0,0,0.1)}.flagged{border:2px solid #ef4444;background:#fee}.search-highlight{background:#fef08a;font-weight:bold}</style>""", unsafe_allow_html=True)
    
    doctors = get_all_doctors()
    if not doctors:
        st.info("No doctors registered yet.")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        doctor = st.selectbox("🩺 Select Doctor:", doctors)
    with col2:
        patients = get_all_patients_for_doctor(doctor)
        if not patients:
            st.info(f"No patients assigned to {doctor}.")
            return
        patient = st.selectbox("👤 Select Patient:", patients)
    
    search_term = st.text_input("🔍 Search in chat:", placeholder="Type to search messages...")
    
    st.subheader(f"💬 Conversation: {doctor} ↔️ {patient}")
    
    try:
        with open("chat_flags.json", "r") as f:
            flags = json.load(f)
    except:
        flags = {}
    
    history = get_conversation(patient)
    chat_text = ""
    
    st.markdown("<div style='background-color:#f9f9f9; padding:15px; border-radius:10px; max-height:500px; overflow-y:auto;'>", unsafe_allow_html=True)
    for idx, msg in enumerate(history):
        who = "👤 Patient" if msg["sender"] == "patient" else f"🩺 Doctor ({msg['doctor']})"
        align = "right" if msg["sender"] == "patient" else "left"
        bg_color = "#DCF8C6" if msg["sender"] == "patient" else "#E6E6FA"
        
        if msg.get("message"):
            chat_text += f"{who}: {msg['message']}\n{msg['timestamp']}\n\n"
            msg_key = f"{patient}_{idx}"
            is_flagged = flags.get(msg_key, False)
            flag_class = "flagged" if is_flagged else ""
            
            display_msg = msg['message']
            if search_term and search_term.lower() in display_msg.lower():
                display_msg = display_msg.replace(search_term, f"<span class='search-highlight'>{search_term}</span>")
            
            flag_icon = "🚩" if is_flagged else ""
            st.markdown(f"""<div style='text-align:{align}; margin:10px;'><div class='chat-msg {flag_class}' style='background-color:{bg_color}; display:inline-block; max-width:70%;'><b>{who}</b> {flag_icon}<br>{display_msg}</div><br><small style='color:gray;'>{msg['timestamp']}</small></div>""", unsafe_allow_html=True)
            
            if st.button(f"🚩 Flag" if not is_flagged else "✅ Unflag", key=f"flag_{idx}"):
                flags[msg_key] = not is_flagged
                with open("chat_flags.json", "w") as f:
                    json.dump(flags, f, indent=4)
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.download_button("📥 Export Chat Log", chat_text, f"chat_{doctor}_{patient}.txt", "text/plain", use_container_width=True)
    
    st.markdown("---")
    reply = st.text_input("💬 Send message as Admin:")
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("📨 Send Reply", use_container_width=True):
            if reply:
                save_admin_reply(username, doctor, patient, reply)
                st.success("Reply sent ✅")
                st.rerun()
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            clear_patient_chat(patient)
            st.success("Chat cleared ✅")
            st.rerun()

def show_admin_dashboard(username, role="Admin"):
    with st.sidebar:
        lang_choice = st.sidebar.selectbox("Select Language", ["English", "Kannada", "Hindi"])
        labels = translations[lang_choice]
        st.markdown(f"""<div style='background-color:#FF4444; padding:10px; border-radius:8px; text-align:center; color:white; font-size:18px; font-weight:bold;'>👤 Logged in as: {username} | Role: {role}</div>""", unsafe_allow_html=True)
        selected = option_menu(labels["admin_dashboard"], [labels["home"], labels["test_dashboards"], labels["login_history"], labels["user_feedback"], labels["subscription_access"], labels["user_profile"], "Appointments", labels["patient_chat"]], icons=["house", "bar-chart-line", "activity", "envelope", "key", "person-circle", "calendar-check", "chat-dots"], default_index=0, orientation="vertical")

    if selected == labels["test_dashboards"]:
        st.title(labels["test_dashboards"])
        st.markdown("""<style>div[data-testid="stTabs"] button {font-weight: bold; color: #0072ff; background: rgba(255,255,255,0.6); border: 2px solid #0072ff; border-radius: 10px; margin: 6px; padding: 10px 30px;} div[data-testid="stTabs"] button:hover {background: rgba(255,255,255,0.8); color: #0056cc;} div[data-testid="stTabs"] button:focus {background: #0072ff; color: white;}</style>""", unsafe_allow_html=True)
        tabs = st.tabs([labels["diabetes_dashboard"], labels["heart_dashboard"], labels["parkinson_dashboard"], labels["liver_dashboard"], labels["lung_dashboard"], labels["kidney_dashboard"]])
        
        def render_dashboard(df, title, file_key):
            st.subheader(title)
            if not df.empty:
                col1, col2 = st.columns([3, 1])
                with col1:
                    user_search = st.text_input(f"🔍 Search by username", key=f"search_{file_key}")
                with col2:
                    if st.button("🗑️ Delete All", key=f"del_{file_key}"):
                        if st.session_state.get(f"confirm_{file_key}"):
                            pd.DataFrame(columns=df.columns).to_csv(f"data/{file_key}_results.csv", index=False)
                            st.success("Data deleted!")
                            st.rerun()
                        else:
                            st.session_state[f"confirm_{file_key}"] = True
                            st.warning("Click again to confirm")
                
                col3, col4 = st.columns(2)
                with col3:
                    start_date = st.date_input("From", value=pd.to_datetime('2025-01-01').date(), key=f"start_{file_key}")
                with col4:
                    end_date = st.date_input("To", value=datetime.now().date(), key=f"end_{file_key}")
                
                filtered_df = df.copy()
                username_col = 'Name' if 'Name' in df.columns else 'Username'
                if user_search and username_col in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df[username_col].astype(str).str.contains(user_search, case=False, na=False)]
                if 'Timestamp' in filtered_df.columns:
                    filtered_df['Date'] = pd.to_datetime(filtered_df['Timestamp'], errors='coerce').dt.date
                    filtered_df = filtered_df[(filtered_df['Date'] >= start_date) & (filtered_df['Date'] <= end_date)]
                    filtered_df = filtered_df.drop('Date', axis=1)
                
                st.dataframe(filtered_df, use_container_width=True)
                st.download_button("📥 Export CSV", filtered_df.to_csv(index=False), f"{file_key}.csv", "text/csv", key=f"csv_{file_key}")
                
                if 'Result' in filtered_df.columns:
                    result_counts = filtered_df['Result'].value_counts()
                    st.bar_chart(result_counts)
            else:
                st.info(labels.get("no_results", "No test results found yet."))
        
        with tabs[0]:
            render_dashboard(load_diabetes_results(), labels.get("diabetes_history", "Diabetes Test History"), "diabetes")
        with tabs[1]:
            render_dashboard(load_heart_disease_results(), labels.get("heart_history", "Heart Disease Test History"), "heart_disease")
        with tabs[2]:
            render_dashboard(load_parkison_results(), labels.get("parkinson_history", "Parkinson Test History"), "parkison")
        with tabs[3]:
            render_dashboard(load_liver_results(), labels.get("liver_history", "Liver Disease Test History"), "liver")
        with tabs[4]:
            render_dashboard(load_lung_cancer_results(), labels.get("lung_history", "Lung Cancer Test History"), "lung_cancer")
        with tabs[5]:
            render_dashboard(load_chronic_kidney_results(), labels.get("kidney_history", "Chronic Kidney Test History"), "chronic_kidney")

    if selected == labels["user_feedback"]:
        st.markdown(f"<h1>{labels['feedback_title']}</h1>", unsafe_allow_html=True)
        feedback_data = load_feedback_json()
        if feedback_data:
            for entry in reversed(feedback_data):
                st.markdown(f"""<div style='background: rgba(255,255,255,0.8); backdrop-filter: blur(6px); padding:15px; margin-bottom:12px; border-radius:10px; box-shadow: 2px 2px 6px rgba(0,0,0,0.15);'><p style='margin:0; font-weight:bold; color:#0072ff;'>🧑 {entry['username']}</p><p style='margin:8px 0; font-size:15px; color:#333;'>{entry['comment']}</p><p style='margin:0; font-size:13px; color:gray;'>🕒 {entry['timestamp']}</p></div>""", unsafe_allow_html=True)
        else:
            st.info("No feedback submitted yet.")

    if selected == labels["login_history"]:
        st.markdown(f"<h1>{labels['login_title']}</h1>", unsafe_allow_html=True)
        try:
            with open("data/data.json", "r") as f:
                data = json.load(f)
                df = pd.DataFrame(data)
                
                if not df.empty:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    login_counts = df.groupby(['username', 'ip_address']).size().reset_index(name='count')
                    suspicious = login_counts[login_counts['count'] > 10]
                    if not suspicious.empty:
                        st.warning("⚠️ Suspicious Activity Detected:")
                        for _, row in suspicious.iterrows():
                            st.error(f"User '{row['username']}' from IP {row['ip_address']}: {row['count']} logins")
                    
                    st.dataframe(df, use_container_width=True)
                    st.download_button("📥 Export CSV", df.to_csv(index=False), "login_history.csv", "text/csv")
                else:
                    st.info("No login history found yet.")
        except FileNotFoundError:
            st.info("No login history found yet.")

    if selected == labels["home"]:
        st.markdown(f"<h1 style='color:#000000;'>{labels['home_title']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='color: #0072ff;'>{labels['overview']}</h2>", unsafe_allow_html=True)
        try:
            total_users = len(load_auth_json())
            total_predictions = 0
            positive_count = 0
            negative_count = 0
            for load_func in [load_diabetes_results, load_heart_disease_results, load_parkison_results, load_liver_results, load_lung_cancer_results, load_chronic_kidney_results]:
                df = load_func()
                if not df.empty:
                    total_predictions += len(df)
                    if 'Result' in df.columns:
                        positive_count += df['Result'].str.contains('Disease|Diabetic|Cancer|Parkinson', case=False, na=False).sum()
                        negative_count += df['Result'].str.contains('No|Not', case=False, na=False).sum()
            try:
                with open("data/data.json", "r") as f:
                    login_data = json.load(f)
                    total_logins = len(login_data) if isinstance(login_data, list) else 0
            except:
                total_logins = 0
        except Exception as e:
            total_users = 0
            total_predictions = 0
            positive_count = 0
            negative_count = 0
            total_logins = 0
        st.markdown("""<style>.analytics-card {background-color: transparent; padding: 1rem; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); margin-bottom: 1rem; transition: 0.3s ease; text-align: center;} .analytics-card:hover {background-color: #eef6ff; transform: scale(1.02); cursor: pointer;} .card-title {font-size: 18px; font-weight: bold; margin-bottom: 0.5rem;} .card-value {font-size: 24px; color: #0072ff;}</style>""", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='analytics-card'><div class='card-title'>🧑💻 {labels['total_users']}</div><div class='card-value'>{total_users}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='analytics-card'><div class='card-title'>📈 {labels['predictions_made']}</div><div class='card-value'>{total_predictions}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='analytics-card'><div class='card-title'>🟢 {labels['positive']}</div><div class='card-value'>{positive_count}</div></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='analytics-card'><div class='card-title'>🩺 {labels['active_modules']}</div><div class='card-value'>6</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='analytics-card'><div class='card-title'>📊 Total Logins</div><div class='card-value'>{total_logins}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='analytics-card'><div class='card-title'>🔴 {labels['negative']}</div><div class='card-value'>{negative_count}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='color: #0072ff;'>{labels['admin_insights']}</h2>", unsafe_allow_html=True)
        st.markdown(labels["insights_list"])

    if selected == labels["subscription_access"]:
        st.markdown("""<style>.sub-card{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:20px;border-radius:15px;color:white;margin:10px 0;box-shadow:0 8px 16px rgba(0,0,0,0.2)}.sub-card h3{margin:0;font-size:24px}.sub-card p{margin:5px 0;font-size:16px}.status-active{background:#10b981;padding:5px 15px;border-radius:20px;font-weight:bold}.status-expired{background:#ef4444;padding:5px 15px;border-radius:20px;font-weight:bold}.form-card{background:rgba(255,255,255,0.05);backdrop-filter:blur(10px);padding:25px;border-radius:15px;border:1px solid rgba(255,255,255,0.1);margin:15px 0}</style>""", unsafe_allow_html=True)
        st.markdown(f"<h1 style='background:linear-gradient(90deg,#667eea,#764ba2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:42px;font-weight:bold'>{labels['subscription_title']}</h1>", unsafe_allow_html=True)
        
        try:
            with open("subscriptions.json", "r") as f:
                subs = json.load(f)
        except:
            subs = {}
        
        auth_data = load_auth_json()
        usernames = [u["username"] for u in auth_data] if auth_data else []
        
        total_revenue = sum(v.get("amount", 0) for v in subs.values())
        active_subs = sum(1 for v in subs.values() if v.get("active"))
        expired_subs = len(subs) - active_subs
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 Total Revenue", f"${total_revenue}", delta="+12%")
        col2.metric("✅ Active", active_subs, delta=f"+{active_subs}")
        col3.metric("❌ Expired", expired_subs)
        col4.metric("🔄 Auto-Renew", sum(1 for v in subs.values() if v.get("auto_renew")))
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if subs:
            for user, data in subs.items():
                status = "Active" if data.get("active") else "Expired"
                status_class = "status-active" if data.get("active") else "status-expired"
                expiry = data.get("expiry", "N/A")
                days_left = (pd.to_datetime(expiry) - datetime.now()).days if data.get("active") else 0
                st.markdown(f"""<div class='sub-card'><h3>👤 {user}</h3><p>💵 Amount: <b>${data.get('amount', 0)}</b> | 📅 Expiry: <b>{expiry}</b> | ⏳ Days Left: <b>{days_left}</b></p><p><span class='{status_class}'>{status}</span> {'🔄 Auto-Renew Enabled' if data.get('auto_renew') else ''}</p></div>""", unsafe_allow_html=True)
            
            df_subs = pd.DataFrame([{"Username": k, "Amount": v.get("amount", 0), "Expiry": v.get("expiry", "N/A"), "Status": "Active" if v.get("active") else "Expired", "Auto-Renew": "Yes" if v.get("auto_renew") else "No"} for k, v in subs.items()])
            st.download_button("📥 Export All Subscriptions", df_subs.to_csv(index=False), "subscriptions.csv", "text/csv", use_container_width=True)
        else:
            st.info("📊 No subscriptions yet. Add your first subscriber below!")
        
        st.markdown("<div class='form-card'>", unsafe_allow_html=True)
        st.markdown("### 🆕 Add/Update Subscription")
        col1, col2 = st.columns(2)
        with col1:
            sel_user = st.selectbox("👤 Select User", usernames, key="add_user")
            amount = st.number_input("💵 Amount ($)", min_value=0, value=50, step=10)
        with col2:
            plan = st.selectbox("📅 Plan", ["Monthly (30 days)", "Quarterly (90 days)", "Yearly (365 days)", "Custom"])
            days = st.number_input("⏱️ Duration (days)", min_value=1, value=30 if "Monthly" in plan else 90 if "Quarterly" in plan else 365 if "Yearly" in plan else 30)
        
        col3, col4 = st.columns(2)
        with col3:
            auto_renew = st.checkbox("🔄 Enable Auto-Renew", value=True)
        with col4:
            payment_method = st.selectbox("💳 Payment Method", ["Credit Card", "PayPal", "Bank Transfer", "Cash"])
        
        if st.button("✨ Add Subscription", use_container_width=True):
            expiry = (datetime.now() + pd.Timedelta(days=days)).strftime("%Y-%m-%d")
            subs[sel_user] = {"amount": amount, "expiry": expiry, "active": True, "auto_renew": auto_renew, "payment_method": payment_method, "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            with open("subscriptions.json", "w") as f:
                json.dump(subs, f, indent=4)
            st.success(f"✅ Subscription added for {sel_user}! Expires on {expiry}")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='form-card'>", unsafe_allow_html=True)
        st.markdown("### 💸 Refund Management")
        col1, col2 = st.columns([2, 1])
        with col1:
            refund_user = st.selectbox("👤 Select User for Refund", list(subs.keys()) if subs else [], key="refund_user")
        with col2:
            refund_reason = st.selectbox("📝 Reason", ["User Request", "Service Issue", "Duplicate Payment", "Other"])
        
        if st.button("🚫 Process Refund", use_container_width=True) and refund_user:
            refund_amt = subs[refund_user].get("amount", 0)
            subs[refund_user]["active"] = False
            subs[refund_user]["refunded"] = True
            subs[refund_user]["refund_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            subs[refund_user]["refund_reason"] = refund_reason
            with open("subscriptions.json", "w") as f:
                json.dump(subs, f, indent=4)
            st.warning(f"✅ Refunded ${refund_amt} to {refund_user}. Reason: {refund_reason}")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    if selected == labels["user_profile"]:
        st.markdown("""<style>.profile-header{background:linear-gradient(135deg,#667eea,#764ba2);padding:30px;border-radius:15px;color:white;margin-bottom:20px}.action-btn{padding:10px 20px;border-radius:8px;border:none;font-weight:bold;cursor:pointer;margin:5px}.ban-btn{background:#ef4444;color:white}.suspend-btn{background:#f59e0b;color:white}.reset-btn{background:#3b82f6;color:white}.activity-card{background:rgba(255,255,255,0.05);padding:15px;border-radius:10px;margin:10px 0;border-left:4px solid #667eea}</style>""", unsafe_allow_html=True)
        st.markdown(f"<h1 style='background:linear-gradient(90deg,#667eea,#764ba2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:42px;font-weight:bold'>{labels['profile_title']}</h1>", unsafe_allow_html=True)
        
        auth_data = load_auth_json()
        if auth_data:
            usernames = [entry["username"] for entry in auth_data]
            selected_user = st.selectbox("🔍 Select User", usernames)
            user_info = next((u for u in auth_data if u["username"] == selected_user), None)
            
            if user_info:
                try:
                    with open("user_status.json", "r") as f:
                        user_status = json.load(f)
                except:
                    user_status = {}
                
                status = user_status.get(selected_user, {}).get("status", "Active")
                status_color = "#10b981" if status == "Active" else "#ef4444" if status == "Banned" else "#f59e0b"
                
                st.markdown(f"<div class='profile-header'><h2>👤 {user_info['name']}</h2><p style='font-size:18px'>@{user_info['username']} | {user_info['email']}</p><span style='background:{status_color};padding:5px 15px;border-radius:20px;font-weight:bold'>{status}</span></div>", unsafe_allow_html=True)
                
                tab1, tab2, tab3 = st.tabs(["📝 Edit Profile", "🔒 Security Actions", "📊 Activity Log"])
                
                with tab1:
                    st.subheader("Edit User Information")
                    new_name = st.text_input("Name", value=user_info.get("name", ""))
                    new_email = st.text_input("Email", value=user_info.get("email", ""))
                    if st.button("💾 Save Changes", use_container_width=True):
                        for u in auth_data:
                            if u["username"] == selected_user:
                                u["name"] = new_name
                                u["email"] = new_email
                        with open("_secret_auth_.json", "w") as f:
                            json.dump(auth_data, f, indent=4)
                        st.success("✅ Profile updated successfully!")
                        st.rerun()
                
                with tab2:
                    st.subheader("Security Actions")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("🚫 Ban User", use_container_width=True):
                            user_status[selected_user] = {"status": "Banned", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                            with open("user_status.json", "w") as f:
                                json.dump(user_status, f, indent=4)
                            st.error(f"User {selected_user} has been banned")
                            st.rerun()
                    
                    with col2:
                        if st.button("⏸️ Suspend User", use_container_width=True):
                            user_status[selected_user] = {"status": "Suspended", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                            with open("user_status.json", "w") as f:
                                json.dump(user_status, f, indent=4)
                            st.warning(f"User {selected_user} has been suspended")
                            st.rerun()
                    
                    with col3:
                        if st.button("✅ Activate User", use_container_width=True):
                            user_status[selected_user] = {"status": "Active", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                            with open("user_status.json", "w") as f:
                                json.dump(user_status, f, indent=4)
                            st.success(f"User {selected_user} has been activated")
                            st.rerun()
                    
                    st.markdown("---")
                    st.subheader("🔑 Password Reset")
                    new_password = st.text_input("New Password", type="password")
                    confirm_password = st.text_input("Confirm Password", type="password")
                    if st.button("🔄 Reset Password", use_container_width=True):
                        if new_password == confirm_password and new_password:
                            for u in auth_data:
                                if u["username"] == selected_user:
                                    u["password"] = new_password
                            with open("_secret_auth_.json", "w") as f:
                                json.dump(auth_data, f, indent=4)
                            st.success("✅ Password reset successfully!")
                        else:
                            st.error("❌ Passwords don't match or empty")
                
                with tab3:
                    st.subheader("User Activity Log")
                    try:
                        with open("data/data.json", "r") as f:
                            login_data = json.load(f)
                        user_logins = [l for l in login_data if l["username"] == selected_user]
                        st.metric("Total Logins", len(user_logins))
                        
                        if user_logins:
                            for login in user_logins[-10:]:
                                st.markdown(f"<div class='activity-card'>🕒 {login['timestamp']} | 🌐 IP: {login.get('ip_address', 'N/A')} | 💻 {login.get('device', 'N/A')}</div>", unsafe_allow_html=True)
                        else:
                            st.info("No login activity found")
                    except:
                        st.info("No activity data available")
                    
                    st.markdown("---")
                    st.subheader("Test History")
                    total_tests = 0
                    for load_func in [load_diabetes_results, load_heart_disease_results, load_parkison_results, load_liver_results, load_lung_cancer_results, load_chronic_kidney_results]:
                        df = load_func()
                        if not df.empty:
                            username_col = 'Name' if 'Name' in df.columns else 'Username'
                            if username_col in df.columns:
                                user_tests = df[df[username_col] == selected_user]
                                total_tests += len(user_tests)
                    st.metric("Total Tests Taken", total_tests)
            else:
                st.info("No user data found.")
        else:
            st.info("No users registered yet.")

    if selected == labels["patient_chat"]:
        show_admin_convo(username)

    if selected == "Appointments":
        show_admin_app(username)
