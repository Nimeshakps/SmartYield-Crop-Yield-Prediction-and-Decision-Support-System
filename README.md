#  SmartYield: Crop Yield Prediction and Decision Support System

SmartYield is a machine learning-based decision support system that predicts soybean crop yield using field-level soil properties, microclimate measurements, and historical weather data. The project aims to provide accurate early-season yield estimation to support precision agriculture and data-driven farming decisions.

---

##  Features

- End-to-end machine learning pipeline for crop yield prediction
- Automated data preprocessing and feature engineering
- Bayesian hyperparameter optimization using Optuna
- Multiple state-of-the-art regression models:
  - XGBoost
  - LightGBM
  - CatBoost
- Stacking ensemble for improved predictive performance
- Model evaluation using RMSE, MAE, and R²
- Interactive decision-support dashboard (under development)

---

##  Technologies Used

- Python
- Pandas
- NumPy
- Scikit-learn
- XGBoost
- LightGBM
- CatBoost
- Optuna
- SHAP
- Matplotlib
- Seaborn
- Joblib

---

---

##  Machine Learning Pipeline

1. Data Collection
2. Data Cleaning
3. Feature Engineering
4. Feature Selection
5. Hyperparameter Optimization (Optuna)
6. Model Training
7. Model Evaluation
8. Yield Prediction
9. Decision Support Dashboard

---

##  Model Evaluation

The project compares multiple gradient boosting models:

- XGBoost
- LightGBM
- CatBoost
- Stacking Ensemble

Performance is evaluated using:

- Root Mean Squared Error (RMSE)
- Mean Absolute Error (MAE)
- R² Score

The best-performing model is selected based on cross-validation performance.

---

##  Explainable AI (Future improvements)

To improve transparency and interpretability, SHAP (SHapley Additive Explanations) is used to:

- Identify the most influential environmental variables
- Explain individual predictions
- Visualize global feature importance

---

##  Application

SmartYield is designed to assist:

- Farmers
- Agricultural Researchers
- Agronomists
- Precision Agriculture Systems
- Agricultural Decision Support Platforms

by providing reliable crop yield predictions before harvest.

---


##  License

This project is intended for educational and research purposes.

---

##  Author

**Sachini Nimesha**

Mechanical Engineering Undergraduate

University of Peradeniya

Sri Lanka

---

