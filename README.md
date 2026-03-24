 Clinical Decision Assistance Tool for Early Cancer Screening

A full-stack web application built for Butaro Hospital to assist clinicians in early cancer detection using explainable machine learning.

## Features
- **Early Cancer Screening Form**: Captures patient data (age, gender, history, smoking, symptoms).
- **ML Prediction**: Uses a Random Forest Classifier trained on synthetic data to predict risk levels (Low, Medium, High).
- **Explainable AI**: Provides clinical explanations for predictions based on input features.
- **Data Persistence**: Stores every screening result in a SQLite database.
- **Responsive UI**: Professional clinical interface with loading indicators and styled results.

## Technical Stack
- **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-CORS
- **Machine Learning**: Scikit-learn, Pandas, Joblib
- **Frontend**: HTML5, CSS3 (Vanilla), JavaScript (ES6 Fetch)
- **Database**: SQLite

## Project Structure
```
├── app.py              # Main Flask application
├── requirements.txt    # Project dependencies
├── models/
│   ├── train_model.py  # Script to generate data and train model
│   └── model.pkl       # Trained Random Forest model
├── templates/
│   └── index.html      # Main frontend template
├── static/
│   ├── css/style.css   # Custom styling
│   └── js/script.js    # Frontend logic and API integration
├── database/           # Database storage
├── instance/           # Flask instance folder (contains patients.db)
└── tests.py            # Unit tests
```

## Setup Instructions
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Train Model** (Optional, already included):
   ```bash
   python models/train_model.py
   ```
3. **Run Application**:
   ```bash
   python app.py
   ```
4. **Access UI**: Open `http://127.0.0.1:5000` in your browser.

## API Documentation
### POST `/predict`
Accepts patient data and returns a risk prediction.
- **Request Body**:
  ```json
  {
    "age": 65,
    "gender": 1,
    "history": 1,
    "smoking": 1,
    "symptoms": 2
  }
  ```
- **Response**:
  ```json
  {
    "risk_level": "High",
    "probability": 85.5,
    "explanation": "High risk primarily due to: family history of cancer, smoking status, presence of symptoms, age above 50."
  }
  ```

## Testing
Run the unit tests using:
```bash
python tests.py
```
