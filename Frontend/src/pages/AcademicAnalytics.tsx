import { useAppState } from "@/lib/app-state";
import {
  getTotalEarned,
  getExpectedByTerm,
  getCompletionPct,
  DEGREE_OPTIONS,
  FIXED_REQUIREMENTS,
} from "@/lib/academic-rules";
import { predictRisk, type PredictionResponse } from "@/lib/api";
import { useEffect, useState } from "react";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  RadialBarChart,
  RadialBar,
  BarChart,
  Bar,
} from "recharts";
import {
  Sparkles,
  TrendingUp,
  AlertTriangle,
  Brain,
} from "lucide-react";

const COLORS = [
  "hsl(185, 75%, 50%)",
  "hsl(255, 55%, 58%)",
  "hsl(155, 70%, 45%)",
];

const AcademicAnalytics = () => {
  const { degree, term, model, credits } = useAppState();
  const [prediction, setPrediction] =
    useState<PredictionResponse | null>(null);

  const config = DEGREE_OPTIONS[degree];
  const termNum = parseInt(term.replace("Term ", "")) || 4;

  useEffect(() => {
    let mounted = true;

    async function runPrediction() {
      try {
        const result = await predictRisk({
          model,
          degree,
          term,
          credits,
        });

        if (mounted) setPrediction(result);
      } catch (err) {
        console.error("Analytics prediction failed:", err);
      }
    }

    runPrediction();

    return () => {
      mounted = false;
    };
  }, [model, degree, term, credits]);

  if (!config) return null;

  const totalEarned = getTotalEarned(credits);
  const completion = getCompletionPct(degree, credits);

  // ------------------------------------------------
  // Experiential Credits
  // ------------------------------------------------

  const experiential =
    credits.pep +
    credits.sip +
    credits.shortIIP +
    credits.longIIP +
    credits.ee +
    credits.ri;

  const experientialTotal =
    FIXED_REQUIREMENTS.pep +
    FIXED_REQUIREMENTS.sip +
    FIXED_REQUIREMENTS.shortIIP +
    FIXED_REQUIREMENTS.longIIP +
    FIXED_REQUIREMENTS.ee +
    FIXED_REQUIREMENTS.ri;

  // ------------------------------------------------
  // Credit Distribution
  // ------------------------------------------------

  const donutData = [
    { name: "Core", value: credits.core },
    { name: "GE", value: credits.ge },
    { name: "Experiential", value: experiential },
  ];

  // ------------------------------------------------
  // Progress vs Expected
  // ------------------------------------------------

  const progressData = Array.from(
    { length: config.totalTerms },
    (_, i) => {
      const t = i + 1;
      return {
        term: `T${t}`,
        expected: getExpectedByTerm(degree, t),
        actual:
          t <= termNum
            ? Math.round(totalEarned * (t / termNum))
            : null,
      };
    }
  );

  // ------------------------------------------------
  // Completion Gauge
  // ------------------------------------------------

  const gaugeData = [
    {
      value: completion,
      fill: "hsl(185, 75%, 50%)",
    },
  ];

  // ------------------------------------------------
  // Risk Segmentation
  // ------------------------------------------------

  const riskSegments = [
    { level: "Low", value: 56 },
    { level: "Medium", value: 30 },
    { level: "High", value: 14 },
  ];

  // ------------------------------------------------
  // Credit Breakdown
  // ------------------------------------------------

  const creditBreakdown = [
    {
      category: "Core",
      earned: credits.core,
    },
    {
      category: "GE",
      earned: credits.ge,
    },
    {
      category: "Experiential",
      earned: experiential,
    },
  ];

  const riskLevel = prediction?.risk_level ?? "Medium";
  const probability = prediction?.probability ?? 0;

  const riskColor =
    riskLevel === "Low"
      ? "text-success"
      : riskLevel === "Medium"
      ? "text-warning"
      : "text-destructive";

  // ------------------------------------------------
  // UI
  // ------------------------------------------------

  return (
    <div className="space-y-6">

      <h2 className="text-lg font-semibold flex items-center gap-2">
        <Brain className="h-5 w-5 text-primary" />
        Academic Analytics
      </h2>

      {/* Progress vs Expected */}

      <div className="glass-card p-4">

        <h3 className="text-sm font-semibold mb-3">
          Academic Progress vs Expected
        </h3>

        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={progressData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="term" />
            <YAxis />
            <Tooltip />

            <Line
              type="monotone"
              dataKey="expected"
              stroke="hsl(215,15%,50%)"
              strokeDasharray="5 5"
              strokeWidth={2}
              dot={false}
            />

            <Line
              type="monotone"
              dataKey="actual"
              stroke="hsl(185,75%,50%)"
              strokeWidth={2}
              dot={{ r: 3 }}
            />

          </LineChart>
        </ResponsiveContainer>

      </div>

      {/* Middle Row */}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">

        {/* Credit Distribution */}

        <div className="glass-card p-4">

          <h3 className="text-sm font-semibold mb-2">
            Credit Distribution
          </h3>

          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={donutData}
                cx="50%"
                cy="50%"
                innerRadius={55}
                outerRadius={80}
                paddingAngle={3}
                dataKey="value"
              >
                {donutData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>

        </div>

        {/* Credit Breakdown */}

        <div className="glass-card p-4">

          <h3 className="text-sm font-semibold mb-2">
            Credit Category Breakdown
          </h3>

          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={creditBreakdown}>
              <XAxis dataKey="category" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="earned" fill="hsl(185,75%,50%)" />
            </BarChart>
          </ResponsiveContainer>

        </div>

        {/* Completion Gauge */}

        <div className="glass-card p-4 flex flex-col items-center">

          <h3 className="text-sm font-semibold mb-2">
            Overall Completion
          </h3>

          <div className="w-[140px] h-[140px]">
            <ResponsiveContainer width="100%" height="100%">
              <RadialBarChart
                cx="50%"
                cy="50%"
                innerRadius="70%"
                outerRadius="100%"
                startAngle={180}
                endAngle={0}
                data={gaugeData}
                barSize={10}
              >
                <RadialBar
                  dataKey="value"
                  cornerRadius={5}
                  background={{
                    fill: "hsl(220,20%,15%)",
                  }}
                />
              </RadialBarChart>
            </ResponsiveContainer>
          </div>

          <p className="text-3xl font-bold font-mono text-primary -mt-10">
            {completion}%
          </p>

        </div>

      </div>

      {/* Bottom Row */}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">

        {/* Risk Indicator */}

        <div className="glass-card p-4">

          <h3 className="text-sm font-semibold mb-3">
            Risk Indicator
          </h3>

          <div className="flex items-center gap-3 mb-3">

            <AlertTriangle
              className={`h-8 w-8 ${riskColor}`}
            />

            <div>
              <p className={`text-lg font-bold ${riskColor}`}>
                {riskLevel} Risk
              </p>

              <p className="text-xs text-muted-foreground">
                Probability: {probability}%
              </p>
            </div>

          </div>

        </div>

        {/* Risk Segmentation */}

        <div className="glass-card p-4">

          <h3 className="text-sm font-semibold mb-3">
            Student Risk Segmentation
          </h3>

          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={riskSegments}>
              <XAxis dataKey="level" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="hsl(155,70%,45%)" />
            </BarChart>
          </ResponsiveContainer>

        </div>

        {/* AI Insight Engine */}

        <div className="glass-card p-4">

          <div className="flex items-center gap-2 mb-3">
            <Sparkles className="h-4 w-4 text-primary" />
            <h3 className="text-sm font-semibold">
              AI Academic Insight Engine
            </h3>
          </div>

          <p className="text-xs text-muted-foreground">
            Student trajectory is currently aligned with expected
            academic progress. Risk of delayed graduation remains
            low. Maintaining consistent engagement in core
            courses will further improve graduation certainty.
          </p>

        </div>

      </div>

    </div>
  );
};

export default AcademicAnalytics;