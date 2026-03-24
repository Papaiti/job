import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

def generate_synthetic_data(n=1000):
    np.random.seed(42)
    
    # Feature ranges
    age = np.random.randint(18, 90, n)
    gender = np.random.randint(0, 2, n) # 0: Female, 1: Male
    history = np.random.randint(0, 2, n) # 0: No, 1: Yes
    smoking = np.random.randint(0, 2, n) # 0: No, 1: Yes
    symptoms = np.random.randint(0, 4, n) # 0: None, 1: Pain, 2: Lump, 3: Bleeding, 4: Multiple

    # Simplified risk calculation logic
    # Higher age, history, smoking, and symptoms increase risk
    risk_score = (
        (age / 90) * 0.3 +
        history * 0.2 +
        smoking * 0.2 +
        (symptoms / 4) * 0.3 +
        np.random.normal(0, 0.1, n) # Noise
    )
    
    # Labeling: 0: Low (score < 0.4), 1: Medium (0.4 <= score < 0.7), 2: High (score >= 0.7)
    risk_label = np.where(risk_score < 0.4, 0, np.where(risk_score < 0.7, 1, 2))
    
    data = pd.DataFrame({
        'age': age,
        'gender': gender,
        'history': history,
        'smoking': smoking,
        'symptoms': symptoms,
        'risk_label': risk_label
    })
    
    return data

def train_and_save_model():
    data = generate_synthetic_data()
    
    X = data.drop('risk_label', axis=1)
    y = data['risk_label']
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Save the model
    model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_and_save_model()
