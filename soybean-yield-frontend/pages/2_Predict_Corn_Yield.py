"""Predict Yield + Optimize Yield combined workflow."""

import streamlit as st

from streamlit_app.api_client import ApiError, predict, optimize, predict_corn
from streamlit_app.components.forms import render_full_input_form
from streamlit_app.components.utils import (
    render_prediction_metrics,
    render_recommendations,
    sidebar_run_model_selector,
    sidebar_run_model_selector_corn,
)
from streamlit_app.theme import hero, inject_theme


st.set_page_config(
    page_title="Yield Prediction System",
    page_icon="🌾",
    layout="wide"
)

inject_theme()

hero(
    " SmartYield - Predict Your Corn Yield",
    "Predict final harvest yield and optimize controllable factors for higher yield."
)


# ---------------------------------------------------------
# Sidebar model selector
# ---------------------------------------------------------

run_tag, model_name, schema = sidebar_run_model_selector_corn()

import os

IMAGE_PATH = os.path.join(os.path.dirname(__file__), "corn.jpg")

st.sidebar.image(IMAGE_PATH, use_container_width=True, caption="")

if not schema:
    st.warning(
        "Select a run and model with trained artifacts in the sidebar to begin."
    )
    st.stop()


# ---------------------------------------------------------
# Description
# ---------------------------------------------------------

controllables = schema.get("controllable_variables", [])

st.markdown(
    f"""
    <div class="section-card">

    Using model <b>{model_name}</b> trained for weeks
    <b>{schema['season_start_week']}–{schema['season_end_week']}</b>.

    First predict the final harvest yield using your weather and soil inputs.
    After prediction, you can optionally optimize controllable factors.

    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Input form
# ---------------------------------------------------------

raw_row = render_full_input_form(
    schema,
    key_prefix="main_predict"
)


st.markdown("---")


# ---------------------------------------------------------
# Prediction
# ---------------------------------------------------------

if st.button(
    " Predict Yield",
    type="primary",
    use_container_width=True
):

    with st.spinner(
        "Running raw inputs through the model pipeline..."
    ):

        try:
            result = predict_corn(
                run_tag,
                model_name,
                raw_row
            )

        except ApiError as e:
            st.error(
                f"Prediction failed: {e}"
            )

        else:

            st.session_state["prediction_done"] = True
            st.session_state["prediction_result"] = result
            st.session_state["prediction_input"] = raw_row
            st.session_state["run_tag"] = run_tag
            st.session_state["model_name"] = model_name

            st.success(
                "Prediction complete!"
            )


# ---------------------------------------------------------
# Show previous prediction
# ---------------------------------------------------------

if st.session_state.get("prediction_done"):

    st.subheader("🌾 Prediction Result")

    render_prediction_metrics(
        st.session_state["prediction_result"]
    )


    st.markdown("---")


    # -----------------------------------------------------
    # Optimization button appears only after prediction
    # -----------------------------------------------------

    st.subheader("📈 Optimize Yield")

    st.write(
        "Would you like to find recommended changes "
        "to maximize the predicted yield?"
    )


    if st.button(
        " Optimize Yield",
        type="secondary",
        use_container_width=True
    ):

        if not controllables:

            st.warning(
                "No controllable variables are active for this model."
            )

        else:

            st.session_state["show_optimizer"] = True



# ---------------------------------------------------------
# Optimization section
# ---------------------------------------------------------

if st.session_state.get("show_optimizer"):

    st.markdown("---")

    st.subheader(
        "⚙️ Optimization Settings"
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        max_recommendations = st.slider(
            "Max recommendations",
            min_value=1,
            max_value=len(controllables) or 4,
            value=min(4, len(controllables) or 4)
        )


    with col2:

        grid_points = st.slider(
            "Search resolution (grid points)",
            min_value=5,
            max_value=50,
            value=25
        )


    with col3:

        min_gain = st.number_input(
            "Minimum meaningful gain (kg/ha)",
            min_value=0.0,
            value=1.0,
            step=0.5
        )


    if st.button(
        " Run Optimization",
        type="primary",
        use_container_width=True
    ):

        with st.spinner(
            "Searching controllable factors for best achievable yield..."
        ):

            try:

                result = optimize(
                    st.session_state["run_tag"],
                    st.session_state["model_name"],
                    st.session_state["prediction_input"],
                    max_recommendations=max_recommendations,
                    grid_points=grid_points,
                    min_meaningful_gain_kg_ha=min_gain,
                )


            except ApiError as e:

                st.error(
                    f"Optimization failed: {e}"
                )


            else:

                st.success(
                    "Optimization complete!"
                )

                render_recommendations(
                    result
                )