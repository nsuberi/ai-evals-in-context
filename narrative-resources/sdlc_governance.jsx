import { useState, useCallback, useEffect, useRef } from "react";

const TESTS = [
  {
    id: "unit",
    name: "Unit Testing",
    icon: "⬡",
    color: "#2E5C8A",
    traditional: true,
    aiNew: false,
    description: "Validates individual functions, methods, or modules in isolation. The smallest testable parts of software are verified independently from dependencies.",
    sdlcRole: "Catches defects at the source. Cheapest to write, cheapest to fix. Unit tests form the foundation of the testing pyramid—they run fast, fail precisely, and give developers immediate feedback on whether their logic is correct.",
    whoCreates: "The code author (developer or AI-assisted builder) writes unit tests alongside the code. In AI-assisted workflows, AI can generate initial test scaffolds, but the human must validate test intent and edge case coverage.",
    whoValidates: "Peer reviewer during code review. Automated CI pipeline enforces coverage thresholds.",
    aiConsiderations: "AI tools can generate unit tests quickly, but tend to test the happy path. They may miss boundary conditions, error states, and domain-specific edge cases. AI-generated tests that merely mirror the implementation (tautological tests) provide false confidence. Review for meaningful assertions.",
    auditValue: "Demonstrates developer-level rigor. Coverage metrics provide quantitative evidence of testing discipline. Standardized unit test patterns reduce reviewer cognitive load and increase audit defensibility."
  },
  {
    id: "integration",
    name: "Integration Testing",
    icon: "⬢",
    color: "#D4742C",
    traditional: true,
    aiNew: false,
    description: "Verifies that multiple components, services, or modules work correctly together. Tests the interfaces, data flows, and contracts between systems.",
    sdlcRole: "Catches defects that emerge from component interaction—mismatched data formats, timing issues, authentication failures, contract violations. Integration tests validate assumptions that unit tests can't reach.",
    whoCreates: "Engineers with system architecture knowledge. Requires understanding of service boundaries, API contracts, and data flow. AI-assisted builders need engineering guidance for these tests.",
    whoValidates: "Tech lead or architect reviews integration test coverage against system design. CI/CD pipeline runs integration suites in staging environments.",
    aiConsiderations: "Integration tests for AI-powered features must test the integration layer's behavior when the model returns unexpected, degraded, or adversarial outputs. This includes testing graceful degradation, fallback paths, and timeout handling.",
    auditValue: "Proves that components work together as designed. Essential for demonstrating that changes to one service don't break downstream consumers. Standardized contract tests create repeatable, auditable verification."
  },
  {
    id: "e2e",
    name: "End-to-End Testing",
    icon: "◈",
    color: "#2D7D46",
    traditional: true,
    aiNew: false,
    description: "Simulates real user workflows from start to finish across the entire system stack. Validates that the complete application behaves correctly from the user's perspective.",
    sdlcRole: "The final automated safety net before human acceptance testing. E2E tests verify that the system delivers the intended business value through realistic user journeys—not just that individual pieces work.",
    whoCreates: "QA engineers or SDETs, often in collaboration with product managers who define the critical user journeys. AI-assisted builders should not create E2E tests without QA partnership.",
    whoValidates: "QA lead validates scenario coverage against acceptance criteria. Product owner confirms that tested workflows match business-critical paths.",
    aiConsiderations: "E2E tests for AI features must account for non-deterministic outputs. Tests should validate behavioral boundaries (e.g., 'response contains relevant information') rather than exact string matches. Consider testing with adversarial inputs at the E2E level.",
    auditValue: "Demonstrates that the system works as a whole for real users. E2E test results map directly to business requirements, making them the most stakeholder-readable evidence of quality."
  },
  {
    id: "performance",
    name: "Performance Testing",
    icon: "◉",
    color: "#8B2252",
    traditional: true,
    aiNew: false,
    description: "Measures system behavior under load: response times, throughput, resource utilization, and stability under stress. Includes load testing, stress testing, soak testing, and capacity planning.",
    sdlcRole: "Prevents production incidents caused by scale. A system that works for 10 users may fail at 10,000. Performance testing reveals bottlenecks, memory leaks, and degradation patterns before customers experience them.",
    whoCreates: "Performance engineers or SREs with infrastructure knowledge. Requires understanding of production traffic patterns, infrastructure limits, and SLA requirements.",
    whoValidates: "SRE/Infrastructure team reviews results against SLAs and capacity plans. Engineering leadership approves performance baselines for production readiness.",
    aiConsiderations: "AI model inference introduces latency, GPU/memory costs, and rate-limiting concerns that don't exist in traditional software. Performance testing must measure model serving time, token throughput, concurrent request handling, and cost-per-request under load.",
    auditValue: "Quantitative evidence that the system meets its non-functional requirements. Performance baselines enable regression detection. Critical for SLA compliance and capacity planning documentation."
  },
  {
    id: "acceptance",
    name: "Acceptance Testing",
    icon: "✦",
    color: "#6B4C9A",
    traditional: true,
    aiNew: false,
    description: "Formal verification that the system satisfies business requirements and is ready for production. Includes User Acceptance Testing (UAT), regulatory acceptance, and business sign-off.",
    sdlcRole: "The handshake between engineering and the business. Acceptance testing confirms that what was built matches what was needed—not just technically, but functionally, from the perspective of the people who will use and depend on it.",
    whoCreates: "Product owners and business stakeholders define acceptance criteria. QA and engineering implement automated acceptance checks. Business users execute UAT scenarios.",
    whoValidates: "Business stakeholders, product owners, and in regulated industries, compliance officers. This is the formal 'go/no-go' decision point.",
    aiConsiderations: "For AI features, acceptance testing must include evaluation of output quality, appropriateness, and alignment with business intent—not just functional correctness. This often requires human evaluation rubrics and may involve domain expert assessment of AI outputs.",
    auditValue: "The primary governance artifact linking delivered software to business requirements. Acceptance test results are the documented evidence that the organization verified fitness for purpose before deployment."
  },
  {
    id: "steel-thread",
    name: "Steel Thread Testing",
    icon: "⟡",
    color: "#C4841D",
    traditional: false,
    aiNew: true,
    description: "Validates a thin, end-to-end slice of functionality across all architectural layers before building out breadth. Proves the architecture works for one complete path before investing in full feature development.",
    sdlcRole: "De-risks architecture decisions early. Instead of building all components and hoping they integrate, a steel thread proves the entire vertical stack works for one scenario first. This is especially critical for AI features where model integration, data pipelines, and UX patterns are all new.",
    whoCreates: "Architect and tech lead define the thread. A cross-functional pair (engineer + product) implements the minimal path. This is a collaborative exercise by design.",
    whoValidates: "Architecture review board or senior engineers validate that the thread proves the architecture. Product validates that the thread demonstrates real value, not just technical connectivity.",
    aiConsiderations: "Steel threads are particularly important for AI features because they surface integration challenges (latency, non-determinism, prompt engineering, output formatting) before the team has invested heavily. A steel thread for an AI feature should include: data in → model inference → output to user → feedback capture.",
    auditValue: "Documents that architectural decisions were validated empirically, not assumed. Steel thread results provide evidence of deliberate, risk-aware engineering—a key governance differentiator for AI-enabled systems."
  }
];

