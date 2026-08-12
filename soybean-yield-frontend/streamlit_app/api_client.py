# """Thin wrapper around `requests` for calling the Soybean Yield Prediction backend API."""

# import requests
# import streamlit as st

# from streamlit_app.config import API_BASE_URL, REQUEST_TIMEOUT_SECONDS


# class ApiError(Exception):
#     """Raised when the backend returns a non-2xx response, with the server's detail message."""


# def _handle_response(resp: requests.Response):
#     if resp.status_code >= 400:
#         try:
#             detail = resp.json().get("detail", resp.text)
#         except Exception:
#             detail = resp.text
#         raise ApiError(detail)
#     return resp.json()


# @st.cache_data(ttl=60, show_spinner=False)
# def get_runs() -> list:
#     """Lists available week-range run tags."""
#     resp = requests.get(f"{API_BASE_URL}/api/runs", timeout=REQUEST_TIMEOUT_SECONDS)
#     return _handle_response(resp)["runs"]


# @st.cache_data(ttl=60, show_spinner=False)
# def get_models(run_tag: str) -> list:
#     """Lists available models for a given run tag."""
#     resp = requests.get(f"{API_BASE_URL}/api/runs/{run_tag}/models", timeout=REQUEST_TIMEOUT_SECONDS)
#     return _handle_response(resp)["models"]


# @st.cache_data(ttl=60, show_spinner=False)
# def get_schema(run_tag: str, model_name: str) -> dict:
#     """Fetches the form-building schema + reported metrics for a run/model pair."""
#     resp = requests.get(
#         f"{API_BASE_URL}/api/runs/{run_tag}/models/{model_name}/schema",
#         timeout=REQUEST_TIMEOUT_SECONDS,
#     )
#     return _handle_response(resp)


# def predict(run_tag: str, model_name: str, raw_row: dict) -> dict:
#     """Phase 1: predict yield from raw inputs."""
#     resp = requests.post(
#         f"{API_BASE_URL}/api/predict",
#         json={"run_tag": run_tag, "model_name": model_name, "raw_row": raw_row},
#         timeout=REQUEST_TIMEOUT_SECONDS,
#     )
#     return _handle_response(resp)


# def optimize(
#     run_tag: str,
#     model_name: str,
#     raw_row: dict,
#     max_recommendations: int = 4,
#     grid_points: int = 25,
#     min_meaningful_gain_kg_ha: float = 1.0,
# ) -> dict:
#     """Phase 2: recommend controllable-factor changes to maximize predicted yield."""
#     resp = requests.post(
#         f"{API_BASE_URL}/api/optimize",
#         json={
#             "run_tag": run_tag,
#             "model_name": model_name,
#             "raw_row": raw_row,
#             "max_recommendations": max_recommendations,
#             "grid_points": grid_points,
#             "min_meaningful_gain_kg_ha": min_meaningful_gain_kg_ha,
#         },
#         timeout=REQUEST_TIMEOUT_SECONDS,
#     )
#     return _handle_response(resp)


# @st.cache_data(ttl=15, show_spinner=False)
# def check_backend_alive() -> bool:
#     try:
#         resp = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
#         return resp.status_code == 200
#     except requests.RequestException:
#         return False



"""Thin wrapper around `requests` for calling the Soybean Yield Prediction backend API."""

import requests
import streamlit as st

from streamlit_app.config import API_BASE_URL, REQUEST_TIMEOUT_SECONDS


class ApiError(Exception):
    """Raised when the backend returns a non-2xx response, with the server's detail message."""


def _handle_response(resp: requests.Response):
    if resp.status_code >= 400:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        raise ApiError(detail)
    return resp.json()


@st.cache_data(ttl=60, show_spinner=False)
def get_runs() -> list:
    """Lists available week-range run tags."""
    resp = requests.get(f"{API_BASE_URL}/api/runs", timeout=REQUEST_TIMEOUT_SECONDS)
    return _handle_response(resp)["runs"]


@st.cache_data(ttl=60, show_spinner=False)
def get_models(run_tag: str) -> list:
    """Lists available models for a given run tag."""
    resp = requests.get(f"{API_BASE_URL}/api/runs/{run_tag}/models", timeout=REQUEST_TIMEOUT_SECONDS)
    return _handle_response(resp)["models"]


@st.cache_data(ttl=60, show_spinner=False)
def get_schema(run_tag: str, model_name: str) -> dict:
    """Fetches the form-building schema + reported metrics for a run/model pair."""
    resp = requests.get(
        f"{API_BASE_URL}/api/runs/{run_tag}/models/{model_name}/schema",
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    return _handle_response(resp)



#########corn

@st.cache_data(ttl=60, show_spinner=False)
def get_runs_corn() -> list:
    """Lists available week-range run tags."""
    resp = requests.get(f"{API_BASE_URL}/api/runs_corn", timeout=REQUEST_TIMEOUT_SECONDS)
    return _handle_response(resp)["runs"]


@st.cache_data(ttl=60, show_spinner=False)
def get_models_corn(run_tag: str) -> list:
    """Lists available models for a given run tag."""
    resp = requests.get(f"{API_BASE_URL}/api/runs_corn/{run_tag}/models", timeout=REQUEST_TIMEOUT_SECONDS)
    return _handle_response(resp)["models"]


@st.cache_data(ttl=60, show_spinner=False)
def get_schema_corn(run_tag: str, model_name: str) -> dict:
    """Fetches the form-building schema + reported metrics for a run/model pair."""
    resp = requests.get(
        f"{API_BASE_URL}/api/runs_corn/{run_tag}/models/{model_name}/schema",
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    return _handle_response(resp)


#########corn


def predict(run_tag: str, model_name: str, raw_row: dict) -> dict:
    """Phase 1: predict yield from raw inputs."""
    resp = requests.post(
        f"{API_BASE_URL}/api/predict",
        json={"run_tag": run_tag, "model_name": model_name, "raw_row": raw_row},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    return _handle_response(resp)

def predict_corn(run_tag: str, model_name: str, raw_row: dict) -> dict:
    """Phase 1: predict yield from raw inputs."""
    resp = requests.post(
        f"{API_BASE_URL}/api/predict_corn",
        json={"run_tag": run_tag, "model_name": model_name, "raw_row": raw_row},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    return _handle_response(resp)


def optimize(
    run_tag: str,
    model_name: str,
    raw_row: dict,
    max_recommendations: int = 4,
    grid_points: int = 25,
    min_meaningful_gain_kg_ha: float = 1.0,
) -> dict:
    """Phase 2: recommend controllable-factor changes to maximize predicted yield."""
    resp = requests.post(
        f"{API_BASE_URL}/api/optimize",
        json={
            "run_tag": run_tag,
            "model_name": model_name,
            "raw_row": raw_row,
            "max_recommendations": max_recommendations,
            "grid_points": grid_points,
            "min_meaningful_gain_kg_ha": min_meaningful_gain_kg_ha,
        },
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    return _handle_response(resp)


@st.cache_data(ttl=15, show_spinner=False)
def check_backend_alive() -> bool:
    try:
        resp = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        return resp.status_code == 200
    except requests.RequestException:
        return False
