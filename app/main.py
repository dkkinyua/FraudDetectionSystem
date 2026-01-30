import joblib
import numpy as np
import pandas as pd
from app.utilities.utils import get_ip, get_device_type
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

model = joblib.load("jobs/xgboost.pkl")
app = FastAPI(
    version='1.0.0',
    description="Fraud detection API for fraud prediction"
)

# config middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:5173',
        '*' 
    ],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"]
)

class Transaction(BaseModel):
    amount: int
    location: str

@app.get("/", response_class=HTMLResponse)
async def demo_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Fraud Detection API - Live Demo</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-50">
        <div class="max-w-4xl mx-auto p-8">
            <h1 class="text-4xl font-bold mb-4">Fraud Detection API</h1>
            <p class="text-gray-600 mb-8">Real-time transaction fraud detection for e-commerce</p>
            
            <!-- Interactive API Tester -->
            <div class="bg-white rounded-lg shadow p-6 mb-8">
                <h2 class="text-2xl font-bold mb-4">Try It Live</h2>
                <p class="text-gray-600 mb-4">Test our API with different scenarios</p>
                
                <div class="grid grid-cols-2 gap-4 mb-4">
                    <div>
                        <label class="block text-sm font-medium mb-2">Amount ($)</label>
                        <select id="amount" class="w-full border rounded p-2">
                            <option value="10">$10 - Micro transaction</option>
                            <option value="100">$100 - Standard transaction</option>
                            <option value="1000">$1,000 - High-value</option>
                            <option value="10000">$10,000 - Enterprise</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium mb-2">User Location</label>
                        <input type="text" id="location" value="Kenya" class="w-full border rounded p-2">
                    </div>
                </div>
                
                <button onclick="testAPI()" class="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">
                    Test Fraud Detection
                </button>
                
                <div id="result" class="mt-4"></div>
            </div>
            
            <!-- Code Example -->
            <div class="bg-gray-900 text-white rounded-lg p-6 mb-8">
                <h3 class="text-xl font-bold mb-4">Integration Example</h3>
                <pre class="text-sm"><code>curl -X POST https://your-api.com/predict \\
  -H "Content-Type: application/json" \\
  -d '{
    "amount": 100,
    "location": "Kenya"
  }'</code></pre>
            </div>
            
            <!-- Features -->
            <div class="grid grid-cols-3 gap-4">
                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="font-bold mb-2">⚡ Real-time</h3>
                    <p class="text-sm text-gray-600">Sub-50ms response time</p>
                </div>
                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="font-bold mb-2">🎯 Accurate</h3>
                    <p class="text-sm text-gray-600">94%+ fraud detection rate</p>
                </div>
                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="font-bold mb-2">🔧 Easy Integration</h3>
                    <p class="text-sm text-gray-600">Simple REST API</p>
                </div>
            </div>
        </div>
        
        <script>
            async function testAPI() {
                const amount = document.getElementById('amount').value;
                const location = document.getElementById('location').value;
                const resultDiv = document.getElementById('result');
                
                resultDiv.innerHTML = '<p class="text-gray-500">Testing...</p>';
                
                try {
                    const response = await fetch('/predict', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({amount: parseInt(amount), location})
                    });
                    
                    const data = await response.json();
                    const fraudProb = (data.fraud_probability * 100).toFixed(1);
                    const isFraud = data.is_fraud;
                    
                    const color = isFraud ? 'red' : fraudProb > 50 ? 'yellow' : 'green';
                    const bgColor = isFraud ? 'bg-red-50' : fraudProb > 50 ? 'bg-yellow-50' : 'bg-green-50';
                    const textColor = isFraud ? 'text-red-800' : fraudProb > 50 ? 'text-yellow-800' : 'text-green-800';
                    
                    resultDiv.innerHTML = `
                        <div class="${bgColor} border border-${color}-200 rounded p-4">
                            <p class="${textColor} font-bold">
                                ${isFraud ? '⚠️ FRAUD DETECTED' : fraudProb > 50 ? '⚡ REVIEW NEEDED' : '✅ APPROVED'}
                            </p>
                            <p class="text-sm mt-2">Fraud Probability: ${fraudProb}%</p>
                            <p class="text-sm text-gray-600 mt-2">Response JSON:</p>
                            <pre class="text-xs mt-1 bg-white p-2 rounded">${JSON.stringify(data, null, 2)}</pre>
                        </div>
                    `;
                } catch (error) {
                    resultDiv.innerHTML = `<p class="text-red-600">Error: ${error.message}</p>`;
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/predict")
async def predict(request: Request, transaction: Transaction):
    # get device, ip and country
    device = get_device_type(request)
    ip_data = get_ip()

    df = pd.DataFrame([transaction.model_dump()])

    # engineer features
    df["transaction_location"] = ip_data["country"]

    df["location_change"] = (df["location"] != df["transaction_location"]).astype(int)

    df["amount_log"] = np.log1p(df["amount"])
    df["amount_log"] = np.clip(df['amount_log'], 0, 10)

    #create new df
    new_df = df[["amount_log", "location_change"]]

    # predict
    prob = float(model.predict_proba(new_df)[:, 1][0])

    # apply threshold
    threshold = 0.7
    pred = int(prob >= threshold)

    return {
        "fraud_probability": prob,
        "is_fraud": pred
    }


