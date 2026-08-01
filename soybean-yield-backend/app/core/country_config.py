"""
CountryConfig + make_usa_config.

Copied verbatim from the original inference notebook (`YP_prediction_pipeline_decision_making`),
which itself mirrors the training pipeline's config. Rebuilds a CountryConfig for a given run
from the saved `feature_schema.json` instead of re-deriving it from a raw dataset, since the raw
CSV isn't present at inference time -- only the saved model_factory artifacts are.
"""

import re
from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class CountryConfig:
    country_code: str
    raw_path: str
    weather_vars: dict                      # {std_name: raw_prefix}
    weekly_col_pattern: Callable[[str, int], str]
    growing_season_weeks: list
    soil_vars: dict                         # {std_name: raw_prefix}
    soil_depth_regex: Callable[[str], "re.Pattern"]
    region_col: str
    lat_col: str
    lon_col: str
    year_col: str
    raw_target_col: str
    target_unit_to_kg_per_ha: float
    valid_target_range_kg_ha: tuple
    id_cols_to_drop: list = field(default_factory=list)
    baseline_year: int = 1980
    fixed_folds: list = field(default_factory=list)


def make_usa_config(schema: dict) -> CountryConfig:
    """Rebuilds a CountryConfig for a given run purely from its saved feature_schema.json,
    mirroring the training notebook's make_usa_config but taking the already-filtered
    weather_vars / soil_vars dicts straight from the schema instead of re-deriving them,
    since the raw dataset itself isn't present at inference time."""
    season_start_week = schema["season_start_week"]
    season_end_week = schema["season_end_week"]
    weather_vars = schema["weather_vars"]

    return CountryConfig(
        country_code="USA",
        raw_path="",
        weather_vars=weather_vars,
        weekly_col_pattern=lambda prefix, week: f"{prefix}_{week}",
        growing_season_weeks=list(range(season_start_week, season_end_week + 1)),
        soil_vars=schema["soil_vars"],
        soil_depth_regex=lambda prefix: re.compile(rf"^{prefix}_mean_(.+)$"),
        region_col="State", lat_col="lat", lon_col="lng", year_col="year",
        raw_target_col="soybean_yield",
        target_unit_to_kg_per_ha=67.25,
        valid_target_range_kg_ha=(5 * 67.25, 100 * 67.25),
        baseline_year=schema["baseline_year"],
    )
