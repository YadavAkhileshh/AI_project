from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest
import joblib

app = FastAPI()

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load or create model
try:
    model = joblib.load('fraud_detection_model.pkl')
except:
    from sklearn.ensemble import IsolationForest
    model = IsolationForest(contamination=0.05)
    joblib.dump(model, 'fraud_detection_model.pkl')

@app.post("/api/detect-fraud")
async def detect_fraud(transaction_data: dict):
    """Detect fraud in real-time transactions"""
    prediction = model.predict([transaction_data])
    return {"is_fraudulent": True if prediction[0] == -1 else False}

@app.post("/api/upload-transaction")
async def upload_transaction(file: UploadFile = File(...)):
    """Process transaction file and detect fraud"""
    df = pd.read_csv(await file.read())
    predictions = model.predict(df)
    results = df.copy()
    results['is_fraudulent'] = predictions
    return results.to_dict(orient='records')

@app.get("/health")
def health_check():
    return {"status": "ok"}
