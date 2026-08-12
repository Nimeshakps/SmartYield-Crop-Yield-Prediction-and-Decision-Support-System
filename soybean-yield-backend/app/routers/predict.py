"""Phase 1 -- Predict Yield endpoint."""

from fastapi import APIRouter, HTTPException

from app.schemas import PredictRequest, PredictResponse
from app.services.model_registry import (
    ModelFactoryMissingError,
    ModelNotFoundError,
    get_model,
    get_model_corn,
)
from app.services.predictor import predict_from_raw_row, predict_from_raw_row_corn

router = APIRouter(prefix="/api", tags=["predict"])


@router.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest):
    """Phase 1: predicts final (end-of-season) harvest yield in kg/ha and bu/acre from raw,
    un-engineered weekly weather + soil readings for the selected run/model."""
    try:
        loaded = get_model(payload.run_tag, payload.model_name)
    except ModelFactoryMissingError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ModelNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        print("Soil keys in incoming payload.raw_row:",
        {k: v for k, v in payload.raw_row.items() if any(p in k for p in
        ['bdod','cec','cfvo','clay','nitrogen','ocd','ocs','phh2o','sand','silt','soc'])})
        result = predict_from_raw_row(loaded, payload.raw_row)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Prediction failed: {e}")

    return {
        "run_tag": payload.run_tag,
        "model_name": payload.model_name,
        **result,
    }


@router.post("/predict_corn", response_model=PredictResponse)
def predict_corn(payload: PredictRequest):
    """Phase 1: predicts final (end-of-season) harvest yield in kg/ha and bu/acre from raw,
    un-engineered weekly weather + soil readings for the selected run/model."""
    try:
        loaded = get_model_corn(payload.run_tag, payload.model_name)
    except ModelFactoryMissingError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ModelNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        print("Soil keys in incoming payload.raw_row:",
        {k: v for k, v in payload.raw_row.items() if any(p in k for p in
        ['bdod','cec','cfvo','clay','nitrogen','ocd','ocs','phh2o','sand','silt','soc'])})
        result = predict_from_raw_row_corn(loaded, payload.raw_row)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Prediction failed: {e}")

    return {
        "run_tag": payload.run_tag,
        "model_name": payload.model_name,
        **result,
    }
