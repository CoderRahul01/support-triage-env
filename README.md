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

An **OpenEnv**-compliant environment for training and evaluating AI agents on
customer support ticket triage — a real-world task that every company with
customers performs daily.

The agent must read support tickets, classify their category and urgency, write
professional customer responses, and escalate critical cases. Three tasks progress
from easy to hard, with deterministic partial-credit graders at every step.

---

## Environment overview

| Property | Value |
|---|---|
| Action type | `SupportAction` (JSON) |
| Observation type | `SupportObservation` |
| Tasks | 3 (easy / medium / hard) |
| Episode length | 2–3 steps |
| Reward range | 0.0 – 1.0 per episode |
| Reward type | Partial, deterministic |

---

## Tasks

### Task 1 — `classify_ticket` (easy, 2 steps)

The agent receives a single support ticket and must identify:
- **Step 1:** Category — `billing`, `technical`, `account`, or `general`
- **Step 2:** Urgency — `low`, `medium`, `high`, or `critical`

Rewards: +0.50 per correct field → max **1.0**

### Task 2 — `draft_response` (medium, 3 steps)

The agent must classify the ticket AND write a professional response:
- **Step 1:** Category (+0.20 if correct)
- **Step 2:** Urgency (+0.10 if correct)
- **Step 3:** Response draft (+0.70 × quality score)

Response is scored on: greeting, issue acknowledgment, resolution language, length, professionalism.

Max reward: **1.0**

### Task 3 — `triage_queue` (hard, 2 steps)

The agent sees a queue of **5 tickets** and must:
- **Step 1:** Classify all 5 tickets (category + urgency each) → up to +0.40
- **Step 2:** Identify the one ticket needing escalation (+0.30) and draft a response (+0.30)

6 queues including 2 where **multiple tickets are critical** — agent must reason about business impact to pick the right one (QUEUE-005: hospital vs SSL vs DB; QUEUE-006: payments vs board login vs data loss).

Max reward: **1.0**

### Task 4 — `resolve_ticket` (expert, 3 steps, multi-turn)

The agent receives a **deliberately ambiguous ticket** where the subject is vague and the real issue is hidden. The agent must:
- **Step 1:** Ask ONE targeted clarifying question (+0.10 if relevant keywords matched, −0.05 if off-target, −0.10 if empty)
- **Step 2:** After the customer responds with full context, classify **both category AND urgency** (+0.25 + 0.15)
- **Step 3:** Write a personalised resolution response using specifics from the clarification exchange (+0.50 × quality score)

This tests true diagnostic reasoning — the agent cannot succeed by guessing; it must ask the right question to uncover the real issue.

6 ambiguous tickets spanning billing/account/technical confusion, including: billing mistaken for account access, security breach disguised as general strangeness, API rate-limit hidden under "slow system", unauthorised employee access hidden under "settings changed".

Max reward: **1.0**

---

## Action space

```json
{
  "classification": "billing | technical | account | general",
  "urgency": "low | medium | high | critical",
  "response_draft": "string",
  "ticket_classifications": [
    {"ticket_id": "TKT-XXX", "classification": "...", "urgency": "..."}
  ],
  "escalate_ticket_id": "TKT-XXX",
  "escalation_response": "string"
}
```

Only populate the fields relevant to the current step (the `task_description` in the observation tells you exactly what to submit).

## Observation space

```json
{
  "task_name": "classify_ticket | draft_response | triage_queue",
  "ticket": {"ticket_id": "...", "subject": "...", "content": "...", "customer_name": "...", "customer_email": "..."},
  "ticket_queue": [...],
  "task_description": "human-readable instruction for the current step",
  "step": 1,
  "max_steps": 2,
  "done": false,
  "last_action_result": "feedback from grader on previous action",
  "score": 0.50,
  "reward": 0.50,
  "metadata": {}
}
```

---

## Reward design

Rewards are **partial and deterministic** — no binary pass/fail. Agents receive signal on every step, including penalties for invalid or low-quality actions.

