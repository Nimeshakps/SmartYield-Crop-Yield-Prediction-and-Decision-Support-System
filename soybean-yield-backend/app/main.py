"""
Soybean Yield Prediction API -- FastAPI application entrypoint.

Run locally with:
    uvicorn app.main:app --reload --port 8000

Endpoints:
    GET  /api/runs                                            -- list available run tags
    GET  /api/runs/{run_tag}/models                            -- list models for a run
    GET  /api/runs/{run_tag}/models/{model_name}/schema         -- form-building schema + metrics
    POST /api/predict                                           -- Phase 1: predict yield
    POST /api/optimize                                          -- Phase 2: recommend changes
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import API_DESCRIPTION, API_TITLE, API_VERSION, CORS_ORIGINS
from app.routers import optimize, predict, runs

app = FastAPI(title=API_TITLE, description=API_DESCRIPTION, version=API_VERSION)

origins = ["*"] if CORS_ORIGINS.strip() == "*" else [o.strip() for o in CORS_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(runs.router)
app.include_router(predict.router)
app.include_router(optimize.router)


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "service": API_TITLE, "version": API_VERSION}


@app.get("/api/health", tags=["health"])
def health():
    return {"status": "healthy"}
