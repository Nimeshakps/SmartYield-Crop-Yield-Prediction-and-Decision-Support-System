"""Custom CSS for the greenery + yellowish soybean-yield dashboard theme."""

import streamlit as st

from streamlit_app.config import COLORS

CUSTOM_CSS = f"""
<style>
:root {{
    --forest-green: {COLORS['forest_green']};
    --leaf-green: {COLORS['leaf_green']};
    --sage-green: {COLORS['sage_green']};
    --pale-green: {COLORS['pale_green']};
    --sunflower-yellow: {COLORS['sunflower_yellow']};
    --golden-yellow: {COLORS['golden_yellow']};
    --cream: {COLORS['cream']};
}}

.stApp {{
    background: linear-gradient(180deg, {COLORS['cream']} 0%, {COLORS['pale_green']} 100%);
}}

/* Header banner */
.yield-hero {{
    background: linear-gradient(120deg, var(--forest-green) 0%, var(--leaf-green) 55%, var(--sage-green) 100%);
    border-radius: 16px;
    padding: 1.6rem 2rem;
    margin-bottom: 1.4rem;
    box-shadow: 0 4px 18px rgba(47, 82, 51, 0.25);
}}
.yield-hero h1 {{
    color: var(--sunflower-yellow) !important;
    margin: 0;
    font-size: 2rem;
}}
.yield-hero p {{
    color: #F5F5E6;
    margin: 0.3rem 0 0 0;
    font-size: 1rem;
}}

/* Section cards */
.section-card {{
    background: #FFFFFF;
    border: 1px solid var(--sage-green);
    border-left: 6px solid var(--sunflower-yellow);
    border-radius: 12px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 1rem;
}}

/* Metric cards */
div[data-testid="stMetric"] {{
    background: linear-gradient(135deg, {COLORS['text_dark']} !important; 0%, #FFFDF3 100%);
    border: 1px solid var(--golden-yellow);
    border-radius: 12px;
    padding: 0.8rem 1rem 0.4rem 1rem;
}}
div[data-testid="stMetricLabel"] {{
    color: {COLORS['text_dark']} !important;
    font-weight: 600;
}}
div[data-testid="stMetricValue"] {{
    color: {COLORS['text_dark']} !important;
}}

/* Buttons */
.stButton > button, .stFormSubmitButton > button {{
    background: linear-gradient(90deg, var(--sunflower-yellow), var(--golden-yellow));
    color: var(--forest-green);
    font-weight: 700;
    border: none;
    border-radius: 999px;
    padding: 0.55rem 1.6rem;
    transition: transform 0.08s ease-in-out;
}}
.stButton > button:hover, .stFormSubmitButton > button:hover {{
    transform: translateY(-1px);
    background: linear-gradient(90deg, var(--golden-yellow), var(--sunflower-yellow));
    color: var(--forest-green);
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, var(--forest-green) 0%, var(--leaf-green) 100%);
}}
section[data-testid="stSidebar"] * {{
    color: #F5F5E6 !important;
}}
section[data-testid="stSidebar"] .stSelectbox label, section[data-testid="stSidebar"] .stRadio label {{
    color: #1F3A1F;
    font-weight: 600;
}}

/* Selectbox: force the selected value + dropdown options to black text */
section[data-testid="stSidebar"] div[data-baseweb="select"] * {{
    color: var(--text-dark, #1F3A1F) !important;
}}

/* The dropdown options list renders outside the sidebar in a portal */
div[data-baseweb="popover"] li {{
    color: {COLORS['text_dark']} !important;
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    gap: 6px;
}}
.stTabs [data-baseweb="tab"] {{
    background-color: var(--pale-green);
    border-radius: 10px 10px 0 0;
    padding: 0.5rem 1.1rem;
    color: var(--forest-green);
    font-weight: 600;
}}
.stTabs [aria-selected="true"] {{
    background-color: var(--sunflower-yellow) !important;
    color: var(--forest-green) !important;
}}

/* Headings */
h1, h2, h3 {{
    color: var(--forest-green);
}}

/* Recommendation row */
.rec-row {{
    background: #FFFDF3;
    border: 1px solid var(--sunflower-yellow);
    border-radius: 10px;
    padding: 0.7rem 1rem;
    margin-bottom: 0.5rem;
}}

/* Alert / info boxes tuned toward the palette */
div[data-testid="stAlert"] {{
    border-radius: 10px;
}}
</style>
"""


def inject_theme():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def hero(title: str, subtitle: str):
    st.markdown(
        f"""
        <div class="yield-hero">
            <h1>🌱 {title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
