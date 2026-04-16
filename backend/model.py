import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os
import sys

print("🚀 Starting Stroke Prediction Model Training with Height & Weight...")
print("="*50)

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"📂 Current directory: {current_dir}")

# Create models directory
models_dir = os.path.join(current_dir, 'models')
os.makedirs(models_dir, exist_ok=True)
print(f"📁 Models will be saved to: {models_dir}")

# Try multiple possible paths for the dataset
possible_paths = [
    os.path.join(current_dir, 'data', 'healthcare-dataset-stroke-data.csv'),
    os.path.join(current_dir, '..', 'data', 'healthcare-dataset-stroke-data.csv'),
    'data/healthcare-dataset-stroke-data.csv',
    '../data/healthcare-dataset-stroke-data.csv'
]

df = None
for path in possible_paths:
    try:
        print(f"\n🔍 Trying path: {path}")
        df = pd.read_csv(path)
        print(f"✅ Success! Data loaded from: {path}")
        break
    except FileNotFoundError:
        print(f"❌ Not found at: {path}")
        continue

if df is None:
    print("\n❌ ERROR: Could not find the dataset file!")
    print("\nPlease run the download script first:")
    print("python download_stroke_dataset.py")
    sys.exit(1)

print(f"\n✅ Data loaded successfully!")
print(f"📊 Dataset shape: {df.shape}")
print(f"📊 Columns: {df.columns.tolist()}")

# Drop id column if exists
if 'id' in df.columns:
    df = df.drop('id', axis=1)
    print("✅ Dropped 'id' column")

# Handle missing values
print("\n🔍 Checking for missing values...")
print(df.isnull().sum())

# Fill missing BMI values with median
if 'bmi' in df.columns and df['bmi'].isnull().sum() > 0:
    df['bmi'].fillna(df['bmi'].median(), inplace=True)
    print("✅ Filled missing BMI values with median")

# Check class distribution
print(f"\n📊 Stroke Class Distribution:")
print(df['stroke'].value_counts())
stroke_count = df['stroke'].sum()
total_count = len(df)
stroke_percentage = (stroke_count / total_count) * 100
print(f"🎯 Stroke Positive: {stroke_count} out of {total_count} ({stroke_percentage:.2f}%)")

# CREATE HEIGHT AND WEIGHT FROM BMI
print("\n📏 Generating height and weight from BMI...")

# Using average height assumptions to generate realistic data
np.random.seed(42)

def estimate_height_weight(bmi):
    """Generate realistic height and weight from BMI"""
    # Assume height between 150-190 cm
    height_cm = np.random.uniform(150, 190)
    height_m = height_cm / 100
    # Calculate weight from BMI: weight = BMI * height²
    weight_kg = bmi * (height_m ** 2)
    return round(height_cm, 1), round(weight_kg, 1)

# Create height and weight columns
heights = []
weights = []
for bmi in df['bmi']:
    h, w = estimate_height_weight(bmi)
    heights.append(h)
    weights.append(w)

df['height_cm'] = heights
df['weight_kg'] = weights

print("\n📊 Sample of generated height/weight data:")
print(df[['bmi', 'height_cm', 'weight_kg']].head(10))

# Drop the original BMI column
df = df.drop('bmi', axis=1)
print("✅ Dropped original BMI column, now using height and weight")

# Encode categorical variables
print("\n🔄 Encoding categorical variables...")
label_encoders = {}
categorical_cols = ['gender', 'ever_married', 'work_type', 'Residence_type', 'smoking_status']

for col in categorical_cols:
    if col in df.columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        label_encoders[col] = le
        print(f"  ✅ Encoded: {col}")

# Separate features and target
X = df.drop('stroke', axis=1)
y = df['stroke']

print(f"\n📈 Feature matrix shape: {X.shape}")
print(f"🎯 Target vector shape: {y.shape}")
print(f"📋 Feature names: {X.columns.tolist()}")

# Split data with stratification
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\n📊 Train set size: {len(X_train)}")
print(f"📊 Test set size: {len(X_test)}")

# Scale numerical features
scaler = StandardScaler()
numerical_cols = ['age', 'avg_glucose_level', 'height_cm', 'weight_kg']

# Make sure these columns exist
existing_num_cols = [col for col in numerical_cols if col in X_train.columns]
if existing_num_cols:
    X_train[existing_num_cols] = scaler.fit_transform(X_train[existing_num_cols])
    X_test[existing_num_cols] = scaler.transform(X_test[existing_num_cols])
    print(f"✅ Scaled numerical features: {existing_num_cols}")

# Train model
print("\n🤖 Training Random Forest model...")
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    class_weight='balanced',
    n_jobs=-1
)
model.fit(X_train, y_train)
print("✅ Model training complete!")

# Evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\n📊 Model Performance:")
print(f"  ✅ Overall Accuracy: {accuracy:.4f}")

print("\n📊 Detailed Classification Report:")
print(classification_report(y_test, y_pred, target_names=['No Stroke', 'Stroke']))

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
print("\n📊 Confusion Matrix:")
print(f"  True Negatives: {cm[0][0]}")
print(f"  False Positives: {cm[0][1]}")
print(f"  False Negatives: {cm[1][0]}")
print(f"  True Positives: {cm[1][1]}")

# Feature importance
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("\n🔝 Top 10 Most Important Features:")
for idx, row in feature_importance.head(10).iterrows():
    print(f"  {row['feature']}: {row['importance']:.4f}")

# Save model and preprocessors
print("\n💾 Saving model and preprocessors...")

model_path = os.path.join(models_dir, 'stroke_model_height_weight.pkl')
scaler_path = os.path.join(models_dir, 'scaler_height_weight.pkl')
encoders_path = os.path.join(models_dir, 'label_encoders_height_weight.pkl')
features_path = os.path.join(models_dir, 'feature_names_height_weight.pkl')

joblib.dump(model, model_path)
joblib.dump(scaler, scaler_path)
joblib.dump(label_encoders, encoders_path)
joblib.dump(X.columns.tolist(), features_path)

print(f"\n✅ All files saved successfully in:")
print(f"  📁 {model_path}")
print(f"  📁 {scaler_path}")
print(f"  📁 {encoders_path}")
print(f"  📁 {features_path}")

print("\n" + "="*50)
print("🎉 TRAINING COMPLETE! 🎉")
print("="*50)
print("\nNext steps:")
print("1️⃣  Start the FastAPI server:")
print("   uvicorn main_height_weight:app --reload --port 8000")
print("\n2️⃣  Open frontend in browser:")
print("   http://localhost:5500/index_height_weight.html")