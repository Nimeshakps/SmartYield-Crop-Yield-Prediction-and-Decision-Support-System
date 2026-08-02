# """
# Dynamic input form builder.

# Builds the raw-input widgets (weekly weather readings + soil readings + year/region) purely
# from the schema returned by `GET /api/runs/{run_tag}/models/{model_name}/schema`, so the form
# always matches whichever run/model is selected -- exactly the "raw, un-engineered inputs" the
# notebook's Step 5 collects.
# """

# import numpy as np
# import pandas as pd
# import streamlit as st


# def _pretty(std_name: str) -> str:
#     return std_name.replace("_", " ").title()


# def render_weather_table(schema: dict, key_prefix: str) -> pd.DataFrame:
#     """One row per growing-season week, one column per active weather variable.
#     Blank cells are treated as missing (median-imputed by the backend)."""
#     weeks = schema["growing_season_weeks"]
#     weather_vars = schema["weather_vars"]  # {std_name: prefix}

#     default_df = pd.DataFrame(
#         {std_name: [np.nan] * len(weeks) for std_name in weather_vars},
#         index=[f"Week {w}" for w in weeks],
#     )
#     default_df.columns = [_pretty(c) for c in default_df.columns]

#     st.caption(
#         "Enter the weekly reading for each active weather variable, for every week in the "
#         "model's trained growing-season range. Leave a cell empty to mark it missing -- it "
#         "will be median-imputed automatically."
#     )
#     edited = st.data_editor(
#         default_df,
#         use_container_width=True,
#         key=f"{key_prefix}_weather_table",
#         column_config={
#             col: st.column_config.NumberColumn(col, step=0.1, format="%.2f")
#             for col in default_df.columns
#         },
#     )
#     return edited


# def render_soil_table(schema: dict, key_prefix: str) -> pd.DataFrame:
#     """Long-format table: one row per raw soil column (soil doesn't vary by week, only by
#     measurement depth), grouped by standardized variable name."""
#     soil_raw_cols = schema["soil_raw_cols"]  # {std_name: [raw_col, ...]}

#     rows = []
#     for std_name, raw_cols in soil_raw_cols.items():
#         for raw_col in raw_cols:
#             rows.append({"Variable": _pretty(std_name), "Raw column": raw_col, "Value": np.nan})

#     default_df = pd.DataFrame(rows)

#     st.caption(
#         "Enter each raw soil reading once (soil doesn't vary by week). Leave a cell empty to "
#         "mark it missing -- it will be median-imputed automatically."
#     )
#     edited = st.data_editor(
#         default_df,
#         use_container_width=True,
#         hide_index=True,
#         disabled=["Variable", "Raw column"],
#         key=f"{key_prefix}_soil_table",
#         column_config={
#             "Value": st.column_config.NumberColumn("Value", step=0.1, format="%.2f"),
#         },
#     )
#     return edited


# def render_other_inputs(schema: dict, key_prefix: str):
#     """Observation/prediction year + region. Region has zero effect on the prediction (it's
#     excluded from the trained feature set) but engineer_features still requires a valid class."""
#     col1, col2 = st.columns(2)
#     with col1:
#         obs_year = st.number_input(
#             "Observation / prediction year",
#             min_value=1980, max_value=2100, value=2026, step=1,
#             key=f"{key_prefix}_obs_year",
#             help="Used to compute the 'years since baseline' trend feature.",
#         )
#     with col2:
#         region_classes = schema.get("region_classes") or ["(none available)"]
#         region = st.selectbox(
#             "Region (no effect on prediction -- required by the pipeline)",
#             options=region_classes,
#             key=f"{key_prefix}_region",
#         )
#     return int(obs_year), region


# def build_raw_row(schema: dict, weather_df: pd.DataFrame, soil_df: pd.DataFrame,
#                    obs_year: int, region: str) -> dict:
#     """Assembles the flat raw_row dict the backend expects, from the edited weather/soil
#     tables plus year/region. Blank (NaN) cells stay NaN -> sent as null -> imputed server-side."""
#     raw_row = {}

