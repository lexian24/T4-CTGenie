# CTGenie - AI-Powered Clinical Decision Support System

**AI-powered fetal monitoring system with 98.8% accuracy** for CTG (Cardiotocography) interpretation, providing real-time clinical decision support, similar case analysis, and evidence-based recommendations.
**data.ipynb is the data processing and the model training and evaluation notebook.
---

## 🚀 Quick Start Guide

### Prerequisites

- **Python 3.11+** (required for backend)
- **Node.js 16+** and **npm** (required for frontend)

### Step 1: Environment Setup

#### A. Backend Environment

```bash
# Navigate to project root
cd /Users/lexiancheo/Desktop/datathon

# Create Python virtual environment
python3 -m venv ctgenie_venv

# Activate virtual environment
source ctgenie_venv/bin/activate  # On macOS/Linux
# OR
ctgenie_venv\Scripts\activate  # On Windows

# Install backend dependencies
pip install -r ctgenie/backend/requirements.txt
```

**Backend Dependencies:**
- FastAPI (web framework)
- Uvicorn (ASGI server)
- XGBoost (ML model)
- SHAP (explainability)
- NumPy, Pandas, Scikit-learn
- Python-multipart, Pydantic

#### B. Frontend Environment

```bash
# Navigate to frontend directory
cd ctgenie/frontend

# Install Node.js dependencies
npm install
```

**Frontend Dependencies:**
- React 18 (UI framework)
- Vite (build tool)
- CSS3 (styling)

---

### Step 2: Start the Application

**IMPORTANT:** You need **TWO terminal windows** - one for backend, one for frontend.

#### Terminal 1: Start Backend Server

```bash
# Make sure virtual environment is activated
source ctgenie_venv/bin/activate  # On macOS/Linux

# Navigate to backend directory
cd ctgenie/backend

# Start FastAPI server
python main.py
```

**Expected Output:**
```
🏥 CTGenie API Starting...
✅ Loaded model from ../data/models/xgboost_model.json
✅ Loaded scaler from ../data/models/scaler_v2.pkl
✅ Loaded 29 feature names
✅ Loaded metadata (accuracy: 0.9882629107981221)
✅ SHAP explainer initialized
✅ Loaded batch 001: 20 cases
✅ Loaded batch 002: 15 cases
✅ Loaded batch 003: 15 cases
✅ Total cases loaded: 50
✅ Loaded clinical guidelines (version 1.0)
✅ Loaded hardcoded similar cases database for 50 patients
✅ CTGenie API Ready
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Backend URL:** http://localhost:8000

#### Terminal 2: Start Frontend Server

```bash
# Navigate to frontend directory (from project root)
cd ctgenie/frontend

# Start Vite development server
npm run dev
```

**Expected Output:**
```
VITE v5.0.0  ready in 242 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

**Frontend URL:** http://localhost:5173

---

### Step 3: Access the Application

1. **Open your browser** and navigate to: **http://localhost:5173**
2. You should see the **CTGenie Dashboard** with 50 patient cases
3. **Click on any patient** to view:
   - Patient demographics and vital signs
   - AI prediction with confidence scores
   - SHAP feature importance explanations
   - 3 similar historical case studies
   - AI-generated clinical summary
   - Delivery outcomes and recommendations

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                     │
│                  http://localhost:5173                  │
│  • Patient Dashboard                                    │
│  • Interactive CTG Visualizations                       │
│  • AI Predictions Display                               │
│  • Similar Cases Analysis                               │
└────────────────────┬────────────────────────────────────┘
                     │ REST API
                     ↓
┌─────────────────────────────────────────────────────────┐
│                  Backend (FastAPI)                      │
│                  http://localhost:8000                  │
│  • XGBoost ML Model (98.8% accuracy)                    │
│  • SHAP Explainer                                       │
│  • Clinical Guidelines Engine                           │
│  • Similar Cases Database (50 pre-written summaries)    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│                      Data Layer                         │
│  • 50 Synthetic Patient Cases (batch_001-003.json)     │
│  • Trained XGBoost Model & Scaler                       │
│  • Clinical Guidelines (NICE 2022, FIGO)                │
│  • Similar Cases Database (hardcoded summaries)         │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Features

### 1. **High-Accuracy AI Predictions**
- **98.8% accuracy** on test set
- 3-class classification: Normal, Suspect, Pathological
- Trained on 2126 CTG recordings
- 29 CTG features analyzed

### 2. **Explainable AI (SHAP)**
- Feature importance visualization
- Understand which CTG parameters influenced the prediction
- Transparent clinical decision-making

### 3. **Similar Case Analysis**
- Pre-curated groups of clinically similar cases
- 50 pre-written clinical summaries
- Instant load (no generation delay) - perfect for demos

---

## 📁 Project Structure

