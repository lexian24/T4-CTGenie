import './PatientMonitor.css'
import { useLiveFHR, useLiveAstv } from '../hooks/useLiveFHR'

function PatientMonitor({ patient, onClick }) {
  const liveFHR = useLiveFHR(patient.ctg_features.LB, patient.nsp_class)
  const liveAstv = useLiveAstv(patient.ctg_features.ASTV)

  const getRiskColor = (label) => {
    if (label === 'Pathological') return 'critical'
    if (label === 'Suspect') return 'warning'
    return 'normal'
  }

  const getRiskIcon = (label) => {
    if (label === 'Pathological') return '🚨'
    if (label === 'Suspect') return '⚠️'
    return '✓'
  }

  return (
    <div className={`patient-monitor ${getRiskColor(patient.nsp_label)}`} onClick={onClick}>
      <div className="monitor-header">
        <span className="patient-id">{patient.demographics.patient_id}</span>
        <span className={`risk-badge ${getRiskColor(patient.nsp_label)}`}>
          {getRiskIcon(patient.nsp_label)} {patient.nsp_label}
        </span>
      </div>

      <div className="monitor-body">
        <div className="vital-sign">
          <span className="vital-label">FHR</span>
          <span className="vital-value live-value">{liveFHR} bpm</span>
        </div>
        <div className="vital-sign">
          <span className="vital-label">Variability</span>
          <span className="vital-value live-value">{liveAstv} ms</span>
        </div>
        <div className="vital-sign">
          <span className="vital-label">Gestational</span>
          <span className="vital-value">{patient.demographics.gestational_age_weeks}w</span>
        </div>
      </div>

      <div className="monitor-footer">
        <div className="patient-info">
          <span>{patient.demographics.age}yo</span>
          <span>G{patient.demographics.gravida}P{patient.demographics.para}</span>
        </div>
        <button className="view-details">View Details →</button>
      </div>
    </div>
  )
}

export default PatientMonitor
