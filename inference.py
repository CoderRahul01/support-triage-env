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

Runs all 4 tasks sequentially and prints [START]/[STEP]/[END] logs.
Final overall score = average of 4 task scores.
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
API_BASE_URL: str = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME: str = os.getenv("MODEL_NAME", "meta-llama/Llama-3.3-70B-Instruct")
HF_TOKEN: Optional[str] = os.getenv("HF_TOKEN")

# Optional — only needed if using from_docker_image():
LOCAL_IMAGE_NAME: Optional[str] = os.getenv("LOCAL_IMAGE_NAME")

API_KEY: str = HF_TOKEN or ""
if not API_KEY:
    raise ValueError("HF_TOKEN environment variable is required")
BENCHMARK: str = "support_triage_env"
SEED: int = 42
TEMPERATURE: float = 0.1
MAX_TOKENS: int = 2048
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
        f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}",
        flush=True,
    )


# ── LLM interaction ───────────────────────────────────────────────────────────

# Task-specific system prompts aligned with grader rubrics for maximum scoring.
TASK_SYSTEM_PROMPTS: dict = {
    "classify_ticket": (
        "You are a senior customer support triage specialist.\n"
        "CATEGORIES (pick exactly one):\n"
        "  'billing'   — charges, invoices, refunds, payments, subscriptions, pricing\n"
        "  'technical' — bugs, errors, crashes, API issues, performance, integrations\n"
        "  'account'   — login, password, 2FA, access, security, account suspension\n"
        "  'general'   — how-to questions, feature requests, documentation, sales enquiries\n"
        "URGENCY RULES — be strict:\n"
        "  'critical' — ANY of: service/system completely down, production incidents missed, "
        "data loss, security breach, medical/safety risk, financial fraud, payments failing, "
        "alerts not working, hard deadline <2 hours, whole team blocked with no workaround\n"
        "  'high'     — significant business impact, meaningful revenue loss, team blocked "
        "but partial workaround, overdue refund >7 days, deadline within 24h\n"
        "  'medium'   — noticeable but manageable, workaround available, deadline within a week\n"
        "  'low'      — questions, feature requests, minor inconvenience, no deadline\n"
        "Output ONLY a valid JSON object. No markdown, no backticks, no explanation."
    ),
    "draft_response": (
        "You are a senior customer support agent writing professional responses.\n"
        "CATEGORIES: 'billing'=charges/invoices/refunds, 'technical'=bugs/errors/API, "
        "'account'=login/password/access/security, 'general'=how-to/features/sales.\n"
        "URGENCY: 'critical'=emergency/blocking, 'high'=significant impact, "
        "'medium'=noticeable, 'low'=questions.\n"
        "RESPONSE REQUIREMENTS (all mandatory for full score):\n"
        "  1. Start with a warm greeting (Hello / Hi / Dear / Thank you for contacting us)\n"
        "  2. Express empathy (sorry / apologise / understand / sincerely / regret / frustrating)\n"
        "  3. Acknowledge the specific issue using the customer's own words\n"
        "  4. State clear next steps (investigate / escalate / resolve / refund / restore / reset)\n"
        "  5. Commit to a timeline (within 24 hours / immediately / right away / asap / today)\n"
        "  6. Minimum 150 characters — be thorough and professional\n\n"
        "EXAMPLE of a high-quality response draft:\n"
        "\"Hello James, thank you for contacting us. I sincerely apologise for the "
        "inconvenience caused by the billing discrepancy on your account. I completely "
        "understand how frustrating an unexpected charge can be. I am escalating this to "
        "our billing team right away and will investigate the overcharge immediately. "
        "We will process a full refund within 24 hours and send you written confirmation. "
        "Please do not hesitate to reach out if you need anything further.\"\n\n"
        "Output ONLY a valid JSON object. No markdown, no backticks, no explanation."
    ),
    "triage_queue": (
        "You are a senior customer support manager triaging a queue of 5 tickets.\n"
        "CATEGORIES: 'billing'=charges/invoices, 'technical'=bugs/errors/API, "
        "'account'=access/security/suspended, 'general'=how-to/features/sales.\n"
        "URGENCY RULES — be strict:\n"
        "  'critical' = ANY of: system/service completely down, production incidents being missed, "
        "data loss/corruption, security breach, medical/safety risk, financial fraud, "
        "payments failing at scale, alerts not firing, SLA breaches, hard deadline <2h, "
        "whole team/service blocked with no workaround\n"
        "  'high'     = significant business impact, revenue loss, team blocked but partial "
        "workaround exists, overdue refund >7 days, delayed payment >$500, deadline within 24h\n"
        "  'medium'   = noticeable but manageable, workaround available, deadline within a week, "
        "overdue refund <7 days, billing discrepancy <$200\n"
        "  'low'      = questions, feature requests, minor inconvenience, no deadline\n"
        "ESCALATION PRIORITY — follow this exact order:\n"
        "  1. Human safety / medical emergency\n"
        "  2. Unauthorized access / wrong permissions / security exposure / data visible to wrong party\n"
        "  3. Payments failing at scale / financial fraud / data loss\n"
        "  4. System or service completely down for many users\n"
        "  5. Production monitoring / alerts / pipelines broken\n"
        "  6. Significant revenue impact\n"
        "  7. Team productivity blocked\n"
        "When multiple tickets are critical, escalate the HIGHEST priority category above.\n"
        "Security exposure (wrong admin, leaked keys, unauthorized access) ALWAYS beats operational outages.\n"
        "For the escalation response: include greeting, empathy, specific issue acknowledgment, "
        "concrete escalation steps, and a timeline commitment.\n"
        "Output ONLY a valid JSON object. No markdown, no backticks, no explanation."
    ),
    "resolve_ticket": (
        "You are a senior customer support agent resolving ambiguous tickets.\n"
        "STEP 1 — Clarification: Ask ONE specific, targeted question about the most likely "
        "root cause. Focus on: payment/billing issues, technical errors, account access, security.\n"
        "  GOOD: 'Could you confirm whether this relates to a payment or charge on your account, "
        "or is it an issue with logging in or accessing your account?'\n"
        "  BAD: 'Can you tell me more about your issue?' (too vague — scores zero)\n\n"
        "STEP 2 — Classification: Use ALL information including the customer reply. "
        "Categories: 'billing'=payment/charge issues, 'technical'=errors/bugs, "
        "'account'=access/security, 'general'=info/features. "
        "Urgency: 'critical'=blocking/urgent, 'high'=significant, 'medium'=moderate, 'low'=minor.\n\n"
        "STEP 3 — Response: Write a personalised, empathetic response that:\n"
        "  1. Greets the customer by name (Hello / Hi / Dear [name])\n"
        "  2. Shows empathy (sorry / apologise / understand / sincerely / frustrating)\n"
        "  3. Acknowledges the EXACT issue from clarification exchange using their own words\n"
        "  4. Provides specific next steps (resolve / investigate / escalate / restore / refund)\n"
        "  5. Commits to a timeline (within 24 hours / immediately / right away / asap)\n"
        "  6. Minimum 150 characters — be thorough and personalised\n\n"
        "EXAMPLE of a high-quality resolution response:\n"
        "\"Dear Thomas, thank you for clarifying this. I sincerely apologise for the "
        "disruption caused by the failed payment locking your account. I completely "
        "understand how frustrating this must be when you rely on the platform daily. "
        "I am processing the account restoration right away and investigating why the "
        "card update did not automatically re-activate your subscription. "
        "Your account will be fully restored within the next hour and I will send you "
        "confirmation by email. Please do not hesitate to contact us if you need anything further.\"\n\n"
        "Output ONLY a valid JSON object. No markdown, no backticks, no explanation."
    ),
}

