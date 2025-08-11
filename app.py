# main.py
import joblib
import pandas as pd
import os
from fastapi import FastAPI
from models import PredictionRequest
from scripts.model import train_model


app = FastAPI()

@app.get("/")
def root():
    return {"message": "Fraud Detection API is running!"}

@app.post("/train")
def train():
    return train_model()

@app.post("/predict")
def predict(request: PredictionRequest):
    try:
        model_path = "jobs/isolation_forest.pkl"
        if not os.path.exists(model_path):
            return {"error": "Model not found. Train it first via /train."}

        model = joblib.load(model_path)
        df = pd.DataFrame([request.dict()])
        prediction = model.predict(df)[0]
        return {"prediction": int(prediction)}

    except Exception as e:
        return {"error": str(e)}
