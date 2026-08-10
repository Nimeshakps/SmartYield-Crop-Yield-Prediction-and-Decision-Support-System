# """Endpoints for discovering available runs/models and their schema (used to build the UI form)."""

# from fastapi import APIRouter, HTTPException

# from app.core.validation import VALID_RANGES, build_active_controllables
# from app.schemas import ModelsResponse, RunsResponse, SchemaResponse
# from app.services.model_registry import (
#     ModelFactoryMissingError,
#     ModelNotFoundError,
#     get_model,
#     list_models,
#     list_runs,
# )

# router = APIRouter(prefix="/api", tags=["runs"])


# @router.get("/runs", response_model=RunsResponse)
# def get_runs():
#     """Lists available week-range run tags (e.g. 'weeks_14_20', 'weeks_14_30')."""
#     try:
#         return {"runs": list_runs()}
#     except ModelFactoryMissingError as e:
#         raise HTTPException(status_code=404, detail=str(e))


# @router.get("/runs/{run_tag}/models", response_model=ModelsResponse)
# def get_models(run_tag: str):
#     """Lists available trained models for a given run tag."""
#     try:
#         return {"run_tag": run_tag, "models": list_models(run_tag)}
#     except ModelFactoryMissingError as e:
#         raise HTTPException(status_code=404, detail=str(e))
#     except ModelNotFoundError as e:
#         raise HTTPException(status_code=404, detail=str(e))


# @router.get("/runs/{run_tag}/models/{model_name}/schema", response_model=SchemaResponse)
# def get_schema(run_tag: str, model_name: str):
#     """Returns everything the frontend needs to dynamically build the input form: growing
#     season weeks, active weather variables, raw soil columns, region classes, which controllable
#     variables are available for Phase 2 optimization, valid ranges, and reported metrics."""
#     try:
#         loaded = get_model(run_tag, model_name)
#     except ModelFactoryMissingError as e:
#         raise HTTPException(status_code=404, detail=str(e))
#     except ModelNotFoundError as e:
#         raise HTTPException(status_code=404, detail=str(e))

#     schema = loaded.schema
#     active_controllables = build_active_controllables(schema)

#     return {
#         "run_tag": run_tag,
#         "model_name": model_name,
#         "season_start_week": schema["season_start_week"],
#         "season_end_week": schema["season_end_week"],
#         "growing_season_weeks": schema["growing_season_weeks"],
#         "weather_vars": schema["weather_vars"],
#         "soil_raw_cols": schema["soil_raw_cols"],
#         "region_classes": schema["region_classes"],
#         "controllable_variables": list(active_controllables.keys()),
#         "valid_ranges": {k: list(v) for k, v in VALID_RANGES.items()},
#         "mean_rmse_kg_ha": schema.get("mean_rmse_kg_ha"),
#         "mean_r2": schema.get("mean_r2"),
#         "n_features": len(schema.get("feature_cols", [])),
#     }

"""Endpoints for discovering available runs/models and their schema (used to build the UI form)."""

from fastapi import APIRouter, HTTPException

from app.core.validation import VALID_RANGES, build_active_controllables
from app.schemas import ModelsResponse, RunsResponse, SchemaResponse
from app.services.model_registry import (
    ModelFactoryMissingError,
    ModelNotFoundError,
    get_model,
    list_models,
    list_runs,
    get_model_corn,
    list_models_corn,
    list_runs_corn,
)

router = APIRouter(prefix="/api", tags=["runs"])


@router.get("/runs", response_model=RunsResponse)
def get_runs():
    """Lists available week-range run tags (e.g. 'weeks_14_20', 'weeks_14_30')."""
    try:
        return {"runs": list_runs()}
    except ModelFactoryMissingError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/runs/{run_tag}/models", response_model=ModelsResponse)
def get_models(run_tag: str):
    """Lists available trained models for a given run tag."""
    try:
        return {"run_tag": run_tag, "models": list_models(run_tag)}
    except ModelFactoryMissingError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ModelNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/runs/{run_tag}/models/{model_name}/schema", response_model=SchemaResponse)
def get_schema(run_tag: str, model_name: str):
    """Returns everything the frontend needs to dynamically build the input form: growing
    season weeks, active weather variables, raw soil columns, region classes, which controllable
    variables are available for Phase 2 optimization, valid ranges, and reported metrics."""
    try:
        loaded = get_model(run_tag, model_name)
    except ModelFactoryMissingError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ModelNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    schema = loaded.schema
    active_controllables = build_active_controllables(schema)

    return {
        "run_tag": run_tag,
        "model_name": model_name,
        "season_start_week": schema["season_start_week"],
        "season_end_week": schema["season_end_week"],
        "growing_season_weeks": schema["growing_season_weeks"],
        "weather_vars": schema["weather_vars"],
        "soil_raw_cols": schema["soil_raw_cols"],
        "region_classes": schema["region_classes"],
        "controllable_variables": list(active_controllables.keys()),
        "valid_ranges": {k: list(v) for k, v in VALID_RANGES.items()},
        "mean_rmse_kg_ha": schema.get("mean_rmse_kg_ha"),
        "mean_r2": schema.get("mean_r2"),
        "n_features": len(schema.get("feature_cols", [])),
    }
    
    
    
##########corn


@router.get("/runs_corn", response_model=RunsResponse)
def get_runs_corn():
    """Lists available week-range run tags (e.g. 'weeks_14_20', 'weeks_14_30')."""
    try:
        return {"runs": list_runs_corn()}
    except ModelFactoryMissingError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/runs_corn/{run_tag}/models", response_model=ModelsResponse)
def get_models_corn(run_tag: str):
    """Lists available trained models for a given run tag."""
    try:
        return {"run_tag": run_tag, "models": list_models_corn(run_tag)}
    except ModelFactoryMissingError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ModelNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/runs_corn/{run_tag}/models/{model_name}/schema", response_model=SchemaResponse)
def get_schema_corn(run_tag: str, model_name: str):
    """Returns everything the frontend needs to dynamically build the input form: growing
    season weeks, active weather variables, raw soil columns, region classes, which controllable
    variables are available for Phase 2 optimization, valid ranges, and reported metrics."""
    try:
        loaded = get_model_corn(run_tag, model_name)
    except ModelFactoryMissingError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ModelNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    schema = loaded.schema
    active_controllables = build_active_controllables(schema)

    return {
        "run_tag": run_tag,
        "model_name": model_name,
        "season_start_week": schema["season_start_week"],
        "season_end_week": schema["season_end_week"],
        "growing_season_weeks": schema["growing_season_weeks"],
        "weather_vars": schema["weather_vars"],
        "soil_raw_cols": schema["soil_raw_cols"],
        "region_classes": schema["region_classes"],
        "controllable_variables": list(active_controllables.keys()),
        "valid_ranges": {k: list(v) for k, v in VALID_RANGES.items()},
        "mean_rmse_kg_ha": schema.get("mean_rmse_kg_ha"),
        "mean_r2": schema.get("mean_r2"),
        "n_features": len(schema.get("feature_cols", [])),
    }