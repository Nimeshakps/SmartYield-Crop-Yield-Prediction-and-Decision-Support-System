# """
# Model registry: discovers available run tags / model names inside the manually-placed
# model_factory folder, and lazily loads + caches each model's artifacts
# (model.joblib, region_encoder.joblib, imputer.joblib, cluster_artifacts.joblib,
# feature_schema.json) plus the CountryConfig rebuilt from its schema.
# """

# import json
# import os
# import threading
# from pathlib import Path
# from typing import NamedTuple

# import joblib

# from app.config import MODEL_FACTORY_DIR
# from app.core.country_config import CountryConfig, make_usa_config


# class ModelNotFoundError(Exception):
#     """Raised when a requested run_tag / model_name doesn't exist in model_factory."""


# class ModelFactoryMissingError(Exception):
#     """Raised when the model_factory folder itself hasn't been placed yet."""


# class LoadedModel(NamedTuple):
#     model: object
#     region_encoder: object
#     imputer: object
#     cluster_artifacts: dict
#     schema: dict
#     run_cfg: CountryConfig


# _cache: dict[str, LoadedModel] = {}
# _cache_lock = threading.Lock()


# def _check_factory_exists() -> Path:
#     if not MODEL_FACTORY_DIR.is_dir():
#         raise ModelFactoryMissingError(
#             f"model_factory folder not found at '{MODEL_FACTORY_DIR}'. "
#             "Place the model_factory folder produced by the training pipeline at this path "
#             "(or point MODEL_FACTORY_DIR env var at it) before calling this API."
#         )
#     return MODEL_FACTORY_DIR


# def list_runs() -> list[str]:
#     """Lists available week-range run tags (e.g. 'weeks_14_20', 'weeks_14_30')."""
#     factory_dir = _check_factory_exists()
#     return sorted(
#         d for d in os.listdir(factory_dir)
#         if os.path.isdir(os.path.join(factory_dir, d))
#     )


# def list_models(run_tag: str) -> list[str]:
#     """Lists available model names for a given run tag (e.g. 'XGBoost', 'LightGBM')."""
#     factory_dir = _check_factory_exists()
#     run_dir = factory_dir / run_tag
#     if not run_dir.is_dir():
#         raise ModelNotFoundError(f"Run tag '{run_tag}' not found in model_factory.")
#     return sorted(
#         d for d in os.listdir(run_dir) if os.path.isdir(os.path.join(run_dir, d))
#     )


# def get_model(run_tag: str, model_name: str) -> LoadedModel:
#     """Loads (or returns from cache) all artifacts for a given run_tag/model_name pair."""
#     cache_key = f"{run_tag}::{model_name}"
#     with _cache_lock:
#         if cache_key in _cache:
#             return _cache[cache_key]

#     factory_dir = _check_factory_exists()
#     model_dir = factory_dir / run_tag / model_name
#     if not model_dir.is_dir():
#         raise ModelNotFoundError(
#             f"Model '{model_name}' not found for run '{run_tag}' in model_factory."
#         )

#     required_files = [
#         "model.joblib", "region_encoder.joblib", "imputer.joblib",
#         "cluster_artifacts.joblib", "feature_schema.json",
#     ]
#     missing = [f for f in required_files if not (model_dir / f).is_file()]
#     if missing:
#         raise ModelNotFoundError(
#             f"Model folder '{model_dir}' is missing required file(s): {', '.join(missing)}."
#         )

#     model = joblib.load(model_dir / "model.joblib")
#     region_encoder = joblib.load(model_dir / "region_encoder.joblib")
#     imputer = joblib.load(model_dir / "imputer.joblib")
#     cluster_artifacts = joblib.load(model_dir / "cluster_artifacts.joblib")
#     schema = json.load(open(model_dir / "feature_schema.json"))

#     run_cfg = make_usa_config(schema)

#     loaded = LoadedModel(
#         model=model,
#         region_encoder=region_encoder,
#         imputer=imputer,
#         cluster_artifacts=cluster_artifacts,
#         schema=schema,
#         run_cfg=run_cfg,
#     )

#     with _cache_lock:
#         _cache[cache_key] = loaded

#     return loaded


# def clear_cache() -> None:
#     """Clears the in-memory artifact cache (useful after swapping model_factory contents)."""
#     with _cache_lock:
#         _cache.clear()

"""
Model registry: discovers available run tags / model names inside the manually-placed
model_factory folder, and lazily loads + caches each model's artifacts
(model.joblib, region_encoder.joblib, imputer.joblib, cluster_artifacts.joblib,
feature_schema.json) plus the CountryConfig rebuilt from its schema.
"""

import json
import os
import threading
from pathlib import Path
from typing import NamedTuple

import joblib

from app.config import MODEL_FACTORY_DIR
from app.config import MODEL_FACTORY_DIR_CORN
from app.core.country_config import CountryConfig, make_usa_config


class ModelNotFoundError(Exception):
    """Raised when a requested run_tag / model_name doesn't exist in model_factory."""


class ModelFactoryMissingError(Exception):
    """Raised when the model_factory folder itself hasn't been placed yet."""


class LoadedModel(NamedTuple):
    model: object
    region_encoder: object
    imputer: object
    cluster_artifacts: dict
    schema: dict
    run_cfg: CountryConfig


_cache: dict[str, LoadedModel] = {}
_cache_lock = threading.Lock()


def _check_factory_exists() -> Path:
    if not MODEL_FACTORY_DIR.is_dir():
        raise ModelFactoryMissingError(
            f"model_factory folder not found at '{MODEL_FACTORY_DIR}'. "
            "Place the model_factory folder produced by the training pipeline at this path "
            "(or point MODEL_FACTORY_DIR env var at it) before calling this API."
        )
    return MODEL_FACTORY_DIR

