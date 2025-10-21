import streamlit as st

# Page setup
st.set_page_config(page_title="Card Example", layout="centered")

# Custom CSS for card styling
st.markdown("""
    <style>
    .card {
        background-color: #ffffff10;
        backdrop-filter: blur(10px);
        border: 1px solid #ffffff30;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
        text-align: center;
        width: 300px;
        margin: auto;
        transition: 0.3s;
    }
    .card:hover {
        transform: scale(1.03);
        box-shadow: 0px 6px 20px rgba(0,0,0,0.3);
    }
    .card-title {
        font-size: 22px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 10px;
    }
    .card-text {
        font-size: 16px;
        color: #dddddd;
        margin-bottom: 15px;
    }
    
    </style>
""", unsafe_allow_html=True)

# Card content
st.markdown("""
    <div class="card">
        <div class="card-title">🌍 VoyageAI</div>
        <div class="card-text">Your smart travel planner that creates personalized itineraries using AI.</div>
    </div>
""", unsafe_allow_html=True)
