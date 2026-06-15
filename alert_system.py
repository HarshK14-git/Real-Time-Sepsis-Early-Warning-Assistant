# ─────────────────────────────────────────────────────────────────────
# ALERT GENERATION SYSTEM
# Generates structured, prioritised clinical alerts
# ─────────────────────────────────────────────────────────────────────
from datetime import datetime
from config import SEVERITY_LEVELS, SEPSIS_BUNDLE


def generate_alerts(vitals: dict, sirs: dict, qsofa: dict,
                    news2: dict, severity_key: str) -> dict:
    """
    Generates a complete structured alert package including:
    - Primary alert (severity classification)
    - Individual vital sign alerts
    - Clinical flags (organ dysfunction markers)
    - Time-critical actions
    - Sepsis bundle checklist
    """
    config   = SEVERITY_LEVELS[severity_key]
    level    = config["level"]
    alerts   = []
    flags    = []

    # ── Individual vital sign alerts ──────────────────────────────────
    v = vitals

    # Temperature
    if v["temperature"] > 38.0:
        alerts.append(_mk_alert("Fever", f"{v['temperature']}°C",
                                ">38.0°C", "HIGH", level,
                                "Hyperthermia — possible infectious aetiology"))
    elif v["temperature"] < 36.0:
        alerts.append(_mk_alert("Hypothermia", f"{v['temperature']}°C",
                                "<36.0°C", "LOW", level,
                                "Hypothermia in sepsis is a poor prognostic sign"))

    # Heart Rate
    if v["heart_rate"] > 130:
        alerts.append(_mk_alert("Severe Tachycardia", f"{v['heart_rate']} bpm",
                                ">130 bpm", "CRITICAL", level,
                                "Severe tachycardia — haemodynamic compromise"))
        flags.append("Severe tachycardia (HR >130 bpm) — possible cardiogenic or distributive shock")
    elif v["heart_rate"] > 90:
        alerts.append(_mk_alert("Tachycardia", f"{v['heart_rate']} bpm",
                                ">90 bpm", "HIGH", level,
                                "Compensatory tachycardia — evaluate for sepsis or hypovolaemia"))

    # Respiratory Rate
    if v["respiratory_rate"] > 25:
        alerts.append(_mk_alert("Severe Tachypnoea", f"{v['respiratory_rate']}/min",
                                ">25/min", "CRITICAL", level,
                                "Severe respiratory distress — consider ABG and ICU review"))
        flags.append("Severe tachypnoea (RR >25/min) — possible respiratory failure")
    elif v["respiratory_rate"] >= 22:
        alerts.append(_mk_alert("Tachypnoea", f"{v['respiratory_rate']}/min",
                                "≥22/min (qSOFA)", "HIGH", level,
                                "Increased work of breathing — qSOFA criterion met"))
    elif v["respiratory_rate"] > 20:
        alerts.append(_mk_alert("Elevated Respiratory Rate", f"{v['respiratory_rate']}/min",
                                ">20/min (SIRS)", "MODERATE", level,
                                "Respiratory rate above normal — SIRS criterion met"))

    # Blood Pressure
    if v["sbp"] < 90:
        alerts.append(_mk_alert("Severe Hypotension", f"{v['sbp']} mmHg",
                                "<90 mmHg", "CRITICAL", level,
                                "Refractory hypotension — possible septic shock. Vasopressors may be required."))
        flags.append(f"Severe hypotension (SBP {v['sbp']} mmHg) — septic shock criteria")
    elif v["sbp"] <= 100:
        alerts.append(_mk_alert("Hypotension", f"{v['sbp']} mmHg",
                                "≤100 mmHg (qSOFA)", "HIGH", level,
                                "Hypotension — qSOFA criterion met. Fluid resuscitation indicated."))

    # SpO2
    if v["spo2"] < 90:
        alerts.append(_mk_alert("Critical Hypoxaemia", f"{v['spo2']}%",
                                "<90%", "CRITICAL", level,
                                "Critical hypoxaemia — immediate oxygen therapy. Consider intubation."))
        flags.append(f"Critical hypoxaemia (SpO2 {v['spo2']}%) — possible respiratory organ dysfunction")
    elif v["spo2"] < 95:
        alerts.append(_mk_alert("Hypoxaemia", f"{v['spo2']}%",
                                "<95%", "HIGH", level,
                                "Hypoxaemia — supplemental oxygen required. Monitor closely."))

    # Mental Status
    ms = v["mental_status"].lower()
    if ms == "unresponsive":
        alerts.append(_mk_alert("Unresponsive Patient", v["mental_status"].title(),
                                "Alert expected", "CRITICAL", level,
                                "No response to stimuli — immediate emergency review"))
        flags.append("Unresponsive — possible brain dysfunction from sepsis/shock")
    elif ms in ["confused", "lethargic"]:
        alerts.append(_mk_alert("Altered Mental Status", v["mental_status"].title(),
                                "Alert expected", "HIGH", level,
                                "Encephalopathy — possible CNS hypoperfusion or septic encephalopathy"))

    # WBC
    wbc = v.get("wbc")
    if wbc:
        if wbc > 12000:
            alerts.append(_mk_alert("Leukocytosis", f"{wbc:,.0f} cells/µL",
                                    ">12,000 cells/µL", "HIGH", level,
                                    "Elevated WBC — systemic infection or inflammatory response"))
        elif wbc < 4000:
            alerts.append(_mk_alert("Leukopenia", f"{wbc:,.0f} cells/µL",
                                    "<4,000 cells/µL", "HIGH", level,
                                    "Low WBC — immunocompromised or overwhelming sepsis"))

    # Lactate
    lactate = v.get("lactate")
    if lactate:
        if lactate >= 4.0:
            alerts.append(_mk_alert("Critical Hyperlactataemia", f"{lactate} mmol/L",
                                    "≥4.0 mmol/L", "CRITICAL", level,
                                    "Lactate ≥4 mmol/L — septic shock criteria. Tissue hypoperfusion."))
            flags.append(f"Critical lactate ({lactate} mmol/L) — septic shock metabolic criterion")
        elif lactate >= 2.0:
            alerts.append(_mk_alert("Elevated Lactate", f"{lactate} mmol/L",
                                    "≥2.0 mmol/L", "HIGH", level,
                                    "Elevated lactate — possible tissue hypoperfusion. Remeasure after resuscitation."))

    # Creatinine
    creat = v.get("creatinine")
    if creat and creat > 1.2:
        note = "Acute Kidney Injury suspected" if creat > 2.0 else "Creatinine elevated — renal monitoring required"
        priority = "CRITICAL" if creat > 2.0 else "HIGH"
        alerts.append(_mk_alert("Elevated Creatinine", f"{creat} mg/dL",
                                ">1.2 mg/dL", priority, level, note))
        if creat > 2.0:
            flags.append(f"Acute kidney injury suspected (creatinine {creat} mg/dL)")

    # ── SIRS / qSOFA combined alert ───────────────────────────────────
    if sirs["positive"] and qsofa["positive"]:
        alerts.append(_mk_alert("SIRS + qSOFA Positive",
                                f"SIRS {sirs['score']}/4, qSOFA {qsofa['score']}/3",
                                "Both ≥2", "CRITICAL", level,
                                "Both SIRS and qSOFA criteria met — high probability of sepsis with organ dysfunction"))
    elif sirs["positive"]:
        alerts.append(_mk_alert("SIRS Criteria Met",
                                f"SIRS Score {sirs['score']}/4",
                                "≥2 criteria", "HIGH", level,
                                "Systemic Inflammatory Response Syndrome confirmed"))
    elif qsofa["positive"]:
        alerts.append(_mk_alert("qSOFA Criteria Met",
                                f"qSOFA Score {qsofa['score']}/3",
                                "≥2 criteria", "HIGH", level,
                                "qSOFA positive — increased risk of sepsis-related organ dysfunction"))

    # ── High NEWS2 ────────────────────────────────────────────────────
    news2_total = news2.get("total_score", 0)
    if news2_total >= 7:
        alerts.append(_mk_alert("NEWS2 High Risk",
                                f"Score {news2_total}/20",
                                "Threshold: ≥7", "CRITICAL", level,
                                "NEWS2 high risk — urgent clinical review and possible ICU referral required"))
    elif news2_total >= 5:
        alerts.append(_mk_alert("NEWS2 Medium Risk",
                                f"Score {news2_total}/20",
                                "Threshold: ≥5", "HIGH", level,
                                "NEWS2 medium risk — urgent ward-based review within 30 minutes"))

    # Sort by priority level
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MODERATE": 2, "LOW": 3}
    alerts.sort(key=lambda x: priority_order.get(x["priority"], 4))

    # ── Sepsis bundle checklist ───────────────────────────────────────
    bundle = _build_bundle_checklist(severity_key)

    return {
        "total_alerts":         len(alerts),
        "critical_count":       sum(1 for a in alerts if a["priority"] == "CRITICAL"),
        "high_count":           sum(1 for a in alerts if a["priority"] == "HIGH"),
        "alerts":               alerts,
        "organ_dysfunction_flags": flags,
        "organ_dysfunction_present": len(flags) > 0,
        "bundle_checklist":     bundle,
        "alert_generated_at":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "response_time_required": config["response_time"],
        "priority":             config["priority"],
    }


