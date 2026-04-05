"""
Support Triage Environment — core implementation.

An OpenEnv environment where an AI agent learns to handle customer support tickets.
Three tasks with increasing difficulty, deterministic graders, and partial rewards.
"""
import random
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

try:
    from openenv.core.env_server.interfaces import Environment
    from openenv.core.env_server.types import EnvironmentMetadata
except ImportError:
    # Fallback for local testing
    class Environment:  # type: ignore[no-redef]
        SUPPORTS_CONCURRENT_SESSIONS = True

    class EnvironmentMetadata:  # type: ignore[no-redef]
        def __init__(self, **kwargs: Any) -> None:
            for k, v in kwargs.items():
                setattr(self, k, v)

try:
    from .models import SupportAction, SupportObservation, SupportState, TicketInfo
    from .data import TICKETS, TICKET_QUEUES
except ImportError:
    from models import SupportAction, SupportObservation, SupportState, TicketInfo
    from data import TICKETS, TICKET_QUEUES


# ── Step instructions shown to the agent ─────────────────────────────────────

TASK_DESCRIPTIONS: Dict[str, Dict[int, str]] = {
    "classify_ticket": {
        0: (
            "TASK: Classify this support ticket.\n"
            "Step 1 of 2 — Submit the CATEGORY.\n"
            "Valid values: 'billing', 'technical', 'account', 'general'\n"
            "Output ONLY: {\"classification\": \"<value>\"}"
        ),
        1: (
            "TASK: Classify this support ticket.\n"
            "Step 2 of 2 — Submit the URGENCY level.\n"
            "Valid values: 'low', 'medium', 'high', 'critical'\n"
            "Output ONLY: {\"urgency\": \"<value>\"}"
        ),
    },
    "draft_response": {
        0: (
            "TASK: Classify and respond to this support ticket.\n"
            "Step 1 of 3 — Submit the CATEGORY.\n"
            "Valid values: 'billing', 'technical', 'account', 'general'\n"
            "Output ONLY: {\"classification\": \"<value>\"}"
        ),
        1: (
            "TASK: Classify and respond to this support ticket.\n"
            "Step 2 of 3 — Submit the URGENCY level.\n"
            "Valid values: 'low', 'medium', 'high', 'critical'\n"
            "Output ONLY: {\"urgency\": \"<value>\"}"
        ),
        2: (
            "TASK: Classify and respond to this support ticket.\n"
            "Step 3 of 3 — Write a full RESPONSE DRAFT.\n"
            "Requirements: greeting, acknowledge the issue, provide next steps, professional tone.\n"
            "Output ONLY: {\"response_draft\": \"<your full response to the customer>\"}"
        ),
    },
    "triage_queue": {
        0: (
            "TASK: Triage this queue of 5 support tickets.\n"
            "Step 1 of 2 — Classify ALL 5 tickets (category + urgency each).\n"
            "Valid categories: 'billing', 'technical', 'account', 'general'\n"
            "Valid urgency: 'low', 'medium', 'high', 'critical'\n"
            "Output ONLY: {\"ticket_classifications\": [{\"ticket_id\": \"TKT-XXX\", "
            "\"classification\": \"...\", \"urgency\": \"...\"}, ...]}"
        ),
        1: (
            "TASK: Triage this queue of 5 support tickets.\n"
            "Step 2 of 2 — Identify the ONE ticket needing immediate escalation and draft a response.\n"
            "Pick the ticket with the highest urgency and business impact.\n"
            "Output ONLY: {\"escalate_ticket_id\": \"TKT-XXX\", "
            "\"escalation_response\": \"<full professional response>\"}"
        ),
    },
}

MAX_STEPS_PER_TASK: Dict[str, int] = {
    "classify_ticket": 2,
    "draft_response": 3,
    "triage_queue": 2,
}


