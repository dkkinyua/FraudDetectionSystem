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
    amount: int

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
                            <option value="Brazil">Brazil</option>
                            <option value="Mexico">Mexico</option>
                            <option value="Japan">Japan</option>
                            <option value="South Korea">South Korea</option>
                            <option value="Singapore">Singapore</option>
                            <option value="Malaysia">Malaysia</option>
                            <option value="Thailand">Thailand</option>
                            <option value="Indonesia">Indonesia</option>
                            <option value="Philippines">Philippines</option>
                            <option value="Vietnam">Vietnam</option>
                            <option value="Egypt">Egypt</option>
                            <option value="Morocco">Morocco</option>
                            <option value="Algeria">Algeria</option>
                            <option value="Tunisia">Tunisia</option>
                            <option value="Ethiopia">Ethiopia</option>
                            <option value="Rwanda">Rwanda</option>
                            <option value="Zambia">Zambia</option>
                            <option value="Zimbabwe">Zimbabwe</option>
                            <option value="Botswana">Botswana</option>
                            <option value="Namibia">Namibia</option>
                            <option value="Mauritius">Mauritius</option>
                            <option value="Seychelles">Seychelles</option>
                            <option value="Spain">Spain</option>
                            <option value="Italy">Italy</option>
                            <option value="Portugal">Portugal</option>
                            <option value="Netherlands">Netherlands</option>
                            <option value="Belgium">Belgium</option>
                            <option value="Switzerland">Switzerland</option>
                            <option value="Austria">Austria</option>
                            <option value="Sweden">Sweden</option>
                            <option value="Norway">Norway</option>
                            <option value="Denmark">Denmark</option>
                            <option value="Finland">Finland</option>
                            <option value="Poland">Poland</option>
                            <option value="Czech Republic">Czech Republic</option>
                            <option value="Hungary">Hungary</option>
                            <option value="Romania">Romania</option>
                            <option value="Greece">Greece</option>
                            <option value="Turkey">Turkey</option>
                            <option value="Israel">Israel</option>
                            <option value="Saudi Arabia">Saudi Arabia</option>
                            <option value="United Arab Emirates">United Arab Emirates</option>
                            <option value="Qatar">Qatar</option>
                            <option value="Kuwait">Kuwait</option>
                            <option value="Bahrain">Bahrain</option>
                            <option value="Oman">Oman</option>
                            <option value="Argentina">Argentina</option>
                            <option value="Chile">Chile</option>
                            <option value="Colombia">Colombia</option>
                            <option value="Peru">Peru</option>
                            <option value="Venezuela">Venezuela</option>
                            <option value="Ecuador">Ecuador</option>
                            <option value="Bolivia">Bolivia</option>
                            <option value="Paraguay">Paraguay</option>
                            <option value="Uruguay">Uruguay</option>
                            <option value="Costa Rica">Costa Rica</option>
                            <option value="Panama">Panama</option>
                            <option value="Jamaica">Jamaica</option>
                            <option value="Trinidad and Tobago">Trinidad and Tobago</option>
                            <option value="Barbados">Barbados</option>
                            <option value="Bahamas">Bahamas</option>
                            <option value="New Zealand">New Zealand</option>
                            <option value="Fiji">Fiji</option>
                            <option value="Papua New Guinea">Papua New Guinea</option>
                            <option value="Pakistan">Pakistan</option>
                            <option value="Bangladesh">Bangladesh</option>
                            <option value="Sri Lanka">Sri Lanka</option>
                            <option value="Nepal">Nepal</option>
                            <option value="Afghanistan">Afghanistan</option>
                            <option value="Myanmar">Myanmar</option>
                            <option value="Cambodia">Cambodia</option>
                            <option value="Laos">Laos</option>
                            <option value="Mongolia">Mongolia</option>
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
                        <label class="block text-sm font-medium mb-2">Transaction Amount</label>
                        <select id="amount" class="w-full border rounded p-2">
                            <option value="10">$10 - Micro</option>
                            <option value="100">$100 - Standard</option>
                            <option value="1000">$1,000 - High value</option>
                            <option value="10000">$10,000 - Enterprise</option>
                        </select>
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
  -d '{"user_id": "abc-123", "amount": 100}'</pre>
                </div>
            </div>
        </div>
        
        <script>
            let currentUserId = null;
            
            async function createUser() {
                const email = document.getElementById('email').value;
                const country = document.getElementById('country').value;
                const resultDiv = document.getElementById('user-result');
                
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
                const amount = document.getElementById('amount').value;
                const resultDiv = document.getElementById('fraud-result');
                
                if (!userId) {
                    resultDiv.innerHTML = '<p class="text-red-600">Please create a user first!</p>';
                    return;
                }
                
                resultDiv.innerHTML = '<p class="text-gray-500">Testing fraud detection...</p>';
                
                try {
                    const response = await fetch('/predict', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({user_id: userId, amount: parseInt(amount)})
                    });
                    
                    const data = await response.json();
                    const fraudProb = (data.fraud_probability * 100).toFixed(1);
                    const isFraud = data.is_fraud;
                    
                    const bgColor = isFraud ? 'bg-red-50' : fraudProb > 50 ? 'bg-yellow-50' : 'bg-green-50';
                    const borderColor = isFraud ? 'border-red-200' : fraudProb > 50 ? 'border-yellow-200' : 'border-green-200';
                    const textColor = isFraud ? 'text-red-800' : fraudProb > 50 ? 'text-yellow-800' : 'text-green-800';
                    const icon = isFraud ? '⚠️' : fraudProb > 50 ? '⚡' : '✅';
                    const status = isFraud ? 'FRAUD DETECTED' : fraudProb > 50 ? 'REVIEW NEEDED' : 'APPROVED';
                    
                    resultDiv.innerHTML = `
                        <div class="${bgColor} border ${borderColor} rounded p-4">
                            <p class="${textColor} font-bold text-lg">${icon} ${status}</p>
                            <p class="text-sm mt-2">Fraud Probability: ${fraudProb}%</p>
                            <p class="text-sm">User Home: ${data.user_home_country}</p>
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
        "user_home_country": home_location,
        "transaction_country": txn_location,
        "location_mismatch": location_change == 1
    }


