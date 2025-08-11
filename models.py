from pydantic import BaseModel

def PredictionRequest(BaseModel):
    amount: float
    device_freq: int
    location_change: int