"""
Phase 1 -- Predict Yield.

Replicates Step 6 of the inference notebook: raw inputs -> engineered features -> agro-climatic
cluster id -> missing-value flags + median imputation -> model prediction. Also exposes
predict_yield(), used both by the /predict endpoint and internally by the Phase 2 optimizer.
"""

from typing import Optional

import numpy as np
import pandas as pd

from app.config import KG_HA_PER_BU_ACRE
from app.core.feature_engineering import engineer_features
from app.services.model_registry import LoadedModel


def predict_from_raw_row(loaded: LoadedModel, raw_row: dict) -> dict:
    """Runs one raw input row through engineer -> cluster -> impute -> predict, exactly as
    Step 6 of the inference notebook does, and returns kg/ha + bu/acre predictions."""
    prediction_kg_ha = predict_yield(loaded, raw_row)
    prediction_bu_acre = prediction_kg_ha / KG_HA_PER_BU_ACRE
    return {
        "prediction_kg_ha": round(prediction_kg_ha, 2),
        "prediction_bu_acre": round(prediction_bu_acre, 2),
    }


def predict_yield(loaded: LoadedModel, raw_row_dict: dict) -> float:
    """Core reusable prediction function -- identical logic to the notebook's `predict_yield`,
    used directly by the Step 7/8 optimizer to test 'what if this variable were different?'."""
    schema = loaded.schema
    run_cfg = loaded.run_cfg
    cluster_artifacts = loaded.cluster_artifacts
    imputer = loaded.imputer
    model = loaded.model

    df_r = pd.DataFrame([raw_row_dict])
    feat_r, _ = engineer_features(df_r, run_cfg, loaded.region_encoder)
    

    

    cluster_cols = cluster_artifacts["feature_cols"]
    Xc_r = feat_r.reindex(columns=cluster_cols).fillna(0).values
    
    
    
    Xc_r_s = cluster_artifacts["scaler"].transform(Xc_r)
    feat_r["cluster"] = cluster_artifacts["kmeans"].predict(Xc_r_s)

    full_feature_cols = schema["feature_cols"]
    flag_cols = [c for c in full_feature_cols if c.endswith("_was_missing")]
    pre_flag_cols = [c for c in full_feature_cols if not c.endswith("_was_missing")]
    
    

    for c in pre_flag_cols:
        if c not in feat_r.columns:
            feat_r[c] = np.nan

    for flag_col in flag_cols:
        base_col = flag_col[: -len("_was_missing")]
        feat_r[flag_col] = int(pd.isna(feat_r[base_col].iloc[0]))

    feat_r[pre_flag_cols] = imputer.transform(feat_r[pre_flag_cols])

    X_r = feat_r[full_feature_cols].values
    
    
    ############################
    soil_engineered_cols = [c for c in full_feature_cols if any(
        c.startswith(p) for p in [
            'bulk_density', 'cation_exchange_capacity', 'coarse_fragments', 'clay_content',
            'total_nitrogen', 'organic_carbon_density', 'organic_carbon_stocks', 'soil_ph',
            'sand_content', 'silt_content', 'soil_organic_carbon', 'soil_water_holding_proxy',
            'sand_x_low_precipitation',
        ]
    )]
    soil_col_idx = [full_feature_cols.index(c) for c in soil_engineered_cols]
    print("Final soil feature values fed to model:")
    for c, i in zip(soil_engineered_cols, soil_col_idx):
        print(f"    {c}: {X_r[0][i]}")
    #########################
    
    
    
    return float(model.predict(X_r)[0])
