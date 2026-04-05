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

Rewards are **partial and deterministic** — no binary pass/fail.

| Component | Trigger | Max value |
|---|---|---|
| Correct classification | Exact string match | 0.20–0.50 |
| Correct urgency | Exact string match | 0.10–0.50 |
| Response quality | Multi-criterion keyword rubric | 0.30–0.70 |
| Correct escalation target | Exact ticket ID match | 0.30 |
| Queue classification accuracy | Per-ticket accuracy | 0.40 |

The response rubric checks: greeting presence (0.15), issue keyword acknowledgment (0.30), resolution language (0.25), adequate length (0.20), professionalism (0.10).

---

## API endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/reset` | Start new episode. Body: `{"task": "classify_ticket", "seed": 42}` |
| POST | `/step` | Take action. Body: SupportAction JSON |
| GET | `/state` | Current episode state |
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI |

### Example session

```bash
# Reset (start a classify_ticket episode)
curl -X POST http://localhost:8000/reset \
  -H "Content-Type: application/json" \
  -d '{"task": "classify_ticket", "seed": 42}'

# Step 1 — submit classification
curl -X POST http://localhost:8000/step \
  -H "Content-Type: application/json" \
  -d '{"classification": "billing"}'

# Step 2 — submit urgency
curl -X POST http://localhost:8000/step \
  -H "Content-Type: application/json" \
  -d '{"urgency": "high"}'
```

---

## Local setup

```bash
git clone https://github.com/YOUR_USERNAME/support-triage-env
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

| Task | Score |
|---|---|
| classify_ticket | ~0.75 |
| draft_response | ~0.65 |
| triage_queue | ~0.55 |
| **Overall** | **~0.65** |

---

## Project structure

```
support_triage_env/
├── server/
│   ├── __init__.py
│   └── app.py          # FastAPI app (create_app)
├── __init__.py
├── models.py           # SupportAction, SupportObservation, SupportState
├── data.py             # 15 synthetic tickets + 3 triage queues
├── environment.py      # SupportTriageEnvironment class + graders
├── openenv.yaml        # OpenEnv spec
├── Dockerfile
├── requirements.txt
├── inference.py        # Baseline inference script
└── README.md
```
