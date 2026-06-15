# ─────────────────────────────────────────────────────────────────────
# SEPSIS SCORING ENGINE
# SIRS Criteria + qSOFA Score + NEWS2 Score
# ─────────────────────────────────────────────────────────────────────
from config import (
    VITAL_RANGES, SIRS_CRITERIA, QSOFA_CRITERIA,
    NEWS2_RANGES, NEWS2_CONSCIOUSNESS,
    ALTERED_MENTAL_STATUS, SEVERITY_LEVELS
)


# ── VITAL SIGN STATUS ─────────────────────────────────────────────────
def get_vital_status(name: str, value: float) -> str:
    r = VITAL_RANGES.get(name)
    if not r:
        return "normal"
    if value <= r["critical_low"] or (r["critical_high"] < 100 and value >= r["critical_high"]):
        return "critical"
    if value < r["low"] or value > r["high"]:
        return "warning"
    return "normal"


def build_vital_summary(vitals: dict) -> dict:
    summary = {}
    mapping = {
        "Temperature":      ("temperature", f"{vitals['temperature']}°C",       "36.0 – 38.0°C"),
        "Heart Rate":       ("heart_rate",  f"{vitals['heart_rate']} bpm",       "60 – 90 bpm"),
        "Respiratory Rate": ("respiratory_rate", f"{vitals['respiratory_rate']}/min", "12 – 20/min"),
        "Systolic BP":      ("sbp",         f"{vitals['sbp']} mmHg",             "100 – 140 mmHg"),
        "SpO2":             ("spo2",        f"{vitals['spo2']}%",                "≥ 95%"),
        "Mental Status":    (None,          vitals['mental_status'].title(),     "Alert"),
    }
    if vitals.get("dbp"):
        mapping["Diastolic BP"] = ("dbp", f"{vitals['dbp']} mmHg", "60 – 90 mmHg")
    if vitals.get("wbc"):
        mapping["WBC Count"] = ("wbc", f"{vitals['wbc']:,.0f} cells/µL", "4,000 – 12,000 cells/µL")
    if vitals.get("lactate"):
        mapping["Lactate"] = ("lactate", f"{vitals['lactate']} mmol/L", "< 2.0 mmol/L")
    if vitals.get("creatinine"):
        mapping["Creatinine"] = ("creatinine", f"{vitals['creatinine']} mg/dL", "< 1.2 mg/dL")

    for display_name, (field, display_val, normal_range) in mapping.items():
        if field is None:
            # Mental status
            ms = vitals['mental_status'].lower()
            status = "critical" if ms in ["unresponsive", "stuporous", "comatose"] \
                     else "warning" if ms in ALTERED_MENTAL_STATUS \
                     else "normal"
        else:
            status = get_vital_status(field, vitals.get(field, 0) or 0)

        summary[display_name] = {
            "value":        display_val,
            "raw":          vitals.get(field) if field else vitals['mental_status'],
            "status":       status,
            "normal_range": normal_range,
        }
    return summary


