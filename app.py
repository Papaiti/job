from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import joblib
import os
import pandas as pd
import numpy as np
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'butaro-hospital-secret-key' # In production, use an environment variable

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///patients.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Login Manager configuration
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Load the ML model
model_path = os.path.join(os.path.dirname(__file__), 'models', 'model.pkl')
try:
    model = joblib.load(model_path)
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.Integer, nullable=False) # 0: Female, 1: Male
    history = db.Column(db.Integer, nullable=False) # 0: No, 1: Yes
    smoking = db.Column(db.Integer, nullable=False) # 0: No, 1: Yes
    symptoms = db.Column(db.Integer, nullable=False) # 0: None, 1: Pain, 2: Lump, 3: Bleeding, 4: Multiple
    prediction = db.Column(db.String(50), nullable=False)
    probability = db.Column(db.Float, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database
with app.app_context():
    db.create_all()

@app.route('/')
@login_required
def index():
    return render_template('index.html', name=current_user.username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('Username already exists')
            return redirect(url_for('register'))
            
        new_user = User(
            username=username,
            password_hash=generate_password_hash(password, method='scrypt')
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    if not model:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        data = request.json
        
        # Validation
        required_fields = ['age', 'gender', 'history', 'smoking', 'symptoms']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # Preprocess input for model
        input_data = pd.DataFrame([{
            'age': int(data['age']),
            'gender': int(data['gender']),
            'history': int(data['history']),
            'smoking': int(data['smoking']),
            'symptoms': int(data['symptoms'])
        }])
        
        # Prediction
        prediction_idx = model.predict(input_data)[0]
        prediction_proba = model.predict_proba(input_data)[0]
        
        risk_levels = ['Low', 'Medium', 'High']
        risk_level = risk_levels[prediction_idx]
        probability = float(np.max(prediction_proba))
        
        # Simple Explanation
        explanation = generate_explanation(data, risk_level)
        
        # Store in database
        patient = Patient(
            age=int(data['age']),
            gender=int(data['gender']),
            history=int(data['history']),
            smoking=int(data['smoking']),
            symptoms=int(data['symptoms']),
            prediction=risk_level,
            probability=probability,
            user_id=current_user.id
        )
        db.session.add(patient)
        db.session.commit()
        
        return jsonify({
            'risk_level': risk_level,
            'probability': round(probability * 100, 2),
            'explanation': explanation
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def generate_explanation(data, risk_level):
    reasons = []
    if int(data['history']) == 1:
        reasons.append("family history of cancer")
    if int(data['smoking']) == 1:
        reasons.append("smoking status")
    if int(data['symptoms']) > 0:
        reasons.append("presence of symptoms")
    if int(data['age']) > 50:
        reasons.append("age above 50")
        
    if not reasons:
        return "Low risk profile based on current metrics."
        
    explanation = f"{risk_level} risk primarily due to: {', '.join(reasons)}."
    return explanation

if __name__ == '__main__':
    app.run(debug=True)
