import { useState, useEffect } from 'react'
import './App.css'
import PatientMonitor from './components/PatientMonitor'
import PatientDetail from './components/PatientDetail'

function App() {
  const [patients, setPatients] = useState([])
  const [selectedPatient, setSelectedPatient] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Fetch synthetic cases from backend
    fetch('http://localhost:8000/similar-cases', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ctg_features: {
          AC: 0, FM: 0, UC: 0, DL: 0, DS: 0, DP: 0, DR: 0, LB: 130,
          "AC.1": 0, "FM.1": 0, "UC.1": 0, "DL.1": 0, "DS.1": 0, "DP.1": 0,
          ASTV: 50, MSTV: 1, ALTV: 10, MLTV: 8, Width: 50, Min: 100, Max: 160,
          Nmax: 5, Nzeros: 0, Mode: 140, Mean: 130, Median: 135, Variance: 20,
          Tendency: 0, A: 0, B: 0, C: 0, D: 0, E: 0, AD: 0, DE: 0, LD: 0, FS: 0, SUSP: 0, CLASS: 5
        },
        top_k: 20
      })
    })
      .then(res => res.json())
      .then(data => {
        setPatients(data.similar_cases || [])
        setLoading(false)
      })
      .catch(err => {
        console.error('Error fetching patients:', err)
        setLoading(false)
      })
  }, [])

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🏥 CTGenie - Fetal Monitoring Dashboard</h1>
          <div className="stats">
            <div className="stat">
              <span className="stat-value">{patients.length}</span>
              <span className="stat-label">Active Patients</span>
            </div>
            <div className="stat">
              <span className="stat-value">{patients.filter(p => p.nsp_label === 'Pathological').length}</span>
              <span className="stat-label alert">Critical</span>
            </div>
            <div className="stat">
              <span className="stat-value">{patients.filter(p => p.nsp_label === 'Suspect').length}</span>
              <span className="stat-label warning">Suspect</span>
            </div>
          </div>
        </div>
      </header>

      <main className="app-main">
        {loading ? (
          <div className="loading">Loading patient data...</div>
        ) : (
          <div className="monitor-grid">
            {patients.map(patient => (
              <PatientMonitor
                key={patient.case_id}
                patient={patient}
                onClick={() => setSelectedPatient(patient)}
              />
            ))}
          </div>
        )}
      </main>

      {selectedPatient && (
        <PatientDetail
          patient={selectedPatient}
          onClose={() => setSelectedPatient(null)}
        />
      )}
    </div>
  )
}

export default App
