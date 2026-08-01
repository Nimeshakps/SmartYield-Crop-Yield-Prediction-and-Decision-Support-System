# Soybean Yield Prediction -- Frontend Dashboard

A Streamlit dashboard (Python) for the soybean yield prediction backend, styled in a
greenery + yellowish theme. It talks to the FastAPI backend over HTTP and offers the two
prediction phases as separate pages.

## Project layout

```
frontend/
├── app.py                          # Landing page / entrypoint (streamlit run app.py)
├── pages/
│   ├── 1_🌾_Predict_Yield.py        # Phase 1 -- predict yield from raw inputs
│   └── 2_📈_Optimize_Yield.py       # Phase 2 -- recommend changes to maximize yield
├── streamlit_app/                   # Library code (not a page itself)
│   ├── config.py                    # API_BASE_URL + color palette
│   ├── theme.py                     # Custom CSS (greenery/yellow theme) + hero banner
│   ├── api_client.py                 # requests wrapper around the backend API
│   └── components/
│       ├── forms.py                  # Dynamic weekly-weather / soil input tables
│       └── utils.py                  # Sidebar run/model selector, result renderers
├── .streamlit/config.toml            # Streamlit theme config
└── requirements.txt
```

## Setup

```bash
cd frontend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Configure the backend URL

By default the app calls `http://localhost:8000`. Point it elsewhere with:

```bash
export API_BASE_URL=http://localhost:8000
```

## Run

```bash
streamlit run app.py
```

Open the URL Streamlit prints (usually `http://localhost:8501`). Use the left navigation to
switch between **Predict Yield** and **Optimize Yield**, and the sidebar on each page to choose
a week-range run (e.g. `weeks_14_20`) and a trained model (e.g. XGBoost, LightGBM, CatBoost,
Stacking Ensemble).

## How the form works

- The **weekly weather table** has one row per growing-season week and one column per active
  weather variable for the selected model -- exactly the raw columns the model was trained on.
- The **soil table** has one row per raw soil reading (soil doesn't vary by week, only by
  measurement depth).
- Leaving any cell blank marks it missing -- the backend median-imputes it automatically with
  the same imputer fit during training, just like the original notebook.
- **Phase 1 (Predict Yield)** sends these raw inputs straight to the model and shows the
  predicted final harvest yield in kg/ha and bu/acre.
- **Phase 2 (Optimize Yield)** uses the same inputs as a starting point and searches the
  controllable factors available for the selected model (vapor pressure, soil pH, cation
  exchange capacity, total nitrogen) for the changes that would raise predicted yield the most.

## Notes

- Requires the backend API to be running and reachable (see the `backend/` project).
- `region` has no effect on the prediction but is required by the pipeline; pick any option.
- Color theme: forest/leaf/sage greens with sunflower/golden yellow accents, configured in
  `.streamlit/config.toml` and `streamlit_app/theme.py`.
