# ─────────────────────────────────────────────────────────────────────
# FLASK REST API — REAL-TIME SEPSIS EARLY WARNING ASSISTANT
# ─────────────────────────────────────────────────────────────────────
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import json
import traceback
from datetime import datetime

from sepsis_engine  import (calculate_sirs, calculate_qsofa,
                             calculate_news2, classify_severity,
                             build_vital_summary, analyse_trends)
from alert_system   import generate_alerts
from ai_guidance    import get_ai_clinical_insight
from patient_store  import (load_all, save_assessment, get_patient_history,
                             clear_all, compute_stats, to_csv, build_dashboard)
from config         import SEVERITY_LEVELS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


# ─────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────
def parse_vitals(data: dict) -> dict:
    """Validates and parses incoming vitals from request JSON."""
    required = ["temperature", "heart_rate", "respiratory_rate", "sbp", "spo2"]
    missing  = [f for f in required if not data.get(f)]
    if missing:
        raise ValueError(f"Missing required vital signs: {', '.join(missing)}")

    vitals = {
        "temperature":      float(data["temperature"]),
        "heart_rate":       int(data["heart_rate"]),
        "respiratory_rate": int(data["respiratory_rate"]),
        "sbp":              int(data["sbp"]),
        "spo2":             float(data["spo2"]),
        "mental_status":    data.get("mental_status", "Alert"),
        "dbp":              int(data["dbp"])        if data.get("dbp")         else None,
        "wbc":              float(data["wbc"])      if data.get("wbc")         else None,
        "lactate":          float(data["lactate"])  if data.get("lactate")     else None,
        "creatinine":       float(data["creatinine"]) if data.get("creatinine") else None,
        "on_supplemental_o2": bool(data.get("on_supplemental_o2", False)),
    }

    # Basic range validation
    if not (25 <= vitals["temperature"] <= 45):
        raise ValueError("Temperature must be between 25°C and 45°C")
    if not (20 <= vitals["heart_rate"] <= 300):
        raise ValueError("Heart rate must be between 20 and 300 bpm")
    if not (5 <= vitals["respiratory_rate"] <= 70):
        raise ValueError("Respiratory rate must be between 5 and 70/min")
    if not (50 <= vitals["sbp"] <= 250):
        raise ValueError("Systolic BP must be between 50 and 250 mmHg")
    if not (50 <= vitals["spo2"] <= 100):
        raise ValueError("SpO2 must be between 50 and 100%")

    return vitals


# ─────────────────────────────────────────────────────────────────────
# ENDPOINT 1: ASSESS PATIENT — Core function
# POST /api/assess
# ─────────────────────────────────────────────────────────────────────
@app.route("/api/assess", methods=["POST", "OPTIONS"])
def assess():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    try:
        data = request.json or {}

        # Parse and validate
        try:
            vitals = parse_vitals(data)
        except ValueError as e:
            return jsonify({"error": str(e), "type": "validation_error"}), 400

        patient_name = data.get("patient_name", "Unknown Patient").strip() or "Unknown Patient"
        patient_id   = data.get("patient_id",   "N/A").strip()             or "N/A"
        ward         = data.get("ward",          "General Ward").strip()    or "General Ward"
        nurse_id     = data.get("nurse_id",      "").strip()

        # Run all scoring algorithms
        sirs   = calculate_sirs(vitals)
        qsofa  = calculate_qsofa(vitals)
        news2  = calculate_news2(vitals)

        # Classify severity
        severity_key = classify_severity(vitals, sirs, qsofa)
        config       = SEVERITY_LEVELS[severity_key]

        # Build vital summary (with normal/warning/critical status per vital)
        vital_summary = build_vital_summary(vitals)

        # Generate alerts
        alerts = generate_alerts(vitals, sirs, qsofa, news2, severity_key)

        # Trend analysis against patient's previous assessments
        patient_history = get_patient_history(patient_id)
        trend           = analyse_trends(
            {"vitals": vitals, "severity_level": config["level"]},
            patient_history
        )

        # Build full assessment record
        assessment = {
            "assessment_id":    f"SEP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp":        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "patient_name":     patient_name,
            "patient_id":       patient_id,
            "ward":             ward,
            "nurse_id":         nurse_id,
            "vitals":           vitals,
            "vital_summary":    vital_summary,
            "sirs":             sirs,
            "qsofa":            qsofa,
            "news2":            news2,
            "severity":         severity_key,
            "severity_label":   config["label"],
            "severity_level":   config["level"],
            "severity_color":   config["color"],
            "severity_bg":      config["bg_color"],
            "severity_icon":    config["icon"],
            "priority":         config["priority"],
            "response_time":    config["response_time"],
            "message":          config["message"],
            "immediate_actions":config["immediate_actions"],
            "investigations":   config["investigations"],
            "escalation":       config["escalation"],
            "alerts":           alerts,
            "trend_analysis":   trend,
        }

        # Add AI guidance
        ai_guidance = get_ai_clinical_insight(assessment)
        assessment["ai_guidance"] = ai_guidance

        # Persist
        save_assessment(assessment)

        print(f"[ASSESS] {patient_name} ({patient_id}) → {config['label']} "
              f"| SIRS:{sirs['score']} qSOFA:{qsofa['score']} NEWS2:{news2['total_score']}")

        return jsonify({"success": True, "assessment": assessment}), 200

    except Exception as e:
        print(f"[ERROR] /api/assess → {e}")
        print(traceback.format_exc())
        return jsonify({"error": str(e), "type": "server_error"}), 500


