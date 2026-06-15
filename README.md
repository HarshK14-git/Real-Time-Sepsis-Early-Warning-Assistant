# SepsisAI: Real-Time Sepsis Early Warning Assistant

Python Flask Groq AI Chart.js Bootstrap 5

## Project Abstract

The **Real-Time Sepsis Early Warning Assistant (SepsisAI)** is an AI-powered Clinical Decision Support System (CDSS) designed to help healthcare professionals rapidly identify, assess, and respond to sepsis in real time. The platform continuously evaluates patient vital signs using clinically validated scoring methodologies including **SIRS (Systemic Inflammatory Response Syndrome)**, **qSOFA (Quick Sequential Organ Failure Assessment)**, and **NEWS2 (National Early Warning Score 2)** to detect early signs of patient deterioration.

Instead of relying solely on manual interpretation of vital signs, the system automatically calculates risk scores, classifies patient severity levels, generates intelligent clinical alerts, and provides AI-powered recommendations using the **Groq API**. The application also includes patient history tracking, trend analytics, severity progression monitoring, and a real-time ward dashboard to support timely clinical decision-making and improve patient outcomes.

---

## Key Features

### Patient Assessment & Intake

* Structured patient assessment form
* Demographic and clinical data collection
* Real-time validation and error handling
* Assessment timestamp tracking

### Clinical Scoring Engine

* SIRS Score Calculation
* qSOFA Score Calculation
* NEWS2 Risk Assessment
* Automated clinical evaluation

### Severity Classification

Automatically classifies patients into:

* No Risk 🟢
* Sepsis Watch 🟡
* Sepsis Alert 🟠
* Severe Sepsis 🔴
* Septic Shock 🟥

### AI Clinical Guidance

Powered by **Groq API (Llama 3.1)**

Generates:

* Clinical Summary
* Triggering Factors
* Risk Explanation
* Alert Messages
* Immediate Actions
* Escalation Recommendations

### Real-Time Alert Management

* Risk-based alert generation
* Priority classification
* Critical patient identification
* Actionable recommendations

### Patient History & Trend Tracking

* Historical assessment retrieval
* Vital sign trend visualization
* Severity progression tracking
* Risk trend analytics

### Real-Time Ward Dashboard

* Total Patients
* Active Alerts
* High-Risk Patients
* Critical Cases
* Severity Distribution
* Recent Assessments
* Search & Filtering

### Data Export

* CSV export support
* Historical data review
* Patient record management

---

## Tech Stack

### Backend

* Python
* Flask
* Flask-CORS

### AI / Clinical Intelligence

* Groq API
* Llama 3.1 8B Instant

### Frontend

* HTML5
* CSS3
* Bootstrap 5
* Vanilla JavaScript

### Data Visualization

* Chart.js

### Database

* JSON-Based Storage (patients.json)

### Analytics

* Patient Trend Analysis
* Severity Progression Monitoring
* Clinical Risk Visualization

---

## Project Structure

```text
sepsis-early-warning/
│
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── sepsis_engine.py
│   ├── alert_system.py
│   ├── ai_guidance.py
│   ├── patient_store.py
│   └── patients.json
│
├── frontend/
│   ├── index.html
│   │
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       └── app.js
│
├── requirements.txt
│
└── README.md
```

### Backend Components

#### app.py

Flask application responsible for:

* REST API endpoints
* Request validation
* Assessment processing
* Dashboard services

#### sepsis_engine.py

Clinical scoring implementation:

* SIRS Assessment
* qSOFA Assessment
* NEWS2 Assessment

#### alert_system.py

Risk classification and alert generation:

* Severity Mapping
* Priority Assignment
* Alert Logic

#### ai_guidance.py

Groq AI integration:

* Clinical Summaries
* Risk Explanations
* Recommendations
* Alert Narratives

#### patient_store.py

Patient management layer:

* Patient Records
* Assessment History
* Dashboard Analytics
* Trend Calculations

#### patients.json

Local patient database storing:

* Demographics
* Vital Signs
* Clinical Scores
* Severity Levels
* AI Outputs
* Historical Assessments

---

## Clinical Assessment Workflow

1. Patient Assessment Submission
2. Clinical Data Validation
3. SIRS Score Calculation
4. qSOFA Score Calculation
5. NEWS2 Score Calculation
6. Severity Classification
7. AI Clinical Analysis
8. Alert Generation
9. Data Storage
10. Dashboard Update
11. Trend Analytics Generation

---

## Severity Levels

| Level | Classification |
| ----- | -------------- |
| 1     | No Risk        |
| 2     | Sepsis Watch   |
| 3     | Sepsis Alert   |
| 4     | Severe Sepsis  |
| 5     | Septic Shock   |

---

## API Endpoints

### Health Check

GET /api/health

### New Assessment

POST /api/assess

### Dashboard Statistics

GET /api/dashboard

### Patient Records

GET /api/patients

### Single Patient History

GET /api/patient/<patient_id>

### Active Alerts

GET /api/alerts

### Export Data

GET /api/export/csv

### Clear Database

DELETE /api/patients

---

## Dashboard Features

### Overview Cards

* Total Patients
* High-Risk Patients
* Active Alerts
* Critical Cases
* Average SIRS
* Average qSOFA
* Average NEWS2

### Analytics

* Severity Distribution
* Risk Overview
* Trend Analysis
* Patient Progression

### Patient Management

* Search Patients
* View History
* Export Records
* Monitor Alerts

---

## Future Enhancements

* Electronic Health Record (EHR) Integration
* HL7/FHIR Compatibility
* Predictive Machine Learning Models
* Mobile Application
* SMS & Email Notifications
* Cloud Deployment
* Multi-Hospital Monitoring
* Real-Time ICU Integration

---

## Project Goal

The goal of SepsisAI is to demonstrate how Artificial Intelligence, Clinical Informatics, and Real-Time Analytics can be combined to support early sepsis detection, improve response times, assist healthcare professionals, and ultimately improve patient outcomes through intelligent clinical decision support.
