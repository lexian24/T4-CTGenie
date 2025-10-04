// CTG Feature Name Mappings
// Map from abbreviation to full descriptive name
// Based on CTG monitoring standards

export const FEATURE_NAMES = {
  // Measurements - Baseline and Variability
  'LBE': 'Baseline Value (Fetal Heart Rate)',
  'LB': 'Baseline Value (Fetal Heart Rate)',
  'AC': 'Accelerations (per second)',
  'FM': 'Foetal Movement (per second)',
  'UC': 'Uterine Contractions (per second)',
  'ASTV': 'Percentage of Time with Abnormal Short Term Variability',
  'mSTV': 'Mean Value of Short Term Variability',
  'ALTV': 'Percentage of Time with Abnormal Long Term Variability',
  'mLTV': 'Mean Value of Long Term Variability',

  // Decelerations
  'DL': 'Light Decelerations (per second)',
  'DS': 'Severe Decelerations (per second)',
  'DP': 'Prolonged Decelerations (per second)',
  'DR': 'Repetitive Decelerations',

  // Histogram Analysis
  'Width': 'Histogram Width (low frequency, high frequency)',
  'Min': 'Histogram Minimum (low frequency)',
  'Max': 'Histogram Maximum (high frequency)',
  'Nmax': 'Number of Histogram Peaks',
  'Nzeros': 'Number of Histogram Zeros',
  'Mode': 'Histogram Mode',
  'Mean': 'Histogram Mean',
  'Median': 'Histogram Median',
  'Variance': 'Histogram Variance',
  'Tendency': 'Histogram Tendency',

  // FHR Pattern Classification
  'A': 'Calm Sleep',
  'B': 'REM Sleep',
  'C': 'Calm Vigilance',
  'D': 'Active Vigilance',
  'SH': 'Shift Pattern',
  'AD': 'Accelerative/Decelerative Pattern',
  'DE': 'Decelerative Pattern',
  'LD': 'Largely Decelerative Pattern',
  'FS': 'Flat-Sinusoidal Pattern',
  'SUSP': 'Suspect Pattern',

  // Classification
  'CLASS': 'FHR Pattern Class Code',
  'NSP': 'Fetal State Class (Normal=1, Suspect=2, Pathological=3)',

  // Per-second variations (if present)
  'AC.1': 'Accelerations (per second)',
  'FM.1': 'Foetal Movement (per second)',
  'UC.1': 'Uterine Contractions (per second)',
  'DL.1': 'Light Decelerations (per second)',
  'DS.1': 'Severe Decelerations (per second)',
  'DP.1': 'Prolonged Decelerations (per second)',

  // Alternative names that might appear
  'MSTV': 'Mean Value of Short Term Variability',
  'MLTV': 'Mean Value of Long Term Variability',
  'E': 'Pattern E',
}

export const getFeatureName = (abbreviation) => {
  return FEATURE_NAMES[abbreviation] || abbreviation
}

// Extended descriptions for detailed tooltips
export const FEATURE_DESCRIPTIONS = {
  'LB': 'Baseline fetal heart rate measured in beats per minute (bpm). Normal range: 110-160 bpm',
  'AC': 'Number of fetal heart rate accelerations per second. Indicates fetal well-being',
  'FM': 'Fetal movements detected per second via CTG monitoring',
  'UC': 'Uterine contractions per second measured by tocodynamometer',
  'ASTV': 'Percentage of recording time showing abnormal short-term variability (beat-to-beat changes)',
  'ALTV': 'Percentage of recording time showing abnormal long-term variability (oscillations)',
  'DL': 'Light decelerations in fetal heart rate per second',
  'DS': 'Severe decelerations in fetal heart rate per second (drops >30 bpm)',
  'DP': 'Prolonged decelerations lasting >60 seconds',
  'A': 'Calm sleep pattern - quiet fetal state with low variability',
  'B': 'REM sleep pattern - active sleep with moderate variability',
  'C': 'Calm vigilance - awake but quiet state',
  'D': 'Active vigilance - active fetal state with movements',
}