def _check_factory_exists_corn() -> Path:
    if not MODEL_FACTORY_DIR_CORN.is_dir():
        raise ModelFactoryMissingError(
            f"model_factory folder not found at '{MODEL_FACTORY_DIR_CORN}'. "
            "Place the model_factory folder produced by the training pipeline at this path "
            "(or point MODEL_FACTORY_DIR env var at it) before calling this API."
        )
    return MODEL_FACTORY_DIR_CORN


def list_runs() -> list[str]:
    """Lists available week-range run tags (e.g. 'weeks_14_20', 'weeks_14_30')."""
    factory_dir = _check_factory_exists()
    return sorted(
        d for d in os.listdir(factory_dir)
        if os.path.isdir(os.path.join(factory_dir, d))
    )
    
def list_runs_corn() -> list[str]:
    """Lists available week-range run tags (e.g. 'weeks_14_20', 'weeks_14_30')."""
    factory_dir = _check_factory_exists_corn()
    return sorted(
        d for d in os.listdir(factory_dir)
        if os.path.isdir(os.path.join(factory_dir, d))
    )


def list_models(run_tag: str) -> list[str]:
    """Lists available model names for a given run tag (e.g. 'XGBoost', 'LightGBM')."""
    factory_dir = _check_factory_exists()
    run_dir = factory_dir / run_tag
    if not run_dir.is_dir():
        raise ModelNotFoundError(f"Run tag '{run_tag}' not found in model_factory.")
    return sorted(
        d for d in os.listdir(run_dir) if os.path.isdir(os.path.join(run_dir, d))
    )

def list_models_corn(run_tag: str) -> list[str]:
    """Lists available model names for a given run tag (e.g. 'XGBoost', 'LightGBM')."""
    factory_dir = _check_factory_exists_corn()
    run_dir = factory_dir / run_tag
    if not run_dir.is_dir():
        raise ModelNotFoundError(f"Run tag '{run_tag}' not found in model_factory.")
    return sorted(
        d for d in os.listdir(run_dir) if os.path.isdir(os.path.join(run_dir, d))
    )


def get_model(run_tag: str, model_name: str) -> LoadedModel:
    """Loads (or returns from cache) all artifacts for a given run_tag/model_name pair."""
    cache_key = f"{run_tag}::{model_name}"
    with _cache_lock:
        if cache_key in _cache:
            return _cache[cache_key]

    factory_dir = _check_factory_exists()
    model_dir = factory_dir / run_tag / model_name
    if not model_dir.is_dir():
        raise ModelNotFoundError(
            f"Model '{model_name}' not found for run '{run_tag}' in model_factory."
        )

    required_files = [
        "model.joblib", "region_encoder.joblib", "imputer.joblib",
        "cluster_artifacts.joblib", "feature_schema.json",
    ]
    missing = [f for f in required_files if not (model_dir / f).is_file()]
    if missing:
        raise ModelNotFoundError(
            f"Model folder '{model_dir}' is missing required file(s): {', '.join(missing)}."
        )

    model = joblib.load(model_dir / "model.joblib")
    region_encoder = joblib.load(model_dir / "region_encoder.joblib")
    imputer = joblib.load(model_dir / "imputer.joblib")
    cluster_artifacts = joblib.load(model_dir / "cluster_artifacts.joblib")
    schema = json.load(open(model_dir / "feature_schema.json"))

    run_cfg = make_usa_config(schema)

    loaded = LoadedModel(
        model=model,
        region_encoder=region_encoder,
        imputer=imputer,
        cluster_artifacts=cluster_artifacts,
        schema=schema,
        run_cfg=run_cfg,
    )

    with _cache_lock:
        _cache[cache_key] = loaded

    return loaded


def get_model_corn(run_tag: str, model_name: str) -> LoadedModel:
    """Loads (or returns from cache) all artifacts for a given run_tag/model_name pair."""
    cache_key = f"{run_tag}::{model_name}"
    with _cache_lock:
        if cache_key in _cache:
            return _cache[cache_key]

    factory_dir = _check_factory_exists_corn()
    model_dir = factory_dir / run_tag / model_name
    if not model_dir.is_dir():
        raise ModelNotFoundError(
            f"Model '{model_name}' not found for run '{run_tag}' in model_factory."
        )

    required_files = [
        "model.joblib", "region_encoder.joblib", "imputer.joblib",
        "cluster_artifacts.joblib", "feature_schema.json",
    ]
    missing = [f for f in required_files if not (model_dir / f).is_file()]
    if missing:
        raise ModelNotFoundError(
            f"Model folder '{model_dir}' is missing required file(s): {', '.join(missing)}."
        )

    model = joblib.load(model_dir / "model.joblib")
    region_encoder = joblib.load(model_dir / "region_encoder.joblib")
    imputer = joblib.load(model_dir / "imputer.joblib")
    cluster_artifacts = joblib.load(model_dir / "cluster_artifacts.joblib")
    schema = json.load(open(model_dir / "feature_schema.json"))

    run_cfg = make_usa_config(schema)

    loaded = LoadedModel(
        model=model,
        region_encoder=region_encoder,
        imputer=imputer,
        cluster_artifacts=cluster_artifacts,
        schema=schema,
        run_cfg=run_cfg,
    )

    with _cache_lock:
        _cache[cache_key] = loaded

    return loaded


def clear_cache() -> None:
    """Clears the in-memory artifact cache (useful after swapping model_factory contents)."""
    with _cache_lock:
        _cache.clear()