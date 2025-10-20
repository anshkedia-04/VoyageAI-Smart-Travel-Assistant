import streamlit as st
import requests
import datetime
from PIL import Image
import base64

BASE_URL = "http://localhost:8000"  # Backend endpoint

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="🌍 VoyageAI - Smart Travel Planner",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------- LOAD & ENCODE BACKGROUND -----------------
def add_bg_image(image_file):
    with open(image_file, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )



# Call background function
try:
    add_bg_image("Banner.png")
except FileNotFoundError:
    st.warning("⚠️ Banner image not found. Please make sure 'Banner.png' is in the same directory as your Streamlit app.")

# ----------------- CUSTOM CSS -----------------
st.markdown(
    """
    <style>
    body {
        font-family: 'Poppins', sans-serif;
        color: #1a1a1a;
    }

    /* Glassmorphic Main Box */
    .response-box {
        background: rgba(255, 255, 255, 0.35);
        box-shadow: 0 8px 25px rgba(0, 0, 60, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 18px;
        border: 1px solid rgba(255, 255, 255, 0.4);
        padding: 30px;
        margin-top: 20px;
        color: #111827;
        font-size: 1rem;
        line-height: 1.7;
    }

    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #004aad, #007bff);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 10px rgba(0,0,80,0.2);
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #005ce6, #3399ff);
        transform: translateY(-2px);
        box-shadow: 0 6px 14px rgba(0,0,80,0.3);
    }

    input {
        border-radius: 10px !important;
        border: 1px solid #aac6ff !important;
        background-color: #ffffff !important;
        color: #111827 !important;
        box-shadow: 0 1px 4px rgba(0,0,80,0.1);
    }

    h1, h2, h3 {
        color: #ffffff;
        font-weight: 700;
        text-shadow: 0 2px 10px rgba(0,0,0,0.4);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #004aad 0%, #0066cc 100%);
        color: white;
    }
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p {
        color: white;
    }
    [data-testid="stSidebar"] a {
        color: #e0f0ff !important;
        text-decoration: none;
        font-weight: 600;
    }
    [data-testid="stSidebar"] a:hover {
        color: #ffffff !important;
        text-decoration: underline;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------- SIDEBAR -----------------
st.sidebar.title("🧭 VoyageAI")
st.sidebar.markdown("Your **AI-powered travel companion** ✈️")
st.sidebar.divider()
st.sidebar.markdown("**👨‍💻 Developed by:** Ansh Kedia")
st.sidebar.markdown("**📞 Contact No.:** +91-8758838722")

st.sidebar.markdown(
    """
    <a href="mailto:anshkedia.04@gmail.com" target="_blank">
        <button style="
            background: linear-gradient(135deg, #00b4d8, #0077b6);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 10px 22px;
            font-size: 1rem;
            cursor: pointer;
            width: 100%;
            font-weight: 600;
            box-shadow: 0 4px 10px rgba(0,0,60,0.2);
        ">
            📧 Contact via Email
        </button>
    </a>
    """,
    unsafe_allow_html=True
)

# ----------------- HERO SECTION -----------------
st.markdown(
    """
    <div style="
        text-align: center;
        padding: 80px 20px 60px 20px;
    ">
        <h1>🌍 Welcome to VoyageAI</h1>
        <p style="color: #e0ecff; font-size: 1.2rem; font-weight: 400;">
            Your smart travel assistant — plan smarter, travel happier.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------- MAIN CONTENT -----------------
st.header("✨ Plan your perfect trip effortlessly")
st.write("Describe your dream vacation, and VoyageAI will craft a personalized plan for you in seconds — smarter, simpler, and beautifully designed.")

# Input form
with st.form(key="query_form", clear_on_submit=True):
    user_input = st.text_input(
        "✈️ Tell us about your trip:",
        placeholder="e.g. Plan a 5-day trip to Udaipur"
    )
    submit_button = st.form_submit_button("Generate Plan")

# Handle response
if submit_button and user_input.strip():
    try:
        with st.spinner("🤔 VoyageAI is crafting your travel plan..."):
            payload = {"question": user_input}
            response = requests.post(f"{BASE_URL}/query", json=payload)

        if response.status_code == 200:
            answer = response.json().get("answer", "No answer returned.")

            st.subheader("📋 Your Personalized Travel Plan")
            st.write(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d at %H:%M')}")

            st.markdown(
                f"""
                <div class="response-box">
                    {answer}
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                ---
                *This plan was generated by VoyageAI. Please verify travel details, timings, and costs before booking.*
                """
            )
        else:
            st.error("❌ VoyageAI could not generate your plan: " + response.text)

    except Exception as e:
        st.error(f"⚠️ The response failed due to {e}")
