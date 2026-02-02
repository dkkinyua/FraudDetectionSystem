import uuid
import joblib
import numpy as np
import pandas as pd
from app.utilities.utils import get_ip, get_device_type
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
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

# save users in memory for dev
USERS = {} 

class UserCreate(BaseModel):
    email: str
    country: str

class Transaction(BaseModel):
    user_id: str
    amount: float  # Changed to float to accept decimal amounts

@app.post("/users/create")
async def create_user(user: UserCreate):
    user_id = str(uuid.uuid4())
    USERS[user_id] = {
        "email": user.email,
        "home_country": user.country,
        "created_at": str(datetime.now())
    }

    return {
        "user_id": user_id,
        "message": f"User created in {user.country}"
    }

@app.get("/", response_class=HTMLResponse)
async def demo_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Fraud Detection API Demo</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-50 p-8">
        <div class="max-w-4xl mx-auto">
            <h1 class="text-4xl font-bold mb-2">Fraud Detection API</h1>
            <p class="text-gray-600 mb-8">Real-time transaction fraud detection</p>
            
            <!-- Step 1: Create Test User -->
            <div class="bg-white rounded-lg shadow p-6 mb-6">
                <h2 class="text-2xl font-bold mb-4">Step 1: Create Test User</h2>
                <div class="grid grid-cols-2 gap-4 mb-4">
                    <div>
                        <label class="block text-sm font-medium mb-2">Email</label>
                        <input type="email" id="email" value="test@example.com" 
                               class="w-full border rounded p-2">
                    </div>
                    <div>
                        <label class="block text-sm font-medium mb-2">Home Country</label>
                        <select id="country" class="w-full border rounded p-2">
                            <option value="">Select your country</option>
                            <option value="Kenya">Kenya</option>
                            <option value="United States">United States</option>
                            <option value="United Kingdom">United Kingdom</option>
                            <option value="Nigeria">Nigeria</option>
                            <option value="South Africa">South Africa</option>
                            <option value="Uganda">Uganda</option>
                            <option value="Tanzania">Tanzania</option>
                            <option value="Ghana">Ghana</option>
                            <option value="Canada">Canada</option>
                            <option value="Australia">Australia</option>
                            <option value="India">India</option>
                            <option value="China">China</option>
                            <option value="Germany">Germany</option>
                            <option value="France">France</option>
                        </select>
                    </div>
                </div>
                <button onclick="createUser()" 
                        class="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">
                    Create Test User
                </button>
                <div id="user-result" class="mt-4"></div>
            </div>
            
            <!-- Step 2: Test Transaction -->
            <div class="bg-white rounded-lg shadow p-6 mb-6">
                <h2 class="text-2xl font-bold mb-4">Step 2: Test Transaction</h2>
                <div class="grid grid-cols-2 gap-4 mb-4">
                    <div>
                        <label class="block text-sm font-medium mb-2">User ID</label>
                        <input type="text" id="user-id" placeholder="Create user first" 
                               class="w-full border rounded p-2" readonly>
                    </div>
                    <div>
                        <label class="block text-sm font-medium mb-2">Transaction Amount ($)</label>
                        <input type="number" id="amount" placeholder="Enter amount (e.g., 250.50)" 
                               min="0" step="0.01" value="100"
                               class="w-full border rounded p-2">
                        <p class="text-xs text-gray-500 mt-1">Enter any amount you want to test</p>
                    </div>
                </div>
                <button onclick="testTransaction()" 
                        class="bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700">
                    Test Fraud Detection
                </button>
                <div id="fraud-result" class="mt-4"></div>
            </div>
            
            <!-- API Documentation -->
            <div class="bg-gray-900 text-white rounded-lg p-6">
                <h3 class="text-xl font-bold mb-4">Integration Example</h3>
                <div class="text-sm">
                    <p class="mb-2 text-gray-400">1. Create user:</p>
                    <pre class="bg-gray-800 p-3 rounded mb-4 overflow-x-auto">curl -X POST https://your-api.com/users/create \\
  -H "Content-Type: application/json" \\
  -d '{"email": "user@example.com", "country": "Kenya"}'</pre>
                    
                    <p class="mb-2 text-gray-400">2. Check transaction:</p>
                    <pre class="bg-gray-800 p-3 rounded overflow-x-auto">curl -X POST https://your-api.com/predict \\
  -H "Content-Type: application/json" \\
  -d '{"user_id": "abc-123", "amount": 250.50}'</pre>
                </div>
            </div>
        </div>
        
        <script>
            let currentUserId = null;
            
            async function createUser() {
                const email = document.getElementById('email').value;
                const country = document.getElementById('country').value;
                const resultDiv = document.getElementById('user-result');
                
                if (!country) {
                    resultDiv.innerHTML = '<p class="text-red-600">Please select a country!</p>';
                    return;
                }
                
                resultDiv.innerHTML = '<p class="text-gray-500">Creating user...</p>';
                
                try {
                    const response = await fetch('/users/create', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({email, country})
                    });
                    
                    const data = await response.json();
                    currentUserId = data.user_id;
                    
                    // Populate user_id field
                    document.getElementById('user-id').value = currentUserId;
                    
                    resultDiv.innerHTML = `
                        <div class="bg-green-50 border border-green-200 rounded p-4">
                            <p class="text-green-800 font-bold">✓ User Created</p>
                            <p class="text-sm mt-1">User ID: <code class="bg-green-100 px-2 py-1 rounded">${currentUserId}</code></p>
                            <p class="text-sm">Home Country: ${country}</p>
                        </div>
                    `;
                } catch (error) {
                    resultDiv.innerHTML = `<p class="text-red-600">Error: ${error.message}</p>`;
                }
            }
            
            async function testTransaction() {
                const userId = document.getElementById('user-id').value;
                const amount = parseFloat(document.getElementById('amount').value);
                const resultDiv = document.getElementById('fraud-result');
                
                if (!userId) {
                    resultDiv.innerHTML = '<p class="text-red-600">Please create a user first!</p>';
                    return;
                }
                
                if (!amount || amount <= 0) {
                    resultDiv.innerHTML = '<p class="text-red-600">Please enter a valid amount!</p>';
                    return;
                }
                
                resultDiv.innerHTML = '<p class="text-gray-500">Testing fraud detection...</p>';
                
                try {
                    const response = await fetch('/predict', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({user_id: userId, amount: amount})
                    });
                    
                    const data = await response.json();
                    const fraudProb = (data.fraud_probability * 100).toFixed(1);
                    const isFraud = data.is_fraud;
                    
                    const bgColor = isFraud ? 'bg-red-50' : fraudProb > 50 ? 'bg-yellow-50' : 'bg-green-50';
                    const borderColor = isFraud ? 'border-red-200' : fraudProb > 50 ? 'border-yellow-200' : 'border-green-200';
                    const textColor = isFraud ? 'text-red-800' : fraudProb > 50 ? 'text-yellow-800' : 'text-green-800';
                    const icon = isFraud ? '' : fraudProb > 50 ? '' : '';
                    const status = isFraud ? 'FRAUD DETECTED' : fraudProb > 50 ? 'REVIEW NEEDED' : 'APPROVED';
                    
                    resultDiv.innerHTML = `
                        <div class="${bgColor} border ${borderColor} rounded p-4">
                            <p class="${textColor} font-bold text-lg">${icon} ${status}</p>
                            <p class="text-sm mt-2">Amount: $${amount.toFixed(2)}</p>
                            <p class="text-sm">Fraud Probability: ${fraudProb}%</p>
                            <p class="text-sm">Original location: ${data.user_home_country}</p>
                            <p class="text-sm">Transaction From: ${data.transaction_country}</p>
                            <p class="text-sm">Location Mismatch: ${data.location_mismatch ? 'Yes' : 'No'}</p>
                            <details class="mt-3">
                                <summary class="cursor-pointer text-sm ${textColor}">View JSON Response</summary>
                                <pre class="text-xs mt-2 bg-white p-2 rounded overflow-x-auto">${JSON.stringify(data, null, 2)}</pre>
                            </details>
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
    # get user
    user = USERS.get(transaction.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate amount
    if transaction.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")
    
    # get device, ip and country
    device = get_device_type(request)
    ip_data = get_ip(request)
    txn_location = ip_data["country"]

    # get user original location and compare
    home_location = user["home_country"]
    location_change = int(home_location != txn_location)

    df = pd.DataFrame([{
        "amount": transaction.amount,
        "location_change": location_change
    }])

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
        "is_fraud": pred,
        "amount": transaction.amount,
        "user_home_country": home_location,
        "transaction_country": txn_location,
        "location_mismatch": location_change == 1
    }