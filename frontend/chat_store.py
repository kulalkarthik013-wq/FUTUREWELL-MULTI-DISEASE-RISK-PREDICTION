import json
from datetime import datetime
from pathlib import Path

# Path to JSON storage
DATA_PATH = Path(r"D:\proj\frontend\data\chat_data.json")

# -------------------------------
# Internal helpers
# -------------------------------
def _load():
    if not DATA_PATH.exists():
        DATA_PATH.write_text(
            json.dumps({"doctors": [], "patients": [], "chat_messages": []}, indent=4),
            encoding="utf-8"
        )
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# -------------------------------
# Authentication
# -------------------------------
def authenticate_doctor(username, password):
    data = _load()
    return any(doc for doc in data.get("doctors", []) if doc["username"] == username and doc["password"] == password)

# -------------------------------
# Doctor & Patient Management
# -------------------------------
def add_doctor(username, password, name, specialty):
    """Add a doctor with a specialty (ortho/cardio)."""
    data = _load()
    if "doctors" not in data:
        data["doctors"] = []
    # prevent duplicates
    if any(d["username"] == username for d in data["doctors"]):
        return False
    data["doctors"].append({
        "username": username,
        "password": password,
        "name": name,
        "specialty": specialty
    })
    _save(data)
    return True

def assign_patient_to_doctor(patient_username, specialty):
    """Assign patient to a doctor of given specialty."""
    data = _load()
    if "patients" not in data:
        data["patients"] = []
    doctor = next((d for d in data.get("doctors", []) if d["specialty"] == specialty), None)
    if not doctor:
        return None
    patient = next((p for p in data["patients"] if p["username"] == patient_username), None)
    if not patient:
        patient = {"username": patient_username, "doctor": doctor["username"]}
        data["patients"].append(patient)
    else:
        patient["doctor"] = doctor["username"]
    _save(data)
    return doctor

def get_patient_doctor(patient_username):
    data = _load()
    patient = next((p for p in data.get("patients", []) if p["username"] == patient_username), None)
    return patient.get("doctor") if patient else None

# -------------------------------
# Patient & Doctor Messages
# -------------------------------
def save_patient_message(patient_username, message):
    if not message.strip():
        return
    data = _load()
    doctor_username = get_patient_doctor(patient_username)
    data["chat_messages"].append({
        "sender": "patient",
        "patient": patient_username,
        "doctor": doctor_username,
        "message": message,
        "media": None,
        "timestamp": datetime.now().isoformat(timespec="seconds")
    })
    _save(data)

def save_doctor_reply(doctor_username, patient_username, message):
    if not message.strip():
        return
    data = _load()
    data["chat_messages"].append({
        "sender": "doctor",
        "patient": patient_username,
        "doctor": doctor_username,
        "message": message,
        "media": None,
        "timestamp": datetime.now().isoformat(timespec="seconds")
    })
    _save(data)

# -------------------------------
# Conversation Retrieval
# -------------------------------
def get_patient_history(patient_username):
    data = _load()
    return [m for m in data.get("chat_messages", []) if m.get("patient") == patient_username]

def get_conversation(patient_username):
    """Return conversation restricted to patient + their assigned doctor."""
    doctor_username = get_patient_doctor(patient_username)
    history = get_patient_history(patient_username)
    if doctor_username:
        history = [m for m in history if m.get("doctor") == doctor_username]
    return history

def get_all_patients_for_doctor(doctor_username):
    data = _load()
    return [p["username"] for p in data.get("patients", []) if p.get("doctor") == doctor_username]

# -------------------------------
# Media Handling
# -------------------------------
def save_patient_media(patient_username, uploaded_file):
    folder = Path(f"patient_data/{patient_username}/media")
    folder.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{timestamp}_{uploaded_file.name}"
    file_path = folder / file_name

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    doctor_username = get_patient_doctor(patient_username)
    data = _load()
    data["chat_messages"].append({
        "sender": "patient",
        "patient": patient_username,
        "doctor": doctor_username,
        "message": None,
        "media": str(file_path),
        "timestamp": datetime.now().isoformat(timespec="seconds")
    })
    _save(data)
    return str(file_path)

def clear_patient_chat(patient_username):
    """Delete all chat messages for a patient."""
    data = _load()
    data["chat_messages"] = [m for m in data.get("chat_messages", [])
                             if m.get("patient") != patient_username]
    _save(data)
    return True



def get_all_doctors():
    data = _load()
    return [d["username"] for d in data.get("doctors", [])]

# -------------------------------
# Admin Messages
# -------------------------------
def save_admin_reply(admin_username, doctor_username, patient_username, message):
    if not message.strip():
        return
    data = _load()
    data["chat_messages"].append({
        "sender": "admin",
        "patient": patient_username,
        "doctor": doctor_username,
        "message": message,
        "media": None,
        "timestamp": datetime.now().isoformat(timespec="seconds")
    })
    _save(data)
