import { useEffect, useState } from "react";
import { useAppState } from "@/lib/app-state";
import {
  getCompletionPct,
  getExpectedByTerm,
  getTotalEarned,
  DEGREE_OPTIONS,
} from "@/lib/academic-rules";
import { predictStudent, getModelInfo } from "@/lib/api";
import { RadialBarChart, RadialBar, ResponsiveContainer } from "recharts";
import { Shield, AlertTriangle, AlertCircle } from "lucide-react";

type BackendPrediction = {
  prediction: "On-Time" | "Delayed";
  probability: number;
  risk_level: "Low" | "Medium" | "High";
  model_version: string;
  model_used: string;
};

export function ExecutivePanel() {
  const { degree, term, credits, model } = useAppState();

  const [prediction, setPrediction] = useState<BackendPrediction | null>(null);
  const [modelInfo, setModelInfo] = useState<any>(null);

  const termNum = parseInt(term.replace("Term ", "")) || 4;

  // --------------------------------------------------
  // Fetch Prediction
  // --------------------------------------------------
  useEffect(() => {
    async function runPrediction() {
      try {
        const result = await predictStudent({
          model,

          semester: termNum,
          failed_courses: 0,

          attendance_rate: 0.85,
          stress_level: 0.4,
          extracurricular_score: 0.6,

          internship_completed: 0,
          family_income_level: 2,
          part_time_job: 0,
          scholarship: 0,
          campus_resident: 1,
        });

        setPrediction(result);
      } catch (err) {
        console.error("Prediction failed:", err);
      }
    }

    runPrediction();
  }, [model, term]);

  // --------------------------------------------------
  // Fetch Model Metrics
  // --------------------------------------------------
  useEffect(() => {
    async function loadModelInfo() {
      try {
        const info = await getModelInfo();
        setModelInfo(info);
      } catch (err) {
        console.error("Model info failed:", err);
      }
    }

    loadModelInfo();
  }, []);

  // --------------------------------------------------
  // Derived UI Values
  // --------------------------------------------------

  const riskLevel = prediction?.risk_level ?? "Medium";
  const probabilityPct = prediction?.probability ?? 0;

  const riskColor =
    riskLevel === "Low"
      ? "text-success"
      : riskLevel === "Medium"
      ? "text-warning"
      : "text-destructive";

  const riskBg =
    riskLevel === "Low"
      ? "bg-success/10 border-success/20"
      : riskLevel === "Medium"
      ? "bg-warning/10 border-warning/20"
      : "bg-destructive/10 border-destructive/20";

  const RiskIcon =
    riskLevel === "Low"
      ? Shield
      : riskLevel === "Medium"
      ? AlertTriangle
      : AlertCircle;

  const statusLabel =
    riskLevel === "Low"
      ? "Eligible"
      : riskLevel === "Medium"
      ? "Attention Needed"
      : "At Risk";

  const gaugeData = [
    {
      value: probabilityPct,
      fill:
        riskLevel === "Low"
          ? "hsl(155,70%,45%)"
          : riskLevel === "Medium"
          ? "hsl(40,85%,55%)"
          : "hsl(0,72%,55%)",
    },
  ];

  const selectedModel = modelInfo?.selected_model;

  const accuracy = modelInfo
    ? (modelInfo.metrics[selectedModel]?.accuracy * 100).toFixed(2)
    : "--";

  const f1 = modelInfo
    ? (modelInfo.metrics[selectedModel]?.f1 * 100).toFixed(2)
    : "--";

  const precision = modelInfo
    ? (modelInfo.metrics[selectedModel]?.precision * 100).toFixed(2)
    : "--";

  const recall = modelInfo
    ? (modelInfo.metrics[selectedModel]?.recall_delayed * 100).toFixed(2)
    : "--";

  return (
    <div className="glass-card-glow p-5 animate-fade-in-up">
      <div className="flex items-start justify-between gap-6">
        <div className="flex-1 space-y-4">
          <div className="flex items-center gap-3">
            <h2 className="text-lg font-semibold">
              Executive Command Panel
            </h2>

            <span
              className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium ${riskBg} ${riskColor}`}
            >
              <RiskIcon className="h-3 w-3" />
              {statusLabel}
            </span>
          </div>

          {/* MODEL PERFORMANCE */}

          <div className="grid grid-cols-2 gap-x-8 gap-y-3 lg:grid-cols-4">

            <MetricItem
              label="Risk Level"
              value={riskLevel}
              valueClass={riskColor}
            />

            <MetricItem
              label="Model Accuracy"
              value={`${accuracy}%`}
            />

            <MetricItem
              label="F1 Score"
              value={`${f1}%`}
            />

            <MetricItem
              label="Precision"
              value={`${precision}%`}
            />

            <MetricItem
              label="Recall"
              value={`${recall}%`}
            />
          </div>

          <div className="text-xs text-muted-foreground">
            Target Variable:{" "}
            <span className="font-medium">
              Graduation Outcome (On-Time vs Delayed)
            </span>
          </div>
        </div>

        {/* GAUGE */}

        <div className="flex-shrink-0 w-[130px] h-[130px]">
          <ResponsiveContainer width="100%" height="100%">
            <RadialBarChart
              cx="50%"
              cy="50%"
              innerRadius="70%"
              outerRadius="100%"
              startAngle={180}
              endAngle={0}
              data={gaugeData}
              barSize={8}
            >
              <RadialBar
                dataKey="value"
                cornerRadius={4}
                background={{ fill: "hsl(220,20%,15%)" }}
              />
            </RadialBarChart>
          </ResponsiveContainer>

          <p className="text-center -mt-12 text-2xl font-bold font-mono">
            {probabilityPct}%
          </p>

          <p className="text-center text-[10px] text-muted-foreground mt-0.5">
            Probability of Delay
          </p>
        </div>
      </div>
    </div>
  );
}

function MetricItem({
  label,
  value,
  valueClass = "text-foreground",
}: {
  label: string;
  value: string;
  valueClass?: string;
}) {
  return (
    <div>
      <p className="text-[10px] uppercase tracking-wider text-muted-foreground">
        {label}
      </p>

      <p className={`text-lg font-semibold font-mono ${valueClass}`}>
        {value}
      </p>
    </div>
  );
}