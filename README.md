# FUTURE WELL: MULTI‑DISEASE RISK PREDICTION

**Future Well** is an intelligent, high‑performance enterprise healthcare web portal built using the Streamlit framework. It features secure multi‑tier user classification paths, intercepts user login packets, writes structural audit trails via a JSON tracking engine, and dynamically switches execution panels depending on administrative, clinical, or client privilege vectors. The platform integrates advanced machine learning architectures (including CatBoost) to provide predictive insights for multi-disease risks.

---
## Screenshots
<table>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/d4d104df-6a89-4712-ae51-61ba30a5d00c" width="100%" alt="Dashboard View 1"/></td>
    <td><img src="https://github.com/user-attachments/assets/262a0bb1-aabe-48ba-92b6-284b2b1212ca" width="100%" alt="Dashboard View 2"/></td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/803b0383-f608-4129-9dd5-5e1ca32bc6e8" width="100%" alt="Dashboard View 3"/></td>
    <td><img src="https://github.com/user-attachments/assets/baf9c794-8dfb-4f63-852c-5962751e61bf" width="100%" alt="Dashboard View 4"/></td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/e56f5921-d76d-4c11-953c-3b84a230599a" width="100%" alt="Dashboard View 5"/></td>
    <td><img src="https://github.com/user-attachments/assets/8be1f7cb-190f-48c5-914f-4f9d01427078" width="100%" alt="Dashboard View 6"/></td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/786e751c-b2a8-4ff6-8f81-95822b9468b4" width="100%" alt="Dashboard View 7"/></td>
    <td><img src="https://github.com/user-attachments/assets/94868842-5923-4d0b-a32c-e1064593a8e1" width="100%" alt="Dashboard View 8"/></td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/9e3c3765-439e-46d6-b0d3-80ccb9879af4" width="100%" alt="Dashboard View 9"/></td>
    <td><img src="https://github.com/user-attachments/assets/0d90ccca-adfe-434e-837b-cbc561f18a90" width="100%" alt="Dashboard View 10"/></td>
  </tr>
</table>

---
## ⚡ Core Platform Features

* **Dynamic Role‑Based Access Control (RBAC):** Automated login UI state manager that queries session vectors and mounts distinct interfaces based on user authorization.
* **Advanced ML Prediction Pipeline:** Modular data preparation, feature engineering, and evaluation systems powered by production-ready models (including CatBoost and Pima analytics).
* **Clinical Communication & Scheduling:** Integrated doctor-patient chat environments and specialized appointment matrices.
* **Modern High‑Contrast Interface Design:** Custom Google Fonts styling with dynamic CSS animations, custom backgrounds, and glowing brand assets.
* **Persistent Session Isolation Engine:** Flushes residual unencrypted browser memory frames and authorization keys on boot to prevent state leakage.
* **Automated Audit & Transaction Telemetry:** Tracks global administration and user-specific analytical transactions across independent JSON storage layers.

---

## 🔐 Default Access Credentials

For testing and deployment verification, use the following sandbox credentials:

| Role | Username | Password | Notes / Ext. Ref |
| --- | --- | --- | --- |
| **Administrator** | `admin` | `admin123` | Global system control and transaction monitoring |
| **Clinical Staff** | `doctor` | `doc123` | Assigned to **Dr. Bharath** (ID: `152004`) |
| **Client / User** | `user` | *(Self-register)* | General patient health metric tracking |

---

## 📂 System Project Directory Structure

