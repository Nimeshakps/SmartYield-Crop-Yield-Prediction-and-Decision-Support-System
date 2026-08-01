# """Shared UI utilities: sidebar run/model selector, metric cards, recommendation renderer."""

# import streamlit as st

# from streamlit_app import api_client
# from streamlit_app.api_client import ApiError


# def sidebar_run_model_selector():
#     """Renders the sidebar controls for choosing a week-range run and a trained model.
#     Returns (run_tag, model_name, schema) or (None, None, None) if unavailable."""
#     st.sidebar.markdown("## 🌾 Model selection")

#     if not api_client.check_backend_alive():
#         st.sidebar.error(
#             "Can't reach the backend API. Make sure it's running and that API_BASE_URL is "
#             "set correctly (see streamlit_app/config.py)."
#         )
#         return None, None, None

#     try:
#         runs = api_client.get_runs()
#     except ApiError as e:
#         st.sidebar.error(f"No models available yet: {e}")
#         return None, None, None

#     if not runs:
#         st.sidebar.warning("No runs found in model_factory yet.")
#         return None, None, None

#     run_tag = st.sidebar.selectbox("Week-range run", options=runs, key="sidebar_run_tag")

#     try:
#         models = api_client.get_models(run_tag)
#     except ApiError as e:
#         st.sidebar.error(f"Couldn't list models for '{run_tag}': {e}")
#         return run_tag, None, None

#     if not models:
#         st.sidebar.warning(f"No trained models found for run '{run_tag}'.")
#         return run_tag, None, None

#     model_name = st.sidebar.selectbox("Model", options=models, key="sidebar_model_name")

#     try:
#         schema = api_client.get_schema(run_tag, model_name)
#     except ApiError as e:
#         st.sidebar.error(f"Couldn't load schema: {e}")
#         return run_tag, model_name, None

#     st.sidebar.markdown("---")
#     st.sidebar.markdown("### 📊 Reported performance")
#     if schema.get("mean_rmse_kg_ha") is not None:
#         st.sidebar.metric("CV RMSE", f"{schema['mean_rmse_kg_ha']:,.1f} kg/ha")
#     if schema.get("mean_r2") is not None:
#         st.sidebar.metric("CV R²", f"{schema['mean_r2']:.3f}")
#     st.sidebar.caption(
#         f"Growing season: weeks {schema['season_start_week']}–{schema['season_end_week']} · "
#         f"{schema.get('n_features', '?')} trained features"
#     )

#     return run_tag, model_name, schema


# def render_prediction_metrics(result: dict):
#     col1, col2 = st.columns(2)
#     with col1:
#         st.metric("Predicted yield", f"{result['prediction_kg_ha']:,.1f} kg/ha")
#     with col2:
#         st.metric("Predicted yield", f"{result['prediction_bu_acre']:,.1f} bu/acre")


# def render_recommendations(result: dict):
#     st.markdown("#### 🎯 Baseline vs. optimized")
#     col1, col2, col3 = st.columns(3)
#     with col1:
#         st.metric("Baseline yield", f"{result['baseline_yield_kg_ha']:,.1f} kg/ha")
#     with col2:
#         st.metric("Best achievable yield", f"{result['final_yield_kg_ha']:,.1f} kg/ha",
#                    delta=f"{result['improvement_kg_ha']:,.1f} kg/ha")
#     with col3:
#         st.metric("Improvement", f"{result['improvement_pct']:,.1f}%")

#     st.info(result["message"])

#     if result["recommendations"]:
#         st.markdown("#### 🛠️ Recommended changes (in order of impact)")
#         for i, rec in enumerate(result["recommendations"], start=1):
#             arrow = "⬆️" if rec["direction"] == "increase" else ("⬇️" if rec["direction"] == "decrease" else "➡️")
#             st.markdown(
#                 f"""
#                 <div class="rec-row">
#                     <b>{i}. {rec['variable']}</b> {arrow} {rec['direction'].title()}
#                     from <b>{rec['from_value']}</b> to <b>{rec['to_value']}</b>
#                     — gain of <b>+{rec['gain_kg_ha']:,.1f} kg/ha</b>
#                     (yield after this change: {rec['yield_after_kg_ha']:,.1f} kg/ha)
#                 </div>
#                 """,
#                 unsafe_allow_html=True,
#             )



"""Shared UI utilities: sidebar run/model selector, metric cards, recommendation renderer."""

import streamlit as st

from streamlit_app import api_client
from streamlit_app.api_client import ApiError
from streamlit_app.components.forms import VARIABLE_UNITS

