export function normalizeAction(text) {
  let result = text.toLowerCase().replace(/[^a-z0-9 ]+/g, " ");
  result = result.replace(/\b(must|should|required|requires|require|cannot|can not|use|using)\b/g, " ");
  result = result.replace(/\b(no|not|the|a|an|to|on|with|without)\b/g, " ");
  result = result.replace(/apis/g, "api");
  return result.split(/\s+/).filter(Boolean).join(" ");
}

export function findConstraintContradiction(constraints) {
  const positive = {};
  const negative = {};

  for (const raw of constraints) {
    const text = raw.toLowerCase();
    const hasNegative = /\b(must not|cannot|can not|no)\b/.test(text);
    const hasPositive = /\b(must|requires|required)\b/.test(text);

    if (hasPositive && !hasNegative) {
      positive[normalizeAction(text)] = raw;
    }
    if (hasNegative) {
      negative[normalizeAction(text)] = raw;
    }
  }

  for (const [action, posText] of Object.entries(positive)) {
    if (action && Object.prototype.hasOwnProperty.call(negative, action)) {
      return `Hard constraints contradict each other: '${posText}' conflicts with '${negative[action]}'.`;
    }
  }
  return null;
}

export const PIECES = {
  king: "Define objective, constraints, success criteria, and final decision.",
  queen: "Decompose, assign, sequence, and synthesize the plan.",
  bishop_causal: "Analyze causes, dependencies over time, and second-order effects.",
  bishop_pattern: "Identify reusable patterns, analogies, and strategic tradeoffs.",
  rook_logic: "Validate rules, contradictions, dependencies, and acceptance criteria.",
  rook_resource: "Validate time, resources, tools, capacity, and external limits.",
  knight_creative: "Generate alternatives, simplifications, and unexpected paths.",
  knight_recovery: "Generate fallback paths, workarounds, and recovery experiments.",
  pawn_research: "Gather raw information and sources.",
  pawn_writing: "Draft or rewrite text.",
  pawn_coding: "Implement code changes.",
  pawn_design: "Shape UX, wireframes, or visual hierarchy.",
  pawn_data: "Handle tables, schemas, metrics, or calculations.",
  pawn_communication: "Prepare stakeholder messages.",
  pawn_operations: "Run checklists, schedules, or deployment steps.",
  pawn_qa: "Test, review, and report defects."
};

export function buildBoard(goal, constraints = []) {
  const contradiction = findConstraintContradiction(constraints);
  const conflicts = contradiction
    ? [
        {
          conflict_type: "constraint",
          severity: "critical",
          blocking: true,
          summary: contradiction,
          agents_involved: ["rook_logic", "king", "queen"]
        }
      ]
    : [];

  return {
    goal,
    constraints: constraints.map((description) => ({ description, hard: true })),
    status: contradiction ? "checkmate" : "planning",
    active_agents: Object.keys(PIECES),
    tasks: [
      {
        id: "king_goal",
        assigned_to: "king",
        title: "Define governance frame",
        expected_output: "Objective, constraints, success criteria, decision criteria."
      },
      {
        id: "queen_decompose",
        assigned_to: "queen",
        title: "Decompose objective",
        expected_output: "Workstreams, owners, dependencies, and approval request."
      },
      {
        id: "bishops_analyze",
        assigned_to: "bishop_causal,bishop_pattern",
        title: "Analyze meaning and consequences",
        expected_output: "Risks, forecasts, patterns, tradeoffs, recommendations."
      },
      {
        id: "rooks_validate",
        assigned_to: "rook_logic,rook_resource",
        title: "Validate feasibility",
        expected_output: "Valid, invalid, blocked, risk, or veto."
      },
      {
        id: "knights_explore",
        assigned_to: "knight_creative,knight_recovery",
        title: "Explore alternatives",
        expected_output: "Alternatives, workarounds, assumption challenges, recovery paths."
      },
      {
        id: "pawns_execute",
        assigned_to: "pawns",
        title: "Execute atomic tasks",
        expected_output: "Evidence-backed execution reports and blockers."
      }
    ],
    decisions: [],
    risks: [],
    conflicts,
    metadata: {
      generated_at: new Date().toISOString(),
      runtime: "checkmate-agent-system npm cli"
    }
  };
}

export function formatText(board) {
  const constraints = board.constraints.length
    ? board.constraints
    : [{ description: "none specified" }];

  const lines = [
    "CheckMate Brief",
    "",
    `King: ${board.goal}`,
    "Constraints:",
    ...constraints.map((item) => `- ${item.description}`),
    "",
    "Bishops: analyze causal implications, patterns, risks, and tradeoffs.",
    "Rooks: validate hard constraints, dependencies, resources, and timeline.",
    "Knights: propose alternatives, assumption challenges, and recovery paths.",
    "Queen: synthesize a dependency-ordered plan and request approval.",
    "Pawns: execute the smallest concrete tasks and report evidence.",
    "Decision: pending King approval.",
    "",
    "Suggested tasks:",
    ...board.tasks.map((task) => `- ${task.id} (${task.assigned_to}): ${task.title}`)
  ];

  if (board.status === "checkmate" && board.conflicts && board.conflicts.length) {
    const summary = board.conflicts[0].summary;
    lines.unshift(
      `CHECKMATE: ${summary}`,
      "The King must relax the objective, relax constraints, or redefine success.",
      ""
    );
  }

  return lines.join("\n");
}

