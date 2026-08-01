"""
Validation ranges & controllable-variable definitions.

Copied verbatim from the inference notebook's Step 5 (validation ranges) and Step 7
(controllable candidates for the optimizer). Any manually entered value AND any value the
optimizer tries is checked/clipped against these ranges, so the pipeline can never propose or
accept a physically invalid reading (e.g. negative vapor pressure).

EDIT THESE to match the actual units/scale used in your dataset -- the numbers below are
placeholder agronomic ranges from the original notebook; they are not guaranteed to match your
raw CSV's exact units (e.g. SoilGrids CEC/nitrogen units can vary by source/depth).
"""

import numpy as np
import pandas as pd

VALID_RANGES = {
    "vapor_pressure": (0.0, 10.0),               # kPa -- vapor pressure cannot be negative
    "soil_ph": (3.0, 10.0),                       # pH scale, realistic agricultural soil range
    "cation_exchange_capacity": (0.0, 60.0),      # cmol(+)/kg soil
    "total_nitrogen": (0.0, 20.0),                # g/kg soil
    "coarse_fragments": (0.0, 20.0), 
    "organic_carbon_stocks": (0.0, 20.0), 
    "sand_content": (0.0, 20.0), 
    
}

# Only these variables are considered controllable -- everything a farmer can plausibly act on.
# Precipitation, maximum temperature, and minimum temperature are excluded: this crop is grown
# in an open (uncontrolled) environment, so a farmer cannot set those to a target value.
CONTROLLABLE_CANDIDATES = {
    "precipitation": {"kind": "weather"},
    "maximum_temperature": {"kind": "weather"},
    "minimum_temperature": {"kind": "weather"},
    "vapor_pressure": {"kind": "weather"},
    "soil_ph": {"kind": "soil"},
    "cation_exchange_capacity": {"kind": "soil"},
    "total_nitrogen": {"kind": "soil"},
    "coarse_fragments":{"kind": "soil"},
    "organic_carbon_stocks":{"kind": "soil"},
    "sand_content":{"kind": "soil"},
}

# Variables actually eligible for optimization recommendations (excludes the uncontrollable
# weather variables above, even though they appear in CONTROLLABLE_CANDIDATES for lookup).
OPTIMIZABLE_VARS = {"vapor_pressure", "soil_ph", "cation_exchange_capacity", "total_nitrogen","sand_content","organic_carbon_stocks","coarse_fragments"}


def validate_value(std_name, col, value):
    """Returns (is_valid, message). NaN (missing) always passes -- it gets imputed later."""
    if std_name not in VALID_RANGES or pd.isna(value):
        return True, ""
    lo, hi = VALID_RANGES[std_name]
    if value < lo or value > hi:
        return False, f"{col} = {value} is outside the valid range [{lo}, {hi}] for {std_name}."
    return True, ""


def clip_to_valid_range(std_name, value):
    """Clips a single value into VALID_RANGES, if that std_name has a defined range."""
    if std_name not in VALID_RANGES or pd.isna(value):
        return value
    lo, hi = VALID_RANGES[std_name]
    return min(max(value, lo), hi)


def build_active_controllables(schema: dict) -> dict:
    """Determines which controllable variables are actually active for this run's schema
    (i.e. present in its weather_vars / soil_raw_cols), and the raw columns backing each one."""
    active = {}
    for std_name, meta in CONTROLLABLE_CANDIDATES.items():
        if std_name not in OPTIMIZABLE_VARS:
            continue
        if meta["kind"] == "weather" and std_name in schema.get("weather_vars", {}):
            prefix = schema["weather_vars"][std_name]
            raw_cols = [f"{prefix}_{w}" for w in schema["growing_season_weeks"]]
            active[std_name] = {**meta, "raw_cols": raw_cols}
        elif meta["kind"] == "soil" and std_name in schema.get("soil_raw_cols", {}):
            raw_cols = schema["soil_raw_cols"][std_name]
            active[std_name] = {**meta, "raw_cols": raw_cols}
    return active


def get_current_value(std_name, row_dict, active_controllables):
    cols = active_controllables[std_name]["raw_cols"]
    return float(np.nanmean([row_dict.get(c, np.nan) for c in cols]))


def set_uniform_value(std_name, row_dict, new_value, active_controllables):
    """Returns a COPY of row_dict with every raw column for this variable set to the same
    value -- e.g. 'raise average growing-season precipitation to new_value across every week',
    or 'raise soil pH to new_value across every measured depth'."""
    new_row = dict(row_dict)
    for c in active_controllables[std_name]["raw_cols"]:
        new_row[c] = new_value
    return new_row


def get_search_bounds(std_name, current_value):
    """Heuristic, farmer-editable search ranges -- there's no historical-percentile data
    available at inference time, so bounds are a mix of physically sensible domain limits
    (soil pH) and +/- reasonable swings around the current value for everything else. Final
    bounds are always clipped to VALID_RANGES so the optimizer can never propose or lock in a
    physically invalid value (e.g. negative vapor pressure)."""
    if np.isnan(current_value):
        lo, hi = (4.5, 8.5) if std_name == "soil_ph" else (0.0, 10.0)
    elif std_name == "vapor_pressure":
        lo, hi = max(current_value * 0.5, 0.0), max(current_value * 1.5, current_value + 1.0)
    elif std_name == "soil_ph":
        lo, hi = 4.5, 8.5
    elif std_name == "cation_exchange_capacity":
        lo, hi = max(current_value * 0.5, 0.0), max(current_value * 1.5, current_value + 5.0)
    elif std_name == "total_nitrogen":
        lo, hi = max(current_value * 0.5, 0.0), max(current_value * 1.8, current_value + 5.0)
    elif std_name == "sand_content":
            lo, hi = max(current_value * 0.5, 0.0), max(current_value * 1.8, current_value + 5.0)
    elif std_name == "organic_carbon_stocks":
            lo, hi = max(current_value * 0.5, 0.0), max(current_value * 1.8, current_value + 5.0)
    elif std_name == "coarse_fragments":
            lo, hi = max(current_value * 0.5, 0.0), max(current_value * 1.8, current_value + 5.0)
    else:
        lo, hi = current_value * 0.5, current_value * 1.5

    if std_name in VALID_RANGES:
        valid_lo, valid_hi = VALID_RANGES[std_name]
        lo, hi = max(lo, valid_lo), min(hi, valid_hi)
        if lo > hi:
            lo, hi = valid_lo, valid_hi

    return lo, hi