```text
├── requirements.txt               # Direct package dependency manifest
├── data/                          # Secure localized patient records and datasets
│   └── patientdata/               # Granular clinical data frames
│
├── code/                          # Production Machine Learning Core Pipeline
│   ├── pima/                      # Diabetes risk model configurations
│   ├── artifact/                  # Saved binary transformers and scaler assets
│   ├── catboost/                  # Gradient boosted tree ensembles
│   ├── config/                    # Hyperparameter and path definitions
│   ├── dataprep.py                # Missing value imputation and normalization pipelines
│   ├── feature_engineer.py        # Outlier tracking and interaction term extraction
│   ├── model.py                   # Global model loading and prediction wrapper
│   └── evaluation.py              # Precision, Recall, and ROC-AUC benchmarking
│
├── login/                         # Multi‑tier compartmentalized dashboard views
│   ├── admin_dashboard.py         # Administrative operations module
│   ├── doc.py                     # Clinical operational viewports (Dr. Bharath interface)
│   └── user_dashboard.py          # Client metric tracking panel
│
├── storage/                       # Persistent JSON Telemetry Engine
│   ├── subscription.json          # Portal subscription tiers
│   ├── chatstore.json             # Encrypted clinical conversation logs
│   ├── admin_trans.json           # Administrative system modification logs
│   └── user_trans.json            # Patient predictive computation logs
│
├── assets/                        # Design Systems & Visual Media Assets
│   ├── logo.png                   # High‑resolution neural glow asset
│   ├── positive.png               # High-contrast positive diagnostic indicator icon
│   ├── negative.png               # High-contrast negative diagnostic indicator icon
│   ├── background1.jpg            # Sidebar layout layout canvas
│   ├── background2.jpg            # Supplementary workspace backdrop
│   └── background3.jpg            # High‑contrast core workspace background asset
│
└── frontend/                      # Streamlit UI Orchestration Workspace
    ├── app.py                     # Main orchestration gateway entry point
    ├── feedback.py                # User experience and clinical feedback capture
    ├── manualaccess.py            # Override interface for manual operational entry
    ├── secret-auth.py             # Core cryptographic hashing and authentication logic
    └── logger.py                  # Async telemetry logging engine

```

---

## 🛠️ System Technology Stack

* **Core UI Engine:** Streamlit Web Framework (v2022 deployment baseline)
* **Predictive Architecture:** CatBoost Classifier, Scikit-Learn Pipeline
* **Identity Management:** Custom authenticated login UI widget framework with remote token mappings (`streamlitauthui`)
* **Graphics Processing:** Pillow (PIL) binary rendering pipeline
* **Design Systems:** Base64 asset injection pipelines, custom CSS injection, Google Fonts API

---

## 🚀 Local Initialization and Setup

### Prerequisites

* Python 3.9 or higher installed in an isolated virtual environment.

### 1. Install Dependencies

Run the installation targeted at the dependencies manifest located in the root directory:

```bash
pip install -r requirements.txt

```

### 2. Launch the Application

Navigate to the orchestration workspace containing `app.py` and run the interface engine using Python's standard module pathway:

```bash
cd frontend
python -m streamlit run app.py

```

Access locally via your web browser: **http://localhost:8501**

---

## ⚙️ Structural Code Highlights

### Event Routing & Privilege Escalation

```python
if LOGGED_IN:
    username = st.session_state.get("USERNAME", "guest")
    role = st.session_state.get("ROLE", "user")

    log_login_event_json(username, role)

    if role == "admin":
        show_admin_dashboard(username)
    elif role == "doctor":
        # Routes directly to clinical viewport assigned to Dr. Bharath (152004)
        show_doc_dashboard(username) 
    else:
        show_user_dashboard(username)

```

---

## 📖 Usage

1. Log in using your designated access profile (`admin`, `doctor`, or `user`).
2. **Clinicians (`doctor`)** can navigate to the chat module to schedule appointments or communicate using the credentials tied to `Dr.Bharath`.
3. Run live risk assessments using the modular pipeline under the `code/` folder to process raw clinical inputs against pre-trained CatBoost models.
4. System metrics and transactions can be audited dynamically inside the `admin_trans.json` and `user_trans.json` profiles.

---

## 🤝 Contributing

Contributions are welcome! Please fork the repository, build on a feature branch, and submit a pull request. For extensive updates to the ML pipeline configuration, open an issue first to align changes with the core `evaluation.py` criteria.

---

## 👨‍💻 Author

**Karthik S Kulal**

GitHub: [Karthik S Kulal] https://github.com/kulalkarthik013-wq)

---

## 📝 Compliance & Attribution

* **Distribution Engine:** Internal Proprietary Platform
* **System Operations Framework:** Engineered and Maintained by **Karthik S Kulal** © 2026
* **License:** This project is licensed under the MIT License © 2026 Karthik S Kulal
