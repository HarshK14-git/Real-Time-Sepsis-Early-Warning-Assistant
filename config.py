# ─────────────────────────────────────────────────────────────────────
# CLINICAL THRESHOLDS AND CONFIGURATION
# Real-Time Sepsis Early Warning Assistant
# ─────────────────────────────────────────────────────────────────────

# ── VITAL SIGN REFERENCE RANGES ───────────────────────────────────────
VITAL_RANGES = {
    "temperature": {
        "critical_low":  35.0, "low":  36.0,
        "high":          38.0, "critical_high": 39.5,
        "unit": "°C", "label": "Temperature"
    },
    "heart_rate": {
        "critical_low":  40,   "low":  60,
        "high":          90,   "critical_high": 130,
        "unit": "bpm", "label": "Heart Rate"
    },
    "respiratory_rate": {
        "critical_low":  8,    "low":  12,
        "high":          20,   "critical_high": 30,
        "unit": "/min", "label": "Respiratory Rate"
    },
    "sbp": {
        "critical_low":  80,   "low":  100,
        "high":          140,  "critical_high": 180,
        "unit": "mmHg", "label": "Systolic BP"
    },
    "dbp": {
        "critical_low":  40,   "low":  60,
        "high":          90,   "critical_high": 120,
        "unit": "mmHg", "label": "Diastolic BP"
    },
    "spo2": {
        "critical_low":  90.0, "low":  95.0,
        "high":          100.0,"critical_high": 100.0,
        "unit": "%", "label": "SpO2"
    },
    "wbc": {
        "critical_low":  2000, "low":  4000,
        "high":          12000,"critical_high": 20000,
        "unit": "cells/µL", "label": "WBC Count"
    },
    "lactate": {
        "critical_low":  0.0,  "low":  0.0,
        "high":          2.0,  "critical_high": 4.0,
        "unit": "mmol/L", "label": "Lactate"
    },
    "creatinine": {
        "critical_low":  0.0,  "low":  0.0,
        "high":          1.2,  "critical_high": 3.5,
        "unit": "mg/dL", "label": "Creatinine"
    },
}

# ── SIRS CRITERIA ──────────────────────────────────────────────────────
# ≥2 criteria required for SIRS positive
SIRS_CRITERIA = {
    "temperature":       {"condition": "temp > 38.0 or temp < 36.0",
                          "description": "Temperature >38.0°C or <36.0°C"},
    "heart_rate":        {"condition": "hr > 90",
                          "description": "Heart Rate >90 bpm"},
    "respiratory_rate":  {"condition": "rr > 20",
                          "description": "Respiratory Rate >20/min"},
    "wbc":               {"condition": "wbc > 12000 or wbc < 4000",
                          "description": "WBC >12,000 or <4,000 cells/µL"},
}

# ── qSOFA CRITERIA ─────────────────────────────────────────────────────
# ≥2 criteria = high sepsis risk
QSOFA_CRITERIA = {
    "respiratory_rate":  {"condition": "rr >= 22",
                          "description": "Respiratory Rate ≥22/min"},
    "mental_status":     {"condition": "altered_mentation",
                          "description": "Altered mental status (GCS <15)"},
    "sbp":               {"condition": "sbp <= 100",
                          "description": "Systolic BP ≤100 mmHg"},
}

# ── NEWS2 SCORING TABLE ───────────────────────────────────────────────
NEWS2_RANGES = {
    "respiratory_rate": [
        (0, 8,    3), (9, 11,   1), (12, 20,  0),
        (21, 24,  2), (25, 9999, 3)
    ],
    "spo2_scale1": [
        (0, 91,   3), (92, 93,  2), (94, 95, 1), (96, 100, 0)
    ],
    "sbp": [
        (0, 90,   3), (91, 100, 2), (101, 110, 1),
        (111, 219, 0), (220, 9999, 3)
    ],
    "heart_rate": [
        (0, 40,   3), (41, 50,  1), (51, 90,  0),
        (91, 110,  1), (111, 130, 2), (131, 9999, 3)
    ],
    "temperature": [
        (0, 35.0,  3), (35.1, 36.0, 1), (36.1, 38.0, 0),
        (38.1, 39.0, 1), (39.1, 99.0, 2)
    ],
}

# NEWS2 consciousness scores
NEWS2_CONSCIOUSNESS = {
    "alert":        0,
    "confused":     3,
    "lethargic":    3,
    "unresponsive": 3,
}

