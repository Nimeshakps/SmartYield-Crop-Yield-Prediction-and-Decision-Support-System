"""Frontend configuration: backend API location and theme colors."""

import os

# Point this at your running FastAPI backend. Override with the API_BASE_URL env var,
# e.g. when the backend is deployed separately from the Streamlit app.
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

REQUEST_TIMEOUT_SECONDS = 60

# ── Greenery + yellowish palette, used by theme.py for custom CSS ──
COLORS = {
    "forest_green": "#2F5233",
    "leaf_green": "#4C7A3F",
    "sage_green": "#8CB369",
    "pale_green": "#EAF3E1",
    "sunflower_yellow": "#F2C94C",
    "golden_yellow": "#E0A800",
    "cream": "#FBFBF3",
    "text_dark": "#1F3A1F",
    "white": "#FFFFFF",
}