#     weather_vars = schema["weather_vars"]
#     weeks = schema["growing_season_weeks"]
#     pretty_to_std = {_pretty(std): std for std in weather_vars}

#     for pretty_col in weather_df.columns:
#         std_name = pretty_to_std.get(pretty_col)
#         if std_name is None:
#             continue
#         prefix = weather_vars[std_name]
#         for week, value in zip(weeks, weather_df[pretty_col].tolist()):
#             raw_row[f"{prefix}_{week}"] = None if pd.isna(value) else float(value)

#     for _, row in soil_df.iterrows():
#         raw_col = row["Raw column"]
#         value = row["Value"]
#         raw_row[raw_col] = None if pd.isna(value) else float(value)

#     raw_row["obs_year"] = obs_year
#     raw_row["region"] = region

#     return raw_row


# def render_full_input_form(schema: dict, key_prefix: str) -> dict:
#     """Renders the complete raw-input form (weather + soil + year/region) and returns the
#     assembled raw_row dict, ready to send to /api/predict or /api/optimize.

#     NOTE: this renders the widgets directly on the page (not inside an st.form), so every
#     cell edit triggers a full script rerun. Prefer `render_form_with_submit` below, which
#     wraps everything in an st.form so edits are batched and only submitted on button click."""
#     st.markdown("#### 🌦️ Weekly weather readings")
#     weather_df = render_weather_table(schema, key_prefix)

#     st.markdown("#### 🌱 Soil readings")
#     soil_df = render_soil_table(schema, key_prefix)

#     st.markdown("#### 📅 Other")
#     obs_year, region = render_other_inputs(schema, key_prefix)

#     return build_raw_row(schema, weather_df, soil_df, obs_year, region)


# def render_form_with_submit(schema: dict, key_prefix: str, submit_label: str, extra_controls=None):
#     """Renders the full raw-input form INSIDE an st.form, so editing weather/soil table cells
#     does not trigger a script rerun (and the network calls that come with one) on every
#     keystroke -- only clicking the submit button does.

#     `extra_controls` is an optional no-arg callable that renders additional widgets (e.g.
#     search-resolution sliders) inside the same form and returns whatever value(s) the caller
#     needs.

#     Returns (submitted: bool, raw_row: dict, extra_result).
#     """
#     with st.form(key=f"{key_prefix}_form", border=False):
#         st.markdown("#### 🌦️ Weekly weather readings")
#         weather_df = render_weather_table(schema, key_prefix)

#         st.markdown("#### 🌱 Soil readings")
#         soil_df = render_soil_table(schema, key_prefix)

#         st.markdown("#### 📅 Other")
#         obs_year, region = render_other_inputs(schema, key_prefix)

#         extra_result = extra_controls() if extra_controls else None

#         submitted = st.form_submit_button(submit_label, type="primary", use_container_width=True)

#     raw_row = build_raw_row(schema, weather_df, soil_df, obs_year, region)
#     return submitted, raw_row, extra_result



"""
Dynamic input form builder.

Builds the raw-input widgets (weekly weather readings + soil readings + year/region) purely
from the schema returned by `GET /api/runs/{run_tag}/models/{model_name}/schema`, so the form
always matches whichever run/model is selected -- exactly the "raw, un-engineered inputs" the
notebook's Step 5 collects.
"""

import numpy as np
import pandas as pd
import streamlit as st

# Measurement units for each standardized variable name, shown alongside labels so farmers
# know what scale to enter values in. Edit this if your dataset uses different units.
VARIABLE_UNITS = {
    # weather
    "precipitation": "mm/day",
    "maximum_temperature": "°C",
    "minimum_temperature": "°C",
    "vapor_pressure": "Pa",
    "solar_radiation": "W/m²",
    "snow_water_equivalent":"kg/m²",
    # soil
    "soil_ph": "pH",
    "cation_exchange_capacity": "cmol(c)/kg",
    "total_nitrogen": "g/kg",
    "clay_content": "%",
    "sand_content": "%",
    "soil_organic_carbon": "g/kg",
    "bulk_density":"g/cm³",
    "coarse_fragments":"volume %",
    "organic_carbon_density":"kg/m³",
    "organic_carbon_stocks":"t/ha",
    "silt_content":"%"
}