const RITUALS = [
  {
    id: "define-tsr",
    name: "Define Test Summary Report Standards",
    phase: "governance-setup",
    icon: "📋",
    description: "Establish a standardized template defining what a Test Summary Report (TSR) must contain: test objectives, scope (areas covered and not covered), testing approach, defect report, platform details, overall assessment, and go/no-go recommendation.",
    purpose: "Standardization reduces uncertainty and increases audit defensibility (Qodex). When every TSR follows the same structure, reviewers know exactly where to find critical information, teams can't accidentally omit required sections, and historical comparison becomes possible.",
    traditional: true,
    aiNew: true,
    aiRationale: "AI-era additions to the TSR standard include: AI model provenance documentation, non-determinism handling approach, bias/fairness test results, explainability assessments (Alation, IAA), adversarial testing results, and model card references (DoD AIES Guidebook). The FINOS framework adds requirements for documenting hallucination risk mitigation and foundation model versioning."
  },
  {
    id: "prepare-tsr",
    name: "Prepare Test Summary Report for Production",
    phase: "pre-production",
    icon: "📝",
    description: "For each proposed change to production, the responsible team prepares a TSR documenting: what was tested, what passed, what failed and why, what risks remain, and an explicit recommendation on production readiness.",
    purpose: "Forces the team to synthesize their testing work into a coherent narrative before asking for promotion to production. The act of writing the report often surfaces gaps that running the tests alone does not.",
    traditional: true,
    aiNew: true,
    aiRationale: "For AI-enabled changes, the TSR preparation must include evidence of model behavior testing beyond functional correctness: output appropriateness testing, fairness assessments, robustness checks, and continuous monitoring plans (IAA Testing Paper, Section 6-7). The FINOS risk catalogue requires documenting mitigations for operational risks like hallucination and non-deterministic behavior."
  },
  {
    id: "evaluate-tsr",
    name: "Evaluate Test Summary Report",
    phase: "gate",
    icon: "🔍",
    description: "An independent reviewer (not the author) evaluates the TSR against the defined standard. Checks: Are all required sections present and complete? Do test results support the go/no-go recommendation? Are there unaddressed risks? Is the evidence sufficient for production promotion?",
    purpose: "Separation of duties between preparation and evaluation is a core governance principle. The evaluator brings fresh eyes and can identify blind spots, missing coverage, or unsupported conclusions that the author may have normalized.",
    traditional: true,
    aiNew: true,
    aiRationale: "For AI features, the evaluator must assess whether the team has adequately tested for AI-specific risks: Has non-determinism been addressed? Are there fairness metrics? Has the team documented how they'll detect model drift post-deployment? The IAA framework emphasizes that AI testing requires 'continuous testing and monitoring' beyond the initial deployment gate."
  },
  {
    id: "monitor-production",
    name: "Post-Production Monitoring & Decision",
    phase: "post-production",
    icon: "📡",
    description: "After deployment, actively monitor the new code in production. Define success criteria and observation windows. Decide: Is it performing as expected? Does it need rollback? Are additional changes needed?",
    purpose: "Production is the ultimate test environment. Monitoring closes the feedback loop between what we thought would happen (the TSR) and what actually happened. This is where governance becomes operational.",
    traditional: true,
    aiNew: true,
    aiRationale: "AI systems require fundamentally different monitoring than traditional software. Model drift, changing data distributions, fairness degradation over time, and emergent behaviors that weren't present in testing are all AI-specific risks (FINOS AIR-OP-005, AIR-OP-006). The IAA paper emphasizes 'continuous monitoring' with 'feedback loops and model re-training' as essential lifecycle practices. The Alation governance framework stresses real-time performance tracking with drift and fairness metrics."
  }
];

const ROLES = [
  { id: "developer", name: "Developer / AI Builder", color: "#2E5C8A", abbrev: "DEV" },
  { id: "tech-lead", name: "Tech Lead / Architect", color: "#D4742C", abbrev: "TL" },
  { id: "qa", name: "QA / SDET", color: "#2D7D46", abbrev: "QA" },
  { id: "product", name: "Product Owner", color: "#6B4C9A", abbrev: "PO" },
  { id: "sre", name: "SRE / Platform", color: "#8B2252", abbrev: "SRE" },
  { id: "compliance", name: "Compliance / Governance", color: "#C4841D", abbrev: "GOV" },
  { id: "business", name: "Business Stakeholder", color: "#4A7C59", abbrev: "BIZ" }
];

