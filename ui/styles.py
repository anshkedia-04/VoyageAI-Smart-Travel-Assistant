"""Modern coastal-editorial travel concierge CSS for VoyageAI."""

VOYAGE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

:root {
    --vy-navy: #0B2545;
    --vy-teal: #0F766E;
    --vy-teal-soft: #ECFDF5;
    --vy-coral: #D97706;
    --vy-bg: #F7FAFC;
    --vy-surface: #FFFFFF;
    --vy-border: #E2E8F0;
    --vy-muted: #475569;
    --vy-subtle: #64748B;
}

.stApp {
    background-color: var(--vy-bg);
    color: var(--vy-navy);
}

.block-container {
    padding-top: 1.6rem !important;
    padding-bottom: 3rem !important;
    max-width: 1260px !important;
}

h1, h2, h3, h4 {
    font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--vy-navy);
    letter-spacing: -0.02em;
}

p, label, li, td, th, .stMarkdown, .stCaption {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

footer {visibility: hidden;}
#MainMenu {visibility: hidden;}

/* Hero Banner */
.vy-hero {
    background: linear-gradient(125deg, #0B2545 0%, #134E4A 65%, #0F766E 100%);
    border-radius: 18px;
    padding: 1.7rem 2rem;
    margin-bottom: 1.3rem;
    color: #FFFFFF;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1.25rem;
    box-shadow: 0 14px 32px -14px rgba(11, 37, 69, 0.35);
    border: 1px solid rgba(255, 255, 255, 0.12);
}

.vy-brand {
    display: flex;
    align-items: center;
    gap: 0.9rem;
}

.vy-badge-icon {
    width: 46px;
    height: 46px;
    border-radius: 12px;
    background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 1.15rem;
    color: #0B2545;
    font-family: 'Plus Jakarta Sans', sans-serif;
    box-shadow: 0 6px 18px -4px rgba(245, 158, 11, 0.55);
    flex-shrink: 0;
}

.vy-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    margin: 0;
    color: #FFFFFF;
    line-height: 1.15;
}

.vy-subtitle {
    margin: 0.25rem 0 0 0;
    font-size: 0.9rem;
    color: #CCFBF1;
    font-weight: 400;
}

.vy-pills {
    display: flex;
    gap: 0.55rem;
    flex-wrap: wrap;
    align-items: center;
}

.vy-pill {
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 999px;
    padding: 0.38rem 0.85rem;
    font-size: 0.78rem;
    color: #F0FDFA;
    font-weight: 500;
    white-space: nowrap;
}

.vy-pill-online {
    background: rgba(16, 185, 129, 0.22);
    border-color: rgba(110, 231, 183, 0.45);
    color: #ECFDF5;
}

.vy-pill-offline {
    background: rgba(245, 158, 11, 0.22);
    border-color: rgba(252, 211, 77, 0.45);
    color: #FEF3C7;
}

/* Panel Headers */
.vy-panel-box {
    background: var(--vy-surface);
    border: 1px solid var(--vy-border);
    border-radius: 14px;
    padding: 1.2rem 1.35rem;
    margin-bottom: 0.9rem;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
}

.vy-panel-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.98rem;
    font-weight: 700;
    color: var(--vy-navy);
    margin: 0 0 0.2rem 0;
}

.vy-panel-sub {
    font-size: 0.82rem;
    color: var(--vy-subtle);
    margin: 0;
}

/* Itinerary Day Cards */
.vy-days-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1rem;
    margin: 0.75rem 0 1.25rem 0;
}

@media (max-width: 980px) {
    .vy-days-grid {
        grid-template-columns: 1fr;
    }
}

.vy-day-card {
    background: var(--vy-surface);
    border: 1px solid var(--vy-border);
    border-top: 4px solid var(--vy-teal);
    border-radius: 14px;
    padding: 1.2rem 1.3rem;
    box-shadow: 0 4px 14px -6px rgba(11, 37, 69, 0.08);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.vy-day-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 24px -10px rgba(11, 37, 69, 0.16);
}

.vy-day-header {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    margin-bottom: 0.75rem;
    padding-bottom: 0.65rem;
    border-bottom: 1px solid #F1F5F9;
}

.vy-day-badge {
    background: #CCFBF1;
    color: #0F766E;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.74rem;
    font-weight: 700;
    padding: 0.26rem 0.58rem;
    border-radius: 999px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    flex-shrink: 0;
}

.vy-day-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: var(--vy-navy);
    margin: 0;
}

.vy-day-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.vy-day-list li {
    position: relative;
    padding-left: 1.15rem;
    margin-bottom: 0.5rem;
    font-size: 0.88rem;
    line-height: 1.55;
    color: #334155;
}

.vy-day-list li::before {
    content: "•";
    position: absolute;
    left: 0;
    color: var(--vy-coral);
    font-weight: 800;
}

/* Logistics Cards */
.vy-info-card {
    background: var(--vy-surface);
    border: 1px solid var(--vy-border);
    border-left: 4px solid #0B2545;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.85rem;
}

.vy-info-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--vy-navy);
    margin: 0 0 0.45rem 0;
}

.vy-info-body {
    font-size: 0.88rem;
    color: #334155;
    line-height: 1.6;
}

.vy-info-body ul {
    margin: 0.35rem 0 0 1.1rem;
    padding: 0;
}

.vy-info-body li {
    margin-bottom: 0.35rem;
}

/* Welcome / Empty State */
.vy-welcome-card {
    background: linear-gradient(135deg, #FFFFFF 0%, #F0FDFA 100%);
    border: 1px dashed #99F6E4;
    border-radius: 16px;
    padding: 2rem;
    text-align: left;
}

.vy-welcome-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.25rem;
    font-weight: 800;
    color: var(--vy-navy);
    margin-bottom: 0.45rem;
}

.vy-welcome-text {
    color: var(--vy-muted);
    font-size: 0.92rem;
    line-height: 1.6;
    margin-bottom: 1rem;
}

/* Tabs & Buttons */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.45rem;
    background: #FFFFFF;
    padding: 0.35rem;
    border-radius: 12px;
    border: 1px solid var(--vy-border);
    margin-bottom: 1.15rem;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 0.48rem 1rem;
    font-weight: 600;
    font-size: 0.9rem;
    color: var(--vy-muted);
}

.stTabs [aria-selected="true"] {
    background-color: var(--vy-navy) !important;
    color: #FFFFFF !important;
}

div.stButton > button[kind="primary"],
div.stFormSubmitButton > button {
    background: linear-gradient(135deg, #0F766E 0%, #0D9488 100%);
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    box-shadow: 0 6px 16px -6px rgba(15, 118, 110, 0.55);
}

div.stButton > button[kind="primary"]:hover,
div.stFormSubmitButton > button:hover {
    background: linear-gradient(135deg, #0D655E 0%, #0B7A70 100%);
}
</style>
"""
