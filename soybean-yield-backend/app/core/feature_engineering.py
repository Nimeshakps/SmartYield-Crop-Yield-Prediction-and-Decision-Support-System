"""
engineer_features / build_feature_cols.

Copied verbatim (logic-for-logic) from the training pipeline's Step 4 / Step 7, as reproduced in
the inference notebook, so raw inputs are transformed into model-ready features using the exact
same logic the model was trained on -- no reimplementation, no drift.
"""

from typing import Optional

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from app.core.country_config import CountryConfig


def engineer_features(df: pd.DataFrame, cfg: CountryConfig, region_encoder: Optional[LabelEncoder] = None):
    feat = df.copy()

    for std_name, prefix in cfg.weather_vars.items():
        gs_cols = [cfg.weekly_col_pattern(prefix, w) for w in cfg.growing_season_weeks
                   if cfg.weekly_col_pattern(prefix, w) in feat.columns]
        if gs_cols:
            feat[f"growing_season_{std_name}_mean"] = feat[gs_cols].mean(axis=1)
            feat[f"growing_season_{std_name}_sum"] = feat[gs_cols].sum(axis=1)
            feat[f"growing_season_{std_name}_std"] = feat[gs_cols].std(axis=1)

    if {"growing_season_maximum_temperature_mean", "growing_season_minimum_temperature_mean"} <= set(feat.columns):
        feat["growing_season_diurnal_temperature_range"] = (
            feat["growing_season_maximum_temperature_mean"] - feat["growing_season_minimum_temperature_mean"])
    if {"growing_season_precipitation_mean", "growing_season_solar_radiation_mean"} <= set(feat.columns):
        feat["growing_season_precipitation_x_solar_radiation"] = (
            feat["growing_season_precipitation_mean"] * feat["growing_season_solar_radiation_mean"])
    if {"growing_season_vapor_pressure_mean", "growing_season_maximum_temperature_mean"} <= set(feat.columns):
        feat["growing_season_vapor_pressure_x_max_temperature"] = (
            feat["growing_season_vapor_pressure_mean"] * feat["growing_season_maximum_temperature_mean"])
    max_temp_prefix = cfg.weather_vars.get("maximum_temperature")
    if max_temp_prefix:
        gs_max_cols = [cfg.weekly_col_pattern(max_temp_prefix, w) for w in cfg.growing_season_weeks
                       if cfg.weekly_col_pattern(max_temp_prefix, w) in feat.columns]
        if gs_max_cols:
            feat["growing_season_heat_stress_degree_days"] = (feat[gs_max_cols] - 30).clip(lower=0).sum(axis=1)
    if {"growing_season_precipitation_sum", "growing_season_maximum_temperature_mean"} <= set(feat.columns):
        feat["growing_season_water_balance_proxy"] = (
            feat["growing_season_precipitation_sum"] - feat["growing_season_maximum_temperature_mean"] * 10)

    for std_name, prefix in cfg.soil_vars.items():
        pattern = cfg.soil_depth_regex(prefix)
        depth_cols = [c for c in feat.columns if pattern.match(c)]
        if depth_cols:
            feat[f"{std_name}_depth_averaged_mean"] = feat[depth_cols].mean(axis=1)
            feat[f"{std_name}_topsoil_mean"] = feat[sorted(depth_cols)[0]]
    if {"clay_content_depth_averaged_mean", "soil_organic_carbon_depth_averaged_mean"} <= set(feat.columns):
        feat["soil_water_holding_proxy"] = (
            feat["clay_content_depth_averaged_mean"] + feat["soil_organic_carbon_depth_averaged_mean"])
    if {"sand_content_depth_averaged_mean", "growing_season_precipitation_sum"} <= set(feat.columns):
        feat["sand_x_low_precipitation"] = (
            feat["sand_content_depth_averaged_mean"] / (feat["growing_season_precipitation_sum"] + 1))
        
  

    if region_encoder is None:
        region_encoder = LabelEncoder()
        feat["region_encoded"] = region_encoder.fit_transform(feat["region"])
    else:
        feat["region_encoded"] = region_encoder.transform(feat["region"])

    feat["years_since_baseline"] = feat["obs_year"] - cfg.baseline_year
    return feat, region_encoder


def build_feature_cols(feat: pd.DataFrame, cfg: CountryConfig) -> list:
    cols = (
        [f"growing_season_{v}_mean" for v in cfg.weather_vars] +
        [f"growing_season_{v}_sum" for v in cfg.weather_vars] +
        [f"growing_season_{v}_std" for v in cfg.weather_vars] +
        [f"{v}_depth_averaged_mean" for v in cfg.soil_vars] +
        [f"{v}_topsoil_mean" for v in cfg.soil_vars] +
        ["growing_season_diurnal_temperature_range",
         "growing_season_precipitation_x_solar_radiation",
         "growing_season_vapor_pressure_x_max_temperature",
         "growing_season_heat_stress_degree_days",
         "growing_season_water_balance_proxy",
         "soil_water_holding_proxy",
         "sand_x_low_precipitation",
         "years_since_baseline", "cluster"]
    )
    return [c for c in cols if c in feat.columns]

def debug_soil_feature_coverage(df: pd.DataFrame, cfg: CountryConfig, feature_cols: list) -> None:
    """Diagnostic only -- does not affect predictions.

    Reports, for each configured soil variable:
      1. Whether its raw depth columns were actually found in the input row
         (if not, engineer_features() never creates the engineered soil column,
         and it gets NaN -> imputed to the training-set median every time,
         regardless of what you pass in).
      2. Whether the resulting engineered feature is even part of the model's
         trained feature set (schema['feature_cols']) -- if it isn't, soil inputs
         legitimately have zero effect on this model's predictions by design.

    Call this right after engineer_features(), passing the SAME df you passed in
    and schema['feature_cols'].
    """
    print("=== Soil feature coverage diagnostic ===")
    for std_name, prefix in cfg.soil_vars.items():
        pattern = cfg.soil_depth_regex(prefix)
        depth_cols = [c for c in df.columns if pattern.match(c)]
        status = "OK" if depth_cols else "NO MATCH -> NaN -> imputed to training median (input ignored)"
        print(f"  {std_name} (prefix={prefix!r}): matched raw columns = {depth_cols}  [{status}]")

        for feat_name in (f"{std_name}_depth_averaged_mean", f"{std_name}_topsoil_mean"):
            in_model = feat_name in feature_cols
            note = "used by model" if in_model else "NOT in trained feature_cols -- no effect on prediction"
            print(f"      -> {feat_name}: {note}")
    print("=========================================")