const DEFAULT_ASSIGNMENTS = {
  "unit": { creates: ["developer"], validates: ["developer", "tech-lead"] },
  "integration": { creates: ["developer", "tech-lead"], validates: ["tech-lead", "qa"] },
  "e2e": { creates: ["qa"], validates: ["qa", "product"] },
  "performance": { creates: ["sre"], validates: ["sre", "tech-lead"] },
  "acceptance": { creates: ["product", "business"], validates: ["product", "business", "compliance"] },
  "steel-thread": { creates: ["developer", "tech-lead"], validates: ["tech-lead", "product"] },
  "define-tsr": { creates: ["tech-lead", "compliance"], validates: ["compliance"] },
  "prepare-tsr": { creates: ["developer", "qa"], validates: ["tech-lead"] },
  "evaluate-tsr": { creates: ["tech-lead", "compliance"], validates: ["compliance", "product"] },
  "monitor-production": { creates: ["sre", "developer"], validates: ["tech-lead", "product", "sre"] }
};

const FLOWCHART_NODES = [
  { id: "requirements", label: "Requirements & Design", phase: "plan", time: "1-2 weeks", bottleneck: "Misaligned stakeholder expectations; unclear AI behavior specifications" },
  { id: "steel-thread", label: "Steel Thread", phase: "validate", time: "3-5 days", bottleneck: "Architecture unknowns; AI model integration latency and non-determinism surfaced late" },
  { id: "implement", label: "Implementation", phase: "build", time: "1-4 weeks", bottleneck: "AI-generated code volume outpacing review capacity; comprehension debt" },
  { id: "unit-test", label: "Unit Testing", phase: "test", time: "Continuous", bottleneck: "AI-generated tests may be tautological; false confidence in coverage metrics" },
  { id: "integration-test", label: "Integration Testing", phase: "test", time: "2-5 days", bottleneck: "Environment availability; AI model endpoint instability; contract mismatches" },
  { id: "e2e-test", label: "E2E Testing", phase: "test", time: "3-5 days", bottleneck: "Non-deterministic AI outputs make assertions brittle; test flakiness" },
  { id: "perf-test", label: "Performance Testing", phase: "test", time: "2-3 days", bottleneck: "GPU/inference cost visibility; AI serving latency under load" },
  { id: "prepare-tsr", label: "Prepare TSR", phase: "govern", time: "1-2 days", bottleneck: "Incomplete AI-specific documentation; missing model cards or fairness data" },
  { id: "evaluate-tsr", label: "Evaluate TSR", phase: "govern", time: "1-2 days", bottleneck: "Reviewer lacks AI domain expertise; rubber-stamping vs. genuine evaluation" },
  { id: "acceptance", label: "Acceptance Testing", phase: "accept", time: "2-5 days", bottleneck: "Business stakeholders unsure how to evaluate AI behavior; unclear pass criteria" },
  { id: "deploy", label: "Deploy to Production", phase: "ship", time: "Hours-1 day", bottleneck: "Feature flags and rollback plans for AI features; canary deployment scope" },
  { id: "monitor", label: "Monitor & Decide", phase: "operate", time: "Ongoing", bottleneck: "Drift detection gaps; delayed feedback loops; unclear rollback triggers for AI" }
];

const PHASE_COLORS = {
  plan: "#6B7280", validate: "#C4841D", build: "#2E5C8A", test: "#2D7D46",
  govern: "#8B2252", accept: "#6B4C9A", ship: "#D4742C", operate: "#1B2A4A"
};

function RoleTag({ role, onRemove, small }) {
  const r = ROLES.find(rl => rl.id === role);
  if (!r) return null;
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 4,
      background: r.color + "18", color: r.color, border: `1px solid ${r.color}40`,
      borderRadius: 4, padding: small ? "1px 6px" : "2px 8px",
      fontSize: small ? 10 : 11, fontWeight: 600, letterSpacing: 0.3
    }}>
      {r.abbrev}
      {onRemove && <span onClick={onRemove} style={{ cursor: "pointer", marginLeft: 2, opacity: 0.6 }}>×</span>}
    </span>
  );
}

function RolePicker({ assigned, onToggle }) {
  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
      {ROLES.map(r => {
        const active = assigned.includes(r.id);
        return (
          <button key={r.id} onClick={() => onToggle(r.id)} style={{
            display: "inline-flex", alignItems: "center", gap: 3,
            background: active ? r.color + "20" : "#f8f8f8",
            color: active ? r.color : "#999",
            border: `1px solid ${active ? r.color + "60" : "#e0e0e0"}`,
            borderRadius: 4, padding: "2px 8px", fontSize: 11, fontWeight: 600,
            cursor: "pointer", transition: "all 0.15s", letterSpacing: 0.3
          }}>
            {active ? "✓ " : ""}{r.abbrev}
          </button>
        );
      })}
    </div>
  );
}

