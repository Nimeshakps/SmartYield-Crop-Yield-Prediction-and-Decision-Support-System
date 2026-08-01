# Soybean Yield Prediction -- Backend API

FastAPI backend for the soybean yield prediction pipeline, converted from the
`YP_prediction_pipeline_decision_making` inference notebook into a proper, git-ready backend
service.

It exposes two prediction phases as REST endpoints, both operating on **raw, un-engineered**
weekly weather + soil readings (exactly the columns in the original training CSV):

- **Phase 1 -- Predict Yield** (`POST /api/predict`): runs raw inputs through the same
  `engineer_features` -> cluster -> impute -> predict pipeline used at training time, and
  returns the model's predicted final (end-of-season) harvest yield.
- **Phase 2 -- Optimize Yield** (`POST /api/optimize`): starting from the farmer's Phase 1
  inputs, greedily searches the controllable variables (Vapor Pressure, Soil pH, Cation
  Exchange Capacity, Total Nitrogen -- whichever are active for the selected model) to
  recommend up to 4 changes that maximize predicted yield.

## Project layout

```
backend/
├── app/
│   ├── main.py                 # FastAPI app + routers
│   ├── config.py               # paths / settings
│   ├── schemas.py               # Pydantic request/response models
│   ├── core/
│   │   ├── country_config.py    # CountryConfig + make_usa_config (verbatim from notebook)
│   │   ├── feature_engineering.py # engineer_features / build_feature_cols (verbatim)
│   │   └── validation.py        # valid ranges + controllable-variable definitions
│   ├── services/
│   │   ├── model_registry.py    # discovers + loads + caches model_factory artifacts
│   │   ├── predictor.py         # Phase 1 prediction logic
│   │   └── optimizer.py         # Phase 2 optimization logic
│   └── routers/
│       ├── runs.py              # GET /api/runs, /models, /schema
│       ├── predict.py           # POST /api/predict
│       └── optimize.py          # POST /api/optimize
├── model_factory/               # <-- place the trained model_factory folder here manually
├── requirements.txt
├── run.py
├── Dockerfile
└── .env.example
```

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Add your trained models

Copy the `model_factory` folder produced by the training pipeline into `backend/model_factory/`,
keeping its structure exactly as-is:

```
model_factory/<run_tag>/<ModelName>/{model.joblib, region_encoder.joblib, imputer.joblib,
cluster_artifacts.joblib, feature_schema.json}
```

(This step is done manually and is **not** part of this generated codebase.)

### Run the API

```bash
python run.py
# or
uvicorn app.main:app --reload --port 8000
```

The API will be live at `http://localhost:8000`, with interactive docs at
`http://localhost:8000/docs`.

## API summary

| Method | Path                                                    | Purpose                                   |
|--------|----------------------------------------------------------|--------------------------------------------|
| GET    | `/api/runs`                                               | List available week-range run tags        |
| GET    | `/api/runs/{run_tag}/models`                                | List models trained for a run              |
| GET    | `/api/runs/{run_tag}/models/{model_name}/schema`              | Form-building schema + reported metrics   |
| POST   | `/api/predict`                                             | Phase 1: predict yield                     |
| POST   | `/api/optimize`                                             | Phase 2: recommend controllable changes    |

### Example: `POST /api/predict`

```json
{
  "run_tag": "weeks_14_20",
  "model_name": "XGBoost",
  "raw_row": {
    "prcp_14": 2.1, "prcp_15": 1.8, "...": "...",
    "phh2o_mean_0-5cm": 6.4, "...": "...",
    "obs_year": 2026,
    "region": "Iowa"
  }
}
```

### Example: `POST /api/optimize`

Same `raw_row` payload as `/api/predict`, plus optional `max_recommendations`, `grid_points`,
and `min_meaningful_gain_kg_ha` overrides.

## Notes

- `region` has zero effect on the prediction (it's excluded from the trained feature set) but is
  still required by `engineer_features`, so the frontend should send any valid class from the
  schema's `region_classes` list.
- Leave any raw reading blank/`null` to mark it missing -- it will be median-imputed with the
  training-time imputer, exactly like the original notebook.
