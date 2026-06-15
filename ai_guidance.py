# ─────────────────────────────────────────────────────────────────────
# AI CLINICAL GUIDANCE MODULE
# Groq API integration for personalised clinical insights
# ─────────────────────────────────────────────────────────────────────
import re

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# ── PASTE YOUR GROQ API KEY HERE ──────────────────────────────────────
API_KEY = "paste your api key here"


def get_ai_clinical_insight(assessment: dict) -> dict:
    """
    Generates a personalised AI clinical narrative using Llama 3.1.
    Returns structured insight with narrative, risk_factors, and
    recommended_focus areas.
    """
    if not GROQ_AVAILABLE or not API_KEY or "paste" in API_KEY:
        return {
            "available": False,
            "reason": "AI guidance unavailable — API key not configured.",
            "narrative": None,
            "risk_factors": [],
            "recommended_focus": []
        }

    try:
        client = Groq(api_key=API_KEY)
        v       = assessment.get("vitals", {})
        sirs    = assessment.get("sirs", {})
        qsofa   = assessment.get("qsofa", {})
        news2   = assessment.get("news2", {})

        sirs_met  = [c["criterion"] for c in sirs.get("met_criteria", [])]
        qsofa_met = [c["criterion"] for c in qsofa.get("met_criteria", [])]
        flags     = assessment.get("alerts", {}).get("organ_dysfunction_flags", [])

        prompt = f"""You are a clinical decision support AI embedded in a hospital sepsis 
early warning system. Provide a concise, specific, actionable clinical insight for the 
following patient assessment. Be direct and clinical. Do not be generic.

PATIENT: {assessment.get('patient_name','Unknown')}, {assessment.get('ward','Unknown Ward')}
SEVERITY: {assessment.get('severity_label','')}

VITAL SIGNS:
- Temperature: {v.get('temperature')}°C
- Heart Rate: {v.get('heart_rate')} bpm
- Respiratory Rate: {v.get('respiratory_rate')}/min
- Systolic BP: {v.get('sbp')} mmHg
- SpO2: {v.get('spo2')}%
- Mental Status: {v.get('mental_status','')}
{f"- WBC: {v.get('wbc'):,.0f} cells/µL" if v.get('wbc') else ""}
{f"- Lactate: {v.get('lactate')} mmol/L" if v.get('lactate') else ""}
{f"- Creatinine: {v.get('creatinine')} mg/dL" if v.get('creatinine') else ""}

SCORES:
- SIRS Score: {sirs.get('score',0)}/4 ({"POSITIVE" if sirs.get('positive') else "negative"}) — Criteria met: {', '.join(sirs_met) if sirs_met else 'None'}
- qSOFA Score: {qsofa.get('score',0)}/3 ({"POSITIVE" if qsofa.get('positive') else "negative"}) — Criteria met: {', '.join(qsofa_met) if qsofa_met else 'None'}
- NEWS2 Score: {news2.get('total_score',0)}/20 ({news2.get('risk_level','LOW')} risk)
{f"ORGAN DYSFUNCTION: {'; '.join(flags)}" if flags else ""}

Respond in this EXACT JSON format with no other text:
{{
  "narrative": "2-3 sentence clinical summary specific to these exact vitals. Explain the most concerning finding and why.",
  "risk_factors": ["specific risk factor 1", "specific risk factor 2", "specific risk factor 3"],
  "recommended_focus": ["single most important next action", "second priority action", "monitoring parameter to watch"],
  "clinical_reasoning": "1 sentence explaining the scoring rationale for this severity classification",
  "disclaimer": "⚕️ Clinical decision support tool only. Follow institutional protocols and clinical judgment."
}}"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.2
        )

        raw  = response.choices[0].message.content.strip()
        data = _extract_json(raw)

        if data:
            return {
                "available":          True,
                "narrative":          data.get("narrative", ""),
                "risk_factors":       data.get("risk_factors", []),
                "recommended_focus":  data.get("recommended_focus", []),
                "clinical_reasoning": data.get("clinical_reasoning", ""),
                "disclaimer":         data.get("disclaimer", "⚕️ Clinical decision support tool only."),
                "model_used":         "llama-3.1-8b-instant",
            }

        return {"available": True, "narrative": raw, "risk_factors": [], "recommended_focus": []}

    except Exception as e:
        print(f"AI guidance error: {e}")
        return {
            "available": False,
            "reason":    f"AI service error: {str(e)}",
            "narrative": None,
            "risk_factors": [],
            "recommended_focus": []
        }


def _extract_json(text: str) -> dict | None:
    import json

    # Method 1: Direct parse
    try:
        return json.loads(text)
    except Exception:
        pass

    # Method 2: Extract from ```json blocks
    try:
        m = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if m:
            return json.loads(m.group(1).strip())
    except Exception:
        pass

    # Method 3: Find JSON object
    try:
        m = re.search(r'\{.*\}', text, re.DOTALL)
        if m:
            return json.loads(m.group(0))
    except Exception:
        pass

    return None