// ======================================================
// REAL-TIME SEPSIS EARLY WARNING ASSISTANT
// APP.JS - PART 1
// Core Configuration + Dashboard Engine
// ======================================================

// ======================================================
// CONFIG
// ======================================================

const API_BASE = "http://127.0.0.1:5000/api";

const AUTO_REFRESH_INTERVAL = 30000;

// ======================================================
// GLOBAL STATE
// ======================================================

const AppState = {

    dashboard: null,

    patients: [],

    alerts: [],

    currentPatient: null,

    severityChart: null,

    riskChart: null,

    heartRateChart: null,

    respiratoryChart: null,

    spo2Chart: null,

    severityTrendChart: null
};

// ======================================================
// DOM ELEMENTS
// ======================================================

const loader = document.getElementById("loader");

const totalPatients =
    document.getElementById("totalPatients");

const highRiskPatients =
    document.getElementById("highRiskPatients");

const criticalPatients =
    document.getElementById("criticalPatients");

const avgSirs =
    document.getElementById("avgSirs");

const avgQsofa =
    document.getElementById("avgQsofa");

const avgNews2 =
    document.getElementById("avgNews2");

const exportCsvBtn =
    document.getElementById("exportCsvBtn");

const refreshDashboardBtn =
    document.getElementById("refreshDashboardBtn");

// ======================================================
// LOADER
// ======================================================

function showLoader() {

    if(loader){

        loader.style.display = "flex";
    }
}

function hideLoader() {

    if(loader){

        loader.style.display = "none";
    }
}

// ======================================================
// TOAST SYSTEM
// ======================================================

function showToast(
    title,
    message,
    type = "info"
){

    const toast = document.createElement("div");

    toast.className =
        `toast-container-custom ${type}`;

    toast.innerHTML = `
        <div class="toast-title">
            ${title}
        </div>

        <div class="toast-message">
            ${message}
        </div>
    `;

    document.body.appendChild(toast);

    setTimeout(() => {

        toast.classList.add("show");

    }, 100);

    setTimeout(() => {

        toast.classList.remove("show");

        setTimeout(() => {

            toast.remove();

        }, 500);

    }, 4000);
}

// ======================================================
// API CLIENT
// ======================================================

class ApiClient {

    static async get(endpoint){

        try{

            const response =
                await fetch(
                    `${API_BASE}${endpoint}`
                );

            if(!response.ok){

                throw new Error(
                    `HTTP ${response.status}`
                );
            }

            return await response.json();

        }
        catch(error){

            console.error(error);

            showToast(
                "API Error",
                error.message,
                "danger"
            );

            throw error;
        }
    }