function FlowchartSVG({ assignments }) {
  const w = 920, nodeH = 52, nodeW = 150, gap = 12, rowGap = 70;
  const rows = [
    ["requirements", "steel-thread", "implement"],
    ["unit-test", "integration-test", "e2e-test", "perf-test"],
    ["prepare-tsr", "evaluate-tsr", "acceptance"],
    ["deploy", "monitor"]
  ];

  const positions = {};
  rows.forEach((row, ri) => {
    const totalW = row.length * nodeW + (row.length - 1) * gap;
    const startX = (w - totalW) / 2;
    row.forEach((id, ci) => {
      positions[id] = { x: startX + ci * (nodeW + gap), y: ri * rowGap + 20 };
    });
  });

  const connections = [
    ["requirements", "steel-thread"], ["steel-thread", "implement"],
    ["implement", "unit-test"], ["implement", "integration-test"],
    ["unit-test", "integration-test"], ["integration-test", "e2e-test"],
    ["e2e-test", "perf-test"], ["perf-test", "prepare-tsr"],
    ["e2e-test", "prepare-tsr"], ["prepare-tsr", "evaluate-tsr"],
    ["evaluate-tsr", "acceptance"], ["acceptance", "deploy"],
    ["deploy", "monitor"], ["monitor", "requirements"]
  ];

  const svgH = rows.length * rowGap + nodeH + 20;

  return (
    <svg viewBox={`0 0 ${w} ${svgH}`} style={{ width: "100%", height: "auto" }}>
      <defs>
        <marker id="arrow" viewBox="0 0 10 7" refX="10" refY="3.5" markerWidth="8" markerHeight="6" orient="auto-start-reverse">
          <polygon points="0 0, 10 3.5, 0 7" fill="#999" />
        </marker>
      </defs>
      {connections.map(([from, to], i) => {
        const fp = positions[from], tp = positions[to];
        if (!fp || !tp) return null;
        const fx = fp.x + nodeW / 2, fy = fp.y + nodeH;
        const tx = tp.x + nodeW / 2, ty = tp.y;
        const isLoop = from === "monitor" && to === "requirements";
        if (isLoop) {
          return (
            <path key={i} d={`M ${fx} ${fy} C ${fx + 80} ${fy + 40}, ${w - 20} ${svgH - 10}, ${w - 10} ${20} C ${w} ${0}, ${tp.x + nodeW + 30} ${ty + nodeH / 2}, ${tp.x + nodeW} ${ty + nodeH / 2}`}
              fill="none" stroke="#ccc" strokeWidth={1.5} strokeDasharray="4 3" markerEnd="url(#arrow)" />
          );
        }
        const midY = (fy + ty) / 2;
        return (
          <path key={i} d={`M ${fx} ${fy} C ${fx} ${midY}, ${tx} ${midY}, ${tx} ${ty}`}
            fill="none" stroke="#bbb" strokeWidth={1.5} markerEnd="url(#arrow)" />
        );
      })}
      {FLOWCHART_NODES.map(node => {
        const pos = positions[node.id];
        if (!pos) return null;
        const pc = PHASE_COLORS[node.phase];
        return (
          <g key={node.id}>
            <rect x={pos.x} y={pos.y} width={nodeW} height={nodeH} rx={6}
              fill={pc + "12"} stroke={pc} strokeWidth={1.5} />
            <text x={pos.x + nodeW / 2} y={pos.y + 18} textAnchor="middle"
              fontSize={10} fontWeight={700} fill={pc} fontFamily="system-ui">
              {node.label}
            </text>
            <text x={pos.x + nodeW / 2} y={pos.y + 32} textAnchor="middle"
              fontSize={8.5} fill="#888" fontFamily="system-ui">
              {node.time}
            </text>
            <text x={pos.x + nodeW / 2} y={pos.y + 44} textAnchor="middle"
              fontSize={7} fill={pc + "99"} fontFamily="system-ui" fontStyle="italic">
              {node.phase.toUpperCase()}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

export default function SDLCGovernanceBreadboard() {
  const [activeTab, setActiveTab] = useState("tests");
  const [expandedItem, setExpandedItem] = useState(null);
  const [assignments, setAssignments] = useState(DEFAULT_ASSIGNMENTS);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [filterAI, setFilterAI] = useState("all");

  const toggleAssignment = useCallback((itemId, type, roleId) => {
    setAssignments(prev => {
      const current = prev[itemId]?.[type] || [];
      const next = current.includes(roleId)
        ? current.filter(r => r !== roleId)
        : [...current, roleId];
      return { ...prev, [itemId]: { ...prev[itemId], [type]: next } };
    });
  }, []);

  const generateAIAnalysis = useCallback(async () => {
    setAiLoading(true);
    const assignmentSummary = Object.entries(assignments).map(([id, roles]) => {
      const item = [...TESTS, ...RITUALS].find(t => t.id === id);
      return `${item?.name}: Created by [${(roles.creates || []).join(", ")}], Validated by [${(roles.validates || []).join(", ")}]`;
    }).join("\n");

    try {
      const response = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 1000,
          system: `You are an expert in SDLC governance, testing strategy, and AI-era software development. Analyze the responsibility assignments for testing and governance rituals. Return ONLY valid JSON with no markdown. Structure: {"bottlenecks":[{"area":"...","risk":"high|medium|low","issue":"...","suggestion":"..."}],"handoffDelays":[{"from":"...","to":"...","estimatedDelay":"...","cause":"..."}],"accelerators":["..."],"overallAssessment":"..."}`,
          messages: [{
            role: "user",
            content: `Analyze these test and governance responsibility assignments for bottlenecks, handoff delays, and acceleration opportunities. Consider the Jobs to Be Done theory—governance should accelerate experimentation that leads to products which truly matter for people.\n\nAssignments:\n${assignmentSummary}\n\nIdentify: 1) Bottleneck areas where responsibilities are concentrated or misaligned, 2) Handoff delays between phases, 3) Opportunities to accelerate without sacrificing quality. Return JSON only.`
          }]
        })
      });
      const data = await response.json();
      const text = data.content?.map(i => i.text || "").join("") || "";
      const cleaned = text.replace(/```json|```/g, "").trim();
      setAiAnalysis(JSON.parse(cleaned));
    } catch (err) {
      setAiAnalysis({ error: "Analysis unavailable. Review the flowchart and bottleneck table below for manual assessment.", bottlenecks: [], handoffDelays: [], accelerators: [], overallAssessment: "Unable to generate AI analysis. Please review the governance flowchart and bottleneck analysis table manually." });
    }
    setAiLoading(false);
  }, [assignments]);

  const items = activeTab === "tests" ? TESTS : RITUALS;
  const filtered = filterAI === "all" ? items : filterAI === "ai-new" ? items.filter(i => i.aiNew) : items.filter(i => i.traditional && !i.aiNew);

  return (
    <div style={{ fontFamily: "'Newsreader', 'Georgia', serif", background: "#FAFAF8", minHeight: "100vh", color: "#1a1a1a" }}>
      <link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,wght@0,300;0,400;0,600;0,700;1,300;1,400&family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />

      {/* Header */}
      <div style={{ background: "linear-gradient(135deg, #1B2A4A 0%, #2E3D5F 50%, #1B2A4A 100%)", padding: "40px 32px 32px", borderBottom: "3px solid #C4841D" }}>
        <div style={{ maxWidth: 1100, margin: "0 auto" }}>
          <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 11, letterSpacing: 3, color: "#C4841D", textTransform: "uppercase", marginBottom: 8 }}>
            SDLC Governance Breadboard
          </div>
          <h1 style={{ fontFamily: "'Newsreader', serif", fontSize: 32, fontWeight: 300, color: "#fff", margin: 0, lineHeight: 1.2 }}>
            Testing, Governance & the Path to Production
          </h1>
          <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 13, color: "#94A3B8", marginTop: 10, lineHeight: 1.6, maxWidth: 700 }}>
            An interactive exploration of test types, governance rituals, and responsibility assignments—designed to spark conversation about how governance choices accelerate or brake the experimentation that leads to products which truly matter.
          </p>
        </div>
      </div>

      <div style={{ maxWidth: 1100, margin: "0 auto", padding: "24px 32px" }}>

        {/* Tab Navigation */}
        <div style={{ display: "flex", gap: 2, marginBottom: 20 }}>
          {[
            { id: "tests", label: "Test Types", count: TESTS.length },
            { id: "rituals", label: "Governance Rituals", count: RITUALS.length },
            { id: "flowchart", label: "Path to Production" },
            { id: "analysis", label: "AI Bottleneck Analysis" }
          ].map(tab => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{
              fontFamily: "'DM Sans', sans-serif", fontSize: 12, fontWeight: 600,
              padding: "10px 20px", border: "none", cursor: "pointer",
              background: activeTab === tab.id ? "#1B2A4A" : "#E8E8E4",
              color: activeTab === tab.id ? "#fff" : "#666",
              borderRadius: tab.id === "tests" ? "6px 0 0 6px" : tab.id === "analysis" ? "0 6px 6px 0" : 0,
              transition: "all 0.15s", letterSpacing: 0.3
            }}>
              {tab.label}{tab.count ? ` (${tab.count})` : ""}
            </button>
          ))}
        </div>

        {/* Filter for AI-era vs Traditional */}
        {(activeTab === "tests" || activeTab === "rituals") && (
          <div style={{ display: "flex", gap: 8, marginBottom: 20, alignItems: "center" }}>
            <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 11, color: "#888", letterSpacing: 0.5, textTransform: "uppercase" }}>Filter:</span>
            {[
              { id: "all", label: "All" },
              { id: "traditional", label: "Traditional SDLC" },
              { id: "ai-new", label: "New/Changed for AI Era" }
            ].map(f => (
              <button key={f.id} onClick={() => setFilterAI(f.id)} style={{
                fontFamily: "'DM Sans', sans-serif", fontSize: 11, padding: "4px 12px",
                border: `1px solid ${filterAI === f.id ? "#C4841D" : "#ddd"}`,
                background: filterAI === f.id ? "#C4841D10" : "transparent",
                color: filterAI === f.id ? "#C4841D" : "#888",
                borderRadius: 4, cursor: "pointer", fontWeight: 500
              }}>
                {f.label}
              </button>
            ))}
          </div>
        )}

        {/* Tests / Rituals Cards */}
        {(activeTab === "tests" || activeTab === "rituals") && (
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {filtered.map(item => {
              const isExpanded = expandedItem === item.id;
              const itemAssign = assignments[item.id] || { creates: [], validates: [] };
              return (
                <div key={item.id} style={{
                  background: "#fff", border: "1px solid #E4E4E0", borderRadius: 8,
                  overflow: "hidden", transition: "all 0.2s",
                  boxShadow: isExpanded ? "0 4px 20px rgba(0,0,0,0.08)" : "0 1px 3px rgba(0,0,0,0.04)"
                }}>
                  {/* Card Header */}
                  <div onClick={() => setExpandedItem(isExpanded ? null : item.id)}
                    style={{ padding: "16px 20px", cursor: "pointer", display: "flex", alignItems: "center", gap: 14 }}>
                    <span style={{ fontSize: 22, color: item.color || "#C4841D" }}>{item.icon}</span>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 14, fontWeight: 700, color: "#1a1a1a" }}>
                          {item.name}
                        </span>
                        {item.traditional && !item.aiNew && (
                          <span style={{ fontSize: 9, padding: "1px 6px", background: "#E8F0F8", color: "#2E5C8A", borderRadius: 3, fontFamily: "'DM Sans', sans-serif", fontWeight: 600, letterSpacing: 0.3 }}>
                            TRADITIONAL
                          </span>
                        )}
                        {item.aiNew && (
                          <span style={{ fontSize: 9, padding: "1px 6px", background: "#FDF3EB", color: "#C4841D", borderRadius: 3, fontFamily: "'DM Sans', sans-serif", fontWeight: 600, letterSpacing: 0.3 }}>
                            {item.traditional ? "EVOLVED FOR AI" : "NEW FOR AI ERA"}
                          </span>
                        )}
                      </div>
                      <p style={{ fontFamily: "'Newsreader', serif", fontSize: 13, color: "#666", margin: "4px 0 0", lineHeight: 1.4 }}>
                        {item.description}
                      </p>
                    </div>
                    <div style={{ display: "flex", gap: 3, flexShrink: 0 }}>
                      {(itemAssign.creates || []).map(r => <RoleTag key={`c-${r}`} role={r} small />)}
                      <span style={{ color: "#ccc", fontSize: 10, alignSelf: "center" }}>→</span>
                      {(itemAssign.validates || []).map(r => <RoleTag key={`v-${r}`} role={r} small />)}
                    </div>
                    <span style={{ color: "#ccc", fontSize: 16, transform: isExpanded ? "rotate(180deg)" : "rotate(0)", transition: "transform 0.2s" }}>▾</span>
                  </div>

                  {/* Expanded Detail */}
                  {isExpanded && (
                    <div style={{ padding: "0 20px 20px", borderTop: "1px solid #f0f0ec" }}>
                      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginTop: 16 }}>
                        {/* Left Column */}
                        <div>
                          {item.sdlcRole && (
                            <div style={{ marginBottom: 16 }}>
                              <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 10, fontWeight: 700, color: "#999", letterSpacing: 1, textTransform: "uppercase", marginBottom: 6 }}>
                                Role in the SDLC
                              </div>
                              <p style={{ fontFamily: "'Newsreader', serif", fontSize: 13.5, color: "#444", lineHeight: 1.6, margin: 0 }}>
                                {item.sdlcRole}
                              </p>
                            </div>
                          )}
                          {item.purpose && (
                            <div style={{ marginBottom: 16 }}>
                              <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 10, fontWeight: 700, color: "#999", letterSpacing: 1, textTransform: "uppercase", marginBottom: 6 }}>
                                Purpose
                              </div>
                              <p style={{ fontFamily: "'Newsreader', serif", fontSize: 13.5, color: "#444", lineHeight: 1.6, margin: 0 }}>
                                {item.purpose}
                              </p>
                            </div>
                          )}
                          {(item.aiConsiderations || item.aiRationale) && (
                            <div style={{ background: "#FDF3EB", border: "1px solid #C4841D30", borderRadius: 6, padding: 14 }}>
                              <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 10, fontWeight: 700, color: "#C4841D", letterSpacing: 1, textTransform: "uppercase", marginBottom: 6 }}>
                                {item.aiConsiderations ? "AI-Era Considerations" : "What's New for AI"}
                              </div>
                              <p style={{ fontFamily: "'Newsreader', serif", fontSize: 13, color: "#7A5A30", lineHeight: 1.6, margin: 0 }}>
                                {item.aiConsiderations || item.aiRationale}
                              </p>
                            </div>
                          )}
                        </div>
                        {/* Right Column - Role Assignments */}
                        <div>
                          <div style={{ marginBottom: 16 }}>
                            <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 10, fontWeight: 700, color: "#999", letterSpacing: 1, textTransform: "uppercase", marginBottom: 6 }}>
                              Audit & Standardization Value
                            </div>
                            <p style={{ fontFamily: "'Newsreader', serif", fontSize: 13, color: "#444", lineHeight: 1.6, margin: 0 }}>
                              {item.auditValue || "Standardizing this ritual across all teams reduces uncertainty for reviewers and increases defensibility during audits. Consistent processes create predictable, comparable artifacts."}
                            </p>
                          </div>
                          <div style={{ background: "#F6F6F4", borderRadius: 6, padding: 14, marginBottom: 12 }}>
                            <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 10, fontWeight: 700, color: "#999", letterSpacing: 1, textTransform: "uppercase", marginBottom: 8 }}>
                              Who Creates
                            </div>
                            <RolePicker assigned={itemAssign.creates || []} onToggle={(r) => toggleAssignment(item.id, "creates", r)} />
                          </div>
                          <div style={{ background: "#F6F6F4", borderRadius: 6, padding: 14 }}>
                            <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 10, fontWeight: 700, color: "#999", letterSpacing: 1, textTransform: "uppercase", marginBottom: 8 }}>
                              Who Validates
                            </div>
                            <RolePicker assigned={itemAssign.validates || []} onToggle={(r) => toggleAssignment(item.id, "validates", r)} />
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* Flowchart Tab */}
        {activeTab === "flowchart" && (
          <div>
            <div style={{ background: "#fff", border: "1px solid #E4E4E0", borderRadius: 8, padding: 24, marginBottom: 20 }}>
              <h2 style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 16, fontWeight: 700, margin: "0 0 4px", color: "#1B2A4A" }}>
                Path to Production Flowchart
              </h2>
              <p style={{ fontFamily: "'Newsreader', serif", fontSize: 13, color: "#888", margin: "0 0 20px" }}>
                Each node shows the activity, estimated time, and lifecycle phase. The feedback loop from monitoring back to requirements reflects the continuous nature of production software.
              </p>
              <FlowchartSVG assignments={assignments} />
              <div style={{ display: "flex", flexWrap: "wrap", gap: 12, marginTop: 16, justifyContent: "center" }}>
                {Object.entries(PHASE_COLORS).map(([phase, color]) => (
                  <div key={phase} style={{ display: "flex", alignItems: "center", gap: 4 }}>
                    <div style={{ width: 10, height: 10, borderRadius: 2, background: color }} />
                    <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 10, color: "#888", textTransform: "uppercase", letterSpacing: 0.5 }}>{phase}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Bottleneck Table */}
            <div style={{ background: "#fff", border: "1px solid #E4E4E0", borderRadius: 8, overflow: "hidden" }}>
              <div style={{ padding: "16px 20px", borderBottom: "1px solid #f0f0ec" }}>
                <h3 style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 14, fontWeight: 700, margin: 0, color: "#1B2A4A" }}>
                  Activity Bottleneck Analysis
                </h3>
                <p style={{ fontFamily: "'Newsreader', serif", fontSize: 12, color: "#888", margin: "4px 0 0" }}>
                  Each activity on the path to production has potential bottlenecks. Governance choices—who is responsible, what standards exist, how handoffs work—determine whether these bottlenecks accelerate or brake experimentation.
                </p>
              </div>
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontFamily: "'DM Sans', sans-serif", fontSize: 12 }}>
                  <thead>
                    <tr style={{ background: "#F6F6F4" }}>
                      {["Activity", "Phase", "Time", "Potential Bottleneck", "Governance Lever"].map(h => (
                        <th key={h} style={{ padding: "10px 14px", textAlign: "left", fontWeight: 700, fontSize: 10, letterSpacing: 0.5, color: "#888", textTransform: "uppercase", borderBottom: "1px solid #e4e4e0" }}>
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {FLOWCHART_NODES.map((node, i) => (
                      <tr key={node.id} style={{ background: i % 2 ? "#FAFAF8" : "#fff" }}>
                        <td style={{ padding: "10px 14px", fontWeight: 600, color: PHASE_COLORS[node.phase], borderBottom: "1px solid #f0f0ec" }}>
                          {node.label}
                        </td>
                        <td style={{ padding: "10px 14px", borderBottom: "1px solid #f0f0ec" }}>
                          <span style={{ fontSize: 9, padding: "2px 6px", background: PHASE_COLORS[node.phase] + "15", color: PHASE_COLORS[node.phase], borderRadius: 3, fontWeight: 600, letterSpacing: 0.3, textTransform: "uppercase" }}>
                            {node.phase}
                          </span>
                        </td>
                        <td style={{ padding: "10px 14px", color: "#666", fontFamily: "'JetBrains Mono', monospace", fontSize: 11, borderBottom: "1px solid #f0f0ec" }}>
                          {node.time}
                        </td>
                        <td style={{ padding: "10px 14px", color: "#555", fontFamily: "'Newsreader', serif", fontSize: 12, lineHeight: 1.5, borderBottom: "1px solid #f0f0ec", maxWidth: 280 }}>
                          {node.bottleneck}
                        </td>
                        <td style={{ padding: "10px 14px", color: "#888", fontFamily: "'Newsreader', serif", fontSize: 11.5, fontStyle: "italic", lineHeight: 1.5, borderBottom: "1px solid #f0f0ec", maxWidth: 200 }}>
                          {node.phase === "govern" ? "Standardized TSR templates reduce reviewer decision fatigue" :
                           node.phase === "test" ? "Shared test standards make results comparable across teams" :
                           node.phase === "accept" ? "Clear acceptance criteria defined before development begins" :
                           node.phase === "operate" ? "Automated monitoring with defined rollback triggers" :
                           "Clear roles and responsibilities reduce ambiguity"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* JTBD Callout */}
            <div style={{ marginTop: 20, background: "#1B2A4A", borderRadius: 8, padding: 24, color: "#fff" }}>
              <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 10, letterSpacing: 2, color: "#C4841D", textTransform: "uppercase", marginBottom: 8 }}>
                Jobs to Be Done Perspective
              </div>
              <p style={{ fontFamily: "'Newsreader', serif", fontSize: 15, lineHeight: 1.7, margin: 0, color: "#CBD5E1" }}>
                Governance is not the opposite of experimentation—it is the infrastructure that makes experimentation safe enough to actually do. When teams trust the path to production, they experiment more boldly, not less. Every bottleneck in this flowchart is a place where governance either enables or prevents the team from learning whether their product truly accomplishes a job for someone. The goal is not to minimize governance—it is to make governance so standardized and predictable that teams spend their creative energy on the product, not on navigating the process.
              </p>
            </div>
          </div>
        )}

        {/* AI Analysis Tab */}
        {activeTab === "analysis" && (
          <div>
            <div style={{ background: "#fff", border: "1px solid #E4E4E0", borderRadius: 8, padding: 24, marginBottom: 20 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                <div>
                  <h2 style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 16, fontWeight: 700, margin: 0, color: "#1B2A4A" }}>
                    AI-Powered Governance Analysis
                  </h2>
                  <p style={{ fontFamily: "'Newsreader', serif", fontSize: 13, color: "#888", margin: "4px 0 0" }}>
                    Based on your current responsibility assignments, analyze bottlenecks and acceleration opportunities.
                  </p>
                </div>
                <button onClick={generateAIAnalysis} disabled={aiLoading} style={{
                  fontFamily: "'DM Sans', sans-serif", fontSize: 12, fontWeight: 700,
                  padding: "10px 24px", background: aiLoading ? "#ccc" : "#C4841D", color: "#fff",
                  border: "none", borderRadius: 6, cursor: aiLoading ? "default" : "pointer",
                  letterSpacing: 0.3
                }}>
                  {aiLoading ? "Analyzing..." : "⚡ Generate Analysis"}
                </button>
              </div>

              {/* Current Assignments Summary */}
              <div style={{ background: "#F6F6F4", borderRadius: 6, padding: 16, marginBottom: 16 }}>
                <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 10, fontWeight: 700, color: "#999", letterSpacing: 1, textTransform: "uppercase", marginBottom: 10 }}>
                  Current Assignments Summary
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                  {Object.entries(assignments).map(([id, roles]) => {
                    const item = [...TESTS, ...RITUALS].find(t => t.id === id);
                    return (
                      <div key={id} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11 }}>
                        <span style={{ fontFamily: "'DM Sans', sans-serif", fontWeight: 600, color: "#555", minWidth: 160 }}>
                          {item?.name}
                        </span>
                        <div style={{ display: "flex", gap: 2 }}>
                          {(roles.creates || []).map(r => <RoleTag key={`c-${r}`} role={r} small />)}
                          <span style={{ color: "#ccc", fontSize: 9, alignSelf: "center" }}>→</span>
                          {(roles.validates || []).map(r => <RoleTag key={`v-${r}`} role={r} small />)}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* AI Analysis Results */}
              {aiAnalysis && !aiAnalysis.error && (
                <div>
                  {aiAnalysis.overallAssessment && (
                    <div style={{ background: "#1B2A4A", borderRadius: 6, padding: 16, marginBottom: 16 }}>
                      <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 10, fontWeight: 700, color: "#C4841D", letterSpacing: 1, textTransform: "uppercase", marginBottom: 6 }}>
                        Overall Assessment
                      </div>
                      <p style={{ fontFamily: "'Newsreader', serif", fontSize: 14, color: "#CBD5E1", lineHeight: 1.6, margin: 0 }}>
                        {aiAnalysis.overallAssessment}
                      </p>
                    </div>
                  )}

                  {aiAnalysis.bottlenecks?.length > 0 && (
                    <div style={{ marginBottom: 16 }}>
                      <h3 style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 700, color: "#8B2252", marginBottom: 8 }}>
                        Identified Bottlenecks
                      </h3>
                      {aiAnalysis.bottlenecks.map((b, i) => (
                        <div key={i} style={{ background: b.risk === "high" ? "#FEE2E2" : b.risk === "medium" ? "#FEF3C7" : "#E8F0F8", borderRadius: 6, padding: 12, marginBottom: 8, borderLeft: `3px solid ${b.risk === "high" ? "#DC2626" : b.risk === "medium" ? "#D97706" : "#2E5C8A"}` }}>
                          <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 12, fontWeight: 700, color: "#333" }}>{b.area}</div>
                          <p style={{ fontFamily: "'Newsreader', serif", fontSize: 12.5, color: "#555", margin: "4px 0", lineHeight: 1.5 }}>{b.issue}</p>
                          <p style={{ fontFamily: "'Newsreader', serif", fontSize: 12, color: "#2D7D46", margin: 0, fontStyle: "italic" }}>💡 {b.suggestion}</p>
                        </div>
                      ))}
                    </div>
                  )}

                  {aiAnalysis.handoffDelays?.length > 0 && (
                    <div style={{ marginBottom: 16 }}>
                      <h3 style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 700, color: "#D4742C", marginBottom: 8 }}>
                        Handoff Delays
                      </h3>
                      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
                        <thead>
                          <tr style={{ background: "#F6F6F4" }}>
                            {["From", "To", "Est. Delay", "Cause"].map(h => (
                              <th key={h} style={{ padding: "8px 12px", textAlign: "left", fontFamily: "'DM Sans', sans-serif", fontWeight: 700, fontSize: 10, letterSpacing: 0.5, color: "#888", textTransform: "uppercase", borderBottom: "1px solid #e4e4e0" }}>{h}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {aiAnalysis.handoffDelays.map((h, i) => (
                            <tr key={i}>
                              <td style={{ padding: "8px 12px", fontFamily: "'DM Sans', sans-serif", fontWeight: 600, color: "#555", borderBottom: "1px solid #f0f0ec" }}>{h.from}</td>
                              <td style={{ padding: "8px 12px", fontFamily: "'DM Sans', sans-serif", fontWeight: 600, color: "#555", borderBottom: "1px solid #f0f0ec" }}>{h.to}</td>
                              <td style={{ padding: "8px 12px", fontFamily: "'JetBrains Mono', monospace", fontSize: 11, color: "#D4742C", borderBottom: "1px solid #f0f0ec" }}>{h.estimatedDelay}</td>
                              <td style={{ padding: "8px 12px", fontFamily: "'Newsreader', serif", color: "#666", borderBottom: "1px solid #f0f0ec" }}>{h.cause}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}

                  {aiAnalysis.accelerators?.length > 0 && (
                    <div>
                      <h3 style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 700, color: "#2D7D46", marginBottom: 8 }}>
                        Acceleration Opportunities
                      </h3>
                      {aiAnalysis.accelerators.map((a, i) => (
                        <div key={i} style={{ background: "#EBF5EE", borderRadius: 6, padding: 10, marginBottom: 6, borderLeft: "3px solid #2D7D46" }}>
                          <p style={{ fontFamily: "'Newsreader', serif", fontSize: 12.5, color: "#1a5632", margin: 0, lineHeight: 1.5 }}>🚀 {a}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {aiAnalysis?.error && (
                <div style={{ background: "#FEF3C7", borderRadius: 6, padding: 16, borderLeft: "3px solid #D97706" }}>
                  <p style={{ fontFamily: "'Newsreader', serif", fontSize: 13, color: "#92400E", margin: 0 }}>{aiAnalysis.error}</p>
                </div>
              )}
            </div>

            {/* Sources & Framework References */}
            <div style={{ background: "#fff", border: "1px solid #E4E4E0", borderRadius: 8, padding: 20 }}>
              <h3 style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 700, color: "#1B2A4A", marginTop: 0, marginBottom: 12 }}>
                Framework Sources & References
              </h3>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                {[
                  { name: "FINOS AI Governance Framework", org: "Fintech Open Source Foundation", focus: "Risk catalogue with operational, security, and regulatory risks for AI in financial services. Mitigations mapped to preventative and detective controls." },
                  { name: "IAA Testing of AI Models Paper", org: "International Actuarial Association", focus: "Comprehensive testing taxonomy: functional, integration, output appropriateness, security, bias/fairness, explainability. Continuous monitoring lifecycle." },
                  { name: "Alation Explainable AI Governance", org: "Alation", focus: "Transparency, accountability, fairness, and security as governance pillars. Model registries, data lineage, and audit-ready documentation." },
                  { name: "DoD DTE&A AIES Guidebook", org: "Dept. of Defense / IDA", focus: "Test and evaluation of AI-enabled systems. Model cards, data cards, assurance cases, and the SEPTAR framework for proactive T&E planning." },
                  { name: "Qodex Test Report Best Practices", org: "Qodex.ai", focus: "Standardized TSR templates, 8-step report creation process, audience-specific reporting, exit criteria assessment." }
                ].map((src, i) => (
                  <div key={i} style={{ background: "#F6F6F4", borderRadius: 6, padding: 12 }}>
                    <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 12, fontWeight: 700, color: "#1B2A4A" }}>{src.name}</div>
                    <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 10, color: "#888", marginBottom: 6 }}>{src.org}</div>
                    <p style={{ fontFamily: "'Newsreader', serif", fontSize: 12, color: "#666", margin: 0, lineHeight: 1.5 }}>{src.focus}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
