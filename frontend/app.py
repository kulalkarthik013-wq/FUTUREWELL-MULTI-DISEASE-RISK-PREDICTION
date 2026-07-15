import base64
from io import BytesIO
import streamlit as st
from PIL import Image
from streamlit_login_auth_ui.widgets import __login__
from logger import log_login_event_json
from Login.admin_dashboard import show_admin_dashboard
from Login.user_dashboard import show_user_dashboard
from Login.doc import show_doc_dashboard

# --- COMPLETELY DESTROY COOKIE MANAGER EMPTY SPACE ---
st.markdown(
    """
    <style>
    /* 1. Hide the cookie manager sync iframe completely */
    iframe[title*="cookie_manager"], 
    iframe[src*="cookie_manager"] {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
        width: 0px !important;
        position: absolute !important;
    }

    /* 2. Collapse its enclosing element-container wrapper to zero height and remove spacing */
    div[data-testid="element-container"]:has(iframe[title*="cookie_manager"]),
    div[data-testid="element-container"]:has(iframe[src*="cookie_manager"]) {
        display: none !important;
        height: 0px !important;
        min-height: 0px !important;
        margin: 0px !important;
        padding: 0px !important;
    }

    /* 3. Adjust the parent vertical flex block to drop any residual flex gap gaps */
    div[data-testid="stVerticalBlock"] > div:has(iframe[src*="cookie_manager"]) {
        display: none !important;
        margin-top: 0px !important;
        margin-bottom: 0px !important;
    }

    /* 4. Fix standard component tab masks */
    div[data-testid="stTabs"] > div {
        -webkit-mask-image: none !important;
        mask-image: none !important;
    }
    div[data-testid="stTabs"]::after {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
) 

# --- SESSION STATE INITIALIZATION ---
if 'initialized' not in st.session_state:
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state['initialized'] = True
    st.session_state['LOGGED_IN'] = False
    st.session_state['LOGOUT_BUTTON_HIT'] = False

# --- BACKGROUND UTILITIES ---
def set_background(image_file):
    with open(image_file, "rb") as file:
        encoded = base64.b64encode(file.read()).decode()
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def sidebar_background(image_file):
    with open(image_file, "rb") as file:
        encoded = base64.b64encode(file.read()).decode()
    css = f"""
    <style>
    section[data-testid="stSidebar"] {{
        background-image: url("data:image/jpeg;base64,{encoded}");
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Apply backgrounds
set_background("background7.jpg")
sidebar_background("background1.jpg")

# --- IMAGE CACHING & PROCESSING ---
@st.cache_data
def logo_to_base64(image_path):
    img = Image.open(image_path)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Neural pulse CSS animation
st.markdown("""
    <style>
    .neural-logo {
        width: 150px;
        animation: pulseGlow 3s infinite ease-in-out;
        filter: drop-shadow(0 0 10px #00f2ff);
    }
    @keyframes pulseGlow {
        0% { transform: scale(1); filter: drop-shadow(0 0 10px #00f2ff); }
        50% { transform: scale(1.05); filter: drop-shadow(0 0 20px #00f2ff); }
        100% { transform: scale(1); filter: drop-shadow(0 0 10px #00f2ff); }
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER HEADER ---
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    st.markdown(
        f'<img src="data:image/png;base64,{logo_to_base64("logo3.png")}" class="neural-logo">',
        unsafe_allow_html=True
    )
    
with col2:
    st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700&display=swap" rel="stylesheet">
        <div style='background-color: transparent; padding: 25px; margin-left: 0px; border-radius: 2px;'>
            <h1 style="
                font-weight: 300;
                font-size: 38px;
                color: #f1f1f1;
                font-family: 'Montserrat', sans-serif;
                margin: 0;
                -webkit-text-stroke: 2px #F96969;
                text-shadow: -4px -2px 0 #000000;
            ">
                FUTURE WELL
            </h1>
        </div>
    """, unsafe_allow_html=True)

st.markdown('<hr style="margin-top: 2rem;">', unsafe_allow_html=True)      
    
# --- LOGIN SETUP ---
__login__obj = __login__(
    auth_token="courier_auth_token",
    company_name="Shims",
    width=200, height=250,
    logout_button_name='Logout',
    hide_menu_bool=False,
    hide_footer_bool=False,
    lottie_url='https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json'
)

LOGGED_IN = __login__obj.build_login_ui()

# --- DASHBOARD ROUTING ---
if LOGGED_IN:
    username = st.session_state.get("USERNAME", "guest")
    role = st.session_state.get("ROLE", "user")

    # Log the login event
    log_login_event_json(username, role)

    # Route based on role
    if role == "admin":
        show_admin_dashboard(username)
    elif role == "doctor":
        show_doc_dashboard(username)
    else:
        show_user_dashboard(username)

# --- FOOTER ---
st.markdown("""
    <hr style="margin-top: 2rem;">
    <div style='text-align: center; color:black; font-size: 14px;'>
        Developed by <strong>AlphaGroup</strong> © 2025
    </div>
""", unsafe_allow_html=True)
