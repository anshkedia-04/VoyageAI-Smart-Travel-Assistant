from __future__ import annotations

import datetime
import html
import re

import pandas as pd
import plotly.express as px
import streamlit as st

from ui.client import (
    DEFAULT_CLOUD_URL,
    DEFAULT_LOCAL_URL,
    check_backend_health,
    get_default_backend_url,
    query_direct_llm,
    query_travel_backend,
)
from ui.parser import (
    compose_travel_prompt,
    estimate_trip_budget,
    format_inline_markdown_safe,
    parse_travel_plan,
)
from ui.styles import VOYAGE_CSS

st.set_page_config(
    page_title="VoyageAI · Smart Travel Concierge",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(VOYAGE_CSS, unsafe_allow_html=True)

CURATED_PRESETS = {
    "Goa · 4D": {
        "destination": "Goa, India",
        "days": 4,
        "travelers": 2,
        "budget": "Mid-Range Comfort",
        "currency": "INR",
        "interests": ["Beaches & Relaxation", "Food & Local Cafés", "Off-Beat Gems"],
    },
    "Switzerland · 5D": {
        "destination": "Lucerne & Interlaken, Switzerland",
        "days": 5,
        "travelers": 2,
        "budget": "Luxury & Boutique",
        "currency": "EUR",
        "interests": ["Nature & Scenic", "Culture & Heritage", "Off-Beat Gems"],
    },
    "Tokyo · 6D": {
        "destination": "Tokyo & Hakone, Japan",
        "days": 6,
        "travelers": 2,
        "budget": "Mid-Range Comfort",
        "currency": "USD",
        "interests": ["Culture & Heritage", "Food & Local Cafés", "Nightlife & Shopping"],
    },
    "Manali · 4D": {
        "destination": "Manali & Solang Valley, Himachal Pradesh",
        "days": 4,
        "travelers": 4,
        "budget": "Backpacker / Value",
        "currency": "INR",
        "interests": ["Adventure & Outdoors", "Nature & Scenic", "Off-Beat Gems"],
    },
    "Paris · 4D": {
        "destination": "Paris, France",
        "days": 4,
        "travelers": 2,
        "budget": "Mid-Range Comfort",
        "currency": "EUR",
        "interests": ["Culture & Heritage", "Food & Local Cafés", "Nightlife & Shopping"],
    },
    "Bali · 5D": {
        "destination": "Ubud & Uluwatu, Bali",
        "days": 5,
        "travelers": 2,
        "budget": "Mid-Range Comfort",
        "currency": "USD",
        "interests": ["Beaches & Relaxation", "Nature & Scenic", "Culture & Heritage"],
    },
}

SAMPLE_PREVIEW_ANSWER = """### Day 1: Lakeside Heritage & Old City Walk
- Arrive in Udaipur and check into a heritage haveli near Lal Ghat overlooking Lake Pichola.
- Afternoon guided walk through City Palace Museum and Jagdish Temple.
- Sunset boat cruise on Lake Pichola past Jag Mandir, followed by rooftop dinner at Ambrai Ghat.

### Day 2: Monsoon Palace, Crafts & Cultural Evening
- Morning drive up to Sajjangarh (Monsoon Palace) for panoramic Aravalli valley views.
- Visit Shilpgram rural arts & crafts village and Bagore Ki Haveli.
- Evening folk performance at Dharohar followed by traditional Rajasthani thali dining.

### Day 3: Off-Beat Day Trip to Badi Lake & Bahubali Hills
- Early sunrise trek up Bahubali Hills overlooking the tranquil waters of Badi Lake.
- Quiet lakeside coffee stop away from main tourist crowds and return for Fateh Sagar promenade.
- Depart with local block-print souvenirs from Hathi Pol Bazaar.

Hotels:
- Taj Lake Palace (Luxury): ₹ 38,000 – ₹ 55,000 / night
- Jagat Niwas Palace (Mid-Range Heritage): ₹ 7,500 – ₹ 12,000 / night
- Zostel Udaipur (Backpacker): ₹ 900 – ₹ 2,200 / night

Restaurants:
- Ambrai (Lakeside Rajasthani & North Indian): ₹ 1,800 for two
- Millets of Mewar (Healthy local café): ₹ 900 for two
- Upré by 1559 AD (Rooftop sunset dining): ₹ 2,400 for two

Transportation:
- Auto-rickshaws & app cabs for intra-city hops (₹ 150–₹ 350 per ride); private cab for Badi Lake (~₹ 1,600 half-day).

Cost Breakdown:
- Stay (2 nights mid-range): ₹ 18,000
- Meals & Cafés: ₹ 7,500
- Entry Tickets, Boat & Local Transit: ₹ 5,200

Per Day Expense Budget:
- Approx. ₹ 7,675 per person per day (Mid-Range Comfort)

Weather:
- Clear skies, daytime highs around 26–30°C and pleasant evenings near 16–19°C.
"""


def _init_session_state() -> None:
    defaults = {
        "vy_destination": "Goa, India",
        "vy_days": 4,
        "vy_travelers": 2,
        "vy_budget": "Mid-Range Comfort",
        "vy_currency": "INR",
        "vy_interests": ["Beaches & Relaxation", "Food & Local Cafés", "Off-Beat Gems"],
        "vy_history": [],
        "vy_active_trip_idx": None,
        "vy_backend_status": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def _apply_preset(preset_name: str) -> None:
    preset = CURATED_PRESETS[preset_name]
    st.session_state["vy_destination"] = preset["destination"]
    st.session_state["vy_days"] = preset["days"]
    st.session_state["vy_travelers"] = preset["travelers"]
    st.session_state["vy_budget"] = preset["budget"]
    st.session_state["vy_currency"] = preset["currency"]
    st.session_state["vy_interests"] = list(preset["interests"])


def _render_hero() -> None:
    status = st.session_state.get("vy_backend_status")
    if status is True:
        status_pill = '<div class="vy-pill vy-pill-online">● API Online</div>'
    elif status is False:
        status_pill = '<div class="vy-pill vy-pill-offline">○ API Sleeping / Offline</div>'
    else:
        status_pill = '<div class="vy-pill">LangGraph Multi-Agent</div>'

    st.markdown(
        f"""
        <div class="vy-hero">
            <div class="vy-brand">
                <div class="vy-badge-icon">VA</div>
                <div>
                    <h1 class="vy-title">VoyageAI Travel Concierge</h1>
                    <p class="vy-subtitle">
                        Agentic Itinerary Architect · Live Weather, Curated Places &amp; Cost Breakdown
                    </p>
                </div>
            </div>
            <div class="vy-pills">
                {status_pill}
                <div class="vy-pill">Classic + Off-Beat Plans</div>
                <div class="vy-pill">Real-Time Tooling</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_itinerary_view(
    title: str,
    subtitle: str,
    raw_answer: str,
    is_sample: bool = False,
) -> None:
    parsed = parse_travel_plan(raw_answer)

    head_col, dl_col = st.columns([2.2, 1.0])
    with head_col:
        badge = "Sample Dossier Preview" if is_sample else "Generated Itinerary"
        st.caption(badge)
        st.subheader(title)
        st.caption(subtitle)
    with dl_col:
        safe_slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_") or "trip"
        st.download_button(
            "Download Markdown (.md)",
            data=raw_answer,
            file_name=f"voyageai_{safe_slug}.md",
            mime="text/markdown",
            width="stretch",
        )

    if parsed.intro_lines:
        intro_html = "<br>".join(format_inline_markdown_safe(line) for line in parsed.intro_lines[:4])
        st.markdown(
            f'<div class="vy-info-card"><div class="vy-info-body">{intro_html}</div></div>',
            unsafe_allow_html=True,
        )

    if parsed.days:
        cards_chunks = ['<div class="vy-days-grid">']
        for day in parsed.days:
            items_html = "".join(
                f"<li>{format_inline_markdown_safe(item)}</li>" for item in day.items
            )
            if not items_html:
                items_html = "<li>Flexible exploration &amp; local dining.</li>"
            cards_chunks.append(
                f"""
                <div class="vy-day-card">
                    <div class="vy-day-header">
                        <span class="vy-day-badge">Day {html.escape(day.day_number)}</span>
                        <h4 class="vy-day-title">{html.escape(day.title)}</h4>
                    </div>
                    <ul class="vy-day-list">{items_html}</ul>
                </div>
                """
            )
        cards_chunks.append("</div>")
        st.markdown("".join(cards_chunks), unsafe_allow_html=True)

    if parsed.sections:
        st.markdown("#### Stays, Dining, Transit & Budget")
        sec_cols = st.columns(2, gap="medium")
        for idx, section in enumerate(parsed.sections):
            bullets: list[str] = []
            paragraphs: list[str] = []
            for line in section.lines:
                if line.startswith(("- ", "• ", "* ")):
                    bullets.append(f"<li>{format_inline_markdown_safe(line[2:].strip())}</li>")
                else:
                    paragraphs.append(f"<p style='margin:0 0 0.35rem 0;'>{format_inline_markdown_safe(line)}</p>")

            body_html = "".join(paragraphs)
            if bullets:
                body_html += f"<ul>{''.join(bullets)}</ul>"
            if not body_html:
                body_html = "<p>Details included in full brief below.</p>"

            sec_cols[idx % 2].markdown(
                f"""
                <div class="vy-info-card">
                    <div class="vy-info-title">{html.escape(section.heading)}</div>
                    <div class="vy-info-body">{body_html}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if not parsed.days and not parsed.sections:
        st.markdown(raw_answer)

    with st.expander("View Full Raw Markdown Response", expanded=False):
        st.markdown(raw_answer)

    st.caption(
        "AI-generated itinerary: verify seasonal opening hours, transit schedules, and live rates before booking."
    )


def _render_planner_tab() -> None:
    col_left, col_right = st.columns([1.05, 1.55], gap="large")

    with col_left:
        st.markdown(
            """
            <div class="vy-panel-box">
                <p class="vy-panel-title">Craft Your Trip Brief</p>
                <p class="vy-panel-sub">
                    Pick a curated getaway or customize destination, pace, and budget.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption("Curated quick-start getaways")
        preset_names = list(CURATED_PRESETS.keys())
        p_cols = st.columns(3)
        for idx, name in enumerate(preset_names):
            if p_cols[idx % 3].button(name, key=f"preset_{idx}", width="stretch"):
                _apply_preset(name)

        destination = st.text_input(
            "Destination",
            key="vy_destination",
            placeholder="e.g. Kyoto, Japan or Udaipur, Rajasthan",
        )

        c1, c2 = st.columns(2)
        with c1:
            days = st.number_input("Days", min_value=1, max_value=14, key="vy_days")
        with c2:
            travelers = st.number_input("Travelers", min_value=1, max_value=12, key="vy_travelers")

        c3, c4 = st.columns(2)
        with c3:
            budget = st.selectbox(
                "Budget Tier",
                options=["Backpacker / Value", "Mid-Range Comfort", "Luxury & Boutique"],
                key="vy_budget",
            )
        with c4:
            currency = st.selectbox(
                "Currency",
                options=["INR", "USD", "EUR", "GBP", "JPY"],
                key="vy_currency",
            )

        interests = st.multiselect(
            "Travel Style & Interests",
            options=[
                "Culture & Heritage",
                "Food & Local Cafés",
                "Nature & Scenic",
                "Beaches & Relaxation",
                "Adventure & Outdoors",
                "Nightlife & Shopping",
                "Off-Beat Gems",
            ],
            key="vy_interests",
        )

        include_offbeat = st.checkbox(
            "Include off-beat hidden gems alongside classic landmarks",
            value=True,
        )

        custom_notes = st.text_area(
            "Special Requests or Custom Prompt (Optional)",
            placeholder="e.g. Vegetarian-friendly dining, scenic rail routes, stroller-accessible spots...",
            height=80,
        )

        with st.expander("Backend & Model Connection", expanded=False):
            configured_backend = get_default_backend_url()
            try:
                secret_url = str(st.secrets.get("VOYAGEAI_BACKEND_URL", "")).strip()
                if secret_url:
                    configured_backend = secret_url.rstrip("/")
            except Exception:
                pass

            primary_label = (
                "Configured Backend"
                if configured_backend != DEFAULT_CLOUD_URL
                else "Cloud API (Render)"
            )
            endpoint_choice = st.radio(
                "Execution Mode",
                options=[
                    primary_label,
                    "Localhost (:8000)",
                    "Direct API (Groq / OpenAI)",
                    "Custom URL",
                ],
                index=0,
            )
            direct_api_key = ""
            base_url = configured_backend
            model_provider = st.selectbox("LLM Provider", options=["groq", "openai"], index=0)

            if endpoint_choice == "Direct API (Groq / OpenAI)":
                secret_name = "GROQ_API_KEY" if model_provider == "groq" else "OPENAI_API_KEY"
                default_secret = ""
                try:
                    default_secret = str(st.secrets.get(secret_name, ""))
                except Exception:
                    default_secret = ""
                direct_api_key = st.text_input(
                    f"{model_provider.upper()} API Key",
                    value=default_secret,
                    type="password",
                    help="Used directly from Streamlit without needing the Render backend.",
                )
            else:
                if endpoint_choice == primary_label:
                    base_url = configured_backend
                elif endpoint_choice == "Localhost (:8000)":
                    base_url = DEFAULT_LOCAL_URL
                else:
                    base_url = st.text_input("Custom Backend URL", value=DEFAULT_LOCAL_URL)

                if st.button("Check / Wake Backend", width="stretch"):
                    with st.spinner("Pinging VoyageAI backend..."):
                        ok, msg = check_backend_health(base_url, timeout=15)
                    st.session_state["vy_backend_status"] = ok
                    if ok:
                        st.success(msg)
                    else:
                        st.warning(msg)

        generate_clicked = st.button(
            "Generate Travel Plan",
            type="primary",
            width="stretch",
        )

    if generate_clicked:
        if not destination.strip():
            st.error("Please enter a destination before generating a travel plan.")
        else:
            prompt = compose_travel_prompt(
                destination=destination,
                days=int(days),
                travelers=int(travelers),
                budget_tier=budget,
                currency=currency,
                interests=interests,
                include_offbeat=include_offbeat,
                custom_notes=custom_notes,
            )
            with st.spinner("Planning itinerary, checking weather & local spots..."):
                if endpoint_choice == "Direct API (Groq / OpenAI)":
                    ok, result_text = query_direct_llm(
                        provider=model_provider,
                        api_key=direct_api_key,
                        question=prompt,
                    )
                else:
                    ok, result_text = query_travel_backend(
                        base_url=base_url,
                        question=prompt,
                        model_provider=model_provider,
                    )
            st.session_state["vy_backend_status"] = ok
            if ok:
                trip_record = {
                    "title": f"{destination.strip()} ({int(days)} Days)",
                    "subtitle": (
                        f"{int(travelers)} {'Traveler' if travelers == 1 else 'Travelers'} · "
                        f"{budget} · {currency} · Generated {datetime.datetime.now().strftime('%H:%M')}"
                    ),
                    "answer": result_text,
                    "prompt": prompt,
                }
                st.session_state["vy_history"].insert(0, trip_record)
                st.session_state["vy_active_trip_idx"] = 0
            else:
                st.error(result_text)

    with col_right:
        history = st.session_state["vy_history"]
        if history:
            if len(history) > 1:
                labels = [f"{i + 1}. {item['title']}" for i, item in enumerate(history)]
                selected = st.selectbox(
                    "Saved Trips in This Session",
                    options=list(range(len(history))),
                    format_func=lambda idx: labels[idx],
                    index=st.session_state.get("vy_active_trip_idx") or 0,
                )
                st.session_state["vy_active_trip_idx"] = selected

            active_trip = history[st.session_state.get("vy_active_trip_idx") or 0]
            _render_itinerary_view(
                title=active_trip["title"],
                subtitle=active_trip["subtitle"],
                raw_answer=active_trip["answer"],
                is_sample=False,
            )
        else:
            st.markdown(
                """
                <div class="vy-welcome-card">
                    <div class="vy-welcome-title">Ready for your next departure</div>
                    <div class="vy-welcome-text">
                        Configure your trip on the left and click <strong>Generate Travel Plan</strong>
                        to query the live LangGraph travel agent. Below is a live sample dossier showing
                        how your day-by-day cards, dining picks, and cost breakdown are formatted.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.write("")
            _render_itinerary_view(
                title="Udaipur & Badi Lake (3 Days)",
                subtitle="2 Travelers · Mid-Range Comfort · INR · Layout Preview",
                raw_answer=SAMPLE_PREVIEW_ANSWER,
                is_sample=True,
            )


def _render_toolkit_tab() -> None:
    st.subheader("Interactive Trip Budget & Packing Planner")
    st.caption("Estimate total trip spend by category and track pre-departure essentials offline.")

    left, right = st.columns([1.1, 1.1], gap="large")

    with left:
        st.markdown("#### Cost Breakdown Estimator")
        c1, c2, c3 = st.columns(3)
        t_days = c1.number_input("Trip Days", min_value=2, max_value=30, value=5, key="tk_days")
        t_travelers = c2.number_input("Travelers", min_value=1, max_value=15, value=2, key="tk_trav")
        t_symbol = c3.selectbox("Symbol", options=["₹", "$", "€", "£"], index=0, key="tk_sym")

        s1, s2 = st.columns(2)
        stay_night = s1.number_input("Stay / Night (Group)", min_value=0.0, value=6500.0, step=500.0)
        transport_total = s2.number_input("Flights & Transit (Group)", min_value=0.0, value=18000.0, step=1000.0)

        s3, s4 = st.columns(2)
        food_day = s3.number_input("Food / Person / Day", min_value=0.0, value=1500.0, step=250.0)
        act_day = s4.number_input("Activities / Person / Day", min_value=0.0, value=1200.0, step=250.0)

        breakdown = estimate_trip_budget(
            days=int(t_days),
            travelers=int(t_travelers),
            stay_per_night=float(stay_night),
            food_per_person_day=float(food_day),
            activities_per_person_day=float(act_day),
            transport_total=float(transport_total),
        )

        m1, m2 = st.columns(2)
        m1.metric("Total Trip Estimate", f"{t_symbol} {breakdown['Total Estimated']:,.0f}")
        m2.metric("Per Traveler", f"{t_symbol} {breakdown['Per Person']:,.0f}")

        chart_df = pd.DataFrame(
            {
                "Category": [
                    "Stay & Lodging",
                    "Dining & Food",
                    "Activities & Entry",
                    "Flights & Local Transit",
                ],
                "Amount": [
                    breakdown["Stay & Lodging"],
                    breakdown["Dining & Food"],
                    breakdown["Activities & Entry"],
                    breakdown["Flights & Local Transit"],
                ],
            }
        )
        fig = px.pie(
            chart_df,
            names="Category",
            values="Amount",
            hole=0.52,
            color_discrete_sequence=["#0B2545", "#0F766E", "#D97706", "#64748B"],
            title="Estimated Spend Distribution",
        )
        fig.update_layout(height=320, margin=dict(l=12, r=12, t=42, b=12))
        st.plotly_chart(fig, width="stretch")

    with right:
        st.markdown("#### Pre-Departure Packing Checklist")
        checklist_groups = {
            "Documents & Finance": [
                "Passport / Government ID & digital backups",
                "Boarding passes, hotel confirmations & travel insurance",
                "Forex card / local cash & international roaming check",
            ],
            "Tech & Connectivity": [
                "Universal power adapter & multi-port charger",
                "Power bank (cabin luggage) & offline Google Maps downloaded",
            ],
            "Clothing & Health": [
                "Weather-layered outfits & comfortable walking shoes",
                "First-aid kit, prescription meds & sunscreen",
            ],
        }
        total_items = sum(len(v) for v in checklist_groups.values())
        checked_count = 0
        for group_name, items in checklist_groups.items():
            st.markdown(f"**{group_name}**")
            for idx, item in enumerate(items):
                if st.checkbox(item, key=f"pack_{group_name}_{idx}"):
                    checked_count += 1

        progress = checked_count / max(total_items, 1)
        st.progress(progress, text=f"Packing readiness: {checked_count}/{total_items} items ready")


def _render_architecture_tab() -> None:
    st.subheader("VoyageAI Multi-Agent Architecture & API")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Orchestration", "LangGraph ReAct")
    k2.metric("API Layer", "FastAPI + Uvicorn")
    k3.metric("Default Groq Model", "llama-3.3-70b-versatile")
    k4.metric("OpenAI Option", "o4-mini")

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("#### Agent Tooling Pipeline")
        st.markdown(
            """
            1. **WeatherInfoTool**: Fetches current conditions & multi-day forecasts (`OpenWeatherMap`).
            2. **PlaceSearchTool**: Queries attractions, dining, activities & transit (`Geoapify` with `Tavily` fallback).
            3. **CalculatorTool**: Computes lodging, per-day, and total trip arithmetic accurately.
            4. **CurrencyConverterTool**: Converts budgets across international currencies.
            """
        )

    with c2:
        st.markdown("#### Backend API Endpoints")
        st.code(
            "GET  /health   -> {\"status\": \"ok\", \"groq_configured\": true, ...}\n"
            "POST /query    -> {\"question\": \"Plan 4 days in Goa\", \"model_provider\": \"groq\"}\n"
            "                 returns {\"answer\": \"...markdown itinerary...\"}",
            language="text",
        )
        st.markdown("#### Run Full Stack Locally")
        st.code(
            "uvicorn main:app --reload --port 8000\n"
            "streamlit run streamlit_app.py",
            language="bash",
        )


def main() -> None:
    _init_session_state()
    _render_hero()

    tab_planner, tab_toolkit, tab_arch = st.tabs(
        [
            "Trip Planner",
            "Budget & Packing Toolkit",
            "Agent Architecture & API",
        ]
    )

    with tab_planner:
        _render_planner_tab()

    with tab_toolkit:
        _render_toolkit_tab()

    with tab_arch:
        _render_architecture_tab()


if __name__ == "__main__":
    main()