def _mk_alert(name: str, value: str, threshold: str, priority: str,
              sev_level: int, note: str) -> dict:
    priority_icons = {
        "CRITICAL": "🔴", "HIGH": "🟠", "MODERATE": "🟡", "LOW": "🟢"
    }
    return {
        "alert_name":   name,
        "value":        value,
        "threshold":    threshold,
        "priority":     priority,
        "priority_icon": priority_icons.get(priority, "⚪"),
        "clinical_note": note,
        "requires_action": priority in ["CRITICAL", "HIGH"],
    }


def _build_bundle_checklist(severity_key: str) -> dict:
    if severity_key in ["NO_RISK", "SEPSIS_WATCH"]:
        return {"applicable": False, "bundle_type": None, "items": []}

    items = []
    if severity_key in ["SEPSIS_ALERT", "SEVERE_SEPSIS", "SEPTIC_SHOCK"]:
        for task in SEPSIS_BUNDLE["1_hour_bundle"]:
            items.append({"task": task, "completed": False, "time_target": "Within 1 hour"})

    return {
        "applicable":  True,
        "bundle_type": "1-Hour Sepsis Bundle (Surviving Sepsis Campaign)",
        "items":       items,
        "guideline":   "Based on Surviving Sepsis Campaign International Guidelines 2021",
    }