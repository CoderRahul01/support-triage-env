---
title: Enterprise Support Operations Benchmark
emoji: 🎫
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
app_port: 8000
tags:
  - openenv
---

# Enterprise Support Operations Benchmark (ESOB)

> **OpenEnv-compliant** reinforcement learning environment for training and evaluating AI agents on enterprise support operations — a domain requiring real business judgment, SLA-aware prioritisation, and multi-turn negotiation under emotional escalation.

[![Phase 1](https://img.shields.io/badge/Phase%201-Passed-brightgreen)](https://github.com/CoderRahul01/Enterprise-Support-Operations-Benchmark)
[![Phase 2](https://img.shields.io/badge/Phase%202-Passed-brightgreen)](https://github.com/CoderRahul01/Enterprise-Support-Operations-Benchmark)
[![HF Space](https://img.shields.io/badge/HuggingFace-Space-yellow)](https://huggingface.co/spaces/PengoSword123/enterprise-support-operations-benchmark)

---

## Motivation

Most LLM benchmarks test knowledge retrieval or reasoning over clean inputs. Real enterprise work is different: it requires **judgment under ambiguity**, **prioritisation under time pressure**, and **managing human emotion** — all at once, with incomplete information, while business consequences accumulate in the background.

Customer support operations are the highest-volume instance of this problem at every company on earth. Every hour, support agents must decide: which ticket is truly urgent vs. merely loud? Which queue order minimises SLA breaches? How do you handle a customer who gives you nothing to work with, then escalates when your first answer misses the mark?

Current LLM evaluations have no environment that specifically tests this combination. ESOB fills that gap — providing a training signal for LLMs to develop **business judgment**, not just language fluency.

---

## Why This Matters for RL Training

ESOB is designed to develop four capabilities that are poorly addressed by existing benchmarks:

| Capability | How ESOB trains it |
|---|---|
| **Ambiguity resolution** | `resolve_ticket` withholds key information; agent must ask one targeted question to uncover the real issue |
| **SLA-aware prioritisation** | `triage_queue` rewards agents that correctly rank tickets by deadline proximity using a Kendall tau grader |
| **Emotional escalation management** | `resolve_ticket` generates a deterministic customer reaction; vague plans trigger an escalating customer in step 3 |
| **Business impact reasoning** | All graders distinguish urgency levels with real decision criteria: safety > security > financial > operational |

The partial reward structure means every step yields a training signal — including wrong answers — enabling incremental policy improvement without sparse reward problems.

---

## Novel Contributions

**1. SLA-Aware Queue Prioritisation with Kendall Tau Grader**

Each ticket in `triage_queue` carries a `deadline_minutes` field — the SLA breach threshold. The agent must output a `processing_order` list ranking all 5 tickets to minimise total SLA breaches. The grader scores this using normalised Kendall tau correlation between the agent's order and the optimal order (shortest deadline first, ties broken by urgency). This is a genuine operations research sub-problem embedded in the environment, not available in any other support triage benchmark.

**2. Stateful Customer Simulation with Deterministic Reply Templates**

`resolve_ticket` is a 3-step multi-turn negotiation. After the agent's clarifying question (step 1), the environment reveals a pre-written customer reply. After the agent's resolution plan (step 2), the environment deterministically generates a customer reaction — *satisfied* or *escalating* — based on whether the plan contains the required resolution keywords. No LLM is involved in generating customer state; everything is reproducible and auditable.

**3. Multi-Turn Negotiation Scoring with Component-Level Partial Credit**

`resolve_ticket` scores each step independently:
- Step 1: clarification targeting quality (0.25 max)
- Step 2: resolution plan completeness — empathy + specific action keywords + timeline commitment (0.50 max, three components scored separately)
- Step 3: closure quality conditioned on whether the customer is satisfied or escalating (0.25 max)

This creates a fine-grained reward signal that distinguishes agents who can *almost* negotiate from agents who fail at the first ambiguity.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      inference.py                           │
│  ┌──────────┐   ┌─────────────┐   ┌──────────────────────┐ │
│  │  reset() │──▶│ Task-specific│──▶│   parse_action()     │ │
│  │  (task)  │   │ LLM prompt  │   │   JSON → SupportAction│ │
│  └────┬─────┘   └─────────────┘   └──────────┬───────────┘ │
│       │                                        │             │
│       ▼                                        ▼             │
│  ┌──────────┐                        ┌──────────────────┐   │
│  │  step()  │◀───────────────────────│  env.step()      │   │
│  │  (grader │                        │  (deterministic  │   │
│  │  reward) │                        │   graders)       │   │
│  └──────────┘                        └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────┐
│  FastAPI Server     │  ← OpenEnv HTTP interface
│  POST /reset        │
│  POST /step         │
│  GET  /health       │
│  GET  /metadata     │
│  GET  /schema       │
│  GET  /docs         │
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
| Score range | (0.001, 0.999) — epsilon-clamped |
| Reward type | Partial, deterministic, component-level |
| Dataset | 40 tickets · 8 queues with SLA deadlines · 8 ambiguous tickets with customer simulation |
| Concurrent sessions | Supported |
| Graders | 100% deterministic — zero LLM calls inside graders |

---

## Tasks

### Task 1 — `classify_ticket` ★☆☆☆ Easy · 2 steps

| Step | Action | Max Reward |
|---|---|---|
| 1 | Category: `billing` / `technical` / `account` / `general` | +0.50 |
| 2 | Urgency: `low` / `medium` / `high` / `critical` | +0.50 |

**Challenge:** Several tickets sit at category and urgency boundaries (e.g. billing issues that manifest as account lockouts; technical errors that look like general how-to questions).

---

### Task 2 — `draft_response` ★★☆☆ Medium · 3 steps

| Step | Action | Max Reward |
|---|---|---|
| 1 | Category classification | +0.20 |
| 2 | Urgency classification | +0.10 |
| 3 | Full professional response draft | +0.70 |

The response is scored against a **7-criterion rubric** with a character trigram specificity bonus. Generic, template-like responses score poorly — the grader rewards vocabulary drawn from the actual ticket content.

---

### Task 3 — `triage_queue` ★★★☆ Hard · 2 steps

The agent sees a **queue of 5 tickets**, each with a `deadline_minutes` SLA field.

| Step | Action | Max Reward |
|---|---|---|
| 1 | Classify all 5 tickets + submit `processing_order` (SLA-ranked) | +0.50 |
| 2 | Identify the ONE escalation ticket + draft escalation response | +0.50 |

**Step 1 scoring breakdown:**
- Classification accuracy (category + urgency for all 5 tickets): up to +0.20
- SLA ordering quality via Kendall tau correlation: up to +0.30

**What makes it hard:** The SLA ordering and escalation decision are often in tension. The ticket with the tightest deadline is not always the ticket with the highest business impact. Agents must reason about both simultaneously.

**Hard queues with multiple criticals:**
- QUEUE-005: Hospital patient access (10 min SLA) vs DB corruption (18 min) vs SSL expiry (20 min) → *safety wins*
- QUEUE-006: Webhook killing 340 payments (15 min) vs project deletion (25 min) vs board login (30 min) → *widest financial impact wins*
- QUEUE-007: Wrong admin access (20 min, ongoing data exposure) vs SRE alerts broken (25 min) → *active security exposure wins*

---

### Task 4 — `resolve_ticket` ★★★★ Expert · 3 steps · Multi-turn Negotiation

The agent receives a **deliberately vague ticket** — the real issue is hidden. The environment simulates a real customer across all three steps.

| Step | Action | Grader | Max Reward |
|---|---|---|---|
| 1 | Ask ONE targeted clarifying question | Keyword targeting score | +0.25 |
| 2 | Submit resolution plan (action + timeline + empathy) | 3-component score | +0.50 |
| 3 | Write closure response acknowledging customer reaction | Reaction-conditioned score | +0.25 |

**The negotiation loop:**
1. Agent asks question → environment reveals pre-written customer reply (deterministic from dataset)
2. Agent submits resolution plan → environment generates customer reaction:
   - **Satisfied** if plan contains ≥ half of the required resolution keywords
   - **Escalating** if plan is vague or missing key commitments
3. Agent writes closure response acknowledging the reaction type — scoring is conditioned on which reaction was generated

**Why this is hard:** The agent cannot succeed by guessing. It must diagnose from limited information, ask the right question, commit to a specific plan (not just classify), then adapt its closure to whether the customer is satisfied or escalating. All 8 ambiguous tickets are designed so the vague subject maps plausibly to 2–3 different categories.

---

## Difficulty Progression

| Task | Difficulty | Expected: Weak Model | Expected: Strong Model | Ceiling |
|---|---|---|---|---|
| `classify_ticket` | ★☆☆☆ | 0.40–0.55 | 0.70–0.85 | 1.00 |
| `draft_response` | ★★☆☆ | 0.35–0.50 | 0.60–0.75 | 1.00 |
| `triage_queue` | ★★★☆ | 0.20–0.35 | 0.45–0.65 | 1.00 |
| `resolve_ticket` | ★★★★ | 0.15–0.30 | 0.35–0.55 | 1.00 |
| **Overall** | | **0.28–0.43** | **0.53–0.70** | **1.00** |

A model scoring > 0.75 on `resolve_ticket` would represent a genuine breakthrough in LLM negotiation capability.

---

## Dataset

| Type | Count | Coverage |
|---|---|---|
| Single tickets | 40 | Billing (12) · Technical (14) · Account (9) · General (5) |
| Triage queues | 8 | 2 easy · 3 medium · 3 hard (multi-critical) — all with SLA deadlines |
| Ambiguous tickets | 8 | With customer reply templates, reaction templates, required resolution keywords |

**Triage queue SLA ranges (deadline_minutes by urgency tier):**
- Critical: 10–30 min
- High: 75–120 min
- Medium: 180–480 min
- Low: 480–720 min

**Ambiguous ticket negotiation scenarios:**
- Billing/account overlap: payment failure causing account lockout, duplicate charge, seat overcharge
- Account/security: compromised account, former employee retaining admin access
- Technical/unclear: API rate limiting, CORS error after deployment, 503 endpoint failure
- Complex: customer escalating with active and ongoing revenue loss

---

## Reward Design

Rewards are **partial and deterministic** — no binary pass/fail. Every step yields a training signal.

### Classification rewards

| Outcome | Value |
|---|---|
| Correct classification | +0.10 to +0.50 (task-dependent) |
| Empty submission | −0.10 |
| Invalid value | −0.10 |
| Invalid escalation ticket ID | −0.15 |

### SLA ordering reward (triage_queue step 1)

| Outcome | Value |
|---|---|
| Perfect Kendall tau (τ = 1.0) | +0.30 |
| Partial match (τ = 0.5, random ordering) | +0.15 |
| Perfect reversal (τ = 0.0) | +0.00 |
| No `processing_order` submitted | +0.00 |

### Resolution plan reward (resolve_ticket step 2)

| Component | Condition | Value |
|---|---|---|
| Empathy | Any empathy keyword present | +0.10 |
| Specific action | ≥ half of `required_resolution_keywords` matched | +0.25 |
| Specific action (partial) | 1+ keywords matched, below threshold | +0.12 |
| Timeline commitment | Any timeline keyword present | +0.15 |

### Response quality rubric (7 criteria — used in draft_response and triage_queue step 2)

| Criterion | Points |
|---|---|
| Greeting | 0.10 |
| Empathy | 0.10 |
| Issue acknowledgment (≥2 ticket-specific keywords) | 0.25 |
| Resolution language (≥2 action words) | 0.20 |
| Timeline commitment | 0.10 |
| Length ≥ 100 chars | 0.15 |
| Professional tone | 0.10 |
| Trigram specificity bonus | up to +0.08 |
| Echo penalty (verbatim subject) | −0.10 |

---

## Agent Design (inference.py)

The baseline agent uses **task-specific system prompts** aligned precisely with each grader's rubric:

- `classify_ticket`: Decision trees for category and urgency with explicit boundary examples
- `draft_response`: Enumerates all 7 response rubric criteria with a worked example
- `triage_queue`: SLA ordering algorithm + escalation priority order (safety > security > financial > operational) with worked examples
- `resolve_ticket`: Three-phase negotiation guide — clarification strategy, resolution plan structure (empathy + action + timeline), closure conditioned on reaction type

**Robustness:** JSON retry mechanism — if the first response fails to parse, the bad output is sent back to the model with a correction request at temperature=0.

---

## API Reference

| Method | Path | Description |
|---|---|---|
| `POST` | `/reset` | Start episode: `{"task": "triage_queue", "seed": 42}` |
| `POST` | `/step` | Take action: `{"action": {<SupportAction fields>}}` |
| `GET` | `/state` | Current episode state |
| `GET` | `/health` | Health check |
| `GET` | `/metadata` | Environment metadata |
| `GET` | `/schema` | Action/observation JSON schema |
| `GET` | `/docs` | Swagger UI |

### Quick start

```bash
# Health check
curl https://pengosword123-enterprise-support-operations-benchmark.hf.space/health

# Reset — start a triage_queue episode
curl -X POST https://pengosword123-enterprise-support-operations-benchmark.hf.space/reset \
  -H "Content-Type: application/json" \
  -d '{"task": "triage_queue", "seed": 42}'

# Step — submit classifications + SLA processing order
curl -X POST https://pengosword123-enterprise-support-operations-benchmark.hf.space/step \
  -H "Content-Type: application/json" \
  -d '{
    "action": {
      "ticket_classifications": [
        {"ticket_id": "TKT-004", "classification": "account", "urgency": "critical"},
        {"ticket_id": "TKT-002", "classification": "technical", "urgency": "high"},
        {"ticket_id": "TKT-013", "classification": "technical", "urgency": "medium"},
        {"ticket_id": "TKT-005", "classification": "billing", "urgency": "low"},
        {"ticket_id": "TKT-009", "classification": "general", "urgency": "low"}
      ],
      "processing_order": ["TKT-004", "TKT-002", "TKT-013", "TKT-005", "TKT-009"]
    }
  }'
```

---

## Local Setup

```bash
git clone https://github.com/CoderRahul01/Enterprise-Support-Operations-Benchmark
cd Enterprise-Support-Operations-Benchmark

pip install -r requirements.txt

# Run environment server
uvicorn server.app:app --host 0.0.0.0 --port 8000

# Run baseline agent (requires HF_TOKEN)
export HF_TOKEN=hf_xxx
python inference.py
```

### Docker

```bash
docker build -t enterprise-support-ops-env .
docker run -p 8000:8000 enterprise-support-ops-env
curl http://localhost:8000/health
```

---

## Project Structure

```
support-triage-env/
├── server/
│   ├── __init__.py
│   └── app.py              # FastAPI app — OpenEnv HTTP interface
├── __init__.py
├── models.py               # SupportAction, SupportObservation, SupportState (Pydantic)
├── data.py                 # 40 tickets · 8 queues (SLA deadlines) · 8 ambiguous tickets
├── environment.py          # SupportTriageEnvironment + 4 task graders + Kendall tau + customer sim
├── inference.py            # Baseline agent (task-specific prompts + JSON retry)
├── openenv.yaml            # OpenEnv spec
├── Dockerfile              # python:3.11-slim, single worker
├── requirements.txt
└── README.md
```

---

## Design Rationale

**Why support operations?**
Every company with customers performs this work daily at scale. The domain is universally understood, ground-truth labels are objectively verifiable, and decision quality exists on a continuous spectrum — ideal for partial reward RL.

**Why SLA ordering?**
Queue prioritisation is an operations research problem that most LLMs perform poorly at because training data contains almost no explicit SLA reasoning. The Kendall tau grader provides a precise, continuous signal for this capability — not just "did you pick the right one" but "how wrong was your ordering, pair by pair."

**Why customer simulation in resolve_ticket?**
Negotiation training requires consequences. If a vague resolution plan has no downstream effect, agents never learn to commit to specifics. By generating a deterministic customer reaction based on plan quality, the environment creates a real stake: write a weak plan, face an escalating customer, score lower on step 3.

**Why partial rewards?**
Binary pass/fail creates sparse reward problems. Every step in ESOB yields a learning signal — even a wrong classification yields 0.0 rather than a penalty, so agents can improve incrementally. The component-level scoring in `resolve_ticket` means an agent that gets empathy and action right but forgets the timeline still scores 0.35/0.50, not 0.
