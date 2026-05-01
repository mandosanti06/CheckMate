# CheckMate Schemas

Use these schemas as implementation templates. Keep messages and outputs
structured so authority boundaries are enforceable.

## Agent Interface

```json
{
  "agent_id": "bishop_1",
  "piece": "bishop",
  "role": "causal_reasoning",
  "input": {
    "goal": "string",
    "context": {},
    "constraints": [],
    "available_tools": [],
    "messages": []
  },
  "output": {
    "status": "success | blocked | needs_clarification | conflict",
    "summary": "string",
    "findings": [],
    "recommendations": [],
    "risks": [],
    "proposed_actions": [],
    "confidence": 0.0
  },
  "metadata": {
    "timestamp": "ISO-8601",
    "reasoning_mode": "linear | diagonal | nonlinear | executive | evaluative | atomic",
    "dependencies": [],
    "escalation_target": "king | queen | rook | bishop | knight | none"
  }
}
```

## Message

```json
{
  "message_id": "msg_001",
  "from": "bishop_1",
  "to": "queen",
  "type": "analysis_report",
  "priority": "low | normal | high | critical",
  "payload": {
    "claim": "The proposed plan has a long-term dependency risk.",
    "evidence": [],
    "recommended_action": "Ask rook_1 to validate the dependency chain."
  },
  "requires_response": true,
  "allowed_responses": [
    "acknowledge",
    "request_more_detail",
    "reject",
    "escalate"
  ]
}
```

## Board State

```json
{
  "goal": "Build a project plan for X",
  "constraints": [],
  "active_agents": [],
  "tasks": [],
  "decisions": [],
  "risks": [],
  "conflicts": [],
  "status": "idle | planning | validating | executing | check | checkmate | complete"
}
```

## Conflict

```json
{
  "conflict_type": "goal | constraint | evidence | priority | execution | interpretation",
  "agents_involved": [],
  "severity": "low | medium | high | critical",
  "blocking": true,
  "claims": [
    {
      "claim": "string",
      "evidence": [],
      "risk_if_wrong": "string",
      "confidence": 0.0,
      "preferred_resolution": "string"
    }
  ]
}
```

## Message Types

- `goal_order`
- `task_assignment`
- `analysis_report`
- `constraint_report`
- `creative_proposal`
- `execution_report`
- `conflict_notice`
- `approval_request`
- `veto_notice`
- `promotion_request`

## Conflict Outcomes

- `accept_plan`
- `revise_plan`
- `split_plan`
- `run_experiment`
- `escalate_to_king`
- `declare_check`
- `declare_checkmate`

