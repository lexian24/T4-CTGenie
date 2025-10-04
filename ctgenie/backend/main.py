"""
CTGenie - FastAPI Backend
AI-powered Clinical Decision Support System for CTG Monitoring
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import numpy as np
import json
from datetime import datetime
from model_service import get_model

app = FastAPI(
    title="CTGenie API",
    description="Clinical Decision Support System for CTG Fetal Monitoring",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage
CASE_DATABASE = []
SIMILAR_CASES_DB = {}  # Hardcoded similar cases and summaries
GUIDELINES = {}


# Pydantic models for API
class CTGFeatures(BaseModel):
    """CTG feature input schema"""
    LB: float  # Baseline fetal heart rate
    AC: float  # Accelerations
    FM: float  # Fetal movements
    UC: float  # Uterine contractions
    DL: float  # Light decelerations
    DS: float  # Severe decelerations
    DP: float  # Prolonged decelerations
    ASTV: float  # Short term variability
    MSTV: float  # Mean short term variability
    ALTV: float  # Long term variability
    MLTV: float  # Mean long term variability
    # Add other features as needed

    class Config:
        schema_extra = {
            "example": {
                "LB": 120.0,
                "AC": 3.0,
                "FM": 5.0,
                "UC": 4.0,
                "DL": 0.0,
                "DS": 0.0,
                "DP": 0.0,
                "ASTV": 45.0,
                "MSTV": 1.2,
                "ALTV": 8.0,
                "MLTV": 8.5
            }
        }


class PatientContext(BaseModel):
    """Patient demographic and clinical context"""
    patient_id: Optional[str] = None
    age: int
    gestational_age_weeks: float
    gravida: int
    para: int
    risk_factors: List[str] = []


class PredictionRequest(BaseModel):
    """Complete prediction request"""
    ctg_features: Dict[str, float]
    patient_context: Optional[PatientContext] = None


class PredictionResponse(BaseModel):
    """Prediction response with explanations"""
    prediction: int  # 0=Normal, 1=Suspect, 2=Pathological
    prediction_label: str
    confidence: float
    probabilities: Dict[str, float]
    shap_values: Optional[Dict[str, float]] = None
    similar_cases: Optional[List[Dict[str, Any]]] = None
    clinical_recommendations: Optional[List[str]] = None
    guidelines: Optional[List[Dict[str, Any]]] = None


class CaseQuery(BaseModel):
    """Query for similar cases"""
    ctg_features: Dict[str, float]
    top_k: int = 5


# Startup: Load model and data
@app.on_event("startup")
async def load_resources():
    """Load ML model, case database, and clinical guidelines on startup"""
    global CASE_DATABASE, SIMILAR_CASES_DB, GUIDELINES

    print("🏥 CTGenie API Starting...")

    # Load trained model
    model = get_model()
    model.load()

    # Load synthetic case database (all batches)
    try:
        all_cases = []
        for batch_num in [1, 2, 3]:
            batch_file = f"../data/synthetic_cases/batch_{batch_num:03d}.json"
            try:
                with open(batch_file, "r") as f:
                    batch_cases = json.load(f)
                    all_cases.extend(batch_cases)
                    print(f"✅ Loaded batch {batch_num:03d}: {len(batch_cases)} cases")
            except FileNotFoundError:
                print(f"⚠️  Batch {batch_num:03d} not found, skipping...")
                continue

        CASE_DATABASE = all_cases
        print(f"✅ Total cases loaded: {len(CASE_DATABASE)}")
    except Exception as e:
        print(f"⚠️  Could not load case database: {e}")
        CASE_DATABASE = []

    # Load clinical guidelines
    try:
        with open("../data/clinical_guidelines/ctg_interpretation_guidelines.json", "r") as f:
            GUIDELINES = json.load(f)
        print(f"✅ Loaded clinical guidelines (version {GUIDELINES.get('version', 'unknown')})")
    except Exception as e:
        print(f"⚠️  Could not load guidelines: {e}")
        GUIDELINES = {}

    # Load hardcoded similar cases database
    try:
        with open("../data/similar_cases_database.json", "r") as f:
            SIMILAR_CASES_DB = json.load(f)
        print(f"✅ Loaded hardcoded similar cases database for {len(SIMILAR_CASES_DB)} patients")
    except Exception as e:
        print(f"⚠️  Could not load similar cases database: {e}")
        SIMILAR_CASES_DB = {}

    print("✅ CTGenie API Ready")


@app.get("/")
async def root():
    """Health check endpoint"""
    model = get_model()
    return {
        "service": "CTGenie API",
        "status": "operational",
        "version": "1.0.0",
        "model_info": model.get_model_info(),
        "cases_loaded": len(CASE_DATABASE),
        "guidelines_loaded": bool(GUIDELINES)
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict_ctg(request: PredictionRequest):
    """
    Predict NSP classification from CTG features with full clinical context

    Returns prediction, confidence, SHAP explanations, similar cases, and recommendations
    """

    model = get_model()

    # Check if model is loaded
    if not model.model:
        # Fallback to rule-based for demo if model not available
        return _fallback_prediction(request)

    try:
        # Real model prediction
        prediction, probabilities, shap_values_array = model.predict(request.ctg_features)

        # Get SHAP explanation
        shap_explanation = model.get_shap_explanation(shap_values_array, top_k=10)

        labels = model.class_names
        confidence = float(probabilities[prediction])

    except Exception as e:
        print(f"❌ Prediction error: {e}")
        # Fallback to rule-based
        return _fallback_prediction(request)

    # Find similar cases
    similar_cases = find_similar_cases(request.ctg_features, top_k=3)

    # Generate recommendations
    recommendations = generate_recommendations(
        prediction=prediction,
        features=request.ctg_features,
        patient_context=request.patient_context
    )

    # Retrieve relevant guidelines
    relevant_guidelines = get_relevant_guidelines(prediction)

    return PredictionResponse(
        prediction=prediction,
        prediction_label=labels[prediction],
        confidence=confidence,
        probabilities={
            "Normal": round(probabilities[0], 3),
            "Suspect": round(probabilities[1], 3),
            "Pathological": round(probabilities[2], 3)
        },
        shap_values=shap_explanation,
        similar_cases=similar_cases,
        clinical_recommendations=recommendations,
        guidelines=relevant_guidelines
    )


def _fallback_prediction(request: PredictionRequest):
    """Fallback rule-based prediction when model not available"""
    # Mock prediction based on simple rules
    baseline_hr = request.ctg_features.get("LB", 120)
    variability = request.ctg_features.get("ASTV", 50)
    accelerations = request.ctg_features.get("AC", 2)
    decelerations = request.ctg_features.get("DP", 0)

    # Simple rule-based classification for demo
    if variability > 40 and accelerations > 0 and decelerations == 0:
        prediction = 0  # Normal
        confidence = 0.92
    elif variability < 30 or decelerations > 2:
        prediction = 2  # Pathological
        confidence = 0.85
    else:
        prediction = 1  # Suspect
        confidence = 0.68

    labels = ["Normal", "Suspect", "Pathological"]

    # Mock probabilities
    probs = [0.1, 0.2, 0.7]
    probs[prediction] = confidence
    remaining = (1.0 - confidence) / 2
    for i in range(3):
        if i != prediction:
            probs[i] = remaining

    # Mock SHAP values (top contributing features)
    shap_values = {
        "ASTV": variability - 50,
        "LB": (baseline_hr - 130) * 0.1,
        "AC": accelerations * 5,
        "DP": decelerations * -10
    }

    # Find similar cases
    similar_cases = find_similar_cases(request.ctg_features, top_k=3)

    # Generate recommendations
    recommendations = generate_recommendations(
        prediction=prediction,
        features=request.ctg_features,
        patient_context=request.patient_context
    )

    # Retrieve relevant guidelines
    relevant_guidelines = get_relevant_guidelines(prediction)

    return PredictionResponse(
        prediction=prediction,
        prediction_label=labels[prediction] + " (Rule-based fallback)",
        confidence=confidence,
        probabilities={
            "Normal": round(probs[0], 3),
            "Suspect": round(probs[1], 3),
            "Pathological": round(probs[2], 3)
        },
        shap_values=shap_values,
        similar_cases=similar_cases,
        clinical_recommendations=recommendations,
        guidelines=relevant_guidelines
    )


@app.post("/similar-cases")
async def get_similar_cases(query: CaseQuery):
    """
    Retrieve hardcoded similar historical cases with pre-written summaries (for MVP/presentation)
    """
    # Use hardcoded similar cases if available
    if SIMILAR_CASES_DB:
        # Find the patient case that matches this query (by CTG pattern)
        patient_case = find_patient_by_ctg(query.ctg_features)

        if patient_case and patient_case['case_id'] in SIMILAR_CASES_DB:
            # Get hardcoded similar case IDs and summary
            similar_data = SIMILAR_CASES_DB[patient_case['case_id']]
            similar_case_ids = similar_data.get('similar_case_ids', [])
            cases_summary = similar_data.get('summary', '')

            # Fetch full data for similar cases
            all_cases_dict = {c['case_id']: c for c in CASE_DATABASE}
            similar_cases = []

            for similar_id in similar_case_ids[:query.top_k]:
                if similar_id in all_cases_dict:
                    case = all_cases_dict[similar_id].copy()
                    case['similarity_score'] = 0.95  # Hardcoded high similarity
                    case['case_study_essay'] = generate_case_study_essay(case)
                    similar_cases.append(case)

            return {
                "query": query.ctg_features,
                "similar_cases": similar_cases,
                "cases_summary": cases_summary,
                "count": len(similar_cases)
            }

    # Fallback to dynamic generation if hardcoded not available
    similar = find_similar_cases(query.ctg_features, query.top_k, full_data=True)
    cases_summary = generate_case_studies_summary(similar) if similar else ""

    return {
        "query": query.ctg_features,
        "similar_cases": similar,
        "cases_summary": cases_summary,
        "count": len(similar)
    }


@app.get("/guidelines/{category}")
async def get_guidelines(category: str):
    """
    Retrieve clinical guidelines for specific category

    Categories: baseline_heart_rate, variability, accelerations, decelerations, three_tier_classification
    """
    if not GUIDELINES:
        raise HTTPException(status_code=503, detail="Guidelines not loaded")

    guidelines = GUIDELINES.get("guidelines", [])
    category_guidelines = [g for g in guidelines if g.get("category") == category]

    if not category_guidelines:
        raise HTTPException(status_code=404, detail=f"No guidelines found for category: {category}")

    return {
        "category": category,
        "guidelines": category_guidelines,
        "source": GUIDELINES.get("source", "Unknown")
    }


@app.get("/intervention-algorithm/{pattern_category}")
async def get_intervention_algorithm(pattern_category: str):
    """
    Get step-by-step intervention algorithm for specific CTG pattern

    Categories: category_2, category_3
    """
    if not GUIDELINES:
        raise HTTPException(status_code=503, detail="Guidelines not loaded")

    algorithms = GUIDELINES.get("intervention_algorithms", [])

    # Map pattern category to algorithm ID
    algorithm_map = {
        "category_2": "INT-001",
        "indeterminate": "INT-001",
        "category_3": "INT-002",
        "abnormal": "INT-002"
    }

    algorithm_id = algorithm_map.get(pattern_category.lower())
    if not algorithm_id:
        raise HTTPException(status_code=400, detail=f"Invalid pattern category: {pattern_category}")

    algorithm = next((a for a in algorithms if a.get("algorithm_id") == algorithm_id), None)

    if not algorithm:
        raise HTTPException(status_code=404, detail=f"Algorithm not found for: {pattern_category}")

    return algorithm


# Helper functions

def find_patient_by_ctg(ctg_features: Dict[str, float]) -> Optional[Dict[str, Any]]:
    """Find the patient case that matches the given CTG features"""
    if not CASE_DATABASE:
        return None

    # Look for exact match on key features (LB, ASTV, AC)
    query_lb = ctg_features.get('LB', 0)
    query_astv = ctg_features.get('ASTV', 0)
    query_ac = ctg_features.get('AC', 0)

    for case in CASE_DATABASE:
        case_ctg = case.get('ctg_features', {})
        case_lb = case_ctg.get('LB', 0)
        case_astv = case_ctg.get('ASTV', 0)
        case_ac = case_ctg.get('AC', 0)

        # Check if it's a very close match (within small tolerance)
        if (abs(case_lb - query_lb) < 1.0 and
            abs(case_astv - query_astv) < 1.0 and
            abs(case_ac - query_ac) < 0.01):
            return case

    return None


def generate_case_study_essay(case: Dict[str, Any]) -> str:
    """Generate a detailed case study essay from case data"""
    demo = case.get("demographics", {})
    ctg = case.get("ctg_features", {})
    outcome = case.get("outcome", {})
    narrative = case.get("clinical_narrative", "")

    # Build comprehensive case study
    essay_parts = []

    # Introduction
    intro = f"**Case Presentation:** A {demo.get('age')}-year-old G{demo.get('gravida')}P{demo.get('para')} patient at {demo.get('gestational_age_weeks')} weeks gestation"
    if demo.get('risk_factors') and demo.get('risk_factors')[0] != 'None':
        intro += f" with {', '.join(demo.get('risk_factors'))}"
    intro += f" was admitted on {demo.get('admission_date')} for continuous fetal monitoring."
    essay_parts.append(intro)

    # CTG Findings
    fhr = round(ctg.get('LB', 0))
    astv = round(ctg.get('ASTV', 0))
    ac = ctg.get('AC', 0)
    findings = f"\n\n**CTG Analysis:** Initial assessment revealed a baseline fetal heart rate of {fhr} bpm with {astv}ms variability. "

    if case.get('nsp_label') == 'Normal':
        findings += f"The tracing showed reassuring features with {ac} accelerations present and no concerning decelerations. "
        findings += "Moderate variability was maintained throughout the monitoring period, indicating good fetal oxygenation."
    elif case.get('nsp_label') == 'Suspect':
        findings += f"The tracing demonstrated equivocal features with reduced accelerations and borderline variability. "
        findings += "Close observation was initiated with reassessment every 15-30 minutes. Conservative measures including maternal repositioning and hydration were implemented."
    else:  # Pathological
        findings += f"The tracing exhibited non-reassuring patterns concerning for fetal compromise. "
        findings += "Immediate intervention was required including continuous monitoring, maternal oxygen therapy, and preparation for potential expedited delivery."
    essay_parts.append(findings)

    # Clinical Course
    essay_parts.append(f"\n\n**Clinical Course:** {narrative}")

    # Management & Outcome
    delivery_mode = outcome.get('delivery_mode', 'Unknown')
    apgar_1 = outcome.get('apgar_1min', 0)
    apgar_5 = outcome.get('apgar_5min', 0)
    weight = outcome.get('birth_weight_grams', 0)
    interventions = outcome.get('interventions', [])

    management = f"\n\n**Management & Delivery:** "
    if interventions:
        management += f"Interventions included: {', '.join(interventions)}. "
    management += f"Delivery was accomplished via {delivery_mode.lower()}. "
    management += f"The neonate was born with Apgar scores of {apgar_1} at 1 minute and {apgar_5} at 5 minutes, weighing {weight}g."

    if outcome.get('nicu_admission'):
        management += " The infant required NICU admission for further observation and management."
    else:
        management += " The infant was vigorous and did not require intensive care."
    essay_parts.append(management)

    # Complications
    if outcome.get('maternal_complications') or outcome.get('neonatal_complications'):
        complications = "\n\n**Complications:** "
        if outcome.get('maternal_complications'):
            complications += f"Maternal: {', '.join(outcome.get('maternal_complications'))}. "
        if outcome.get('neonatal_complications'):
            complications += f"Neonatal: {', '.join(outcome.get('neonatal_complications'))}."
        essay_parts.append(complications)

    # Learning Points
    learning = "\n\n**Key Learning Points:** "
    if case.get('nsp_label') == 'Normal':
        learning += "This case demonstrates appropriate management of a reassuring CTG pattern with successful vaginal delivery outcome."
    elif case.get('nsp_label') == 'Suspect':
        learning += "This case highlights the importance of close surveillance with Category 2 tracings and timely conservative interventions to optimize fetal status."
    else:
        learning += "This case emphasizes the critical need for rapid recognition and intervention in Category 3 patterns to prevent adverse neonatal outcomes."
    essay_parts.append(learning)

    return "".join(essay_parts)


def find_similar_cases(ctg_features: Dict[str, float], top_k: int = 5, full_data: bool = False) -> List[Dict[str, Any]]:
    """Find similar cases using cosine similarity on CTG features"""
    if not CASE_DATABASE:
        return []

    # Extract feature vector from query
    query_features = np.array([ctg_features.get(k, 0) for k in sorted(ctg_features.keys())])

    similarities = []
    for case in CASE_DATABASE:
        case_features_dict = case.get("ctg_features", {})
        case_features = np.array([case_features_dict.get(k, 0) for k in sorted(ctg_features.keys())])

        # Cosine similarity
        dot_product = np.dot(query_features, case_features)
        norm_query = np.linalg.norm(query_features)
        norm_case = np.linalg.norm(case_features)

        if norm_query > 0 and norm_case > 0:
            similarity = dot_product / (norm_query * norm_case)
        else:
            similarity = 0

        similarities.append((similarity, case))

    # Sort by similarity and return top k
    similarities.sort(key=lambda x: x[0], reverse=True)

    similar_cases = []
    for sim, case in similarities[:top_k]:
        if full_data:
            # Return full case data for frontend display with essay
            case_copy = case.copy()
            case_copy["similarity_score"] = round(float(sim), 3)
            case_copy["case_study_essay"] = generate_case_study_essay(case)
            similar_cases.append(case_copy)
        else:
            # Return simplified data for prediction API
            similar_cases.append({
                "case_id": case.get("case_id"),
                "similarity_score": round(float(sim), 3),
                "nsp_label": case.get("nsp_label"),
                "clinical_summary": case.get("clinical_narrative", "")[:200] + "...",
                "outcome": case.get("outcome", {}).get("delivery_mode"),
                "patient_age": case.get("demographics", {}).get("age"),
                "gestational_age": case.get("demographics", {}).get("gestational_age_weeks")
            })

    return similar_cases


def generate_recommendations(prediction: int, features: Dict[str, float], patient_context: Optional[PatientContext]) -> List[str]:
    """Generate clinical recommendations based on prediction and context"""
    recommendations = []

    labels = ["Normal", "Suspect", "Pathological"]
    pred_label = labels[prediction]

    if prediction == 0:  # Normal
        recommendations.append("Continue routine fetal monitoring")
        recommendations.append("Reassess in 30 minutes or per protocol")
        recommendations.append("Document normal tracing characteristics")

    elif prediction == 1:  # Suspect
        recommendations.append("⚠️ Category 2 (Indeterminate) pattern detected")
        recommendations.append("Implement conservative measures: maternal repositioning, hydration, oxygen supplementation")
        recommendations.append("Perform fetal scalp stimulation to assess reactivity")
        recommendations.append("Reassess in 15-30 minutes")
        recommendations.append("Notify physician if pattern persists or worsens")

        # Context-specific recommendations
        if patient_context and "Hypertension" in patient_context.risk_factors:
            recommendations.append("📋 Note: Hypertensive disorder present - lower threshold for intervention")

    else:  # Pathological
        recommendations.append("🚨 Category 3 (Abnormal) pattern detected - IMMEDIATE ACTION REQUIRED")
        recommendations.append("1. Call for immediate physician evaluation")
        recommendations.append("2. Initiate intrauterine resuscitation: lateral position, oxygen 10L/min, IV fluid bolus")
        recommendations.append("3. Discontinue oxytocin if applicable")
        recommendations.append("4. Prepare for possible expedited delivery")
        recommendations.append("5. Assemble delivery team")

        if features.get("ASTV", 50) < 30:
            recommendations.append("📊 Reduced variability noted - concerning for fetal compromise")
        if features.get("DP", 0) > 0:
            recommendations.append("📊 Prolonged decelerations detected - assess for cord compression or placental abruption")

    return recommendations


def get_relevant_guidelines(prediction: int) -> List[Dict[str, Any]]:
    """Retrieve relevant clinical guidelines based on prediction"""
    if not GUIDELINES:
        return []

    all_guidelines = GUIDELINES.get("guidelines", [])

    # Always include three-tier classification guideline
    relevant = [g for g in all_guidelines if g.get("guideline_id") == "CTG-005"]

    # Add specific guidelines based on prediction
    if prediction == 2:  # Pathological
        # Add deceleration and variability guidelines
        relevant.extend([g for g in all_guidelines if g.get("guideline_id") in ["CTG-002", "CTG-004"]])

    return relevant


def generate_case_studies_summary(cases: List[Dict[str, Any]]) -> str:
    """
    Generate an intelligent summary synthesizing insights from multiple similar cases

    Args:
        cases: List of similar case dictionaries (typically 3 cases)

    Returns:
        Formatted markdown summary with key clinical insights
    """
    if not cases or len(cases) == 0:
        return "No similar cases available for analysis."

    # Extract common patterns
    nsp_labels = [case.get('nsp_label', 'Unknown') for case in cases]
    risk_factors_all = []
    delivery_modes = []
    interventions_all = []
    gestational_ages = []
    nicu_admissions = 0
    apgar_scores = []

    for case in cases:
        demo = case.get('demographics', {})
        outcome = case.get('outcome', {})

        # Collect risk factors
        rf = demo.get('risk_factors', [])
        if rf and rf[0] != 'None':
            risk_factors_all.extend(rf)

        # Collect outcomes
        delivery_modes.append(outcome.get('delivery_mode', 'Unknown'))
        interventions_all.extend(outcome.get('interventions', []))

        # Collect demographics
        gestational_ages.append(demo.get('gestational_age_weeks', 0))

        # NICU admissions
        if outcome.get('nicu_admission'):
            nicu_admissions += 1

        # Apgar scores
        apgar_1 = outcome.get('apgar_1min', 0)
        apgar_5 = outcome.get('apgar_5min', 0)
        apgar_scores.append((apgar_1, apgar_5))

    # Analyze CTG patterns
    avg_baseline = np.mean([case.get('ctg_features', {}).get('LB', 0) for case in cases])
    avg_variability = np.mean([case.get('ctg_features', {}).get('ASTV', 0) for case in cases])
    avg_accelerations = np.mean([case.get('ctg_features', {}).get('AC', 0) for case in cases])
    avg_decels_light = np.mean([case.get('ctg_features', {}).get('DL', 0) for case in cases])
    avg_decels_severe = np.mean([case.get('ctg_features', {}).get('DS', 0) for case in cases])

    # Count common classifications
    from collections import Counter
    nsp_counter = Counter(nsp_labels)
    most_common_nsp = nsp_counter.most_common(1)[0] if nsp_counter else ('Unknown', 0)

    # Build summary
    summary_parts = []

    # Header
    summary_parts.append(f"## Clinical Case Summary Analysis ({len(cases)} Similar Cases)\n")

    # Classification Overview
    summary_parts.append(f"### Classification Pattern\n")
    summary_parts.append(f"- **Predominant Classification**: {most_common_nsp[0]} ({most_common_nsp[1]}/{len(cases)} cases)\n")
    if len(set(nsp_labels)) > 1:
        summary_parts.append(f"- **Distribution**: {', '.join([f'{label} ({count})' for label, count in nsp_counter.items()])}\n")

    # CTG Characteristics
    summary_parts.append(f"\n### CTG Pattern Characteristics\n")
    summary_parts.append(f"- **Average Baseline FHR**: {avg_baseline:.1f} bpm\n")
    summary_parts.append(f"- **Average Variability (ASTV)**: {avg_variability:.1f} ms\n")
    summary_parts.append(f"- **Average Accelerations**: {avg_accelerations:.3f}/sec\n")
    if avg_decels_light > 0 or avg_decels_severe > 0:
        summary_parts.append(f"- **Decelerations**: Light ({avg_decels_light:.2f}/sec), Severe ({avg_decels_severe:.2f}/sec)\n")

    # Risk Factors
    if risk_factors_all:
        risk_counter = Counter(risk_factors_all)
        summary_parts.append(f"\n### Common Risk Factors\n")
        for risk, count in risk_counter.most_common(5):
            summary_parts.append(f"- {risk} ({count}/{len(cases)} cases)\n")

    # Clinical Outcomes
    summary_parts.append(f"\n### Outcomes & Management\n")
    delivery_counter = Counter(delivery_modes)
    summary_parts.append(f"- **Delivery Methods**: {', '.join([f'{mode} ({count})' for mode, count in delivery_counter.items()])}\n")
    summary_parts.append(f"- **NICU Admissions**: {nicu_admissions}/{len(cases)} cases\n")

    # Apgar analysis
    avg_apgar_1 = np.mean([a[0] for a in apgar_scores])
    avg_apgar_5 = np.mean([a[1] for a in apgar_scores])
    summary_parts.append(f"- **Average Apgar Scores**: 1-min: {avg_apgar_1:.1f}, 5-min: {avg_apgar_5:.1f}\n")

    # Common Interventions
    if interventions_all:
        intervention_counter = Counter(interventions_all)
        summary_parts.append(f"\n### Frequent Interventions\n")
        for intervention, count in intervention_counter.most_common(5):
            summary_parts.append(f"- {intervention} ({count} occurrences)\n")

    # Clinical Insights
    summary_parts.append(f"\n### Key Clinical Insights\n")

    if most_common_nsp[0] == 'Normal':
        summary_parts.append(f"- These cases demonstrate reassuring CTG patterns with good variability and appropriate baseline\n")
        summary_parts.append(f"- Most delivered vaginally with favorable neonatal outcomes\n")
    elif most_common_nsp[0] == 'Suspect':
        summary_parts.append(f"- Category 2 patterns require heightened surveillance and conservative management\n")
        summary_parts.append(f"- Early intervention with repositioning, hydration, and oxygen often beneficial\n")
        summary_parts.append(f"- Close reassessment every 15-30 minutes essential\n")
    else:  # Pathological
        summary_parts.append(f"- Category 3 patterns demand immediate action and preparation for expedited delivery\n")
        summary_parts.append(f"- High rate of emergency interventions and NICU admissions reflects severity\n")
        summary_parts.append(f"- Rapid recognition and response critical for optimizing outcomes\n")

    if gestational_ages:
        avg_ga = np.mean(gestational_ages)
        summary_parts.append(f"- Average gestational age: {avg_ga:.1f} weeks\n")

    return "".join(summary_parts)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
