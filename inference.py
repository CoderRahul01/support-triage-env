"""
Support Triage Environment — Baseline Inference Script
======================================================
MANDATORY env vars:
    HF_TOKEN       Your Hugging Face API key
    API_BASE_URL   LLM endpoint (default: https://router.huggingface.co/v1)
    MODEL_NAME     Model identifier (default: Qwen/Qwen2.5-72B-Instruct)

Usage:
    export HF_TOKEN=hf_xxx
    python inference.py

Runs all 3 tasks sequentially and prints [START]/[STEP]/[END] logs.
Final overall score = average of 3 task scores.
"""

import json
import os
import sys
from typing import List, Optional

from openai import OpenAI

# Allow direct execution from the project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from environment import SupportTriageEnvironment
from models import SupportAction

# ── Configuration ─────────────────────────────────────────────────────────────
HF_TOKEN: Optional[str] = os.getenv("HF_TOKEN")
if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")
API_KEY: str = HF_TOKEN
API_BASE_URL: str = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME: str = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
BENCHMARK: str = "support_triage_env"
SEED: int = 42
TEMPERATURE: float = 0.1
MAX_TOKENS: int = 1024
SUCCESS_THRESHOLD: float = 0.40

TASKS: List[str] = ["classify_ticket", "draft_response", "triage_queue", "resolve_ticket"]
MAX_STEPS: dict = {"classify_ticket": 2, "draft_response": 3, "triage_queue": 2, "resolve_ticket": 3}

# ── Logging ───────────────────────────────────────────────────────────────────

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(
    step: int, action: str, reward: float, done: bool, error: Optional[str]
) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    # Keep action on a single line and truncate for readability
    action_clean = action.replace("\n", " ").replace("\r", " ")[:300]
    print(
        f"[STEP] step={step} action={action_clean} "
        f"reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(
    success: bool, steps: int, score: float, rewards: List[float]
) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True,
    )


# ── LLM interaction ───────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are an expert customer support triage agent. "
    "Read the ticket carefully, then output ONLY a valid JSON object — "
    "no markdown, no backticks, no explanation. Just raw JSON."
)


def get_model_response(
    client: OpenAI,
    task_description: str,
    observation_text: str,
    history: List[str],
) -> str:
    """Call the LLM and return the raw string response."""
    history_block = "\n".join(history[-3:]) if history else "None"

    user_content = (
        f"{observation_text}\n\n"
        f"Task instruction:\n{task_description}\n\n"
        f"Recent history:\n{history_block}\n\n"
        f"Output ONLY the JSON object:"
    )

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        raw = (completion.choices[0].message.content or "{}").strip()
        return raw
    except Exception as exc:
        print(f"[DEBUG] LLM call failed: {exc}", flush=True)
        return "{}"


def parse_action(raw: str) -> SupportAction:
    """Parse raw LLM string → SupportAction (graceful fallback)."""
    text = raw.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
    # Find first { ... } block
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        text = text[start:end]
    try:
        data = json.loads(text)
        return SupportAction(**data)
    except Exception:
        return SupportAction()


def format_observation(obs) -> str:
    """Turn an observation into a plain-text block for the LLM."""
    parts: List[str] = []

    if obs.ticket:
        t = obs.ticket
        parts.append(
            f"=== SUPPORT TICKET ===\n"
            f"ID: {t.ticket_id}\n"
            f"Subject: {t.subject}\n"
            f"From: {t.customer_name} <{t.customer_email}>\n"
            f"Message:\n{t.content}"
        )

    if obs.ticket_queue:
        parts.append("=== TICKET QUEUE (5 tickets) ===")
        for i, t in enumerate(obs.ticket_queue, 1):
            content_preview = t.content if len(t.content) <= 250 else t.content[:250] + "..."
            parts.append(
                f"\n[{i}] {t.ticket_id}\n"
                f"Subject: {t.subject}\n"
                f"From: {t.customer_name} <{t.customer_email}>\n"
                f"Message: {content_preview}"
            )

    if obs.revealed_info:
        parts.append(f"=== {obs.revealed_info} ===")

    if obs.last_action_result:
        parts.append(f"Previous step feedback: {obs.last_action_result}")

    return "\n\n".join(parts)


# ── Episode runner ────────────────────────────────────────────────────────────

def run_task(
    client: OpenAI,
    env: SupportTriageEnvironment,
    task: str,
    seed: int,
) -> float:
    """
    Run one full task episode.
    Returns the normalised score in [0, 1].
    """
    log_start(task=task, env=BENCHMARK, model=MODEL_NAME)

    obs = env.reset(task=task, seed=seed)
    history: List[str] = []
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    try:
        for step_idx in range(MAX_STEPS[task]):
            obs_text = format_observation(obs)
            raw = get_model_response(
                client,
                task_description=obs.task_description,
                observation_text=obs_text,
                history=history,
            )
            action = parse_action(raw)

            error: Optional[str] = None
            try:
                obs = env.step(action)
            except Exception as exc:
                error = str(exc)
                rewards.append(0.0)
                steps_taken = step_idx + 1
                log_step(step_idx + 1, raw, 0.0, True, error)
                break

            reward = obs.reward if obs.reward is not None else 0.0
            done = obs.done
            rewards.append(reward)
            steps_taken = step_idx + 1

            log_step(
                step=step_idx + 1,
                action=raw,
                reward=reward,
                done=done,
                error=error,
            )

            history.append(
                f"Step {step_idx + 1}: {raw[:120]} → reward={reward:.2f}, "
                f"feedback={obs.last_action_result}"
            )

            if done:
                break

        score = obs.score if obs is not None else sum(rewards)
        score = min(max(score, 0.0), 1.0)
        success = score >= SUCCESS_THRESHOLD

    except Exception as exc:
        print(f"[DEBUG] Task '{task}' error: {exc}", flush=True)

    finally:
        log_end(
            success=success,
            steps=steps_taken,
            score=score,
            rewards=rewards,
        )

    return score


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    env = SupportTriageEnvironment()

    all_scores: List[float] = []
    for i, task in enumerate(TASKS):
        task_score = run_task(client, env, task, seed=SEED + i)
        all_scores.append(task_score)

    env.close()

    overall = sum(all_scores) / len(all_scores)
    print(f"\n[SUMMARY] task_scores={all_scores}", flush=True)
    print(f"[SUMMARY] overall_score={overall:.3f}", flush=True)


if __name__ == "__main__":
    main()
