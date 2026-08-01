"""
Phase 2 -- "What should I change to get a higher yield?"

Replicates Steps 7/8 of the inference notebook: greedy coordinate-ascent search over the
controllable variables active for this run (Vapor Pressure, Soil pH, Cation Exchange Capacity,
Total Nitrogen -- whichever are present in this model's schema), up to MAX_RECOMMENDATIONS
rounds. Each round, every not-yet-recommended variable is grid-searched (holding everything
else fixed, including changes already locked in) to find the value that maximizes predicted
yield; whichever variable gives the single biggest gain that round gets locked in, and the
search moves on. Stops early if no remaining variable can meaningfully improve yield further.
"""

from typing import Optional

import numpy as np
import pandas as pd

from app.config import KG_HA_PER_BU_ACRE
from app.core.validation import (
    build_active_controllables,
    get_current_value,
    set_uniform_value,
    get_search_bounds,
)
from app.services.model_registry import LoadedModel
from app.services.predictor import predict_yield

DEFAULT_MAX_RECOMMENDATIONS = 4
DEFAULT_GRID_POINTS = 25
DEFAULT_MIN_MEANINGFUL_GAIN_KG_HA = 1.0


def optimize_yield(
    loaded: LoadedModel,
    raw_row: dict,
    max_recommendations: int = DEFAULT_MAX_RECOMMENDATIONS,
    grid_points: int = DEFAULT_GRID_POINTS,
    min_meaningful_gain_kg_ha: float = DEFAULT_MIN_MEANINGFUL_GAIN_KG_HA,
) -> dict:
    schema = loaded.schema
    active_controllables = build_active_controllables(schema)

    working_row = dict(raw_row)
    baseline_yield = predict_yield(loaded, working_row)

    remaining = dict(active_controllables)
    locked_in = []
    current_yield = baseline_yield

    for _ in range(max_recommendations):
        if not remaining:
            break

        best_choice = None  # (std_name, best_value, best_yield)
        for std_name in remaining:
            cur_val = get_current_value(std_name, working_row, active_controllables)
            lo, hi = get_search_bounds(std_name, cur_val)
            best_val_for_var, best_yield_for_var = cur_val, current_yield
            for val in np.linspace(lo, hi, grid_points):
                trial_row = set_uniform_value(std_name, working_row, val, active_controllables)
                y = predict_yield(loaded, trial_row)
                if y > best_yield_for_var:
                    best_yield_for_var, best_val_for_var = y, val
            if best_choice is None or best_yield_for_var > best_choice[2]:
                best_choice = (std_name, best_val_for_var, best_yield_for_var)

        std_name, best_val, best_yield = best_choice
        gain = best_yield - current_yield
        if gain < min_meaningful_gain_kg_ha:
            break

        cur_val = get_current_value(std_name, working_row, active_controllables)
        direction = "increase" if best_val > cur_val else ("decrease" if best_val < cur_val else "no change")
        locked_in.append({
            "variable": std_name.replace("_", " ").title(),
            "from_value": round(cur_val, 2),
            "to_value": round(float(best_val), 2),
            "direction": direction,
            "gain_kg_ha": round(gain, 2),
            "yield_after_kg_ha": round(best_yield, 2),
        })
        working_row = set_uniform_value(std_name, working_row, best_val, active_controllables)
        current_yield = best_yield
        del remaining[std_name]

    final_yield = current_yield
    improvement_kg_ha = final_yield - baseline_yield
    improvement_pct = (improvement_kg_ha / baseline_yield * 100) if baseline_yield else 0.0

    result = {
        "active_controllable_variables": [k.replace("_", " ").title() for k in active_controllables],
        "baseline_yield_kg_ha": round(baseline_yield, 2),
        "baseline_yield_bu_acre": round(baseline_yield / KG_HA_PER_BU_ACRE, 2),
        "final_yield_kg_ha": round(final_yield, 2),
        "final_yield_bu_acre": round(final_yield / KG_HA_PER_BU_ACRE, 2),
        "improvement_kg_ha": round(improvement_kg_ha, 2),
        "improvement_pct": round(improvement_pct, 2),
        "recommendations": locked_in,
    }

    if not locked_in:
        result["message"] = (
            "None of the controllable factors considered -- vapor pressure, soil pH, cation "
            "exchange capacity, total nitrogen -- meaningfully increase predicted yield beyond "
            "the current inputs, within the ranges explored. Yield cannot be increased by "
            "changing these variables for this scenario."
        )
    else:
        result["message"] = (
            f"Highest achievable yield with all {len(locked_in)} change(s) applied together: "
            f"{final_yield:,.1f} kg/ha (~{final_yield / KG_HA_PER_BU_ACRE:,.1f} bu/acre), an "
            f"improvement of +{improvement_kg_ha:,.1f} kg/ha ({improvement_pct:,.1f}%)."
        )

    return result
