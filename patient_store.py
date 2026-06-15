# ─────────────────────────────────────────────────────────────────────
# PATIENT DATA STORE
# Handles all patient data persistence, retrieval, and trend analysis
# ─────────────────────────────────────────────────────────────────────
import json
import os
from datetime import datetime


DB_FILE = "patients.json"


# ── CRUD ──────────────────────────────────────────────────────────────
def load_all() -> list:
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        try:
            return json.load(f)
        except Exception:
            return []


def save_all(records: list):
    with open(DB_FILE, "w") as f:
        json.dump(records, f, indent=2, default=str)


def save_assessment(assessment: dict) -> dict:
    records = load_all()
    records.append(assessment)
    save_all(records)
    return assessment


def get_patient_history(patient_id: str) -> list:
    """Returns all assessments for a specific patient ID, oldest first."""
    records = load_all()
    history = [r for r in records if r.get("patient_id") == patient_id]
    return sorted(history, key=lambda x: x.get("timestamp", ""))


def clear_all():
    save_all([])


# ── STATISTICS ────────────────────────────────────────────────────────
def compute_stats(records: list) -> dict:
    if not records:
        return {
            "total": 0, "no_risk": 0, "watch": 0,
            "alert": 0, "severe": 0, "shock": 0,
            "high_risk": 0, "critical_rate": 0.0,
            "avg_sirs": 0.0, "avg_qsofa": 0.0, "avg_news2": 0.0,
            "unique_patients": 0,
        }

    total     = len(records)
    no_risk   = sum(1 for r in records if r.get("severity") == "NO_RISK")
    watch     = sum(1 for r in records if r.get("severity") == "SEPSIS_WATCH")
    alert     = sum(1 for r in records if r.get("severity") == "SEPSIS_ALERT")
    severe    = sum(1 for r in records if r.get("severity") == "SEVERE_SEPSIS")
    shock     = sum(1 for r in records if r.get("severity") == "SEPTIC_SHOCK")
    high_risk = alert + severe + shock

    avg_sirs  = round(sum(r.get("sirs",  {}).get("score",  0) for r in records) / total, 2)
    avg_qsofa = round(sum(r.get("qsofa", {}).get("score",  0) for r in records) / total, 2)
    avg_news2 = round(sum(r.get("news2", {}).get("total_score", 0) for r in records) / total, 2)

    unique_pts = len(set(r.get("patient_id", "") for r in records if r.get("patient_id")))

    return {
        "total":            total,
        "no_risk":          no_risk,
        "watch":            watch,
        "alert":            alert,
        "severe":           severe,
        "shock":            shock,
        "high_risk":        high_risk,
        "critical_rate":    round((high_risk / total) * 100, 1) if total > 0 else 0.0,
        "avg_sirs":         avg_sirs,
        "avg_qsofa":        avg_qsofa,
        "avg_news2":        avg_news2,
        "unique_patients":  unique_pts,
    }


# ── CSV EXPORT ────────────────────────────────────────────────────────
def to_csv(records: list) -> str:
    headers = [
        "Assessment ID", "Timestamp", "Patient Name", "Patient ID", "Ward",
        "Temperature (°C)", "Heart Rate (bpm)", "Respiratory Rate (/min)",
        "Systolic BP (mmHg)", "Diastolic BP (mmHg)", "SpO2 (%)",
        "Mental Status", "WBC (cells/µL)", "Lactate (mmol/L)", "Creatinine (mg/dL)",
        "SIRS Score", "SIRS Positive", "qSOFA Score", "qSOFA Positive",
        "NEWS2 Score", "NEWS2 Risk",
        "Severity", "Severity Level", "Priority",
        "Critical Alerts", "Organ Dysfunction",
        "AI Insight Available"
    ]

    def esc(v):
        s = str(v).replace('"', '""')
        return f'"{s}"' if ',' in s or '"' in s or '\n' in s else s

    rows = [",".join(headers)]
    for r in records:
        v     = r.get("vitals", {})
        sirs  = r.get("sirs",   {})
        qsofa = r.get("qsofa",  {})
        news2 = r.get("news2",  {})
        alts  = r.get("alerts", {})
        ai    = r.get("ai_guidance", {})

        row = [
            r.get("assessment_id", ""),
            r.get("timestamp", ""),
            r.get("patient_name", ""),
            r.get("patient_id", ""),
            r.get("ward", ""),
            v.get("temperature", ""),
            v.get("heart_rate", ""),
            v.get("respiratory_rate", ""),
            v.get("sbp", ""),
            v.get("dbp", "") or "",
            v.get("spo2", ""),
            v.get("mental_status", ""),
            v.get("wbc", "") or "",
            v.get("lactate", "") or "",
            v.get("creatinine", "") or "",
            sirs.get("score", ""),
            "YES" if sirs.get("positive") else "NO",
            qsofa.get("score", ""),
            "YES" if qsofa.get("positive") else "NO",
            news2.get("total_score", ""),
            news2.get("risk_level", ""),
            r.get("severity_label", ""),
            r.get("severity_level", ""),
            alts.get("priority", ""),
            alts.get("critical_count", 0),
            "YES" if alts.get("organ_dysfunction_present") else "NO",
            "YES" if ai.get("available") else "NO",
        ]
        rows.append(",".join(esc(c) for c in row))

    return "\n".join(rows)


# ── DASHBOARD DATA ────────────────────────────────────────────────────
def build_dashboard(records: list) -> dict:
    stats      = compute_stats(records)
    recent     = list(reversed(records[-10:]))  # last 10 assessments
    high_risk  = [r for r in records if r.get("severity_level", 0) >= 3]
    critical   = [r for r in high_risk if r.get("severity_level", 0) >= 4]

    # Severity distribution
    severity_distribution = [
        {"severity": "No Risk",      "count": stats["no_risk"], "color": "#059669"},
        {"severity": "Sepsis Watch", "count": stats["watch"],   "color": "#D97706"},
        {"severity": "Sepsis Alert", "count": stats["alert"],   "color": "#EA580C"},
        {"severity": "Severe Sepsis","count": stats["severe"],  "color": "#DC2626"},
        {"severity": "Septic Shock", "count": stats["shock"],   "color": "#7F1D1D"},
    ]

    # Average vitals for trending
    def avg_vital(key):
        vals = [r.get("vitals", {}).get(key) for r in records if r.get("vitals", {}).get(key)]
        return round(sum(vals) / len(vals), 1) if vals else None

    avg_vitals = {
        "temperature":      avg_vital("temperature"),
        "heart_rate":       avg_vital("heart_rate"),
        "respiratory_rate": avg_vital("respiratory_rate"),
        "sbp":              avg_vital("sbp"),
        "spo2":             avg_vital("spo2"),
    }

    return {
        "stats":                  stats,
        "severity_distribution":  severity_distribution,
        "recent_assessments":     recent,
        "high_risk_patients":     high_risk[-5:],
        "critical_patients":      critical[-5:],
        "avg_vitals":             avg_vitals,
        "generated_at":           datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }