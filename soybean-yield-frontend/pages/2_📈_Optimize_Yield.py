"""Phase 2 -- Optimize Yield: same raw inputs, get recommended changes to maximize yield."""

import streamlit as st

from streamlit_app.api_client import ApiError, optimize
from streamlit_app.components.forms import render_full_input_form
from streamlit_app.components.utils import render_recommendations, sidebar_run_model_selector
from streamlit_app.theme import hero, inject_theme

st.set_page_config(page_title="Optimize Yield", page_icon="📈", layout="wide")
inject_theme()
hero(
    "📈 Phase 2 — Optimize Yield",
    "Discover which controllable factors to change, and by how much, to maximize predicted yield.",
)

run_tag, model_name, schema = sidebar_run_model_selector()

if not schema:
    st.warning(
        "Select a run and model with trained artifacts in the sidebar to begin. If none are "
        "listed, make sure the `model_factory` folder has been placed in the backend."
    )
    st.stop()

controllables = schema.get("controllable_variables", [])
st.markdown(
    f"""
    <div class="section-card">
    Using model <b>{model_name}</b> trained for weeks
    <b>{schema['season_start_week']}–{schema['season_end_week']}</b>.
    Starting from your inputs below, a greedy search looks for the best value of each
    controllable factor available for this model —
    <b>{', '.join(c.replace('_', ' ').title() for c in controllables) if controllables else 'none for this run'}</b>
    — and recommends up to a handful of changes, in order of impact, to maximize predicted
    harvest yield. Precipitation and temperature are never recommended, since this crop is
    grown in an open, uncontrolled environment.
    </div>
    """,
    unsafe_allow_html=True,
)

raw_row = render_full_input_form(schema, key_prefix="optimize")

st.markdown("#### ⚙️ Search settings")
col1, col2, col3 = st.columns(3)
with col1:
    max_recommendations = st.slider("Max recommendations", min_value=1, max_value=len(controllables) or 4,
                                     value=min(4, len(controllables) or 4))
with col2:
    grid_points = st.slider("Search resolution (grid points)", min_value=5, max_value=50, value=25)
with col3:
    min_gain = st.number_input("Minimum meaningful gain (kg/ha)", min_value=0.0, value=1.0, step=0.5)

st.markdown("---")
if st.button("📈 Get Recommendations", type="primary", use_container_width=True):
    if not controllables:
        st.warning("No controllable variables are active for this run/model — nothing to optimize.")
    else:
        with st.spinner("Searching controllable factors for the best achievable yield..."):
            try:
                result = optimize(
                    run_tag, model_name, raw_row,
                    max_recommendations=max_recommendations,
                    grid_points=grid_points,
                    min_meaningful_gain_kg_ha=min_gain,
                )
            except ApiError as e:
                st.error(f"Optimization failed: {e}")
            else:
                st.success("Optimization complete!")
                render_recommendations(result)