| Component | Trigger | Value |
|---|---|---|
| Correct classification | Exact string match | +0.20 to +0.50 |
| Correct urgency | Exact string match | +0.10 to +0.50 |
| Response quality | 7-criterion rubric | +0.00 to +0.70 |
| Correct escalation target | Exact ticket ID match | +0.30 |
| Queue classification accuracy | Per-ticket accuracy | up to +0.40 |
| **Invalid classification/urgency value** | Submitted value not in valid set | **−0.10** |
| **Invalid escalation ticket ID** | ID not in current queue | **−0.15** |
| **Empty response** | Response < 20 characters | **−0.20** |

### Response quality rubric (7 criteria, max 1.0)

| Criterion | Points |
|---|---|
| Greeting | 0.10 |
| Empathy / apology | 0.10 |
| Issue acknowledgment (≥2 ticket keywords) | 0.25 |
| Resolution / action language (≥2 terms) | 0.20 |
| Commitment / timeline ("within 24 hours", etc.) | 0.10 |
| Length ≥ 100 chars | 0.15 |
| Professional tone | 0.10 |

---

## API endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/reset` | Start new episode. Body: `{"task": "classify_ticket", "seed": 42}` |
| POST | `/step` | Take action. Body: `{"action": {<SupportAction fields>}}` |
| GET | `/state` | Current episode state (simulation mode only) |
| GET | `/health` | Health check |
| GET | `/metadata` | Environment metadata |
| GET | `/schema` | Action/observation schema |
| GET | `/docs` | Swagger UI |

> **Note:** The REST API creates a fresh environment per request (stateless). Multi-step task evaluation is done via `inference.py`, which manages state locally in Python.

### Example — single reset call

```bash
# Health check
curl https://pengosword123-support-triage-env.hf.space/health

# Reset (returns initial observation)
curl -X POST http://localhost:8000/reset \
  -H "Content-Type: application/json" \
  -d '{"task": "classify_ticket", "seed": 42}'

# Step — action must be wrapped in {"action": {...}}
curl -X POST http://localhost:8000/step \
  -H "Content-Type: application/json" \
  -d '{"action": {"classification": "billing"}}'
```

---

## Local setup

```bash
git clone https://github.com/CoderRahul01/support-triage-env
cd support-triage-env

pip install -r requirements.txt

# Run the server
uvicorn server.app:app --host 0.0.0.0 --port 8000

# Test it
curl http://localhost:8000/health

# Run baseline inference
export HF_TOKEN=hf_xxx
python inference.py
```

## Docker

```bash
docker build -t support-triage-env .
docker run -p 8000:8000 support-triage-env
curl http://localhost:8000/health
```

---

## Baseline scores

Measured with `Qwen/Qwen2.5-72B-Instruct` via HuggingFace Inference API (seed=42):

| Task | Score | Difficulty | Notes |
|---|---|---|---|
| classify_ticket | ~0.75 | Easy | Strong on obvious categories; may miss ambiguous urgency |
| draft_response | ~0.65 | Medium | Good classification; response quality varies by ticket |
| triage_queue | ~0.50 | Hard | QUEUE-005/006 (multiple criticals) challenge even frontier models |
| resolve_ticket | ~0.45 | Expert | Requires asking the right question; off-target questions penalised |
| **Overall** | **~0.59** | | |

Dataset: 30 tickets, 6 triage queues, 6 ambiguous tickets.

---

## Project structure

```
support_triage_env/
├── server/
│   ├── __init__.py
│   └── app.py          # FastAPI app (create_app, root → /docs redirect)
├── .github/workflows/
│   └── sync-to-hf.yml  # Auto-sync to HF Spaces on push to main
├── __init__.py
├── models.py           # SupportAction, SupportObservation, SupportState (Pydantic)
├── data.py             # 30 tickets, 6 queues, 6 ambiguous tickets
├── environment.py      # SupportTriageEnvironment + 4 task graders + trigram scorer
├── openenv.yaml        # OpenEnv spec metadata
├── Dockerfile          # python:3.11-slim, single worker
├── requirements.txt
├── inference.py        # Baseline inference (all 4 tasks, exact hackathon log format)
└── README.md
```