# Fallback for any unexpected task name
_DEFAULT_SYSTEM_PROMPT = (
    "You are an expert customer support triage agent. "
    "Output ONLY a valid JSON object — no markdown, no backticks, no explanation."
)


def get_model_response(
    client: OpenAI,
    task_description: str,
    observation_text: str,
    history: List[str],
    task: str = "",
) -> str:
    """Call the LLM and return the raw string response. Retries once on JSON failure."""
    history_block = "\n".join(history[-3:]) if history else "None"
    system_prompt = TASK_SYSTEM_PROMPTS.get(task, _DEFAULT_SYSTEM_PROMPT)

    user_content = (
        f"{observation_text}\n\n"
        f"Task instruction:\n{task_description}\n\n"
        f"Recent history:\n{history_block}\n\n"
        f"Output ONLY the JSON object:"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]

    for attempt in range(2):
        try:
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=TEMPERATURE if attempt == 0 else 0.0,
                max_tokens=MAX_TOKENS,
            )
            raw = (completion.choices[0].message.content or "{}").strip()
            # Quick validity check — if it parses, return immediately
            _start = raw.find("{")
            _end = raw.rfind("}") + 1
            candidate = raw[_start:_end] if _start != -1 and _end > _start else raw
            json.loads(candidate)  # raises if invalid
            return raw
        except json.JSONDecodeError:
            if attempt == 0:
                # Retry: append the bad response and ask the model to fix it
                print(f"[DEBUG] JSON parse failed on attempt 1, retrying...", flush=True)
                messages.append({"role": "assistant", "content": raw})
                messages.append({
                    "role": "user",
                    "content": (
                        "Your response was not valid JSON. "
                        "Output ONLY the raw JSON object with no extra text:"
                    ),
                })
            else:
                return raw  # return best effort; parse_action handles fallback
        except Exception as exc:
            print(f"[DEBUG] LLM call failed (attempt {attempt + 1}): {exc}", flush=True)
            if attempt == 1:
                return "{}"

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
                task=task,
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
        # Score must be strictly within (0, 1) — use 0.001 so it survives
        # 3-decimal-place formatting in the [END] log line.
        score = min(max(score, 0.001), 0.999)
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