def _pretty(std_name: str) -> str:
    return std_name.replace("_", " ").title()


def _pretty_with_unit(std_name: str) -> str:
    """e.g. 'soil_ph' -> 'Soil Ph (pH)', 'precipitation' -> 'Precipitation (mm)'."""
    label = _pretty(std_name)
    unit = VARIABLE_UNITS.get(std_name)
    return f"{label} ({unit})" if unit else label


def render_weather_table(schema: dict, key_prefix: str) -> pd.DataFrame:
    """One row per growing-season week, one column per active weather variable.
    Blank cells are treated as missing (median-imputed by the backend)."""
    weeks = schema["growing_season_weeks"]
    weather_vars = schema["weather_vars"]  # {std_name: prefix}

    default_df = pd.DataFrame(
        {std_name: [np.nan] * len(weeks) for std_name in weather_vars},
        index=[f"Week {w}" for w in weeks],
    )
    default_df.columns = [_pretty_with_unit(c) for c in default_df.columns]

    st.caption(
        "Enter the weekly reading for each active weather variable, for every week in the "
        "model's trained growing-season range. Leave a cell empty to mark it missing -- it "
        "will be median-imputed automatically."
    )
    edited = st.data_editor(
        default_df,
        use_container_width=True,
        key=f"{key_prefix}_weather_table",
        column_config={
            col: st.column_config.NumberColumn(col, step=0.1, format="%.4f")
            for col in default_df.columns
        },
    )
    return edited


def render_soil_table(schema: dict, key_prefix: str) -> pd.DataFrame:
    """Long-format table: one row per raw soil column (soil doesn't vary by week, only by
    measurement depth), grouped by standardized variable name."""
    soil_raw_cols = schema["soil_raw_cols"]  # {std_name: [raw_col, ...]}

    rows = []
    for std_name, raw_cols in soil_raw_cols.items():
        for raw_col in raw_cols:
            rows.append({"Variable": _pretty_with_unit(std_name), "Raw column": raw_col, "Value": np.nan})

    default_df = pd.DataFrame(rows)

    st.caption(
        "Enter each raw soil reading once (soil doesn't vary by week). Leave a cell empty to "
        "mark it missing -- it will be median-imputed automatically."
    )
    edited = st.data_editor(
        default_df,
        use_container_width=True,
        hide_index=True,
        disabled=["Variable", "Raw column"],
        key=f"{key_prefix}_soil_table",
        column_config={
            "Value": st.column_config.NumberColumn("Value", step=0.1, format="%.4f"),
        },
    )
    return edited


# def render_other_inputs(schema: dict, key_prefix: str):
#     """Observation/prediction year + region. Region has zero effect on the prediction (it's
#     excluded from the trained feature set) but engineer_features still requires a valid class."""
#     col1, col2 = st.columns(2)
#     with col1:
#         obs_year = st.number_input(
#             "Observation / prediction year",
#             min_value=1980, max_value=2100, value=2026, step=1,
#             key=f"{key_prefix}_obs_year",
#             help="Used to compute the 'years since baseline' trend feature.",
#         )
#     with col2:
#         region_classes = schema.get("region_classes") or ["(none available)"]
#         region = st.selectbox(
#             "Region (no effect on prediction -- required by the pipeline)",
#             options=region_classes,
#             key=f"{key_prefix}_region",
#         )
#     return int(obs_year), region


