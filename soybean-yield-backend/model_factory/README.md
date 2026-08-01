# model_factory

This folder is intentionally empty in the repo.

Place the `model_factory` folder produced by the **training pipeline** here manually, keeping
its exact structure:

```
model_factory/
    <run_tag>/                      e.g. weeks_14_20, weeks_14_30
        <ModelName>/                e.g. XGBoost, LightGBM, CatBoost, Stacking_Ensemble
            model.joblib
            region_encoder.joblib
            imputer.joblib
            cluster_artifacts.joblib
            feature_schema.json
```

The backend (`app/services/model_registry.py`) scans this folder at request time to discover
available run tags and models, and loads/caches each model's artifacts on first use.

If you keep `model_factory` somewhere else on disk, point the backend at it with:

```bash
export MODEL_FACTORY_DIR=/absolute/path/to/model_factory
```