# Backend sends recommendation variable names already Title-Cased (e.g. "Soil Ph"), so build a
# lookup from that exact format -> unit, reusing the single VARIABLE_UNITS source of truth.
_PRETTY_TO_UNIT = {std.replace("_", " ").title(): unit for std, unit in VARIABLE_UNITS.items()}
PREFERRED_DEFAULT_MODEL = "Stacking_Ensemble"

def _with_unit(pretty_variable: str) -> str:
    unit = _PRETTY_TO_UNIT.get(pretty_variable)
    return f"{pretty_variable} ({unit})" if unit else pretty_variable


def sidebar_run_model_selector():
    """Renders the sidebar controls for choosing a week-range run and a trained model.
    Returns (run_tag, model_name, schema) or (None, None, None) if unavailable."""
    st.sidebar.markdown("## 🌾 Model selection")

    if not api_client.check_backend_alive():
        st.sidebar.error(
            "Can't reach the backend API. Make sure it's running and that API_BASE_URL is "
            "set correctly (see streamlit_app/config.py)."
        )
        return None, None, None

    try:
        runs = api_client.get_runs()
    except ApiError as e:
        st.sidebar.error(f"No models available yet: {e}")
        return None, None, None

    if not runs:
        st.sidebar.warning("No runs found in model_factory yet.")
        return None, None, None

    run_tag = st.sidebar.selectbox("Week-range run", options=runs, key="sidebar_run_tag")

    try:
        models = api_client.get_models(run_tag)
    except ApiError as e:
        st.sidebar.error(f"Couldn't list models for '{run_tag}': {e}")
        return run_tag, None, None

    if not models:
        st.sidebar.warning(f"No trained models found for run '{run_tag}'.")
        return run_tag, None, None

    # model_name = st.sidebar.selectbox("Model", options=models, key="sidebar_model_name")
    # model_name = st.sidebar.selectbox("Model", options=models, key="sidebar_model_name")
    default_index = models.index(PREFERRED_DEFAULT_MODEL) if PREFERRED_DEFAULT_MODEL in models else 0
    model_name = st.sidebar.selectbox(
        "Model", options=models, index=default_index, key="sidebar_model_name"
    )

    try:
        schema = api_client.get_schema(run_tag, model_name)
    except ApiError as e:
        st.sidebar.error(f"Couldn't load schema: {e}")
        return run_tag, model_name, None

    # st.sidebar.markdown("---")
    # st.sidebar.markdown("### 📊 Reported performance")
    # if schema.get("mean_rmse_kg_ha") is not None:
    #     st.sidebar.metric("CV RMSE", f"{schema['mean_rmse_kg_ha']:,.1f} kg/ha")
    # if schema.get("mean_r2") is not None:
    #     st.sidebar.metric("CV R²", f"{schema['mean_r2']:.3f}")
    # st.sidebar.caption(
    #     f"Growing season: weeks {schema['season_start_week']}–{schema['season_end_week']} · "
    #     f"{schema.get('n_features', '?')} trained features"
    # )
    

    return run_tag, model_name, schema


def render_prediction_metrics(result: dict):
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Predicted yield", f"{result['prediction_kg_ha']:,.1f} kg/ha")
    with col2:
        st.metric("Predicted yield", f"{result['prediction_bu_acre']:,.1f} bu/acre")


def render_recommendations(result: dict):
    st.markdown("#### 🎯 Baseline vs. optimized")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Baseline yield", f"{result['baseline_yield_kg_ha']:,.1f} kg/ha")
    with col2:
        st.metric("Best achievable yield", f"{result['final_yield_kg_ha']:,.1f} kg/ha",
                   delta=f"{result['improvement_kg_ha']:,.1f} kg/ha")
    with col3:
        st.metric("Improvement", f"{result['improvement_pct']:,.1f}%")

    st.info(result["message"])

    if result["recommendations"]:
        st.markdown("#### 🛠️ Recommended changes (in order of impact)")
        for i, rec in enumerate(result["recommendations"], start=1):
            arrow = "⬆️" if rec["direction"] == "increase" else ("⬇️" if rec["direction"] == "decrease" else "➡️")
            st.markdown(
                f"""
                <div class="rec-row">
                    <b>{i}. {_with_unit(rec['variable'])}</b> {arrow} {rec['direction'].title()}
                    from <b>{rec['from_value']}</b> to <b>{rec['to_value']}</b>
                    — gain of <b>+{rec['gain_kg_ha']:,.1f} kg/ha</b>
                    (yield after this change: {rec['yield_after_kg_ha']:,.1f} kg/ha)
                </div>
                """,
                unsafe_allow_html=True,
            )