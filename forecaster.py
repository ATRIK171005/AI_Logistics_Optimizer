import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
import os

try:
    from xgboost import XGBRegressor
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

class DemandForecaster:
    def __init__(self, model_type="xgboost"):
        self.model_type = model_type if (model_type == "xgboost" and HAS_XGB) else "random_forest"
        if self.model_type == "xgboost" and HAS_XGB:
            self.model = XGBRegressor(n_estimators=120, learning_rate=0.08, max_depth=4, random_state=42)
        else:
            self.model = RandomForestRegressor(n_estimators=120, max_depth=8, random_state=42)
            
        self.features = ['Sales_Index', 'Festival_Flag', 'Rain_Storm_Flag', 'Promo_Discount_Pct']
        self.customer_cols = []
        self.is_trained = False
        self.metrics = {"r2": 0.0, "mae": 0.0}

    def train(self, df: pd.DataFrame):
        """Train regression model on historical demand dataset."""
        if df is None or df.empty:
            return 0.0, 0.0
            
        # One-hot encode Customer column
        df_encoded = pd.get_dummies(df, columns=['Customer'], drop_first=False)
        self.customer_cols = [c for c in df_encoded.columns if c.startswith('Customer_')]
        
        # Ensure all feature columns exist
        for col in self.features:
            if col not in df_encoded.columns:
                df_encoded[col] = 0.0
                
        X = df_encoded[self.features + self.customer_cols]
        y = df_encoded['Demand']
        
        self.model.fit(X, y)
        self.is_trained = True
        
        preds = self.model.predict(X)
        r2 = max(0.0, float(r2_score(y, preds)))
        mae = float(mean_absolute_error(y, preds))
        self.metrics = {"r2": round(r2, 3), "mae": round(mae, 2)}
        return r2, mae

    def predict_next_month(self, customer_list, sales_index=1.05, festival_flag=0, rain_flag=0, promo_discount=5.0):
        """Predict next month's customer demand based on economic indices and weather/festival conditions."""
        if not self.is_trained:
            # Fallback default demands if model not trained
            default_demands = {"Pune": 200, "Jaipur": 150, "Lucknow": 180, "Bangalore": 250, "Hyderabad": 220}
            return pd.DataFrame([{"Customer": c, "Demand": default_demands.get(c, 150)} for c in customer_list])
            
        predictions = []
        for cust in customer_list:
            row = {
                'Sales_Index': float(sales_index),
                'Festival_Flag': int(festival_flag),
                'Rain_Storm_Flag': int(rain_flag),
                'Promo_Discount_Pct': float(promo_discount)
            }
            for c_col in self.customer_cols:
                row[c_col] = 1 if c_col == f"Customer_{cust}" else 0
                
            X_pred = pd.DataFrame([row])[self.features + self.customer_cols]
            pred_val = self.model.predict(X_pred)[0]
            # Ensure demand is positive and rounded to integer units
            demand_int = max(50, int(round(pred_val)))
            predictions.append({
                "Customer": cust,
                "Demand": demand_int
            })
            
        return pd.DataFrame(predictions)

    def get_feature_importances(self):
        """Return dataframe of feature importances for UI analysis."""
        if not self.is_trained:
            return pd.DataFrame()
            
        importances = self.model.feature_importances_
        feature_names = [f.replace("Customer_", "City: ") for f in (self.features + self.customer_cols)]
        
        df_imp = pd.DataFrame({
            "Feature": feature_names,
            "Importance": importances
        }).sort_values(by="Importance", ascending=False)
        
        return df_imp
