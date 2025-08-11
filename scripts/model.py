import os
import joblib
import pandas as pd
from dotenv import load_dotenv
from sklearn.ensemble import IsolationForest
from sqlalchemy import create_engine
from pydantic import BaseModel

load_dotenv()

def PredictionRequest(BaseModel):
    amount: float
    device_freq: int
    location_change: int
'''
1. Read data from Transactions sql table
2. Since device, location and transactional_location are not numeric as they are categorical data, we need to encode them to numerical data
3. Set params for IsolationForest and assign them to IsolationForest 
4. Send job to jobs folder
'''
def train_model():
    try:
        engine = create_engine(os.getenv("URL"))
        df = pd.read_sql_table('transactions', con=engine, schema='shop')
        device_freq = df["device"].value_counts(normalize=True)
        df['device_freq'] = df["device"].map(device_freq)
        df["location_change"] = (df["location"] != df["transaction_location"]).astype('int')
        threshold = 0.05
        rare_devices = df[df['device_freq'] < threshold]

        features = df[['amount', 'device_freq', 'location_change']].copy()
        features.columns = ['amount', 'device_freq', 'location_change']

        n_estimators = 100
        contamination = 0.1 # expecting that 10% is fraudulent 

        iso_forest = IsolationForest(
            n_estimators=n_estimators,
            contamination=contamination,
            random_state=42
        )
        iso_forest.fit(features)

        path = "jobs/isolation_forest.pkl"
        if os.path.exists(path):
            print(f"⚠ Model already exists at {path}. Overwriting...")
        else:
            joblib.dump(iso_forest, path)
        print(f"Job loaded into {path} successfully.")

    except Exception as e:
        print(f'Error training model: {e}')

if __name__ == '__main__':
    train_model()

    