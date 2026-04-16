from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import os
from typing import Optional

app = FastAPI(title="Stroke Prediction API with Auto BMI", 
              description="Enter height and weight - BMI calculated automatically",
              version="2.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define model paths
model_path = 'models/stroke_model_height_weight.pkl'
scaler_path = 'models/scaler_height_weight.pkl'
encoders_path = 'models/label_encoders_height_weight.pkl'
features_path = 'models/feature_names_height_weight.pkl'

# Check if all model files exist
model_files_exist = all(os.path.exists(path) for path in 
                       [model_path, scaler_path, encoders_path, features_path])

if model_files_exist:
    # Load model and preprocessors
    try:
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        label_encoders = joblib.load(encoders_path)
        feature_names = joblib.load(features_path)
        print("✅ Model files loaded successfully!")
        print(f"📊 Model features: {feature_names}")
    except Exception as e:
        print(f"❌ Error loading model files: {e}")
        model_files_exist = False
        model = scaler = label_encoders = feature_names = None
else:
    print("⚠️  Warning: Model files not found. Please train the model first.")
    print("   Run: python model.py")
    model = scaler = label_encoders = feature_names = None

class PatientData(BaseModel):
    gender: str
    age: float
    hypertension: int
    heart_disease: int
    ever_married: str
    work_type: str
    Residence_type: str
    avg_glucose_level: float
    height_cm: float
    weight_kg: float
    smoking_status: str

class PredictionResponse(BaseModel):
    prediction: int
    probability: float
    risk_level: str
    message: str
    bmi: float

@app.get("/")
async def root():
    status = "ready" if model_files_exist else "model_not_trained"
    return {
        "message": "Stroke Prediction API with Auto BMI", 
        "status": status,
        "features": ["Height (cm)", "Weight (kg)", "BMI auto-calculated"],
        "model_loaded": model_files_exist,
        "endpoints": {
            "/predict": "POST - Make a prediction with height/weight",
            "/health": "GET - Check API health",
            "/train-status": "GET - Check if model is trained"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "model_loaded": model_files_exist,
        "message": "Model is ready" if model_files_exist else "Please train the model first"
    }

@app.get("/train-status")
async def train_status():
    return {
        "model_trained": model_files_exist,
        "message": "Model is trained and ready!" if model_files_exist else "Model not trained. Please run: python model.py"
    }

def calculate_bmi(height_cm: float, weight_kg: float) -> float:
    """Calculate BMI from height (cm) and weight (kg)"""
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)

@app.post("/predict", response_model=PredictionResponse)
async def predict_stroke(patient: PatientData):
    # Check if model is loaded
    if not model_files_exist or model is None:
        raise HTTPException(
            status_code=503, 
            detail="Model not trained yet. Please run: python model.py first"
        )
    
    try:
        # Calculate BMI (just for display)
        bmi = calculate_bmi(patient.height_cm, patient.weight_kg)
        
        # Validate BMI range
        if bmi < 10 or bmi > 60:
            raise HTTPException(status_code=400, detail="BMI out of normal range. Please check height/weight.")
        
        # Convert input to DataFrame
        input_data = pd.DataFrame([patient.dict()])
        
        # Encode categorical variables
        for col, le in label_encoders.items():
            if col in input_data.columns:
                try:
                    input_data[col] = le.transform(input_data[col].astype(str))
                except ValueError as e:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Invalid value for {col}. Expected one of: {le.classes_.tolist()}"
                    )
        
        # Ensure columns are in the correct order
        input_data = input_data[feature_names]
        
        # Scale numerical features
        numerical_cols = ['age', 'avg_glucose_level', 'height_cm', 'weight_kg']
        input_data[numerical_cols] = scaler.transform(input_data[numerical_cols])
        
        # Make prediction
        prediction = model.predict(input_data)[0]
        probability = float(model.predict_proba(input_data)[0][1])
        
        # Determine risk level and message
        if probability < 0.3:
            risk_level = "Low"
            message = f"✅ Low risk of stroke (BMI: {bmi}). Maintain your healthy lifestyle!"
        elif probability < 0.6:
            risk_level = "Medium"
            message = f"⚠️ Moderate risk (BMI: {bmi}). Consider lifestyle changes and regular checkups."
        else:
            risk_level = "High"
            message = f"🔴 High risk! (BMI: {bmi}) Please consult a healthcare professional immediately."
        
        return PredictionResponse(
            prediction=int(prediction),
            probability=probability,
            risk_level=risk_level,
            message=message,
            bmi=bmi
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/model-info")
async def model_info():
    """Get information about the trained model"""
    if not model_files_exist or model is None:
        raise HTTPException(status_code=404, detail="Model not trained yet")
    
    return {
        "model_type": "Random Forest Classifier",
        "features": feature_names,
        "num_features": len(feature_names),
        "categorical_features": list(label_encoders.keys()),
        "numerical_features": ['age', 'avg_glucose_level', 'height_cm', 'weight_kg']
    }