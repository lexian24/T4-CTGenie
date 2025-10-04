# llm_explainer/glossary.py

# Human- and clinician-friendly metadata for features.
# Keys must match raw feature names in your dataframe (X_final columns).
GLOSSARY = {
    # Variability / physiologic measures
    "MSTV": {
        "parent_name": "short-term heart rate variability",
        "doctor_name": "MSTV",
        "parent_desc": "How much the baby's heart rate changes beat-to-beat over short periods.",
        "doctor_desc": "Mean short-term variability; lower values can indicate reduced autonomic responsiveness.",
        "unit": "bpm (approx.)",
        "ref": "—"
    },
    "ASTV": {
        "parent_name": "time with abnormal short-term variability",
        "doctor_name": "ASTV (%)",
        "parent_desc": "Percent of time with less healthy short-term changes in heart rate.",
        "doctor_desc": "Proportion of epochs with abnormal short-term variability; higher values may indicate compromise.",
        "unit": "%",
        "ref": "—"
    },
    "ALTV": {
        "parent_name": "time with abnormal long-term variability",
        "doctor_name": "ALTV (%)",
        "parent_desc": "Percent of time with less healthy longer swings of heart rate.",
        "doctor_desc": "Proportion of epochs with abnormal long-term variability.",
        "unit": "%",
        "ref": "—"
    },

    # Patterns (binary)
    "SUSP": {
        "parent_name": "suspect pattern",
        "doctor_name": "Suspect pattern",
        "parent_desc": "An in-between pattern that needs closer watching.",
        "doctor_desc": "SisPorto 'suspect' pattern flag; often correlates with intermediate risk.",
        "unit": "0/1",
        "ref": "0 = no, 1 = yes"
    },
    "FS": {
        "parent_name": "flat-sinusoidal pattern",
        "doctor_name": "Flat-sinusoidal pattern (FS)",
        "parent_desc": "A concerning pattern that may signal problems.",
        "doctor_desc": "Associated with pathological states; sustained presence is worrisome.",
        "unit": "0/1",
        "ref": "0 = no, 1 = yes"
    },
    "LD": {
        "parent_name": "largely decelerative pattern",
        "doctor_name": "Largely decelerative pattern (LD)",
        "parent_desc": "Frequent slowdowns in the baby's heart rate.",
        "doctor_desc": "Frequent/recurrent decelerations; may reflect hypoxic episodes.",
        "unit": "0/1",
        "ref": "0 = no, 1 = yes"
    },
    "AD": {
        "parent_name": "accelerative/decelerative pattern",
        "doctor_name": "AD pattern",
        "parent_desc": "Ups and downs in the baby's heart rate.",
        "doctor_desc": "Mixed acceleration/deceleration pattern; context-dependent significance.",
        "unit": "0/1",
        "ref": "0 = no, 1 = yes"
    },
    "DE": {
        "parent_name": "decelerative pattern",
        "doctor_name": "Decelerative pattern (DE)",
        "parent_desc": "More slowdowns than usual in heart rate.",
        "doctor_desc": "Predominant decelerations; consider relation to contractions and baseline.",
        "unit": "0/1",
        "ref": "0 = no, 1 = yes"
    },

    # Histogram / baseline measures
    "LBE": {
        "parent_name": "baseline heart rate (expert)",
        "doctor_name": "Baseline FHR (expert)",
        "parent_desc": "Average heart rate between contractions when the baby is resting.",
        "doctor_desc": "Expert-estimated FHR baseline.",
        "unit": "bpm",
        "ref": "—"
    },
    "Mean": {
        "parent_name": "histogram mean heart rate",
        "doctor_name": "Histogram mean",
        "parent_desc": "Average heart rate across the exam.",
        "doctor_desc": "Mean of FHR distribution; proxy for baseline.",
        "unit": "bpm",
        "ref": "—"
    },
    "Variance": {
        "parent_name": "heart rate spread",
        "doctor_name": "Histogram variance",
        "parent_desc": "How spread-out the heart rate values are.",
        "doctor_desc": "Dispersion of FHR distribution; ties to variability.",
        "unit": "bpm²",
        "ref": "—"
    },

    # Counts and events
    "AC": {
        "parent_name": "accelerations",
        "doctor_name": "Accelerations (AC)",
        "parent_desc": "Moments when the baby's heart rate briefly speeds up.",
        "doctor_desc": "Number/rate of accelerations; reassuring when present.",
        "unit": "count",
        "ref": "—"
    },
    "FM": {
        "parent_name": "fetal movements",
        "doctor_name": "Fetal movement (FM)",
        "parent_desc": "How often the baby moves.",
        "doctor_desc": "Movement counts; context with FHR patterns.",
        "unit": "count",
        "ref": "—"
    },
    "UC": {
        "parent_name": "uterine contractions",
        "doctor_name": "Uterine contractions (UC)",
        "parent_desc": "How often the womb tightens.",
        "doctor_desc": "Frequency of uterine activity; align decelerations with contractions.",
        "unit": "count",
        "ref": "—"
    },
    "DL": {
        "parent_name": "light decelerations",
        "doctor_name": "Light decelerations (DL)",
        "parent_desc": "Small slowdowns in heart rate.",
        "doctor_desc": "Mild decelerations; significance depends on timing/morphology.",
        "unit": "count",
        "ref": "—"
    },
    "DP": {
        "parent_name": "prolonged decelerations",
        "doctor_name": "Prolonged decelerations (DP)",
        "parent_desc": "Longer slowdowns in heart rate.",
        "doctor_desc": "Prolonged decelerations; evaluate relation to uterine activity.",
        "unit": "count",
        "ref": "—"
    },

    # You can add more entries for: Width, Min, Max, Nmax, Nzeros, Mode, Median, Tendency, etc.
}