# ── SIRS SCORE ────────────────────────────────────────────────────────
def calculate_sirs(vitals: dict) -> dict:
    """
    SIRS Criteria (≥2 = SIRS positive):
    1. Temperature >38°C or <36°C
    2. Heart Rate >90 bpm
    3. Respiratory Rate >20/min
    4. WBC >12,000 or <4,000 cells/µL
    Returns score, met criteria list, and all criteria checklist.
    """
    score    = 0
    met      = []
    all_criteria = []

    temp = vitals["temperature"]
    hr   = vitals["heart_rate"]
    rr   = vitals["respiratory_rate"]
    wbc  = vitals.get("wbc")

    # Temperature
    temp_met = temp > 38.0 or temp < 36.0
    if temp_met:
        score += 1
        direction = "HIGH" if temp > 38.0 else "LOW"
        met.append({
            "criterion":   "Temperature",
            "value":       f"{temp}°C",
            "threshold":   ">38.0°C or <36.0°C",
            "direction":   direction,
            "clinical_note": f"Fever ({temp}°C)" if temp > 38.0 else f"Hypothermia ({temp}°C)"
        })
    all_criteria.append({
        "name": "Temperature >38.0°C or <36.0°C",
        "met":  temp_met,
        "value": f"{temp}°C",
        "points": 1 if temp_met else 0
    })

    # Heart Rate
    hr_met = hr > 90
    if hr_met:
        score += 1
        met.append({
            "criterion":   "Heart Rate",
            "value":       f"{hr} bpm",
            "threshold":   ">90 bpm",
            "direction":   "HIGH",
            "clinical_note": f"Tachycardia ({hr} bpm)"
        })
    all_criteria.append({
        "name": "Heart Rate >90 bpm",
        "met":  hr_met,
        "value": f"{hr} bpm",
        "points": 1 if hr_met else 0
    })

    # Respiratory Rate
    rr_met = rr > 20
    if rr_met:
        score += 1
        met.append({
            "criterion":   "Respiratory Rate",
            "value":       f"{rr}/min",
            "threshold":   ">20/min",
            "direction":   "HIGH",
            "clinical_note": f"Tachypnoea ({rr}/min)"
        })
    all_criteria.append({
        "name": "Respiratory Rate >20/min",
        "met":  rr_met,
        "value": f"{rr}/min",
        "points": 1 if rr_met else 0
    })

    # WBC
    if wbc is not None and wbc > 0:
        wbc_met = wbc > 12000 or wbc < 4000
        if wbc_met:
            score += 1
            direction = "HIGH" if wbc > 12000 else "LOW"
            note = f"Leukocytosis ({wbc:,.0f} cells/µL)" if wbc > 12000 \
                   else f"Leukopenia ({wbc:,.0f} cells/µL)"
            met.append({
                "criterion":   "WBC Count",
                "value":       f"{wbc:,.0f} cells/µL",
                "threshold":   ">12,000 or <4,000 cells/µL",
                "direction":   direction,
                "clinical_note": note
            })
        all_criteria.append({
            "name": "WBC >12,000 or <4,000 cells/µL",
            "met":  wbc_met,
            "value": f"{wbc:,.0f} cells/µL",
            "points": 1 if wbc_met else 0
        })

    return {
        "score":         score,
        "max_score":     4,
        "positive":      score >= 2,
        "met_criteria":  met,
        "all_criteria":  all_criteria,
        "interpretation": _interpret_sirs(score),
    }


def _interpret_sirs(score: int) -> str:
    if score == 0:
        return "No SIRS criteria met. Low systemic inflammatory response."
    elif score == 1:
        return "One SIRS criterion met. Subclinical inflammatory response. Monitor closely."
    elif score == 2:
        return "SIRS positive (2 criteria). Systemic inflammatory response present. Evaluate for infection source."
    elif score == 3:
        return "SIRS positive (3 criteria). Significant systemic inflammatory response. Urgent evaluation required."
    else:
        return "SIRS positive (4 criteria). Severe systemic inflammatory response. Immediate clinical assessment required."


# ── qSOFA SCORE ───────────────────────────────────────────────────────
def calculate_qsofa(vitals: dict) -> dict:
    """
    qSOFA Score (0–3, ≥2 = high risk for sepsis-related organ dysfunction):
    1. Respiratory Rate ≥22/min  (+1)
    2. Altered mental status      (+1)
    3. Systolic BP ≤100 mmHg     (+1)
    """
    score    = 0
    met      = []
    all_criteria = []

    rr     = vitals["respiratory_rate"]
    ms     = vitals["mental_status"].lower()
    sbp    = vitals["sbp"]
    altered = ms in ALTERED_MENTAL_STATUS

    # Respiratory Rate
    rr_met = rr >= 22
    if rr_met:
        score += 1
        met.append({
            "criterion":   "Respiratory Rate",
            "value":       f"{rr}/min",
            "threshold":   "≥22/min",
            "direction":   "HIGH",
            "clinical_note": f"Tachypnoea (RR {rr}/min) — reflects respiratory compensation"
        })
    all_criteria.append({
        "name": "Respiratory Rate ≥22/min",
        "met":  rr_met,
        "value": f"{rr}/min",
        "points": 1 if rr_met else 0
    })

    # Mental Status
    if altered:
        score += 1
        met.append({
            "criterion":   "Mental Status",
            "value":       vitals["mental_status"].title(),
            "threshold":   "Altered (GCS <15)",
            "direction":   "ALTERED",
            "clinical_note": f"Encephalopathy — {vitals['mental_status'].title()} (possible cerebral hypoperfusion)"
        })
    all_criteria.append({
        "name": "Altered mental status (GCS <15)",
        "met":  altered,
        "value": vitals["mental_status"].title(),
        "points": 1 if altered else 0
    })

    # Systolic BP
    sbp_met = sbp <= 100
    if sbp_met:
        score += 1
        met.append({
            "criterion":   "Systolic Blood Pressure",
            "value":       f"{sbp} mmHg",
            "threshold":   "≤100 mmHg",
            "direction":   "LOW",
            "clinical_note": f"Hypotension ({sbp} mmHg) — possible haemodynamic compromise"
        })
    all_criteria.append({
        "name": "Systolic BP ≤100 mmHg",
        "met":  sbp_met,
        "value": f"{sbp} mmHg",
        "points": 1 if sbp_met else 0
    })

    return {
        "score":         score,
        "max_score":     3,
        "positive":      score >= 2,
        "met_criteria":  met,
        "all_criteria":  all_criteria,
        "interpretation": _interpret_qsofa(score),
    }


