import pandas as pd
import json
import os
from datetime import datetime
import streamlit as st


# Generic logging function
def log_result(name, prediction, inputs, disease):
    result_map = {
        "diabetes": "Diabetic" if prediction == 1 else "Not Diabetic",
        "heart": "Heart Disease" if prediction == 1 else "No Heart Disease",
        "parkinson": "Parkinson" if prediction == 1 else "No Parkinson",
        "liver": "Liver Disease" if prediction == 1 else "No Liver Disease",
        "lung_cancer": "Lung Cancer" if prediction == 'YES' else "No Lung Cancer",
        "chronic_kidney": "Kidney Disease" if prediction == 1 else "No Kidney Disease"
    }

    result = result_map.get(disease, "Unknown")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record = {
        "Name": name,
        "Timestamp": timestamp,
        "Result": result,
        **inputs
    }

    file_path = os.path.join("data", f"{disease}_results.csv")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
        else:
            df = pd.DataFrame([record])
        df.to_csv(file_path, index=False)
    except Exception as e:
        print(f"Error logging result for {disease}: {e}")

# Individual wrappers
def log_diabetes_result(name, prediction, inputs):
    log_result(name, prediction, inputs, "diabetes")

def log_heart_disease_result(name, prediction, inputs):
    log_result(name, prediction, inputs, "heart")

def log_parkison_result(name, prediction, inputs):
    log_result(name, prediction, inputs, "parkinson")

def log_liver_result(name, prediction, inputs):
    log_result(name, prediction, inputs, "liver")

def log_lung_cancer_result(name, prediction, inputs):
    log_result(name, prediction, inputs, "lung_cancer")

def log_chronic_kidney_result(name, prediction, inputs):
    log_result(name, prediction, inputs, "chronic_kidney")

# Load functions
def load_results(disease):
    file_path = os.path.join("data", f"{disease}_results.csv")
    try:
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        else:
            return pd.DataFrame()
    except Exception as e:
        print(f"Error loading results for {disease}: {e}")
        return pd.DataFrame()

# Individual loaders
def load_diabetes_results():
    return load_results("diabetes")

def load_heart_disease_results():
    return load_results("heart")

def load_parkison_results():
    return load_results("parkinson")

def load_liver_results():
    return load_results("liver")

def load_lung_cancer_results():
    return load_results("lung_cancer")

def load_chronic_kidney_results():
    return load_results("chronic_kidney")


def log_login_event_json(username, role):
    filename = 'data/data.json'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    try:
        import socket
        ip_address = socket.gethostbyname(socket.gethostname())
    except:
        ip_address = "Unknown"
    
    import platform
    device_info = f"{platform.system()} {platform.release()}"

    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "username": username,
        "role": role,
        "ip_address": ip_address,
        "device": device_info
    }

    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                try:
                    data = json.load(f)
                    if not isinstance(data, list):
                        # If file contains a single object, wrap it in a list
                        data = [data]
                except json.JSONDecodeError:
                    # If file is corrupted, reset to empty list
                    data = []
        else:
            data = []

        data.append(entry)

        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

    except Exception as e:
        print(f"Error logging login event: {e}")

# access_manager.py
manual_access = {}

def grant_access(username: str):
    manual_access[username] = True

def revoke_access(username: str):
    manual_access[username] = False

def has_access(username: str) -> bool:
    return manual_access.get(username, False)

def list_access_users():
    return [u for u, v in manual_access.items() if v]

# access_manager.py
FILE = "manual_access.json"

def load_access():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_access(data):
    with open(FILE, "w") as f:
        json.dump(data, f)

def grant_access(username: str):
    data = load_access()
    data[username] = True
    save_access(data)

def revoke_access(username: str):
    data = load_access()
    data[username] = False
    save_access(data)

def list_access_users():
    data = load_access()
    return [u for u, v in data.items() if v]

# --- helper functions ---
def load_manual_access_json():
    try:
        with open("manual_access.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_manual_access_json(data):
    with open("manual_access.json", "w") as f:
        json.dump(data, f, indent=4)

def load_auth_json(auth_filename="_secret_auth_.json"):
    try:
        with open(auth_filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []        



def save_feedback_json(username, comment, file_path="feedback.json"):
    feedback_entry = {
        "username": username,
        "comment": comment,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append(feedback_entry)

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


import streamlit as st
import json
import os
from datetime import datetime

APPOINTMENTS_FILE = r"D:\proj\frontend\appointments.json"

# ------------------ Helpers ------------------
def load_appointments():
    # ✅ Ensure file exists before reading
    if not os.path.exists(APPOINTMENTS_FILE):
        with open(APPOINTMENTS_FILE, "w") as f:
            json.dump({}, f)   # create empty JSON object

    try:
        with open(APPOINTMENTS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # If file is corrupted, reset it
        return {}

def save_appointments(data):
    # ✅ Always ensure file exists before writing
    with open(APPOINTMENTS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def set_session(username, role):
    st.session_state.update({
        'LOGGED_IN': True,
        'USERNAME': username,
        'ROLE': role,
        'LOGOUT_BUTTON_HIT': False
    })
import json
import os
from datetime import datetime

APPOINTMENTS_FILE = r"D:\proj\frontend\appointments.json"

# ------------------ Helpers ------------------
def load_appointments():
    # ✅ Ensure file exists before reading
    if not os.path.exists(APPOINTMENTS_FILE):
        with open(APPOINTMENTS_FILE, "w") as f:
            json.dump({}, f)   # create empty JSON object

    try:
        with open(APPOINTMENTS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # If file is corrupted, reset it
        return {}

def save_appointments(data):
    # ✅ Always ensure file exists before writing
    with open(APPOINTMENTS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def set_session(username, role):
    st.session_state.update({
        'LOGGED_IN': True,
        'USERNAME': username,
        'ROLE': role,
        'LOGOUT_BUTTON_HIT': False
    })