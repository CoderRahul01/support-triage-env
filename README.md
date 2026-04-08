---
title: Support Triage Environment Server
emoji: 🎫
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
app_port: 8000
tags:
  - openenv
---

# Support Triage Environment

> **OpenEnv-compliant** reinforcement learning environment for training and evaluating AI agents on customer support ticket triage — the real-world task every customer-facing company performs daily.

[![Phase 1](https://img.shields.io/badge/Phase%201-Passed-brightgreen)](https://github.com/CoderRahul01/support-triage-env)
[![Phase 2](https://img.shields.io/badge/Phase%202-Passed-brightgreen)](https://github.com/CoderRahul01/support-triage-env)
[![HF Space](https://img.shields.io/badge/HuggingFace-Space-yellow)](https://huggingface.co/spaces/PengoSword123/support-triage-env)

---

## What This Environment Tests

The agent must perform the same cognitive work a skilled support agent does every day:

1. **Read** a realistic customer support ticket (or queue of 5)
2. **Classify** the issue category and urgency level correctly
3. **Write** a professional, empathetic customer response
4. **Escalate** the right ticket from a mixed-priority queue
5. **Diagnose** an ambiguous complaint through targeted clarification

This is not a toy task. It requires multi-step reasoning, domain knowledge, and language quality — making it an ideal benchmark for frontier LLMs.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   inference.py                      │
│  ┌─────────┐    ┌──────────┐    ┌──────────────┐   │
│  │  reset  │───▶│  LLM     │───▶│  parse_action│   │
│  │  (task) │    │  (task-  │    │  (JSON→      │   │
│  └────┬────┘    │  specific│    │  SupportAction│  │
│       │         │  prompt) │    └──────┬───────┘   │
│       ▼         └──────────┘           │            │
│  ┌─────────┐                    ┌──────▼───────┐   │
│  │  step() │◀───────────────────│  env.step()  │   │
│  │  (grader│                    │  (grader)    │   │
│  │  reward)│                    └──────────────┘   │
│  └─────────┘                                        │
└─────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────┐
│  FastAPI Server     │  ← OpenEnv HTTP interface
│  POST /reset        │
│  POST /step         │
│  GET  /health       │
│  GET  /metadata     │
└─────────────────────┘
```

---

## Environment Overview

| Property | Value |
|---|---|
| Action type | `SupportAction` (JSON) |
| Observation type | `SupportObservation` |
| Tasks | **4** (easy → expert) |
| Episode length | 2–3 steps |
| Score range | (0, 1) per episode |
| Reward type | Partial, deterministic |
| Dataset | 40 tickets · 8 queues · 8 ambiguous tickets |
| Concurrent sessions | Supported |

---

## Tasks

### Task 1 — `classify_ticket` ★☆☆☆ Easy · 2 steps

The agent receives a single support ticket and must identify:

| Step | Action | Max Reward |
|---|---|---|
| 1 | Category: `billing` / `technical` / `account` / `general` | +0.50 |
| 2 | Urgency: `low` / `medium` / `high` / `critical` | +0.50 |

**Challenge:** Several tickets sit at category boundaries (e.g. billing issues that manifest as account lockouts; technical errors that look like general how-to questions).

---

### Task 2 — `draft_response` ★★☆☆ Medium · 3 steps

| Step | Action | Max Reward |
|---|---|---|
| 1 | Category classification | +0.20 |
| 2 | Urgency classification | +0.10 |
| 3 | Full professional response draft | +0.70 |

The response is scored against a **7-criterion rubric** (see Reward Design below). Agents that produce generic, template-like responses score poorly — the grader rewards specificity.

---

### Task 3 — `triage_queue` ★★★☆ Hard · 2 steps

The agent sees a **queue of 5 tickets** and must:

| Step | Action | Max Reward |
|---|---|---|
| 1 | Classify all 5 tickets (category + urgency) | +0.40 |
| 2 | Identify the ONE escalation ticket + draft response | +0.60 |

**What makes it hard:** 3 of the 8 queues contain **multiple critical-urgency tickets**. The agent must reason about comparative business impact to pick the right escalation:

- QUEUE-005: Hospital patient access vs SSL cert expiry vs DB corruption → *human safety wins*
- QUEUE-006: Webhook killing 340 payments vs board presentation vs project delete → *widest financial impact wins*
- QUEUE-007: Wrong admin (security exposure) vs SRE alerts broken → *active security risk wins*

---

### Task 4 — `resolve_ticket` ★★★★ Expert · 3 steps · Multi-turn

The agent receives a **deliberately vague ticket** — the real issue is hidden.

| Step | Action | Max Reward |
|---|---|---|
| 1 | Ask ONE targeted clarifying question | +0.10 |
| 2 | After customer reply: classify category + urgency | +0.40 |
| 3 | Write personalised resolution using full context | +0.50 |

**Penalty structure:**
- Off-target clarification question: **−0.05**
- No question submitted: **−0.10**

**Why this is hard:** The agent cannot succeed by guessing. It must diagnose from limited information, ask the right question, then synthesise the full picture from the customer reply. All 8 ambiguous tickets are designed so the vague subject maps plausibly to 2–3 different categories.

---

## Dataset

| Type | Count | Coverage |
|---|---|---|
| Single tickets | 40 | Billing (12) · Technical (14) · Account (9) · General (5) |
| Triage queues | 8 | 2 easy · 3 medium · 3 hard (multi-critical) |
| Ambiguous tickets | 8 | Billing↔Account (3) · Technical↔General (2) · Account↔Technical (3) |

All tickets are **synthetic but realistic** — modelled on actual support patterns across SaaS, e-commerce, fintech, and enterprise software companies. Ground-truth labels are manually verified.

---

## Reward Design

Rewards are **partial and deterministic** — no binary pass/fail. Every step yields a signal.

### Classification rewards

| Outcome | Value |
|---|---|
| Correct classification | +0.20 to +0.50 (task-dependent) |
| Correct urgency | +0.10 to +0.50 |
| Empty submission | −0.10 |
| Invalid value (not in allowed set) | −0.10 |
| Invalid escalation ticket ID | −0.15 |

### Response quality rubric (7 criteria)

Applied to `response_draft` and `escalation_response` fields:

| Criterion | Keywords checked | Points |
|---|---|---|
| Greeting | hello / hi / dear / thank you for | 0.10 |
| Empathy | sorry / apologise / understand / regret / sincerely | 0.10 |
| Issue acknowledgment | ≥2 ticket-specific keywords matched | 0.25 |
| Resolution language | resolve / fix / investigate / escalate / refund / restore + 15 more | 0.20 |
| Timeline commitment | within 24h / immediately / right away / asap / today | 0.10 |
| Length ≥ 100 chars | (professional response length) | 0.15 |
| Professional tone | absence of rude/dismissive language | 0.10 |

**Bonus:** Character trigram overlap between response and ticket keywords → up to +0.08 specificity bonus.

**Penalty:** Response echoes subject line verbatim → −0.10

---

## Agent Design (inference.py)

The baseline agent uses **task-specific system prompts** — one for each of the 4 tasks — each explicitly aligned with the grader's rubric:

- `classify_ticket`: Provides exact category/urgency decision trees with real examples
- `draft_response`: Enumerates all 7 response criteria the agent must include
- `triage_queue`: Encodes escalation priority order (safety > financial > operational)
- `resolve_ticket`: Guides clarification strategy and response personalisation

**Robustness:** The agent includes a JSON retry mechanism — if the first response fails to parse, it sends the bad output back to the model and requests a correction at temperature=0.

---

## Baseline Agent Scores

Measured with `Qwen/Qwen2.5-72B-Instruct` via HuggingFace Inference API (seed=42, temperature=0.1):

| Task | Difficulty | Score | Key challenge |
|---|---|---|---|
| `classify_ticket` | ★☆☆☆ | ~0.75 | Urgency level on boundary cases |
| `draft_response` | ★★☆☆ | ~0.70 | Ticket-specific keyword usage |
| `triage_queue` | ★★★☆ | ~0.55 | Multi-critical escalation reasoning |
| `resolve_ticket` | ★★★★ | ~0.50 | Targeted clarification question |
| **Overall** | | **~0.63** | |

---

## API Reference

| Method | Path | Description |
|---|---|---|
| `POST` | `/reset` | Start episode: `{"task": "classify_ticket", "seed": 42}` |
| `POST` | `/step` | Take action: `{"action": {<SupportAction fields>}}` |
| `GET` | `/state` | Current episode state |
| `GET` | `/health` | Health check |
| `GET` | `/metadata` | Environment metadata |
| `GET` | `/schema` | Action/observation JSON schema |
| `GET` | `/docs` | Swagger UI |

### Quick start

```bash
# Health check
curl https://pengosword123-support-triage-env.hf.space/health

# Reset
curl -X POST https://pengosword123-support-triage-env.hf.space/reset \
  -H "Content-Type: application/json" \
  -d '{"task": "classify_ticket", "seed": 42}'

# Step
curl -X POST https://pengosword123-support-triage-env.hf.space/step \
  -H "Content-Type: application/json" \
  -d '{"action": {"classification": "billing"}}'
```

---

## Local Setup

```bash
git clone https://github.com/CoderRahul01/support-triage-env
cd support-triage-env

pip install -r requirements.txt

# Run environment server
uvicorn server.app:app --host 0.0.0.0 --port 8000

# Run baseline agent (requires HF_TOKEN)
export HF_TOKEN=hf_xxx
python inference.py
```

### Docker

```bash
docker build -t support-triage-env .
docker run -p 8000:8000 support-triage-env
curl http://localhost:8000/health
```

---

## Project Structure

```
support-triage-env/
├── server/
│   ├── __init__.py
│   └── app.py            # FastAPI app — OpenEnv HTTP interface
├── __init__.py
├── models.py             # SupportAction, SupportObservation, SupportState (Pydantic)
├── data.py               # 40 tickets · 8 queues · 8 ambiguous tickets
├── environment.py        # SupportTriageEnvironment + 4 task graders
├── inference.py          # Baseline agent (task-specific prompts + JSON retry)
├── openenv.yaml          # OpenEnv spec
├── Dockerfile            # python:3.11-slim, single worker
├── requirements.txt
└── README.md
```

---

## Design Rationale

**Why support triage?**

- Every company with customers does this — the task is universally understood
- The correct answer is objectively verifiable (ground-truth labels)
- Response quality exists on a continuous spectrum — perfect for partial reward RL
- Multi-turn clarification tests a capability most benchmarks ignore

**Why partial rewards?**

Binary pass/fail creates sparse reward problems. The grader gives agents a learning signal at every step — even a wrong classification yields 0.0 (not a penalty), so agents can learn incrementally.

**Why 4 difficulty levels?**

Agents that can only classify struggle with drafting. Agents that draft well often fail at escalation reasoning. The resolve_ticket task filters out agents that cannot maintain context across turns. This creates a natural skill ladder.