```
datathon/
├── ctgenie/
│   ├── backend/
│   │   ├── main.py                    # FastAPI application
│   │   ├── model_service.py           # ML model wrapper
│   │   └── requirements.txt           # Python dependencies
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── App.jsx                # Main application
│   │   │   ├── components/
│   │   │   │   ├── Dashboard.jsx      # Patient list
│   │   │   │   ├── PatientDetail.jsx  # Patient detail view
│   │   │   │   └── *.css              # Component styles
│   │   │   └── utils/
│   │   ├── package.json               # Node dependencies
│   │   └── vite.config.js             # Vite configuration
│   ├── data/
│   │   ├── synthetic_cases/
│   │   │   ├── batch_001.json         # 20 cases
│   │   │   ├── batch_002.json         # 15 cases
│   │   │   └── batch_003.json         # 15 cases
│   │   ├── similar_cases_database.json  # Pre-written
│   │   ├── models/
│   │   │   ├── xgboost_model.json     # Trained model
│   │   │   └── scaler_v2.pkl          # Feature scaler
│   │   └── clinical_guidelines/
│   │       └── ctg_interpretation_guidelines.json
│   ├── scripts/
│   │   └── generate_hardcoded_case_studies.py
│   └── notebooks/
│       └── model_training.ipynb       # Model training code
└── ctgenie_venv/                      # Python virtual environment
```

---

## 🔧 Troubleshooting

### Backend Issues

**Problem:** Backend won't start - "Module not found"
```bash
# Solution: Ensure virtual environment is activated and dependencies installed
source ctgenie_venv/bin/activate
pip install -r ctgenie/backend/requirements.txt
```

**Problem:** Port 8000 already in use
```bash
# Solution: Kill existing process
lsof -ti:8000 | xargs kill -9

# Or change port in main.py:
# uvicorn.run(app, host="0.0.0.0", port=8001)
```

**Problem:** Model files not found
```bash
# Ensure you're running from the backend directory
cd ctgenie/backend
python main.py
```

**Problem:** Logs not found
```bash
# You can manually create logs as directory at the root directory
and create backend.log and frontend.log files in it
```

### Frontend Issues

**Problem:** Frontend won't start - "npm command not found"
```bash
# Solution: Install Node.js from https://nodejs.org/
# Verify installation:
node --version
npm --version
```

**Problem:** Port 5173 already in use
```bash
# Solution: Kill existing process
lsof -ti:5173 | xargs kill -9
```

**Problem:** CORS errors in browser console
```bash
# Solution: Ensure backend is running on port 8000
# Check backend CORS configuration in main.py
```

### Data/Network Issues

**Problem:** No cases showing in dashboard
- Check browser console for errors
- Verify backend is accessible: http://localhost:8000/
- Check backend logs for case loading messages

**Problem:** "Similar cases not loading"
- Ensure `similar_cases_database.json` exists in `ctgenie/data/`
- Check backend startup logs for "Loaded hardcoded similar cases database"

---

## 📊 Model Performance

- **Training Set:** 1700 CTG recordings
- **Test Set:** 426 CTG recordings
- **Accuracy:** 98.8%
- **Features:** 29 CTG parameters
- **Classes:** 3 (Normal, Suspect, Pathological)
- **Algorithm:** XGBoost (Gradient Boosting)
- **Explainability:** SHAP values for feature importance

---

## 🏥 Clinical Use Case

CTGenie assists obstetricians and midwives in:
- **Real-time CTG interpretation** during labor
- **Early detection** of fetal compromise
- **Evidence-based decision making** with NICE/FIGO guidelines
- **Learning from similar cases** to improve clinical judgment
- **Reducing false positives** and unnecessary interventions

---

## 📝 API Endpoints

### Health Check
```bash
GET http://localhost:8000/
```

### Predict CTG Classification
```bash
POST http://localhost:8000/predict
Content-Type: application/json

{
  "ctg_features": {
    "LB": 120.0,
    "AC": 0.003,
    "FM": 5.0,
    "ASTV": 45.0,
    ...
  }
}
```

### Get Similar Cases
```bash
POST http://localhost:8000/similar-cases
Content-Type: application/json

{
  "ctg_features": { ... },
  "top_k": 3
}
```

### Get Clinical Guidelines
```bash
GET http://localhost:8000/guidelines/baseline_heart_rate
```

---

## 🎉 Quick Test

After starting both servers, test the system:

1. Open browser: http://localhost:5173
2. You should see 50 patient cases
3. Click on **CASE00001**
4. Verify you see:
   - ✅ Patient demographics
   - ✅ AI prediction with confidence
   - ✅ SHAP feature importance
   - ✅ 3 similar cases with essays
   - ✅ AI-generated clinical summary (blue box)
   - ✅ Delivery outcomes

**If all above appear → System is working perfectly! 🎉**
