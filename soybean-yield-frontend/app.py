"""
Soybean Yield Prediction Dashboard -- main entrypoint.

Run with:
    streamlit run streamlit_app/app.py

Uses Streamlit's multipage app support (files under `pages/`) for the two prediction phases:
    1. Predict Yield     -- raw inputs -> predicted final harvest yield
    2. Optimize Yield     -- raw inputs -> recommended changes to maximize yield
"""

import streamlit as st

from streamlit_app.theme import hero, inject_theme

st.set_page_config(
    page_title="Soybean Yield Prediction Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_theme()
hero(
    "Soybean Yield Prediction Dashboard",
    "Predict harvest yield from raw weekly weather + soil readings, and discover which "
    "controllable factors could raise it further.",
)

st.markdown(
    """
    <div class="section-card">
    <h3>👋 Welcome</h3>
    <p>This dashboard talks to the FastAPI backend that wraps the trained soybean yield models.
    Use the sidebar on each page to pick a <b>week-range run</b> (e.g. <code>weeks_14_20</code>)
    and a <b>trained model</b> (e.g. XGBoost, LightGBM, CatBoost, Stacking Ensemble).</p>
    <p>Two phases are available, in the left navigation:</p>
    <ul>
        <li><b>🌾 Predict Yield</b> — enter raw weekly weather + soil readings and get the
        model's predicted final harvest yield.</li>
        <li><b>📈 Optimize Yield</b> — starting from the same inputs, see which controllable
        factors (vapor pressure, soil pH, cation exchange capacity, total nitrogen) to change,
        and by how much, to maximize predicted yield.</li>
    </ul>
    <p>Any raw field can be left blank — it will be median-imputed automatically, exactly like
    the original notebook pipeline.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="section-card">
    <h3>⚙️ Backend connection</h3>
    <p>By default the app looks for the API at <code>http://localhost:8000</code>. To point it
    somewhere else, set the <code>API_BASE_URL</code> environment variable before launching
    Streamlit, e.g.:</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.code("export API_BASE_URL=http://localhost:8000\nstreamlit run streamlit_app/app.py", language="bash")

st.info("👈 Use the sidebar navigation to open **Predict Yield** or **Optimize Yield**.")