def render_other_inputs(schema: dict, key_prefix: str):
    """Observation/prediction year + region. Region has zero effect on the prediction (it's
    excluded from the trained feature set) but engineer_features still requires a valid class."""

    # col1, col2 = st.columns(2)
    # # col1= st.columns(2)
    # with col1:
    #     obs_year = st.number_input(
    #         "Observation / prediction year",
    #         min_value=1980, max_value=2100, value=2026, step=1,
    #         key=f"{key_prefix}_obs_year",
    #         help="Used to compute the 'years since baseline' trend feature.",
    #     )


    # with col2:
    #     region_classes = schema.get("region_classes") or ["(none available)"]
    #     region = st.selectbox(
    #         "Region (no effect on prediction -- required by the pipeline)",
    #         options=region_classes,
    #         key=f"{key_prefix}_region",
    #     )

    obs_year = st.number_input(
        "Observation / prediction year",
        min_value=1980, max_value=2100, value=2026, step=1,
        key=f"{key_prefix}_obs_year",
        help="Used to compute the 'years since baseline' trend feature.",
    )

    region_classes = schema.get("region_classes") or ["(none available)"]
    region = region_classes[0]

    # region="Sri Lanka"
    return int(obs_year), region


def build_raw_row(schema: dict, weather_df: pd.DataFrame, soil_df: pd.DataFrame,
                   obs_year: int, region: str) -> dict:
    """Assembles the flat raw_row dict the backend expects, from the edited weather/soil
    tables plus year/region. Blank (NaN) cells stay NaN -> sent as null -> imputed server-side."""
    raw_row = {}

    weather_vars = schema["weather_vars"]
    weeks = schema["growing_season_weeks"]
    pretty_to_std = {_pretty_with_unit(std): std for std in weather_vars}

    for pretty_col in weather_df.columns:
        std_name = pretty_to_std.get(pretty_col)
        if std_name is None:
            continue
        prefix = weather_vars[std_name]
        for week, value in zip(weeks, weather_df[pretty_col].tolist()):
            raw_row[f"{prefix}_{week}"] = None if pd.isna(value) else float(value)

    for _, row in soil_df.iterrows():
        raw_col = row["Raw column"]
        value = row["Value"]
        raw_row[raw_col] = None if pd.isna(value) else float(value)

    raw_row["obs_year"] = obs_year
    raw_row["region"] = region

    return raw_row


def render_full_input_form(schema: dict, key_prefix: str) -> dict:
    """Renders the complete raw-input form (weather + soil + year/region) and returns the
    assembled raw_row dict, ready to send to /api/predict or /api/optimize.

    NOTE: this renders the widgets directly on the page (not inside an st.form), so every
    cell edit triggers a full script rerun. Prefer `render_form_with_submit` below, which
    wraps everything in an st.form so edits are batched and only submitted on button click."""
    st.markdown("#### 🌦️ Weekly weather readings")
    weather_df = render_weather_table(schema, key_prefix)

    st.markdown("#### 🌱 Soil readings")
    soil_df = render_soil_table(schema, key_prefix)

    st.markdown("#### 📅 Other")
    obs_year, region = render_other_inputs(schema, key_prefix)

    return build_raw_row(schema, weather_df, soil_df, obs_year, region)


def render_form_with_submit(schema: dict, key_prefix: str, submit_label: str, extra_controls=None):
    """Renders the full raw-input form INSIDE an st.form, so editing weather/soil table cells
    does not trigger a script rerun (and the network calls that come with one) on every
    keystroke -- only clicking the submit button does.

    `extra_controls` is an optional no-arg callable that renders additional widgets (e.g.
    search-resolution sliders) inside the same form and returns whatever value(s) the caller
    needs.

    Returns (submitted: bool, raw_row: dict, extra_result).
    """
    with st.form(key=f"{key_prefix}_form", border=False):
        st.markdown("#### 🌦️ Weekly weather readings")
        weather_df = render_weather_table(schema, key_prefix)

        st.markdown("#### 🌱 Soil readings")
        soil_df = render_soil_table(schema, key_prefix)

        st.markdown("#### 📅 Other")
        obs_year, region = render_other_inputs(schema, key_prefix)

        extra_result = extra_controls() if extra_controls else None

        submitted = st.form_submit_button(submit_label, type="primary", use_container_width=True)

    raw_row = build_raw_row(schema, weather_df, soil_df, obs_year, region)
    return submitted, raw_row, extra_result