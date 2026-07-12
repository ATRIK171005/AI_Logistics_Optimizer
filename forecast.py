"""
forecast.py
-----------
Machine learning demand simulation pipeline wrapper.
Aligns with portfolio specification requirements by bridging supervised ensemble
models (`forecaster.py`) to the application controller.
"""

from forecaster import (
    train_and_forecast,
    train_ensemble_forecaster,
    ForecastResult
)

__all__ = ["train_and_forecast", "train_ensemble_forecaster", "ForecastResult"]
