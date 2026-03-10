// -------------------------------------------
// Academic AI Guard - Full API Layer (FIXED)
// -------------------------------------------

const BASE_URL = "http://127.0.0.1:8000";

// -------------------------------------------
// TYPES
// -------------------------------------------

export interface BackendPrediction {
  prediction: "On-Time" | "Delayed";
  probability: number;
  risk_level: "Low" | "Medium" | "High";
  model_version: string;
  model_used: string;
}

export interface PredictionResponse {
  risk_level: "Low" | "Medium" | "High";
  probability: number;
  confidence: number;
  insights: string[];
}

export interface SummaryResponse {
  total_students: number;
  delayed_percentage: number;
  on_time_percentage: number;
}

export interface ModelInfoResponse {
  version: string;
  selected_model: string;
  dataset_size: number;
  metrics: Record<
    string,
    {
      accuracy: number;
      precision: number;
      recall_delayed: number;
      f1: number;
    }
  >;
}

// -------------------------------------------
// SAFE FETCH
// -------------------------------------------

async function safeFetch(url: string, options?: RequestInit) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 8000);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });

    clearTimeout(timeout);

    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || "Request failed");
    }

    return await response.json();
  } catch (err) {
    clearTimeout(timeout);
    console.error("API Error:", err);
    throw err;
  }
}

// -------------------------------------------
// MODEL NAME MAPPING
// -------------------------------------------

function mapModelName(uiModel: string): string {
  const modelMap: Record<string, string> = {
    "Logistic Regression": "logistic",
    "Decision Tree": "decision_tree",
    "Random Forest": "random_forest",
    "Gradient Boosting": "gradient_boosting",
    "XGBoost": "xgboost",
  };

  return modelMap[uiModel] || "logistic";
}

// -------------------------------------------
// REAL BACKEND CALL
// -------------------------------------------

export async function predictStudent(data: {
  model: string;
  semester: number;
  failed_courses: number;

  attendance_rate: number;
  stress_level: number;
  extracurricular_score: number;

  internship_completed: number;
  family_income_level: number;
  part_time_job: number;
  scholarship: number;
  campus_resident: number;
}): Promise<BackendPrediction> {

  return await safeFetch(`${BASE_URL}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

// -------------------------------------------
// WRAPPER USED BY UI
// -------------------------------------------

export async function predictRisk(
  request: any
): Promise<PredictionResponse> {

  const termNum =
    parseInt(request.term?.replace("Term ", "")) || 4;

  const selectedModel = mapModelName(request.model);

  // Example normalized values (replace later if needed)
  const attendance = 0.85;
  const stress = 0.4;
  const extracurricular = 0.6;

  const backendResult = await predictStudent({
    model: selectedModel,

    semester: termNum,
    failed_courses: 0,

    attendance_rate: attendance,
    stress_level: stress,
    extracurricular_score: extracurricular,

    internship_completed: 0,
    family_income_level: 2,
    part_time_job: 0,
    scholarship: 0,
    campus_resident: 1,
  });

  return {
    risk_level: backendResult.risk_level,
    probability: backendResult.probability,
    confidence: 100 - backendResult.probability,
    insights: [
      `Model version ${backendResult.model_version} used.`,
      `Model selected: ${backendResult.model_used}.`,
      `Predicted outcome: ${backendResult.prediction}.`,
    ],
  };
}

// -------------------------------------------
// DASHBOARD ENDPOINTS
// -------------------------------------------

export async function getSummary(): Promise<SummaryResponse> {
  return await safeFetch(`${BASE_URL}/summary`);
}

export async function getModelInfo(): Promise<ModelInfoResponse> {
  return await safeFetch(`${BASE_URL}/model-info`);
}

export async function retrainModel(): Promise<{ message: string }> {
  return await safeFetch(`${BASE_URL}/retrain`, {
    method: "POST",
  });
}