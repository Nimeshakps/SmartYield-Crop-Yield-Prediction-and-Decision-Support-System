"""Pydantic request/response models for the API."""

from typing import Optional

from pydantic import BaseModel, Field


class RunsResponse(BaseModel):
    runs: list[str]


class ModelsResponse(BaseModel):
    run_tag: str
    models: list[str]


class SchemaResponse(BaseModel):
    """Everything the frontend needs to dynamically build the input form for a given
    run_tag/model_name, plus the model's reported training performance."""
    run_tag: str
    model_name: str
    season_start_week: int
    season_end_week: int
    growing_season_weeks: list[int]
    weather_vars: dict[str, str]          # {std_name: raw_prefix}
    soil_raw_cols: dict[str, list[str]]   # {std_name: [raw_col, ...]}
    region_classes: list[str]
    controllable_variables: list[str]     # active for Phase 2 optimization
    valid_ranges: dict[str, list[float]]  # {std_name: [lo, hi]}
    mean_rmse_kg_ha: Optional[float] = None
    mean_r2: Optional[float] = None
    n_features: Optional[int] = None


class PredictRequest(BaseModel):
    run_tag: str
    model_name: str
    raw_row: dict = Field(
        ..., description="Raw column -> value map, including 'obs_year' and 'region'."
    )


class PredictResponse(BaseModel):
    run_tag: str
    model_name: str
    prediction_kg_ha: float
    prediction_bu_acre: float


class OptimizeRequest(BaseModel):
    run_tag: str
    model_name: str
    raw_row: dict
    max_recommendations: int = 4
    grid_points: int = 25
    min_meaningful_gain_kg_ha: float = 1.0


class Recommendation(BaseModel):
    variable: str
    from_value: float
    to_value: float
    direction: str
    gain_kg_ha: float
    yield_after_kg_ha: float


class OptimizeResponse(BaseModel):
    run_tag: str
    model_name: str
    active_controllable_variables: list[str]
    baseline_yield_kg_ha: float
    baseline_yield_bu_acre: float
    final_yield_kg_ha: float
    final_yield_bu_acre: float
    improvement_kg_ha: float
    improvement_pct: float
    recommendations: list[Recommendation]
    message: str


class ErrorResponse(BaseModel):
    detail: str