def _interpret_qsofa(score: int) -> str:
    if score == 0:
        return "qSOFA negative. Low risk of sepsis-related organ dysfunction."
    elif score == 1:
        return "One qSOFA criterion met. Increased vigilance recommended. Reassess frequently."
    elif score == 2:
        return "qSOFA positive (2/3). High risk of sepsis-related organ dysfunction. Initiate sepsis workup."
    else:
        return "qSOFA maximum score (3/3). Very high risk of organ failure and mortality. Urgent intervention required."


# ── NEWS2 SCORE ───────────────────────────────────────────────────────
def calculate_news2(vitals: dict) -> dict:
    """
    National Early Warning Score 2 (NEWS2):
    Aggregate score from: RR, SpO2, Supplemental O2, SBP, HR, Temp, Consciousness
    Score 0-4: Low risk | 5-6: Medium risk | ≥7: High risk
    Any single parameter score ≥3: Urgent review
    """
    scores_breakdown = {}
    total = 0

    def lookup(table_key, value):
        for lo, hi, pts in NEWS2_RANGES[table_key]:
            if lo <= value <= hi:
                return pts
        return 0

    # Respiratory Rate
    rr_pts = lookup("respiratory_rate", vitals["respiratory_rate"])
    scores_breakdown["Respiratory Rate"] = {
        "value": f"{vitals['respiratory_rate']}/min", "points": rr_pts
    }
    total += rr_pts

    # SpO2
    spo2_pts = lookup("spo2_scale1", vitals["spo2"])
    scores_breakdown["SpO2"] = {
        "value": f"{vitals['spo2']}%", "points": spo2_pts
    }
    total += spo2_pts

    # Systolic BP
    sbp_pts = lookup("sbp", vitals["sbp"])
    scores_breakdown["Systolic BP"] = {
        "value": f"{vitals['sbp']} mmHg", "points": sbp_pts
    }
    total += sbp_pts

    # Heart Rate
    hr_pts = lookup("heart_rate", vitals["heart_rate"])
    scores_breakdown["Heart Rate"] = {
        "value": f"{vitals['heart_rate']} bpm", "points": hr_pts
    }
    total += hr_pts

    # Temperature
    temp_pts = lookup("temperature", vitals["temperature"])
    scores_breakdown["Temperature"] = {
        "value": f"{vitals['temperature']}°C", "points": temp_pts
    }
    total += temp_pts

    # Consciousness
    ms_key   = vitals["mental_status"].lower()
    con_pts  = NEWS2_CONSCIOUSNESS.get(ms_key, 0)
    scores_breakdown["Consciousness"] = {
        "value": vitals["mental_status"].title(), "points": con_pts
    }
    total += con_pts

    # Supplemental O2 (assume room air unless specified)
    o2_pts = 2 if vitals.get("on_supplemental_o2") else 0
    if o2_pts:
        scores_breakdown["Supplemental O2"] = {
            "value": "Yes", "points": o2_pts
        }
        total += o2_pts

    # Clinical risk classification
    max_single = max(v["points"] for v in scores_breakdown.values())
    if total >= 7 or max_single >= 3:
        risk = "HIGH"
        risk_action = "Urgent assessment by clinical team. Consider ICU."
    elif total >= 5:
        risk = "MEDIUM"
        risk_action = "Urgent review by nurse or doctor within 30 minutes."
    elif total >= 1:
        risk = "LOW"
        risk_action = "Continue routine monitoring. Reassess in 4–6 hours."
    else:
        risk = "LOW"
        risk_action = "Low risk. Routine monitoring every 4–8 hours."

    return {
        "total_score":       total,
        "max_score":         20,
        "risk_level":        risk,
        "risk_action":       risk_action,
        "scores_breakdown":  scores_breakdown,
        "highest_parameter": max_single,
        "interpretation":    _interpret_news2(total, max_single),
    }


def _interpret_news2(total: int, max_single: int) -> str:
    if total >= 7 or max_single >= 3:
        return f"NEWS2 HIGH risk (score {total}). Urgent clinical review required. Consider ICU/HDU referral."
    elif total >= 5:
        return f"NEWS2 MEDIUM risk (score {total}). Urgent ward-based review. Escalate to clinical team."
    elif total >= 1:
        return f"NEWS2 LOW risk (score {total}). Routine monitoring. Reassess at next scheduled interval."
    else:
        return f"NEWS2 score {total}. Physiologically stable. Continue routine observations."