# ── SEVERITY DEFINITIONS ───────────────────────────────────────────────
SEVERITY_LEVELS = {
    "NO_RISK": {
        "label":        "No Sepsis Risk Detected",
        "short":        "NO RISK",
        "level":        1,
        "color":        "#059669",
        "bg_color":     "#ECFDF5",
        "border_color": "#6EE7B7",
        "icon":         "✅",
        "priority":     "ROUTINE",
        "response_time":"Next scheduled observation",
        "escalation":   "No immediate escalation required. Continue routine nursing care.",
        "message":      "No significant sepsis indicators detected at this time. Continue routine monitoring.",
        "immediate_actions": [
            "Continue routine vital sign monitoring per ward protocol (every 4–8 hours)",
            "Maintain adequate hydration and nutrition",
            "Document assessment in patient record",
            "Educate patient on signs to report: increased pain, fever, confusion"
        ],
        "investigations": [
            "Routine observations as per ward protocol",
            "Reassess immediately if patient condition changes or deteriorates"
        ],
    },
    "SEPSIS_WATCH": {
        "label":        "Sepsis Watch",
        "short":        "WATCH",
        "level":        2,
        "color":        "#D97706",
        "bg_color":     "#FFFBEB",
        "border_color": "#FCD34D",
        "icon":         "👁️",
        "priority":     "ELEVATED",
        "response_time":"Within 1 hour",
        "escalation":   "Notify charge nurse within 30 minutes. Attending physician review within 1 hour.",
        "message":      "One or more early warning signs present. Increase monitoring frequency and initiate workup.",
        "immediate_actions": [
            "Increase vital sign monitoring to every 1–2 hours",
            "Notify charge nurse immediately",
            "Assess fluid intake, urine output, and hydration status",
            "Review recent medications, surgical history, and potential infection sources",
            "Ensure IV access is available",
            "Prepare documentation for physician review"
        ],
        "investigations": [
            "Full blood count (FBC) with differential",
            "C-Reactive Protein (CRP) and ESR",
            "Blood urea, creatinine, and electrolytes",
            "Urine analysis and mid-stream urine culture",
            "Blood cultures x2 if clinical suspicion of infection"
        ],
    },
    "SEPSIS_ALERT": {
        "label":        "Sepsis Alert",
        "short":        "SEPSIS",
        "level":        3,
        "color":        "#EA580C",
        "bg_color":     "#FFF7ED",
        "border_color": "#FB923C",
        "icon":         "⚠️",
        "priority":     "URGENT",
        "response_time":"Within 30 minutes",
        "escalation":   "Immediate physician notification. Initiate Sepsis-6 Bundle within 1 hour.",
        "message":      "Sepsis criteria met. Begin Sepsis Bundle immediately. Time-critical intervention required.",
        "immediate_actions": [
            "ALERT: Notify physician IMMEDIATELY — do not delay",
            "Establish IV access — 2 large-bore peripheral cannulas",
            "Draw blood cultures x2 sets BEFORE administering any antibiotics",
            "Initiate IV fluid resuscitation: 500mL crystalloid (0.9% saline or Hartmann's) bolus",
            "Administer broad-spectrum IV antibiotics within 1 hour of recognition",
            "Apply supplemental oxygen — target SpO2 ≥94%",
            "Monitor urine output — insert urinary catheter, target ≥0.5 mL/kg/hour",
            "Record and repeat observations every 30 minutes",
            "Complete Sepsis-6 Bundle documentation"
        ],
        "investigations": [
            "Blood cultures x2 sets STAT (before antibiotics — critical timing)",
            "Full blood count with differential (STAT)",
            "Comprehensive metabolic panel: U&E, LFTs, bone profile",
            "Serum lactate (STAT — target <2 mmol/L with treatment)",
            "Procalcitonin (PCT)",
            "CRP (STAT)",
            "Coagulation screen: PT, APTT, INR, fibrinogen",
            "Urine analysis, microscopy, and culture",
            "Chest X-ray (PA or portable)",
            "12-lead ECG",
            "Consider additional cultures: wound, sputum, line tips as clinically indicated"
        ],
    },
    "SEVERE_SEPSIS": {
        "label":        "Severe Sepsis",
        "short":        "SEVERE",
        "level":        4,
        "color":        "#DC2626",
        "bg_color":     "#FEF2F2",
        "border_color": "#FCA5A5",
        "icon":         "🚨",
        "priority":     "CRITICAL",
        "response_time":"Immediately",
        "escalation":   "Senior physician/registrar to attend IMMEDIATELY. ICU/HDU referral. Activate sepsis pathway.",
        "message":      "Severe sepsis with evidence of organ dysfunction. Urgent ICU-level intervention required.",
        "immediate_actions": [
            "EMERGENCY: Call senior physician/registrar to bedside NOW",
            "Activate hospital Sepsis Pathway / Code Sepsis if available",
            "Establish 2 large-bore IV lines — prepare for central venous access",
            "Blood cultures x2 BEFORE antibiotics — do NOT delay antibiotics for cultures",
            "Broad-spectrum IV antibiotics STAT (within 1 hour, ideally within 30 minutes)",
            "Aggressive fluid resuscitation: 30 mL/kg crystalloid IV bolus",
            "High-flow oxygen via non-rebreather mask — maintain SpO2 ≥94%",
            "Continuous cardiac monitoring (ECG, SpO2, BP)",
            "Insert urinary catheter — strict hourly urine output monitoring",
            "Consider arterial line for continuous hemodynamic monitoring",
            "Reassess fluid response every 15–30 minutes using dynamic parameters",
            "Prepare for possible ICU transfer — alert ICU team now"
        ],
        "investigations": [
            "Blood cultures x2 sets STAT (before antibiotics)",
            "Arterial blood gas (ABG) with lactate STAT",
            "Serum lactate STAT (target <2 mmol/L; >4 = septic shock)",
            "Full blood count with differential",
            "Comprehensive metabolic panel (U&E, LFTs, creatinine, bilirubin)",
            "Procalcitonin (PCT) and CRP",
            "Coagulation screen (DIC screen: PT, APTT, INR, fibrinogen, D-dimer)",
            "Troponin I and BNP/NT-proBNP",
            "Portable chest X-ray",
            "12-lead ECG",
            "Urine analysis and culture",
            "Consider CT abdomen/chest/pelvis if source unclear",
            "Bedside echocardiography if cardiac dysfunction suspected"
        ],
    },
    "SEPTIC_SHOCK": {
        "label":        "Septic Shock",
        "short":        "SHOCK",
        "level":        5,
        "color":        "#7F1D1D",
        "bg_color":     "#FEF2F2",
        "border_color": "#EF4444",
        "icon":         "🆘",
        "priority":     "LIFE-THREATENING",
        "response_time":"Immediately — seconds matter",
        "escalation":   "CALL RAPID RESPONSE / CRASH TEAM. ICU admission mandatory. Family notification required.",
        "message":      "CRITICAL: Septic shock. Immediate life-saving intervention required. Every minute increases mortality.",
        "immediate_actions": [
            "ACTIVATE CODE SEPSIS / CALL RAPID RESPONSE TEAM NOW",
            "ICU attending physician to bedside STAT",
            "Establish central venous access (if peripheral inadequate)",
            "Blood cultures x2 IMMEDIATELY — antibiotics must start within 1 hour",
            "Broad-spectrum IV antibiotics STAT (within 1 hour, target within 30 minutes)",
            "IV crystalloid bolus: 30 mL/kg as rapidly as possible (pressure bag if needed)",
            "Start vasopressors (Norepinephrine first-line) if MAP <65 mmHg despite fluids",
            "High-flow oxygen — prepare for intubation/mechanical ventilation",
            "Continuous invasive hemodynamic monitoring (arterial line)",
            "Foley catheter — target urine output ≥0.5 mL/kg/hour",
            "Vasopressor titration to maintain MAP ≥65 mmHg",
            "Consider hydrocortisone 200mg/day if refractory to vasopressors",
            "Serial lactate measurements every 2 hours until clearance",
            "Notify next of kin — prognosis discussion required"
        ],
        "investigations": [
            "Blood cultures x2 STAT (simultaneous with starting antibiotics)",
            "Arterial blood gas STAT (pH, PaO2, PaCO2, HCO3, base excess)",
            "Serum lactate STAT (expected >2 mmol/L, often >4 in shock)",
            "Full blood count",
            "Comprehensive metabolic panel",
            "Coagulation screen + DIC screen (D-dimer, fibrinogen)",
            "Troponin, BNP",
            "Procalcitonin",
            "Portable CXR immediately",
            "Point-of-care ultrasound (POCUS) / echocardiography",
            "CT scan when hemodynamically stable — determine source",
            "All available cultures: urine, sputum, wound, lines"
        ],
    },
}

# ── ALTERED MENTAL STATUS KEYWORDS ────────────────────────────────────
ALTERED_MENTAL_STATUS = [
    "confused", "unresponsive", "altered", "lethargic",
    "obtunded", "stuporous", "comatose", "disoriented"
]

# ── SEPSIS BUNDLE COMPONENTS ───────────────────────────────────────────
SEPSIS_BUNDLE = {
    "1_hour_bundle": [
        "Measure lactate level",
        "Blood cultures before antibiotics",
        "Administer broad-spectrum antibiotics",
        "Rapidly administer 30 mL/kg crystalloid for hypotension or lactate ≥4 mmol/L",
        "Apply vasopressors if hypotensive during or after resuscitation to maintain MAP ≥65 mmHg"
    ],
    "3_hour_bundle": [
        "Measure lactate; remeasure if initial >2 mmol/L",
        "Blood cultures before antibiotics",
        "Administer broad-spectrum antibiotics",
        "Administer 30 mL/kg crystalloid if hypotension or lactate ≥4 mmol/L"
    ]
}