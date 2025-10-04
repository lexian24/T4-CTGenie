import { useState, useEffect } from 'react'

/**
 * Custom hook to simulate live fluctuating FHR (Fetal Heart Rate)
 * Based on baseline value with realistic variations
 */
export const useLiveFHR = (baselineFHR, nspClass) => {
  const [currentFHR, setCurrentFHR] = useState(baselineFHR)

  useEffect(() => {
    // Define fluctuation parameters based on fetal state
    let variabilityRange, fluctuationSpeed

    switch (nspClass) {
      case 1: // Normal
        variabilityRange = 5 // ±5 bpm
        fluctuationSpeed = 1500 // ms
        break
      case 2: // Suspect
        variabilityRange = 8 // ±8 bpm (more erratic)
        fluctuationSpeed = 1200 // ms (faster changes)
        break
      case 3: // Pathological
        variabilityRange = 12 // ±12 bpm (highly variable or flat)
        fluctuationSpeed = 1000 // ms (rapid changes)
        break
      default:
        variabilityRange = 5
        fluctuationSpeed = 1500
    }

    const interval = setInterval(() => {
      // Generate realistic fluctuation using sine wave + random noise
      const time = Date.now() / 1000
      const sineWave = Math.sin(time) * (variabilityRange * 0.6)
      const randomNoise = (Math.random() - 0.5) * (variabilityRange * 0.4)
      const fluctuation = sineWave + randomNoise

      const newFHR = baselineFHR + fluctuation

      // Keep within realistic bounds (80-200 bpm)
      const boundedFHR = Math.max(80, Math.min(200, newFHR))

      setCurrentFHR(Math.round(boundedFHR))
    }, fluctuationSpeed)

    return () => clearInterval(interval)
  }, [baselineFHR, nspClass])

  return currentFHR
}

/**
 * Custom hook to simulate live fluctuating variability (ASTV)
 */
export const useLiveAstv = (baselineAstv) => {
  const [currentAstv, setCurrentAstv] = useState(baselineAstv)

  useEffect(() => {
    const interval = setInterval(() => {
      // Small fluctuations ±3 ms
      const fluctuation = (Math.random() - 0.5) * 6
      const newAstv = baselineAstv + fluctuation

      // Keep within realistic bounds (0-100 ms)
      const boundedAstv = Math.max(0, Math.min(100, newAstv))

      setCurrentAstv(Math.round(boundedAstv))
    }, 2000)

    return () => clearInterval(interval)
  }, [baselineAstv])

  return currentAstv
}