# ─────────────────────────────────────────────────────────────────────
# ENDPOINT 2: GET ALL PATIENTS + STATS
# GET /api/patients?limit=50&severity=SEPSIS_ALERT
# ─────────────────────────────────────────────────────────────────────
@app.route("/api/patients", methods=["GET"])
def get_patients():
    try:
        records   = load_all()
        limit     = int(request.args.get("limit", 100))
        severity  = request.args.get("severity", "")
        patient_q = request.args.get("patient", "").lower()

        # Filter
        filtered = records
        if severity:
            filtered = [r for r in filtered if r.get("severity") == severity]
        if patient_q:
            filtered = [r for r in filtered
                        if patient_q in r.get("patient_name", "").lower()
                        or patient_q in r.get("patient_id", "").lower()]

        # Sort newest first, apply limit
        filtered = list(reversed(filtered))[:limit]

        stats = compute_stats(records)
        return jsonify({
            "patients":     filtered,
            "stats":        stats,
            "total_filtered": len(filtered),
            "total_all":    len(records),
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────
# ENDPOINT 3: GET SINGLE PATIENT WITH FULL HISTORY + TRENDS
# GET /api/patient/<patient_id>
# ─────────────────────────────────────────────────────────────────────
@app.route("/api/patient/<patient_id>", methods=["GET"])
def get_patient(patient_id: str):
    try:
        history = get_patient_history(patient_id)
        if not history:
            return jsonify({"error": f"No records found for patient ID: {patient_id}"}), 404

        latest   = history[-1]
        previous = history[:-1]

        # Vital sign trend data
        vitals_timeline = []
        for rec in history:
            v = rec.get("vitals", {})
            vitals_timeline.append({
                "timestamp":      rec.get("timestamp", ""),
                "temperature":    v.get("temperature"),
                "heart_rate":     v.get("heart_rate"),
                "respiratory_rate": v.get("respiratory_rate"),
                "sbp":            v.get("sbp"),
                "spo2":           v.get("spo2"),
                "sirs_score":     rec.get("sirs", {}).get("score", 0),
                "qsofa_score":    rec.get("qsofa", {}).get("score", 0),
                "news2_score":    rec.get("news2", {}).get("total_score", 0),
                "severity_level": rec.get("severity_level", 1),
                "severity_label": rec.get("severity_label", ""),
            })

        # Severity progression
        severity_history = [
            {"timestamp": r.get("timestamp",""), "severity": r.get("severity",""),
             "label": r.get("severity_label",""), "level": r.get("severity_level",1)}
            for r in history
        ]

        # Detect overall trend direction
        if len(history) >= 2:
            first_level = history[0].get("severity_level", 1)
            last_level  = history[-1].get("severity_level", 1)
            if last_level > first_level:
                overall_trend = "DETERIORATING"
            elif last_level < first_level:
                overall_trend = "IMPROVING"
            else:
                overall_trend = "STABLE"
        else:
            overall_trend = "INSUFFICIENT_DATA"

        return jsonify({
            "patient_id":       patient_id,
            "patient_name":     latest.get("patient_name", ""),
            "ward":             latest.get("ward", ""),
            "total_assessments": len(history),
            "latest_assessment": latest,
            "previous_assessments": list(reversed(previous)),
            "vitals_timeline":  vitals_timeline,
            "severity_history": severity_history,
            "overall_trend":    overall_trend,
            "first_assessed":   history[0].get("timestamp", "") if history else "",
            "last_assessed":    history[-1].get("timestamp", "") if history else "",
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────
# ENDPOINT 4: ACTIVE ALERTS — High-risk patients summary
# GET /api/alerts
# ─────────────────────────────────────────────────────────────────────
@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    try:
        records    = load_all()
        high_risk  = [r for r in records if r.get("severity_level", 0) >= 3]

        # Deduplicate — keep only the latest assessment per patient
        seen     = {}
        for rec in reversed(high_risk):
            pid = rec.get("patient_id", rec.get("assessment_id"))
            if pid not in seen:
                seen[pid] = rec

        active_alerts = list(reversed(list(seen.values())))

        return jsonify({
            "total_active_alerts": len(active_alerts),
            "critical":  sum(1 for r in active_alerts if r.get("severity_level",0) >= 4),
            "severe":    sum(1 for r in active_alerts if r.get("severity_level",0) == 3),
            "alerts":    active_alerts,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────
# ENDPOINT 5: DASHBOARD STATISTICS
# GET /api/dashboard
# ─────────────────────────────────────────────────────────────────────
@app.route("/api/dashboard", methods=["GET"])
def dashboard():
    try:
        records = load_all()
        data    = build_dashboard(records)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────
# ENDPOINT 6: EXPORT CSV
# GET /api/export/csv
# ─────────────────────────────────────────────────────────────────────
@app.route("/api/export/csv", methods=["GET"])
def export_csv():
    try:
        records = load_all()
        if not records:
            return jsonify({"error": "No records to export"}), 404

        csv_content = to_csv(records)
        filename    = f"sepsis_assessments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        return Response(
            csv_content,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────
# ENDPOINT 7: CLEAR ALL RECORDS
# DELETE /api/patients
# ─────────────────────────────────────────────────────────────────────
@app.route("/api/patients", methods=["DELETE", "OPTIONS"])
def delete_all():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    try:
        clear_all()
        return jsonify({"message": "All patient records cleared successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────
# ENDPOINT 8: HEALTH CHECK
# GET /api/health
# ─────────────────────────────────────────────────────────────────────
@app.route("/api/health", methods=["GET"])
def health():
    records = load_all()
    stats   = compute_stats(records)
    return jsonify({
        "status":    "healthy",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_records": stats["total"],
        "high_risk_count": stats["high_risk"],
        "algorithms": ["SIRS", "qSOFA", "NEWS2"],
        "severity_tiers": 5,
        "ai_guidance": "enabled" if "paste" not in __import__('ai_guidance').API_KEY else "key_not_set",
    }), 200


if __name__ == "__main__":
    print("=" * 60)
    print("  Real-Time Sepsis Early Warning Assistant")
    print("  Backend API — Starting on port 5000")
    print("=" * 60)
    print()
    print("  Endpoints available:")
    print("  POST   /api/assess          → Submit vitals, get assessment")
    print("  GET    /api/patients        → All patients + stats")
    print("  GET    /api/patient/<id>    → Single patient + trend history")
    print("  GET    /api/alerts          → Active high-risk alerts")
    print("  GET    /api/dashboard       → Dashboard statistics")
    print("  GET    /api/export/csv      → Export CSV for Google Sheets")
    print("  DELETE /api/patients        → Clear all records")
    print("  GET    /api/health          → System health check")
    print()
    app.run(debug=True, port=5000)