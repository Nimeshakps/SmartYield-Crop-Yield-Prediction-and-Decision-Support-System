"""Phase 2 -- Optimize Yield ('what should I change to get a higher yield?') endpoint."""

from fastapi import APIRouter, HTTPException

from app.schemas import OptimizeRequest, OptimizeResponse
from app.services.model_registry import (
    ModelFactoryMissingError,
    ModelNotFoundError,
    get_model,
)
from app.services.optimizer import optimize_yield

router = APIRouter(prefix="/api", tags=["optimize"])


@router.post("/optimize", response_model=OptimizeResponse)
def optimize(payload: OptimizeRequest):
    """Phase 2: greedy coordinate-ascent search over controllable variables (vapor pressure,
    soil pH, cation exchange capacity, total nitrogen -- whichever are active for this run) to
    recommend up to `max_recommendations` changes that maximize predicted yield."""
    try:
        loaded = get_model(payload.run_tag, payload.model_name)
    except ModelFactoryMissingError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ModelNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        result = optimize_yield(
            loaded,
            payload.raw_row,
            max_recommendations=payload.max_recommendations,
            grid_points=payload.grid_points,
            min_meaningful_gain_kg_ha=payload.min_meaningful_gain_kg_ha,
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Optimization failed: {e}")

    return {
        "run_tag": payload.run_tag,
        "model_name": payload.model_name,
        **result,
    }