# ── SEVERITY CLASSIFICATION ───────────────────────────────────────────
def classify_severity(vitals: dict, sirs: dict, qsofa: dict) -> str:
    """
    Composite severity classification using SIRS + qSOFA + clinical markers.
    """
    sbp     = vitals["sbp"]
    spo2    = vitals["spo2"]
    hr      = vitals["heart_rate"]
    ms      = vitals["mental_status"].lower()
    lactate = vitals.get("lactate")
    creat   = vitals.get("creatinine")

    # Organ dysfunction markers
    organ_dysfunction = (
        spo2 < 90 or
        sbp  < 90 or
        ms   in ["unresponsive", "stuporous", "comatose"] or
        hr   > 130 or
        (lactate  is not None and lactate  > 2.0) or
        (creat    is not None and creat    > 2.0)
    )

    # Septic shock: refractory hypotension + criteria
    septic_shock = (
        sbp < 90 and
        (sirs["score"] >= 2 or qsofa["score"] >= 2) and
        organ_dysfunction
    )

    if septic_shock:
        return "SEPTIC_SHOCK"
    elif (sirs["score"] >= 2 or qsofa["score"] >= 2) and organ_dysfunction:
        return "SEVERE_SEPSIS"
    elif sirs["score"] >= 2 or qsofa["score"] >= 2:
        return "SEPSIS_ALERT"
    elif sirs["score"] == 1 or qsofa["score"] == 1:
        return "SEPSIS_WATCH"
    else:
        return "NO_RISK"


# ── TREND ANALYSIS ────────────────────────────────────────────────────
def analyse_trends(current: dict, history: list) -> dict:
    """
    Compares current assessment with previous assessments
    for the same patient to detect deterioration patterns.
    """
    if not history:
        return {"has_trend": False, "trend_direction": "STABLE", "changes": [], "deteriorating": False}

    prev     = history[-1]
    prev_v   = prev.get("vitals", {})
    prev_sev = prev.get("severity_level", 1)
    curr_sev = current.get("severity_level", 1)

    changes = []
    vital_keys = [
        ("temperature",      "Temperature",      "°C",     0.5),
        ("heart_rate",       "Heart Rate",       " bpm",   10),
        ("respiratory_rate", "Respiratory Rate", "/min",   3),
        ("sbp",              "Systolic BP",      " mmHg",  10),
        ("spo2",             "SpO2",             "%",      2),
    ]

    for key, label, unit, threshold in vital_keys:
        curr_val = current.get("vitals", {}).get(key)
        prev_val = prev_v.get(key)
        if curr_val is None or prev_val is None:
            continue
        delta = curr_val - prev_val
        if abs(delta) >= threshold:
            direction = "↑" if delta > 0 else "↓"
            changes.append({
                "vital":     label,
                "previous":  f"{prev_val}{unit}",
                "current":   f"{curr_val}{unit}",
                "delta":     f"{direction} {abs(delta):.1f}{unit}",
                "concerning": _is_concerning_change(key, delta),
            })

    deteriorating = curr_sev > prev_sev
    improving     = curr_sev < prev_sev
    direction     = "DETERIORATING" if deteriorating else "IMPROVING" if improving else "STABLE"

    return {
        "has_trend":        True,
        "previous_severity": prev.get("severity_label", "Unknown"),
        "trend_direction":  direction,
        "severity_change":  curr_sev - prev_sev,
        "changes":          changes,
        "deteriorating":    deteriorating,
        "improving":        improving,
        "assessments_count": len(history) + 1,
        "time_since_last":  prev.get("timestamp", "Unknown"),
        "trend_note":       _build_trend_note(direction, changes),
    }


def _is_concerning_change(key: str, delta: float) -> bool:
    concerning = {
        "temperature":      delta > 0,
        "heart_rate":       delta > 0,
        "respiratory_rate": delta > 0,
        "sbp":              delta < 0,
        "spo2":             delta < 0,
    }
    return concerning.get(key, False)


def _build_trend_note(direction: str, changes: list) -> str:
    if direction == "DETERIORATING":
        return f"Patient condition is DETERIORATING. {len(changes)} vital sign(s) changed significantly since last assessment."
    elif direction == "IMPROVING":
        return f"Patient condition is IMPROVING. {len(changes)} vital sign(s) showed positive changes."
    else:
        concerning = [c for c in changes if c.get("concerning")]
        if concerning:
            return f"Condition STABLE overall, but {len(concerning)} concerning vital sign change(s) detected."
        return "Condition STABLE. No significant deterioration detected since last assessment."