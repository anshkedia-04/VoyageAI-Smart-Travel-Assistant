import streamlit as st
import requests
import datetime
import re

# BASE_URL = "http://localhost:8000"  # Backend endpoint
BASE_URL = "https://voyageai-smart-travel-assistant-1.onrender.com"

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="🌍 VoyageAI - Smart Travel Planner",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🌍 VoyageAI - Smart Travel Planner")

# -------------------- CARD STYLING --------------------
st.markdown("""
    <style>
    .card-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 25px;
        margin: 30px 0;
        padding: 0 20px;
    }
    
    @media (max-width: 1400px) {
        .card-container {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    @media (max-width: 900px) {
        .card-container {
            grid-template-columns: 1fr;
        }
    }
    
    .card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 30px;
        box-shadow: 0px 8px 25px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
        min-height: 300px;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0px 12px 35px rgba(0,0,0,0.4);
    }
    
    .card-title {
        font-size: 26px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 20px;
        text-decoration: underline;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .card-text {
        font-size: 15px;
        color: #f0f0f0;
        line-height: 1.9;
        text-align: left;
    }
    
    .card-text ul {
        list-style-type: none;
        padding-left: 0;
        margin: 0;
    }
    
    .card-text li {
        margin-bottom: 14px;
        padding-left: 28px;
        position: relative;
    }
    
    .card-text li:before {
        content: "✓";
        position: absolute;
        left: 0;
        color: #ffd700;
        font-weight: bold;
        font-size: 18px;
    }
    
    .section-title {
        font-size: 32px;
        font-weight: 700;
        color: #667eea;
        margin-top: 40px;
        margin-bottom: 20px;
        text-align: center;
    }
    
    .other-content {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 25px;
        margin: 20px 0;
        color: #333;
        line-height: 1.8;
    }
    
    .other-content h3 {
        color: #667eea;
        margin-top: 25px;
        margin-bottom: 15px;
        font-size: 22px;
        font-weight: 600;
    }
    
    .other-content ul {
        padding-left: 20px;
        margin-bottom: 15px;
    }
    
    .other-content li {
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------- HELPER FUNCTION --------------------
def parse_travel_plan(answer):
    """Parse the travel plan and extract days and other sections"""
    lines = answer.split('\n')
    
    travel_days = []
    other_sections = []
    current_day = None
    current_details = []
    in_day_section = True
    
    for line in lines:
        stripped = line.strip()
        
        # Skip empty lines
        if not stripped:
            continue
        
        # Check if this is a Day heading
        day_match = re.match(r'^(Day\s+\d+):', stripped, re.IGNORECASE)
        
        if day_match:
            # Save previous day if exists
            if current_day:
                travel_days.append({
                    "title": current_day,
                    "details": current_details
                })
            
            # Start new day
            current_day = day_match.group(1)
            current_details = []
            in_day_section = True
            
        elif in_day_section and current_day:
            # Check if we've hit a non-day section header
            if re.match(r'^(Hotels?|Restaurants?|Activities?|Transportation|Cost|Weather|Budget|Per\s+Day|Total):', stripped, re.IGNORECASE):
                # Save current day and switch to other sections
                travel_days.append({
                    "title": current_day,
                    "details": current_details
                })
                current_day = None
                current_details = []
                in_day_section = False
                other_sections.append(stripped)
            else:
                # Add to current day details
                cleaned = re.sub(r'^[-•*]\s*', '', stripped)
                if cleaned:
                    current_details.append(cleaned)
        else:
            # We're past the day sections
            other_sections.append(stripped)
    
    # Save last day if not already saved
    if current_day and current_details:
        travel_days.append({
            "title": current_day,
            "details": current_details
        })
    
    return travel_days, other_sections

def format_other_sections(sections):
    """Format non-day sections with proper HTML"""
    html = '<div class="other-content">'
    current_list_open = False
    
    for line in sections:
        # Check if it's a section header
        if re.match(r'^(Hotels?|Restaurants?|Activities?|Transportation|Cost|Weather|Budget|Per\s+Day|Total):', line, re.IGNORECASE):
            if current_list_open:
                html += '</ul>'
                current_list_open = False
            html += f'<h3>{line}</h3>'
        # Check if it's a bullet point
        elif line.startswith('•') or line.startswith('-') or line.startswith('*'):
            if not current_list_open:
                html += '<ul>'
                current_list_open = True
            cleaned = re.sub(r'^[-•*]\s*', '', line)
            html += f'<li>{cleaned}</li>'
        else:
            if current_list_open:
                html += '</ul>'
                current_list_open = False
            html += f'<p>{line}</p>'
    
    if current_list_open:
        html += '</ul>'
    
    html += '</div>'
    return html

# -------------------- CHAT SYSTEM --------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

st.header("How can I help you in planning a trip? Let me know where do you want to visit.")

# User input form
with st.form(key="query_form", clear_on_submit=True):
    user_input = st.text_input("User Input", placeholder="e.g. Plan a trip to Goa for 5 days")
    submit_button = st.form_submit_button("Send")

if submit_button and user_input.strip():
    try:
        with st.spinner("🧠 Sit back and relax. I got it..."):
            payload = {"question": user_input}
            response = requests.post(f"{BASE_URL}/query", json=payload)

        if response.status_code == 200:
            answer = response.json().get("answer", "No answer returned.")
            
            # Parse the travel plan
            travel_days, other_sections = parse_travel_plan(answer)
            
            # Display travel days as cards
            if travel_days:
                st.markdown('<div class="section-title">🗓️ Your Travel Itinerary</div>', unsafe_allow_html=True)
                
                cards_html = '<div class="card-container">'
                for day in travel_days:
                    details_html = "<ul>"
                    for detail in day["details"]:
                        # Escape HTML and preserve formatting
                        detail_escaped = (detail.replace('&', '&amp;')
                                               .replace('<', '&lt;')
                                               .replace('>', '&gt;'))
                        details_html += f"<li>{detail_escaped}</li>"
                    details_html += "</ul>"
                    
                    cards_html += f"""
                        <div class="card">
                            <div class="card-title">{day["title"]}</div>
                            <div class="card-text">{details_html}</div>
                        </div>
                    """
                cards_html += '</div>'
                
                st.markdown(cards_html, unsafe_allow_html=True)
                
                # Display other sections
                if other_sections:
                    st.markdown("---")
                    other_html = format_other_sections(other_sections)
                    st.markdown(other_html, unsafe_allow_html=True)
            else:
                # Fallback: display as regular text
                st.markdown(answer)

            # Footer
            st.markdown("---")
            st.caption("⚠️ This travel plan was generated by AI. Please verify information like timings and prices before your trip.")
        else:
            st.error("Bot failed to respond: " + response.text)

    except Exception as e:
        st.error(f"⚠️ The response failed due to: {e}")