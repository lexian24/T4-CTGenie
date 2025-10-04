import { useState, useEffect } from 'react'
import './PatientDetail.css'
import { getFeatureName } from '../utils/featureNames'

function PatientDetail({ patient, onClose }) {
  const [prediction, setPrediction] = useState(null)
  const [similarCases, setSimilarCases] = useState([])
  const [casesSummary, setCasesSummary] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Get AI prediction for this patient
    fetch('http://localhost:8000/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ctg_features: patient.ctg_features })
    })
      .then(res => res.json())
      .then(data => {
        console.log('Prediction data:', data) // Debug log
        setPrediction(data)
      })
      .catch(err => console.error('Error:', err))

    // Get similar cases with AI summary
    fetch('http://localhost:8000/similar-cases', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ctg_features: patient.ctg_features,
        top_k: 3
      })
    })
      .then(res => res.json())
      .then(data => {
        setSimilarCases(data.similar_cases || [])
        setCasesSummary(data.cases_summary || '')
        setLoading(false)
      })
      .catch(err => console.error('Error:', err))
  }, [patient])

  const getRiskColor = (label) => {
    if (label === 'Pathological') return 'critical'
    if (label === 'Suspect') return 'warning'
    return 'normal'
  }

  return (
    <div className="patient-detail-overlay" onClick={onClose}>
      <div className="patient-detail" onClick={e => e.stopPropagation()}>
        <button className="close-button" onClick={onClose}>×</button>

        <div className="detail-header">
          <h2>{patient.demographics.patient_id}</h2>
          <span className={`risk-badge-large ${getRiskColor(patient.nsp_label)}`}>
            {patient.nsp_label}
          </span>
        </div>

        <div className="detail-grid">
          {/* Demographics */}
          <div className="detail-section">
            <h3>Patient Information</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">Age:</span>
                <span className="info-value">{patient.demographics.age} years</span>
              </div>
              <div className="info-item">
                <span className="info-label">Gestational Age:</span>
                <span className="info-value">{patient.demographics.gestational_age_weeks} weeks</span>
              </div>
              <div className="info-item">
                <span className="info-label">Gravida/Para:</span>
                <span className="info-value">G{patient.demographics.gravida}P{patient.demographics.para}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Admission:</span>
                <span className="info-value">{patient.demographics.admission_date}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Risk Factors:</span>
                <span className="info-value">{patient.demographics.risk_factors.join(', ')}</span>
              </div>
            </div>
          </div>

          {/* AI Prediction */}
          <div className="detail-section">
            <h3>AI Assessment</h3>
            {prediction ? (
              <div className="prediction-box">
                <div className="prediction-main">
                  <span className="prediction-label">Predicted Class:</span>
                  <span className={`prediction-value ${getRiskColor(prediction.prediction_label)}`}>
                    {prediction.prediction_label}
                  </span>
                </div>
                <div className="confidence">
                  <span className="confidence-label">Confidence:</span>
                  <div className="confidence-bar">
                    <div
                      className="confidence-fill"
                      style={{width: `${prediction.confidence * 100}%`}}
                    />
                  </div>
                  <span className="confidence-value">{(prediction.confidence * 100).toFixed(1)}%</span>
                </div>
                {prediction.shap_values && Object.keys(prediction.shap_values).length > 0 ? (
                  <div className="top-features">
                    <h4>Top Contributing Factors:</h4>
                    <ul>
                      {Object.entries(prediction.shap_values)
                        .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
                        .slice(0, 5)
                        .map(([feature, value]) => (
                          <li key={feature} title={getFeatureName(feature)}>
                            <span className="feature-name">
                              <span className="feature-abbr">{feature}</span>
                              <span className="feature-tooltip">{getFeatureName(feature)}</span>
                            </span>
                            <span className={`feature-impact ${value > 0 ? 'positive' : 'negative'}`}>
                              {value > 0 ? '+' : ''}{value.toFixed(3)}
                            </span>
                          </li>
                        ))
                      }
                    </ul>
                  </div>
                ) : (
                  <div className="no-shap">
                    <p>SHAP values not available for this prediction</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="loading-box">Analyzing...</div>
            )}
          </div>

          {/* CTG Features */}
          <div className="detail-section full-width">
            <h3>CTG Vital Signs</h3>
            <div className="vital-grid">
              <div className="vital-card">
                <span className="vital-card-label">Baseline FHR</span>
                <span className="vital-card-value">{Math.round(patient.ctg_features.LB)} bpm</span>
              </div>
              <div className="vital-card">
                <span className="vital-card-label">Accelerations</span>
                <span className="vital-card-value">{patient.ctg_features.AC}</span>
              </div>
              <div className="vital-card">
                <span className="vital-card-label">Fetal Movement</span>
                <span className="vital-card-value">{Math.round(patient.ctg_features.FM)}</span>
              </div>
              <div className="vital-card">
                <span className="vital-card-label">Variability (ASTV)</span>
                <span className="vital-card-value">{Math.round(patient.ctg_features.ASTV)} ms</span>
              </div>
              <div className="vital-card">
                <span className="vital-card-label">Light Decelerations</span>
                <span className="vital-card-value">{patient.ctg_features.DL.toFixed(1)}</span>
              </div>
              <div className="vital-card">
                <span className="vital-card-label">Uterine Contractions</span>
                <span className="vital-card-value">{patient.ctg_features.UC.toFixed(1)}</span>
              </div>
            </div>
          </div>

          {/* Clinical Narrative */}
          <div className="detail-section full-width">
            <h3>Clinical Notes</h3>
            <p className="clinical-note">{patient.clinical_narrative}</p>
          </div>

          {/* Similar Cases */}
          <div className="detail-section full-width">
            <h3>📚 Similar Historical Case Studies</h3>
            {loading ? (
              <div className="loading-box">Loading similar cases...</div>
            ) : (
              <>
                {/* AI-Generated Summary */}
                {casesSummary && (
                  <div className="cases-summary-box">
                    <div className="summary-header">
                      <span className="summary-icon">🤖</span>
                      <h4>AI-Generated Clinical Summary</h4>
                    </div>
                    <div className="summary-content"
                         dangerouslySetInnerHTML={{
                           __html: casesSummary
                             .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                             .replace(/###\s+(.*)/g, '<h4>$1</h4>')
                             .replace(/##\s+(.*)/g, '<h3>$1</h3>')
                             .replace(/\n- /g, '<br/>• ')
                             .replace(/\n\n/g, '<br/>')
                         }}
                    />
                  </div>
                )}

                {/* Individual Case Studies */}
                <div className="case-studies">
                  {similarCases.map((similarCase, idx) => (
                    <div key={similarCase.case_id} className="case-study-card">
                      <div className="case-study-header">
                        <div className="case-study-title">
                          <span className="case-study-number">Case Study #{idx + 1}</span>
                          <span className="case-study-id">{similarCase.case_id}</span>
                        </div>
                        <div className="case-study-meta">
                          <span className={`case-badge ${getRiskColor(similarCase.nsp_label)}`}>
                            {similarCase.nsp_label}
                          </span>
                          <span className="similarity-score">
                            {(similarCase.similarity_score * 100).toFixed(0)}% Match
                          </span>
                        </div>
                      </div>
                      <div className="case-study-essay"
                           dangerouslySetInnerHTML={{
                             __html: similarCase.case_study_essay?.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n\n/g, '<br/><br/>')
                           }}
                      />
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>

          {/* Outcome */}
          {patient.outcome && (
            <div className="detail-section full-width">
              <h3>Delivery Outcome</h3>
              <div className="outcome-grid">
                <div className="outcome-item">
                  <span className="outcome-label">Delivery Mode:</span>
                  <span className="outcome-value">{patient.outcome.delivery_mode}</span>
                </div>
                <div className="outcome-item">
                  <span className="outcome-label">Apgar Scores:</span>
                  <span className="outcome-value">{patient.outcome.apgar_1min} (1min) / {patient.outcome.apgar_5min} (5min)</span>
                </div>
                <div className="outcome-item">
                  <span className="outcome-label">Birth Weight:</span>
                  <span className="outcome-value">{patient.outcome.birth_weight_grams}g</span>
                </div>
                <div className="outcome-item">
                  <span className="outcome-label">NICU Admission:</span>
                  <span className="outcome-value">{patient.outcome.nicu_admission ? 'Yes' : 'No'}</span>
                </div>
                <div className="outcome-item">
                  <span className="outcome-label">Interventions:</span>
                  <span className="outcome-value">{patient.outcome.interventions.join(', ')}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default PatientDetail