    static async post(
        endpoint,
        payload
    ){

        try{

            const response =
                await fetch(
                    `${API_BASE}${endpoint}`,
                    {
                        method:"POST",

                        headers:{
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(payload)
                    }
                );

            const data =
                await response.json();

            if(!response.ok){

                throw new Error(
                    data.error ||
                    "Unknown Error"
                );
            }

            return data;

        }
        catch(error){

            console.error(error);

            showToast(
                "Request Failed",
                error.message,
                "danger"
            );

            throw error;
        }
    }

    static async delete(endpoint){

        try{

            const response =
                await fetch(
                    `${API_BASE}${endpoint}`,
                    {
                        method:"DELETE"
                    }
                );

            return await response.json();

        }
        catch(error){

            console.error(error);

            throw error;
        }
    }
}

// ======================================================
// DASHBOARD LOADING
// ======================================================

async function loadDashboard(){

    try{

        showLoader();

        const dashboard =
            await ApiClient.get(
                "/dashboard"
            );

        AppState.dashboard =
            dashboard;

        populateDashboardStats(
            dashboard
        );

        buildSeverityChart(
            dashboard
        );

        buildRiskChart(
            dashboard
        );

        hideLoader();

    }
    catch(error){

        hideLoader();

        console.error(error);
    }
}

// ======================================================
// POPULATE KPI CARDS
// ======================================================

function populateDashboardStats(
    dashboard
){

    const stats =
        dashboard.stats || {};

    totalPatients.textContent =
        stats.unique_patients || 0;

    highRiskPatients.textContent =
        stats.high_risk || 0;

    criticalPatients.textContent =
        (
            stats.severe || 0
        ) +
        (
            stats.shock || 0
        );

    avgSirs.textContent =
        stats.avg_sirs || 0;

    avgQsofa.textContent =
        stats.avg_qsofa || 0;

    avgNews2.textContent =
        stats.avg_news2 || 0;

    console.log(
        "Unique Patients:",
        stats.unique_patients
    );

    console.log(
        "Total Assessments:",
        stats.total
    );
}

// ======================================================
// SEVERITY CHART
// ======================================================

function buildSeverityChart(
    dashboard
){

    const ctx =
        document
        .getElementById(
            "severityChart"
        );

    if(!ctx) return;

    if(
        AppState.severityChart
    ){

        AppState
            .severityChart
            .destroy();
    }

    const distribution =
        dashboard
        .severity_distribution;

    AppState.severityChart =
        new Chart(
            ctx,
            {

                type:"doughnut",

                data:{

                    labels:
                        distribution.map(
                            d => d.severity
                        ),

                    datasets:[{

                        data:
                            distribution.map(
                                d => d.count
                            ),

                        backgroundColor:
                            distribution.map(
                                d => d.color
                            )
                    }]
                },

                options:{

                    responsive:true,

                    plugins:{

                        legend:{
                            position:"bottom"
                        }
                    }
                }
            }
        );
}

// ======================================================
// RISK CHART
// ======================================================

function buildRiskChart(
    dashboard
){

    const ctx =
        document
        .getElementById(
            "riskChart"
        );

    if(!ctx) return;

    if(
        AppState.riskChart
    ){

        AppState
            .riskChart
            .destroy();
    }

    const stats =
        dashboard.stats;

    AppState.riskChart =
        new Chart(
            ctx,
            {

                type:"bar",

                data:{

                    labels:[
                        "No Risk",
                        "Watch",
                        "Alert",
                        "Severe",
                        "Shock"
                    ],

                    datasets:[{

                        label:
                            "Patients",

                        data:[
                            stats.no_risk,
                            stats.watch,
                            stats.alert,
                            stats.severe,
                            stats.shock
                        ]
                    }]
                },

                options:{

                    responsive:true,

                    scales:{

                        y:{
                            beginAtZero:true
                        }
                    }
                }
            }
        );
}

// ======================================================
// EXPORT CSV
// ======================================================

function exportCSV(){

    window.open(
        `${API_BASE}/export/csv`,
        "_blank"
    );
}

// ======================================================
// HEALTH CHECK
// ======================================================

async function checkBackendHealth(){

    try{

        const health =
            await ApiClient.get(
                "/health"
            );

        console.log(
            "Backend Healthy",
            health
        );

    }
    catch(error){

        showToast(
            "Backend Offline",
            "Cannot connect to Flask server",
            "danger"
        );
    }
}

// ======================================================
// AUTO REFRESH
// ======================================================

function startAutoRefresh(){

    setInterval(
        async () => {

            await loadDashboard();

            if(
                typeof loadAlerts
                === "function"
            ){

                loadAlerts();
            }

        },
        AUTO_REFRESH_INTERVAL
    );
}

// ======================================================
// EVENT LISTENERS
// ======================================================

if(exportCsvBtn){

    exportCsvBtn.addEventListener(
        "click",
        exportCSV
    );
}

if(refreshDashboardBtn){

    refreshDashboardBtn.addEventListener(
        "click",
        loadDashboard
    );
}

// ======================================================
// INITIALIZATION
// ======================================================

document.addEventListener(
    "DOMContentLoaded",
    async () => {

        await checkBackendHealth();

        await loadDashboard();

        startAutoRefresh();

        hideLoader();
    }
);
// ======================================================
// APP.JS - PART 2
// Assessment Engine + Results Rendering
// ======================================================

// ======================================================
// FORM ELEMENTS
// ======================================================

const assessmentForm =
    document.getElementById(
        "assessmentForm"
    );

const severityCard =
    document.getElementById(
        "severityCard"
    );

const severityLabel =
    document.getElementById(
        "severityLabel"
    );

const severityIcon =
    document.getElementById(
        "severityIcon"
    );

const sirsScore =
    document.getElementById(
        "sirsScore"
    );

const qsofaScore =
    document.getElementById(
        "qsofaScore"
    );

const news2Score =
    document.getElementById(
        "news2Score"
    );

const aiNarrative =
    document.getElementById(
        "aiNarrative"
    );

const riskFactors =
    document.getElementById(
        "riskFactors"
    );

const recommendedFocus =
    document.getElementById(
        "recommendedFocus"
    );

const clinicalReasoning =
    document.getElementById(
        "clinicalReasoning"
    );

const alertsContainer =
    document.getElementById(
        "alertsContainer"
    );

// ======================================================
// BUILD PAYLOAD
// ======================================================

function buildAssessmentPayload(){

    return {

        patient_id:
            document.getElementById(
                "patientId"
            ).value,

        patient_name:
            document.getElementById(
                "patientName"
            ).value,

        ward:
            document.getElementById(
                "ward"
            ).value,

        nurse_id:
            document.getElementById(
                "nurseId"
            ).value,

        temperature:
            parseFloat(
                document.getElementById(
                    "temperature"
                ).value
            ),

        heart_rate:
            parseInt(
                document.getElementById(
                    "heartRate"
                ).value
            ),

        respiratory_rate:
            parseInt(
                document.getElementById(
                    "respRate"
                ).value
            ),

        sbp:
            parseInt(
                document.getElementById(
                    "sbp"
                ).value
            ),

        dbp:
            parseInt(
                document.getElementById(
                    "dbp"
                ).value
            ),

        spo2:
            parseFloat(
                document.getElementById(
                    "spo2"
                ).value
            ),

        wbc:
            parseFloat(
                document.getElementById(
                    "wbc"
                ).value
            ) || null,

        lactate:
            parseFloat(
                document.getElementById(
                    "lactate"
                ).value
            ) || null,

        creatinine:
            parseFloat(
                document.getElementById(
                    "creatinine"
                ).value
            ) || null,

        mental_status:
            document.getElementById(
                "mentalStatus"
            ).value,

        on_supplemental_o2:
            document.getElementById(
                "supplementalO2"
            ).value === "true"
    };
}

// ======================================================
// FORM VALIDATION
// ======================================================

function validateAssessment(payload){

    const required = [

        payload.patient_id,
        payload.patient_name,
        payload.temperature,
        payload.heart_rate,
        payload.respiratory_rate,
        payload.sbp,
        payload.spo2
    ];

    const missing =
        required.some(
            v =>
            v === null ||
            v === "" ||
            Number.isNaN(v)
        );

    if(missing){

        showToast(
            "Validation Error",
            "Please complete all required fields.",
            "warning"
        );

        return false;
    }

    return true;
}

// ======================================================
// RUN ASSESSMENT
// ======================================================

async function submitAssessment(e){

    e.preventDefault();

    try{

        const payload =
            buildAssessmentPayload();

        if(
            !validateAssessment(
                payload
            )
        ){
            return;
        }

        showLoader();

        const result =
            await ApiClient.post(
                "/assess",
                payload
            );

        hideLoader();

        if(!result.success){

            throw new Error(
                "Assessment Failed"
            );
        }

        const assessment =
            result.assessment;

        AppState.currentPatient =
            assessment;

        renderAssessmentResults(
            assessment
        );

        renderAIGuidance(
            assessment
        );

        renderAssessmentAlerts(
            assessment
        );

        showToast(
            "Assessment Complete",
            assessment.severity_label,
            "success"
        );

        loadDashboard();

        if(
            typeof loadPatients
            === "function"
        ){
            loadPatients();
        }

    }
    catch(error){

        hideLoader();

        console.error(error);

        showToast(
            "Assessment Failed",
            error.message,
            "danger"
        );
    }
}

// ======================================================
// SEVERITY CARD
// ======================================================

function renderAssessmentResults(
    assessment
){

    severityLabel.textContent =
        assessment.severity_label;

    severityIcon.innerHTML =
        assessment.severity_icon;

    severityCard.style.background =
        assessment.severity_color;

    sirsScore.textContent =
        assessment.sirs.score;

    qsofaScore.textContent =
        assessment.qsofa.score;

    news2Score.textContent =
        assessment.news2.total_score;
}

// ======================================================
// AI GUIDANCE
// ======================================================

function renderAIGuidance(
    assessment
){

    const ai =
        assessment.ai_guidance;

    if(
        !ai ||
        !ai.available
    ){

        aiNarrative.innerHTML = `
            <div class="alert alert-warning">
                AI Guidance Not Available
            </div>
        `;

        return;
    }

    aiNarrative.innerHTML = `

        <div class="ai-card">

            <h5>
                Clinical Summary
            </h5>

            <p>
                ${ai.narrative || ""}
            </p>

        </div>
    `;

    riskFactors.innerHTML = `

        <div class="ai-card">

            <h5>
                Risk Factors
            </h5>

            <ul>

                ${
                    (
                        ai.risk_factors || []
                    )
                    .map(
                        item =>
                        `<li>${item}</li>`
                    )
                    .join("")
                }

            </ul>

        </div>
    `;

    recommendedFocus.innerHTML = `

        <div class="ai-card">

            <h5>
                Recommended Focus
            </h5>

            <ul>

                ${
                    (
                        ai.recommended_focus
                        || []
                    )
                    .map(
                        item =>
                        `<li>${item}</li>`
                    )
                    .join("")
                }

            </ul>

        </div>
    `;

    clinicalReasoning.innerHTML = `

        <div class="ai-card">

            <h5>
                Clinical Reasoning
            </h5>

            <p>

                ${
                    ai.clinical_reasoning
                    || "N/A"
                }

            </p>

        </div>
    `;
}

// ======================================================
// ASSESSMENT ALERTS
// ======================================================

function renderAssessmentAlerts(
    assessment
){

    alertsContainer.innerHTML = "";

    const alerts =
        assessment.alerts.alerts
        || [];

    if(alerts.length === 0){

        alertsContainer.innerHTML = `

            <div class="alert alert-success">

                No Active Alerts

            </div>

        `;

        return;
    }

    alerts.forEach(alert => {

        const priority =
            (
                alert.priority
                || ""
            ).toLowerCase();

        const div =
            document.createElement(
                "div"
            );

        div.className =
            `alert-item alert-${priority}`;

        div.innerHTML = `

            <div
                class="d-flex
                justify-content-between">

                <div>

                    <div
                        class="alert-title">

                        ${alert.priority_icon}
                        ${alert.alert_name}

                    </div>

                    <div>

                        Value:
                        ${alert.value}

                    </div>

                    <div>

                        Threshold:
                        ${alert.threshold}

                    </div>

                </div>

                <div>

                    <span
                    class="badge bg-danger">

                    ${alert.priority}

                    </span>

                </div>

            </div>

            <div
            class="alert-note mt-2">

                ${alert.clinical_note}

            </div>

        `;

        alertsContainer
            .appendChild(div);
    });
}

// ======================================================
// VITAL SUMMARY TABLE
// ======================================================

function renderVitalSummary(
    assessment
){

    const summary =
        assessment.vital_summary;

    let html = `

        <table
        class="table table-bordered">

        <thead>

        <tr>

            <th>Vital</th>
            <th>Value</th>
            <th>Status</th>
            <th>Reference</th>

        </tr>

        </thead>

        <tbody>
    `;

    Object.keys(summary)
        .forEach(key => {

        const vital =
            summary[key];

        html += `

            <tr>

                <td>
                    ${key}
                </td>

                <td>
                    ${vital.value}
                </td>

                <td>

                    <span
                    class="
                    badge
                    bg-${
                        getStatusColor(
                            vital.status
                        )
                    }">

                    ${vital.status}

                    </span>

                </td>

                <td>
                    ${vital.normal_range}
                </td>

            </tr>
        `;
    });

    html += `
        </tbody>
        </table>
    `;

    return html;
}

// ======================================================
// STATUS COLOR
// ======================================================

function getStatusColor(status){

    switch(status){

        case "critical":
            return "danger";

        case "warning":
            return "warning";

        default:
            return "success";
    }
}

// ======================================================
// FORM EVENT
// ======================================================

if(assessmentForm){

    assessmentForm.addEventListener(
        "submit",
        submitAssessment
    );
}
// ======================================================
// APP.JS - PART 3
// Patients + Trends + Alerts Dashboard
// ======================================================

// ======================================================
// DOM REFERENCES
// ======================================================

const patientsTable =
    document.getElementById(
        "patientsTable"
    );

const patientSearch =
    document.getElementById(
        "patientSearch"
    );

const patientHistoryContent =
    document.getElementById(
        "patientHistoryContent"
    );

// ======================================================
// LOAD PATIENTS
// ======================================================

async function loadPatients(){

    try{

        const response =
            await ApiClient.get(
                "/patients"
            );

        AppState.patients =
            response.patients || [];

        renderPatientsTable(
            AppState.patients
        );

    }
    catch(error){

        console.error(error);
    }
}

// ======================================================
// RENDER PATIENT TABLE
// ======================================================

function renderPatientsTable(
    patients
){

    if(!patientsTable) return;

    patientsTable.innerHTML = "";

    if(patients.length === 0){

        patientsTable.innerHTML = `
            <tr>
                <td colspan="9"
                class="text-center">
                    No Patient Records
                </td>
            </tr>
        `;

        return;
    }

    patients.forEach(patient => {

        const tr =
            document.createElement(
                "tr"
            );

        tr.innerHTML = `

            <td>
                ${patient.patient_name}
            </td>

            <td>
                ${patient.patient_id}
            </td>

            <td>
                ${patient.ward}
            </td>

            <td>

                <span
                class="badge-severity">

                    ${patient.severity_label}

                </span>

            </td>

            <td>
                ${patient.sirs.score}
            </td>

            <td>
                ${patient.qsofa.score}
            </td>

            <td>
                ${patient.news2.total_score}
            </td>

            <td>
                ${patient.timestamp}
            </td>

            <td>

                <button
                class="btn btn-sm btn-primary"

                onclick="
                    loadPatientHistory(
                        '${patient.patient_id}'
                    )
                ">

                View

                </button>

            </td>

        `;

        patientsTable
            .appendChild(tr);
    });
}

// ======================================================
// SEARCH PATIENTS
// ======================================================

function searchPatients(){

    const query =
        patientSearch.value
        .toLowerCase();

    const filtered =
        AppState.patients.filter(
            p =>
                p.patient_name
                    .toLowerCase()
                    .includes(query)

                ||

                p.patient_id
                    .toLowerCase()
                    .includes(query)
        );

    renderPatientsTable(
        filtered
    );
}

if(patientSearch){

    patientSearch.addEventListener(
        "keyup",
        searchPatients
    );
}

// ======================================================
// LOAD PATIENT HISTORY
// ======================================================

async function loadPatientHistory(
    patientId
){

    try{

        showLoader();

        const patient =
            await ApiClient.get(
                `/patient/${patientId}`
            );

        hideLoader();

        AppState.currentPatient =
            patient;

        renderPatientHistory(
            patient
        );

        renderTrendCharts(
            patient
        );

        const modal =
            new bootstrap.Modal(
                document.getElementById(
                    "patientModal"
                )
            );

        modal.show();

    }
    catch(error){

        hideLoader();

        console.error(error);
    }
}

// ======================================================
// PATIENT HISTORY HTML
// ======================================================

function renderPatientHistory(
    patient
){

    if(!patientHistoryContent)
        return;

    patientHistoryContent.innerHTML = `

        <div class="row">

            <div class="col-md-4">

                <div class="metric-card">

                    <h6>
                        Patient
                    </h6>

                    <h4>
                        ${patient.patient_name}
                    </h4>

                </div>

            </div>

            <div class="col-md-4">

                <div class="metric-card">

                    <h6>
                        Assessments
                    </h6>

                    <h3>
                        ${patient.total_assessments}
                    </h3>

                </div>

            </div>

            <div class="col-md-4">

                <div class="metric-card">

                    <h6>
                        Trend
                    </h6>

                    <h3>
                        ${patient.overall_trend}
                    </h3>

                </div>

            </div>

        </div>

        <hr>

        <div id="patientTimeline">

        </div>

    `;

    const timeline =
        document.getElementById(
            "patientTimeline"
        );

    patient.previous_assessments
        .forEach(record => {

        timeline.innerHTML += `

            <div
            class="alert-item">

                <h6>
                    ${record.timestamp}
                </h6>

                <p>

                    Severity:
                    ${record.severity_label}

                </p>

                <p>

                    NEWS2:
                    ${record.news2.total_score}

                </p>

            </div>

        `;
    });
}

// ======================================================
// TREND CHARTS
// ======================================================

function renderTrendCharts(
    patient
){

    const timeline =
        patient.vitals_timeline;

    renderHeartRateChart(
        timeline
    );

    renderRespChart(
        timeline
    );

    renderSpo2Chart(
        timeline
    );

    renderSeverityChartTrend(
        timeline
    );
}

// ======================================================
// HEART RATE CHART
// ======================================================

function renderHeartRateChart(
    timeline
){

    const ctx =
        document.getElementById(
            "heartRateChart"
        );

    if(!ctx) return;

    if(AppState.heartRateChart){

        AppState
            .heartRateChart
            .destroy();
    }

    AppState.heartRateChart =
        new Chart(ctx,{

        type:"line",

        data:{

            labels:
                timeline.map(
                    x => x.timestamp
                ),

            datasets:[{

                label:
                    "Heart Rate",

                data:
                    timeline.map(
                        x => x.heart_rate
                    ),

                tension:.4
            }]
        }
    });
}

// ======================================================
// RESPIRATORY CHART
// ======================================================

function renderRespChart(
    timeline
){

    const ctx =
        document.getElementById(
            "respChart"
        );

    if(!ctx) return;

    if(AppState.respiratoryChart){

        AppState
            .respiratoryChart
            .destroy();
    }

    AppState.respiratoryChart =
        new Chart(ctx,{

        type:"line",

        data:{

            labels:
                timeline.map(
                    x => x.timestamp
                ),

            datasets:[{

                label:
                    "Respiratory Rate",

                data:
                    timeline.map(
                        x =>
                        x.respiratory_rate
                    )
            }]
        }
    });
}

// ======================================================
// SPO2 CHART
// ======================================================

function renderSpo2Chart(
    timeline
){

    const ctx =
        document.getElementById(
            "spo2Chart"
        );

    if(!ctx) return;

    if(AppState.spo2Chart){

        AppState
            .spo2Chart
            .destroy();
    }

    AppState.spo2Chart =
        new Chart(ctx,{

        type:"line",

        data:{

            labels:
                timeline.map(
                    x => x.timestamp
                ),

            datasets:[{

                label:"SpO₂",

                data:
                    timeline.map(
                        x => x.spo2
                    )
            }]
        }
    });
}

// ======================================================
// SEVERITY TREND
// ======================================================

function renderSeverityChartTrend(
    timeline
){

    const ctx =
        document.getElementById(
            "severityTrendChart"
        );

    if(!ctx) return;

    if(
        AppState.severityTrendChart
    ){

        AppState
            .severityTrendChart
            .destroy();
    }

    AppState.severityTrendChart =
        new Chart(ctx,{

        type:"bar",

        data:{

            labels:
                timeline.map(
                    x => x.timestamp
                ),

            datasets:[{

                label:
                    "Severity Level",

                data:
                    timeline.map(
                        x =>
                        x.severity_level
                    )
            }]
        }
    });
}

// ======================================================
// LOAD ACTIVE ALERTS
// ======================================================

async function loadAlerts(){

    try{

        const response =
            await ApiClient.get(
                "/alerts"
            );

        AppState.alerts =
            response.alerts || [];

        renderActiveAlerts(
            AppState.alerts
        );

    }
    catch(error){

        console.error(error);
    }
}

// ======================================================
// ACTIVE ALERT PANEL
// ======================================================

function renderActiveAlerts(
    alerts
){

    if(!alertsContainer)
        return;

    alertsContainer.innerHTML = "";

    if(alerts.length === 0){

        alertsContainer.innerHTML = `

            <div
            class="alert alert-success">

                No Active Alerts

            </div>
        `;

        return;
    }

    alerts.forEach(alert => {

        const div =
            document.createElement(
                "div"
            );

        div.className =
            "alert-item";

        div.innerHTML = `

            <div
            class="d-flex
            justify-content-between">

                <div>

                    <h5>

                        ${alert.severity_icon}
                        ${alert.patient_name}

                    </h5>

                    <div>

                        ${alert.severity_label}

                    </div>

                    <div>

                        Ward:
                        ${alert.ward}

                    </div>

                </div>

                <div>

                    <button
                    class="btn btn-sm btn-primary"

                    onclick="
                        loadPatientHistory(
                            '${alert.patient_id}'
                        )
                    ">

                    Open

                    </button>

                </div>

            </div>

        `;

        alertsContainer
            .appendChild(div);
    });
}

// ======================================================
// INITIAL LOAD
// ======================================================

document.addEventListener(
    "DOMContentLoaded",
    async () => {

        await loadPatients();

        await loadAlerts();

    }
);
// ======================================================
// APP.JS - PART 4
// Production Features & Final Layer
// ======================================================

// ======================================================
// SEVERITY BADGE CLASS
// ======================================================

function getSeverityBadgeClass(
    severity
){

    const value =
        (severity || "")
        .toUpperCase();

    switch(value){

        case "NO_RISK":
            return "badge-no-risk";

        case "SEPSIS_WATCH":
            return "badge-watch";

        case "SEPSIS_ALERT":
            return "badge-alert";

        case "SEVERE_SEPSIS":
            return "badge-severe";

        case "SEPTIC_SHOCK":
            return "badge-shock";

        default:
            return "badge-secondary";
    }
}

// ======================================================
// SEVERITY CARD THEMES
// ======================================================

function applySeverityTheme(
    assessment
){

    if(!severityCard)
        return;

    const severity =
        assessment.severity;

    const themes = {

        NO_RISK: `
            linear-gradient(
                135deg,
                #059669,
                #10b981
            )
        `,

        SEPSIS_WATCH: `
            linear-gradient(
                135deg,
                #d97706,
                #f59e0b
            )
        `,

        SEPSIS_ALERT: `
            linear-gradient(
                135deg,
                #ea580c,
                #fb923c
            )
        `,

        SEVERE_SEPSIS: `
            linear-gradient(
                135deg,
                #dc2626,
                #ef4444
            )
        `,

        SEPTIC_SHOCK: `
            linear-gradient(
                135deg,
                #7f1d1d,
                #991b1b
            )
        `
    };

    severityCard.style.background =
        themes[severity]
        ||
        themes.NO_RISK;
}

// ======================================================
// OVERRIDE EXISTING RESULT RENDER
// ======================================================

const originalRenderAssessment =
    renderAssessmentResults;

renderAssessmentResults =
    function(assessment){

        originalRenderAssessment(
            assessment
        );

        applySeverityTheme(
            assessment
        );

        updateClinicalSummary(
            assessment
        );
    };

// ======================================================
// CLINICAL SUMMARY BAR
// ======================================================

function updateClinicalSummary(
    assessment
){

    let existing =
        document.getElementById(
            "clinicalSummaryBar"
        );

    if(!existing){

        existing =
            document.createElement(
                "div"
            );

        existing.id =
            "clinicalSummaryBar";

        existing.className =
            "glass-card mt-3";

        document
            .getElementById(
                "resultsSection"
            )
            .appendChild(existing);
    }

    existing.innerHTML = `

        <div
        class="row text-center">

            <div class="col-md-3">

                <h6>
                    Priority
                </h6>

                <h4>
                    ${assessment.priority}
                </h4>

            </div>

            <div class="col-md-3">

                <h6>
                    Response Time
                </h6>

                <h4>
                    ${assessment.response_time}
                </h4>

            </div>

            <div class="col-md-3">

                <h6>
                    Alert Count
                </h6>

                <h4>
                    ${assessment.alerts.total_alerts}
                </h4>

            </div>

            <div class="col-md-3">

                <h6>
                    Organ Dysfunction
                </h6>

                <h4>

                ${
                    assessment.alerts
                    .organ_dysfunction_present
                    ? "YES"
                    : "NO"
                }

                </h4>

            </div>

        </div>
    `;
}

// ======================================================
// DELETE ALL DATA
// ======================================================

async function clearDatabase(){

    const confirmDelete =
        confirm(
            "Delete ALL patient records?"
        );

    if(!confirmDelete)
        return;

    try{

        await ApiClient.delete(
            "/patients"
        );

        showToast(
            "Success",
            "Database Cleared",
            "success"
        );

        await loadDashboard();

        await loadPatients();

        await loadAlerts();

    }
    catch(error){

        showToast(
            "Error",
            error.message,
            "danger"
        );
    }
}

// ======================================================
// ADD CLEAR BUTTON
// ======================================================

function injectAdminButton(){

    const actions =
        document.querySelector(
            ".topbar-actions"
        );

    if(!actions)
        return;

    const btn =
        document.createElement(
            "button"
        );

    btn.className =
        "btn btn-danger";

    btn.innerHTML = `

        <i class="bi bi-trash">
        </i>

        Clear Data
    `;

    btn.addEventListener(
        "click",
        clearDatabase
    );

    actions.appendChild(btn);
}

// ======================================================
// FILTER BY SEVERITY
// ======================================================

function filterPatientsBySeverity(
    severity
){

    if(
        !severity ||
        severity === "ALL"
    ){

        renderPatientsTable(
            AppState.patients
        );

        return;
    }

    const filtered =
        AppState.patients.filter(
            p =>
            p.severity === severity
        );

    renderPatientsTable(
        filtered
    );
}

// ======================================================
// REFRESH EVERYTHING
// ======================================================

async function refreshEverything(){

    try{

        await Promise.all([

            loadDashboard(),

            loadPatients(),

            loadAlerts()

        ]);

        console.log(
            "Dashboard Synced"
        );

    }
    catch(error){

        console.error(error);
    }
}

// ======================================================
// AUTO SYNC
// ======================================================

function startRealtimeSync(){

    setInterval(
        refreshEverything,
        30000
    );
}

// ======================================================
// SIDEBAR ACTIVE STATE
// ======================================================

function setupSidebarNavigation(){

    const links =
        document.querySelectorAll(
            ".menu-link"
        );

    links.forEach(link => {

        link.addEventListener(
            "click",
            function(){

                links.forEach(
                    x =>
                    x.classList
                     .remove("active")
                );

                this.classList
                    .add("active");
            }
        );
    });
}

// ======================================================
// SCROLL TO SECTION
// ======================================================

function setupSmoothNavigation(){

    document
    .querySelectorAll(
        '.menu-link'
    )
    .forEach(link => {

        link.addEventListener(
            "click",
            function(e){

                e.preventDefault();

                const target =
                    document.querySelector(
                        this.getAttribute(
                            "href"
                        )
                    );

                if(target){

                    target.scrollIntoView({

                        behavior:
                            "smooth"
                    });
                }
            }
        );
    });
}

// ======================================================
// HEALTH STATUS INDICATOR
// ======================================================

async function createHealthBadge(){

    try{

        const health =
            await ApiClient.get(
                "/health"
            );

        const badge =
            document.createElement(
                "div"
            );

        badge.className =
            "health-badge";

        badge.innerHTML = `

            <span
            class="badge bg-success">

            ● Backend Online

            </span>

        `;

        document
            .querySelector(
                ".topbar"
            )
            .appendChild(
                badge
            );

    }
    catch(error){

        console.error(error);
    }
}

// ======================================================
// EMPTY STATE
// ======================================================

function renderEmptyState(){

    if(
        AppState.patients.length
        > 0
    ) return;

    const section =
        document.getElementById(
            "patientsSection"
        );

    if(!section)
        return;

    section.innerHTML += `

        <div
        class="glass-card mt-3">

            <div
            class="text-center p-5">

                <h4>
                    No Assessments Yet
                </h4>

                <p>

                    Run your first
                    patient assessment.

                </p>

            </div>

        </div>
    `;
}

// ======================================================
// GLOBAL ERROR HANDLER
// ======================================================

window.addEventListener(
    "error",
    function(event){

        console.error(
            event.error
        );

        showToast(

            "Application Error",

            event.message,

            "danger"
        );
    }
);

// ======================================================
// FINAL BOOTSTRAP
// ======================================================

document.addEventListener(
    "DOMContentLoaded",
    async () => {

        console.log(
            "Sepsis Assistant Started"
        );

        setupSidebarNavigation();

        setupSmoothNavigation();

        injectAdminButton();

        createHealthBadge();

        await refreshEverything();

        renderEmptyState();

        startRealtimeSync();

        showToast(

            "System Ready",

            "Real-Time Sepsis Early Warning Assistant Loaded",

            "success"
        );
    }
);