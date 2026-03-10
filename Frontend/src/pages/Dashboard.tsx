import { useState } from "react";
import { ExecutivePanel } from "@/components/dashboard/ExecutivePanel";
import { KPIGrid } from "@/components/dashboard/KPIGrid";
import { AIInsights } from "@/components/dashboard/AIInsights";
import { CreditBreakdown } from "@/components/dashboard/CreditBreakdown";
import { EditCreditsPanel } from "@/components/dashboard/EditCreditsPanel";

import { useAppState } from "@/lib/app-state";
import {
  getTotalEarned,
  getExpectedByTerm,
  DEGREE_OPTIONS,
} from "@/lib/academic-rules";

import {
  SlidersHorizontal,
  Activity,
  Cpu,
  Database,
  ArrowUpRight,
} from "lucide-react";

const Dashboard = () => {
  const [panelOpen, setPanelOpen] = useState(false);

  const { degree, term, credits } = useAppState();

  const config = DEGREE_OPTIONS[degree];
  const termNum = parseInt(term.replace("Term ", "")) || 4;

  const totalEarned = getTotalEarned(credits);
  const expected = getExpectedByTerm(degree, termNum);
  const deviation = totalEarned - expected;

  const paceLabel =
    deviation >= 0
      ? `Ahead of expected pace (+${deviation} credits)`
      : `Behind expected pace (${deviation} credits)`;

  return (
    <div className="space-y-5">

      {/* ------------------------------------------------ */}
      {/* Header */}
      {/* ------------------------------------------------ */}

      <div className="flex items-center justify-between">

        <div className="space-y-1">
          <h1 className="text-lg font-semibold">
            Executive Dashboard
          </h1>

          <p className="text-xs text-muted-foreground">
            AI-driven academic performance monitoring
          </p>
        </div>

        <button
          onClick={() => setPanelOpen(true)}
          className="flex items-center gap-2 rounded-md border border-primary/20 bg-primary/10 px-3.5 py-1.5 text-xs font-medium text-primary transition-all hover:bg-primary/20 hover:border-primary/30"
        >
          <SlidersHorizontal className="h-3.5 w-3.5" />
          Edit Academic Credits
        </button>
      </div>

      {/* ------------------------------------------------ */}
      {/* Academic Pace Indicator */}
      {/* ------------------------------------------------ */}

      <div className="glass-card p-3 flex items-center justify-between">

        <div className="flex items-center gap-2">

          <Activity className="h-4 w-4 text-primary" />

          <span className="text-xs font-medium">
            Academic Pace Indicator
          </span>

        </div>

        <span
          className={`text-xs font-medium ${
            deviation >= 0 ? "text-success" : "text-warning"
          }`}
        >
          {paceLabel}
        </span>

      </div>

      {/* ------------------------------------------------ */}
      {/* Executive Panel */}
      {/* ------------------------------------------------ */}

      <ExecutivePanel />

      {/* ------------------------------------------------ */}
      {/* KPI Grid */}
      {/* ------------------------------------------------ */}

      <KPIGrid />

      {/* ------------------------------------------------ */}
      {/* System Health Card */}
      {/* ------------------------------------------------ */}

      <div className="glass-card p-4">

        <div className="flex items-center justify-between mb-3">

          <div className="flex items-center gap-2">
            <Cpu className="h-4 w-4 text-primary" />
            <h3 className="text-sm font-semibold">
              System Health
            </h3>
          </div>

          <a
            href="/models"
            className="text-[11px] text-primary flex items-center gap-1 hover:underline"
          >
            Compare Models
            <ArrowUpRight className="h-3 w-3" />
          </a>

        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 text-xs">

          <div className="flex items-center gap-2">
            <Activity className="h-3 w-3 text-success" />
            API Status
          </div>
          <span className="text-success font-medium">Online</span>

          <div className="flex items-center gap-2">
            <Cpu className="h-3 w-3 text-info" />
            Models Loaded
          </div>
          <span>3</span>

          <div className="flex items-center gap-2">
            <Database className="h-3 w-3 text-warning" />
            Dataset Size
          </div>
          <span>10,000</span>

          <div className="flex items-center gap-2">
            <Activity className="h-3 w-3 text-accent" />
            Inference Speed
          </div>
          <span>14 ms</span>

        </div>

      </div>

      {/* ------------------------------------------------ */}
      {/* Insights + Breakdown */}
      {/* ------------------------------------------------ */}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[1fr_1.5fr]">

        <AIInsights />

        <CreditBreakdown />

      </div>

      {/* ------------------------------------------------ */}
      {/* Credits Editor */}
      {/* ------------------------------------------------ */}

      <EditCreditsPanel
        open={panelOpen}
        onClose={() => setPanelOpen(false)}
      />

    </div>
  );
};

export default Dashboard;