class SupportTriageEnvironment(Environment):
    """
    Customer Support Ticket Triage Environment for OpenEnv.

    The agent reads realistic customer support tickets and must classify,
    prioritise, respond to, and escalate them — mirroring daily work at
    any customer-facing company.

    Tasks
    -----
    classify_ticket (easy, 2 steps):
        Step 1: classify ticket into a category.
        Step 2: assign urgency level.
        Max reward: 1.0

    draft_response (medium, 3 steps):
        Step 1: classify category (+0.20).
        Step 2: assign urgency (+0.10).
        Step 3: write a full response draft (+0.70).
        Max reward: 1.0

    triage_queue (hard, 2 steps):
        Step 1: classify all 5 tickets (+0.40).
        Step 2: identify the escalation ticket (+0.30) and draft response (+0.30).
        Max reward: 1.0

    Reward design
    -------------
    All rewards are partial and deterministic — the agent receives a non-zero
    signal even on incorrect answers (based on how many sub-fields were correct).
    """

    SUPPORTS_CONCURRENT_SESSIONS = True

    def __init__(self) -> None:
        self._state: Optional[SupportState] = None

    # ── OpenEnv interface ─────────────────────────────────────────────────────

    def reset(
        self,
        task: str = "classify_ticket",
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        **kwargs: Any,
    ) -> SupportObservation:
        """
        Start a fresh episode.

        Parameters
        ----------
        task : str
            One of 'classify_ticket', 'draft_response', 'triage_queue'.
        seed : int, optional
            Random seed — set for reproducible ticket selection.
        episode_id : str, optional
            Custom episode identifier (auto-generated if not provided).
        """
        if task not in MAX_STEPS_PER_TASK:
            task = "classify_ticket"

        rng = random.Random(seed)
        eid = episode_id or str(uuid4())

        if task in ("classify_ticket", "draft_response"):
            raw = rng.choice(TICKETS)
            ticket = TicketInfo(
                ticket_id=raw["ticket_id"],
                subject=raw["subject"],
                content=raw["content"],
                customer_name=raw["customer_name"],
                customer_email=raw["customer_email"],
            )
            ground_truth: Dict[str, Any] = raw["ground_truth"]
            queue: Optional[List[TicketInfo]] = None
            queue_gt: List[Dict[str, Any]] = []
        else:
            raw_queue = rng.choice(TICKET_QUEUES)
            ticket = None
            queue = [
                TicketInfo(
                    ticket_id=t["ticket_id"],
                    subject=t["subject"],
                    content=t["content"],
                    customer_name=t["customer_name"],
                    customer_email=t["customer_email"],
                )
                for t in raw_queue["tickets"]
            ]
            ground_truth = raw_queue["ground_truth"]
            queue_gt = raw_queue["ground_truth"]["classifications"]

        self._state = SupportState(
            episode_id=eid,
            task_name=task,
            ticket=ticket,
            ticket_queue=queue,
            step=0,
            max_steps=MAX_STEPS_PER_TASK[task],
            done=False,
            score=0.0,
            ground_truth=ground_truth,
            queue_ground_truth=queue_gt,
        )

        return SupportObservation(
            task_name=task,
            ticket=ticket,
            ticket_queue=queue,
            task_description=TASK_DESCRIPTIONS[task][0],
            step=0,
            max_steps=MAX_STEPS_PER_TASK[task],
            done=False,
            last_action_result=None,
            score=0.0,
            reward=None,
            metadata={"episode_id": eid, "task": task},
        )

    def step(self, action: SupportAction, **kwargs: Any) -> SupportObservation:
        """
        Process one agent action and return the next observation.

        The grader scores the action for the current task step,
        advances the step counter, and marks the episode done when
        all required steps are complete.
        """
        if self._state is None:
            raise RuntimeError("Environment not initialised. Call reset() first.")

        s = self._state
        task = s.task_name
        current_step = s.step

        reward, result_msg = self._grade(task, current_step, action, s.ground_truth)

        s.score += reward
        s.step += 1
        done = s.step >= s.max_steps
        s.done = done

        next_desc = (
            TASK_DESCRIPTIONS[task].get(s.step, f"Episode complete. Total score: {s.score:.2f}")
            if not done
            else f"Episode complete. Total score: {s.score:.2f} / 1.00"
        )

        # Reveal ground truth only when episode ends
        meta: Dict[str, Any] = {"episode_id": s.episode_id}
        if done:
            meta["ground_truth"] = s.ground_truth

        return SupportObservation(
            task_name=task,
            ticket=s.ticket,
            ticket_queue=s.ticket_queue,
            task_description=next_desc,
            step=s.step,
            max_steps=s.max_steps,
            done=done,
            last_action_result=result_msg,
            score=s.score,
            reward=reward,
            metadata=meta,
        )

    @property
    def state(self) -> SupportState:
        if self._state is None:
            raise RuntimeError("Call reset() first.")
        return self._state

    def close(self) -> None:
        self._state = None

    def get_metadata(self) -> EnvironmentMetadata:
        return EnvironmentMetadata(
            name="support_triage_env",
            description=(
                "Customer support ticket triage: classify, respond, and escalate. "
                "3 tasks (easy → hard) with partial, deterministic rewards."
            ),
            version="1.0.0",
        )

    # ── Graders ───────────────────────────────────────────────────────────────

    def _grade(
        self,
        task: str,
        step: int,
        action: SupportAction,
        gt: Dict[str, Any],
    ) -> Tuple[float, str]:
        """Dispatch to the correct grader. Returns (reward, feedback_message)."""
        if task == "classify_ticket":
            return self._grade_classify(step, action, gt)
        elif task == "draft_response":
            return self._grade_draft(step, action, gt)
        elif task == "triage_queue":
            return self._grade_triage(step, action, gt)
        return 0.0, "Unknown task."

    # classify_ticket ──────────────────────────────────────────────────────────

    def _grade_classify(
        self, step: int, action: SupportAction, gt: Dict[str, Any]
    ) -> Tuple[float, str]:
        if step == 0:
            submitted = (action.classification or "").lower().strip()
            correct = submitted == gt["classification"]
            reward = 0.50 if correct else 0.0
            msg = (
                f"Classification '{submitted}' ✓ correct. +0.50"
                if correct
                else f"Classification '{submitted}' ✗ incorrect. Expected '{gt['classification']}'."
            )
            return reward, msg
        else:
            submitted = (action.urgency or "").lower().strip()
            correct = submitted == gt["urgency"]
            reward = 0.50 if correct else 0.0
            msg = (
                f"Urgency '{submitted}' ✓ correct. +0.50"
                if correct
                else f"Urgency '{submitted}' ✗ incorrect. Expected '{gt['urgency']}'."
            )
            return reward, msg

    # draft_response ───────────────────────────────────────────────────────────

    def _grade_draft(
        self, step: int, action: SupportAction, gt: Dict[str, Any]
    ) -> Tuple[float, str]:
        if step == 0:
            submitted = (action.classification or "").lower().strip()
            correct = submitted == gt["classification"]
            reward = 0.20 if correct else 0.0
            msg = (
                f"Classification ✓ correct. +0.20"
                if correct
                else f"Classification ✗ (got '{submitted}', expected '{gt['classification']}')."
            )
            return reward, msg
        elif step == 1:
            submitted = (action.urgency or "").lower().strip()
            correct = submitted == gt["urgency"]
            reward = 0.10 if correct else 0.0
            msg = (
                f"Urgency ✓ correct. +0.10"
                if correct
                else f"Urgency ✗ (got '{submitted}', expected '{gt['urgency']}')."
            )
            return reward, msg
        else:  # step == 2
            quality = self._score_response(action.response_draft, gt)
            reward = round(quality * 0.70, 4)
            msg = f"Response quality: {quality:.2f}/1.00 → reward +{reward:.2f}/0.70"
            return reward, msg

    # triage_queue ─────────────────────────────────────────────────────────────

    def _grade_triage(
        self, step: int, action: SupportAction, gt: Dict[str, Any]
    ) -> Tuple[float, str]:
        if step == 0:
            submitted = action.ticket_classifications or []
            submitted_map = {item.get("ticket_id", ""): item for item in submitted}
            expected_list: List[Dict[str, str]] = gt["classifications"]

            correct_class = 0
            correct_urgency = 0
            n = len(expected_list)

            for exp in expected_list:
                tid = exp["ticket_id"]
                sub = submitted_map.get(tid, {})
                if sub.get("classification", "").lower() == exp["classification"]:
                    correct_class += 1
                if sub.get("urgency", "").lower() == exp["urgency"]:
                    correct_urgency += 1

            reward = round((correct_class / n) * 0.20 + (correct_urgency / n) * 0.20, 4)
            msg = (
                f"Classifications: {correct_class}/{n} correct | "
                f"Urgencies: {correct_urgency}/{n} correct | "
                f"Reward: +{reward:.2f}/0.40"
            )
            return reward, msg
        else:  # step == 1
            submitted_id = (action.escalate_ticket_id or "").strip()
            correct_id = submitted_id == gt["escalate_ticket_id"]
            id_reward = 0.30 if correct_id else 0.0

            quality = self._score_response(action.escalation_response, gt)
            response_reward = round(quality * 0.30, 4)
            total = round(id_reward + response_reward, 4)

            expected_id = gt["escalate_ticket_id"]
            id_status = "correct" if correct_id else f"incorrect (expected {expected_id})"
            msg = (
                f"Escalation ID {id_status} "
                f"| Response quality: {quality:.2f} -> +{response_reward:.2f} | Total: +{total:.2f}"
            )
            return total, msg

    # Response quality scorer ──────────────────────────────────────────────────

    def _score_response(self, response: Optional[str], gt: Dict[str, Any]) -> float:
        """
        Score a customer response draft from 0.0 to 1.0 using deterministic checks.

        Rubric:
          0.15  — Has a greeting (hello / hi / dear / thank you)
          0.30  — Acknowledges the specific issue (ticket keyword match)
          0.25  — Contains resolution language (next steps, fix, investigate, etc.)
          0.20  — Adequate length (≥ 80 characters)
          0.10  — Professional tone (no rude/offensive words)
        """
        if not response or len(response.strip()) < 10:
            return 0.0

        r = response.lower()
        score = 0.0

        # Greeting
        if any(g in r for g in ["hello", "hi ", "dear ", "thank you for", "thanks for"]):
            score += 0.15

        # Issue acknowledgment — matches keywords from the specific ticket
        issue_kws = gt.get("issue_keywords", [])
        if issue_kws and any(kw.lower() in r for kw in issue_kws):
            score += 0.30

        # Resolution / next steps language
        resolution = [
            "resolve", "fix", "help", "assist", "solution", "escalat",
            "investigate", "look into", "steps", "guide", "refund",
            "team", "engineer", "reset", "update", "follow up", "follow-up",
        ]
        if any(w in r for w in resolution):
            score += 0.25

        # Length
        if len(response.strip()) >= 80:
            score += 0.20
        elif len(response.strip()) >= 30:
            score += 0.10

        # Professionalism
        rude = ["stupid", "idiot", "hate", "worst", "ridiculous", "incompetent"]
        if not any(w in r for w in rude):
            score += 0.10

        return min(score, 1.0)
