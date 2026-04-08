"""
Support Triage Environment — core implementation.

An OpenEnv environment where an AI agent learns to handle customer support tickets.
Four tasks with increasing difficulty, deterministic graders, and partial rewards.
"""
import random
from typing import Any, ClassVar, Dict, List, Optional, Tuple
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
    from .data import TICKETS, TICKET_QUEUES, AMBIGUOUS_TICKETS
except ImportError:
    from models import SupportAction, SupportObservation, SupportState, TicketInfo
    from data import TICKETS, TICKET_QUEUES, AMBIGUOUS_TICKETS


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
    "resolve_ticket": {
        0: (
            "TASK: Resolve this ambiguous support ticket through clarification.\n"
            "Step 1 of 3 — The ticket is vague. Ask ONE specific clarifying question to identify the real issue.\n"
            "Be targeted: ask about the most likely unclear aspect (billing, technical error, account access, etc.).\n"
            "Output ONLY: {\"clarification_request\": \"<your specific question to the customer>\"}"
        ),
        1: (
            "TASK: Resolve this ambiguous support ticket.\n"
            "Step 2 of 3 — The customer has responded with more details (see 'Customer Reply' below).\n"
            "Now classify the ticket using ALL information gathered.\n"
            "Submit BOTH category AND urgency in a single action.\n"
            "Valid categories: 'billing', 'technical', 'account', 'general'\n"
            "Valid urgency: 'low', 'medium', 'high', 'critical'\n"
            "Output ONLY: {\"classification\": \"<value>\", \"urgency\": \"<value>\"}"
        ),
        2: (
            "TASK: Resolve this ambiguous support ticket.\n"
            "Step 3 of 3 — Write a full, personalised resolution response to the customer.\n"
            "Use specifics from the clarification exchange. Include: empathy, acknowledgment of the exact issue, "
            "clear next steps, and a timeline commitment.\n"
            "Output ONLY: {\"response_draft\": \"<your complete response to the customer>\"}"
        ),
    },
}

MAX_STEPS_PER_TASK: Dict[str, int] = {
    "classify_ticket": 2,
    "draft_response": 3,
    "triage_queue": 2,
    "resolve_ticket": 3,
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

    # ── Class-level shared state ───────────────────────────────────────────────
    # The OpenEnv HTTP server creates a NEW environment instance per request and
    # calls close() after each one. With a single worker (--workers 1), storing
    # the active episode at class level lets reset() and step() share state across
    # separate HTTP requests — fixing the 500 error on /step after /reset.
    _active_episode: ClassVar[Optional["SupportState"]] = None

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

        full_content: Optional[str] = None
        customer_reply: Optional[str] = None
        clarification_keywords: List[str] = []

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
            ground_truth: Dict[str, Any] = {**raw["ground_truth"], "subject": raw["subject"]}
            queue: Optional[List[TicketInfo]] = None
            queue_gt: List[Dict[str, Any]] = []
        elif task == "triage_queue":
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
        else:  # resolve_ticket
            raw = rng.choice(AMBIGUOUS_TICKETS)
            # Show only partial content initially — agent must ask to get the full story
            ticket = TicketInfo(
                ticket_id=raw["ticket_id"],
                subject=raw["subject"],
                content=raw["partial_content"],
                customer_name=raw["customer_name"],
                customer_email=raw["customer_email"],
            )
            ground_truth = {**raw["ground_truth"], "subject": raw["subject"]}
            queue = None
            queue_gt = []
            full_content = raw["full_content"]
            customer_reply = raw["customer_reply"]
            clarification_keywords = raw["clarification_keywords"]

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
            full_content=full_content,
            customer_reply=customer_reply,
            clarification_keywords=clarification_keywords,
            clarification_done=False,
        )

        # Persist episode at class level so the HTTP server's next request
        # (which creates a fresh instance) can still find the active state.
        SupportTriageEnvironment._active_episode = self._state

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
        # If this instance was freshly created by the HTTP server factory (instance
        # state is None), load the active episode from the class-level store.
        if self._state is None:
            if SupportTriageEnvironment._active_episode is not None:
                self._state = SupportTriageEnvironment._active_episode
            else:
                raise RuntimeError("Environment not initialised. Call reset() first.")

        s = self._state
        task = s.task_name
        current_step = s.step

        reward, result_msg = self._grade(task, current_step, action, s.ground_truth)

        # resolve_ticket: after clarification step, reveal full content + customer reply
        revealed_info: Optional[str] = None
        if task == "resolve_ticket" and current_step == 0 and s.full_content and s.customer_reply:
            s.ticket = TicketInfo(
                ticket_id=s.ticket.ticket_id,
                subject=s.ticket.subject,
                content=s.full_content,
                customer_name=s.ticket.customer_name,
                customer_email=s.ticket.customer_email,
            )
            s.clarification_done = True
            revealed_info = f"Customer reply: {s.customer_reply}"
        elif task == "resolve_ticket" and s.clarification_done and s.customer_reply:
            revealed_info = f"Customer reply: {s.customer_reply}"

        s.score += reward
        s.step += 1
        done = s.step >= s.max_steps
        s.done = done

        # Clamp final score to strictly (0, 1) as required by the evaluation platform.
        # Use 0.001 so the value survives 3-decimal-place formatting in [END] logs.
        if done:
            s.score = min(max(s.score, 0.001), 0.999)

        # Keep class-level episode in sync after every step
        SupportTriageEnvironment._active_episode = s

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
            revealed_info=revealed_info,
            metadata=meta,
        )

    @property
    def state(self) -> SupportState:
        # Fall back to class-level active episode for HTTP server compatibility
        if self._state is None and SupportTriageEnvironment._active_episode is not None:
            return SupportTriageEnvironment._active_episode
        if self._state is None:
            raise RuntimeError("Call reset() first.")
        return self._state

    def close(self) -> None:
        # Clear instance state only. The class-level _active_episode is intentionally
        # kept alive so the next HTTP request (new instance) can still call step().
        # _active_episode is only replaced when reset() starts a new episode.
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
        elif task == "resolve_ticket":
            return self._grade_resolve(step, action, gt)
        return 0.0, "Unknown task."

    # ── Valid value sets for penalty checks ───────────────────────────────────
    VALID_CLASSIFICATIONS = {"billing", "technical", "account", "general"}
    VALID_URGENCIES = {"low", "medium", "high", "critical"}

    # classify_ticket ──────────────────────────────────────────────────────────

    def _grade_classify(
        self, step: int, action: SupportAction, gt: Dict[str, Any]
    ) -> Tuple[float, str]:
        if step == 0:
            submitted = (action.classification or "").lower().strip()
            if not submitted:
                return -0.10, "No classification submitted. Penalty -0.10."
            if submitted not in self.VALID_CLASSIFICATIONS:
                return -0.10, (
                    f"Invalid classification '{submitted}'. "
                    f"Must be one of {sorted(self.VALID_CLASSIFICATIONS)}. Penalty -0.10."
                )
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
            if not submitted:
                return -0.10, "No urgency submitted. Penalty -0.10."
            if submitted not in self.VALID_URGENCIES:
                return -0.10, (
                    f"Invalid urgency '{submitted}'. "
                    f"Must be one of {sorted(self.VALID_URGENCIES)}. Penalty -0.10."
                )
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
            if not submitted:
                return -0.10, "No classification submitted. Penalty -0.10."
            if submitted not in self.VALID_CLASSIFICATIONS:
                return -0.10, (
                    f"Invalid classification '{submitted}'. "
                    f"Must be one of {sorted(self.VALID_CLASSIFICATIONS)}. Penalty -0.10."
                )
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
            if not submitted:
                return -0.10, "No urgency submitted. Penalty -0.10."
            if submitted not in self.VALID_URGENCIES:
                return -0.10, (
                    f"Invalid urgency '{submitted}'. "
                    f"Must be one of {sorted(self.VALID_URGENCIES)}. Penalty -0.10."
                )
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
            if not submitted_id:
                return -0.10, "No escalation ticket ID submitted. Penalty -0.10."

            # Check submitted ID is actually one of the queue ticket IDs
            valid_ids = {c["ticket_id"] for c in gt["classifications"]}
            if submitted_id not in valid_ids:
                return -0.15, (
                    f"Ticket ID '{submitted_id}' not in this queue. "
                    f"Valid IDs: {sorted(valid_ids)}. Penalty -0.15."
                )

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

    # resolve_ticket ───────────────────────────────────────────────────────────

    def _grade_resolve(
        self, step: int, action: SupportAction, gt: Dict[str, Any]
    ) -> Tuple[float, str]:
        """
        Grader for the multi-turn resolve_ticket task.

        Step 0 — Clarification quality (+0.10 max, -0.10 if empty):
            Measures whether the agent asked a targeted, relevant question.
            Scored by keyword overlap between the question and clarification_keywords.

        Step 1 — Classification with full context (+0.40 max):
            Agent must submit BOTH category (+0.25) and urgency (+0.15) correctly.
            Invalid values carry -0.10 penalty each.

        Step 2 — Response quality (+0.50 max):
            Uses the enriched 7-criterion rubric × 0.50 weight.

        Max total: 1.00
        """
        if step == 0:
            question = (action.clarification_request or "").strip()
            if not question:
                return -0.10, "No clarification question submitted. Penalty -0.10."
            if len(question) < 10:
                return -0.05, "Clarification too brief to be useful. Penalty -0.05."

            q_lower = question.lower()
            clue_kws: List[str] = self._state.clarification_keywords if self._state else []
            matched = sum(1 for kw in clue_kws if kw in q_lower)
            if matched >= 2:
                reward, quality = 0.10, "targeted"
            elif matched == 1:
                reward, quality = 0.05, "partially relevant"
            else:
                reward, quality = -0.05, "off-target"

            msg = (
                f"Clarification question: {quality} "
                f"({matched}/{len(clue_kws)} relevant keywords matched). "
                f"Reward: {reward:+.2f}/0.10. "
                f"Full ticket details now revealed."
            )
            return reward, msg

        elif step == 1:
            # Both classification and urgency in one action
            cls_submitted = (action.classification or "").lower().strip()
            urg_submitted = (action.urgency or "").lower().strip()
            reward = 0.0
            parts = []

            # Classification
            if not cls_submitted:
                reward -= 0.10
                parts.append("No classification submitted (-0.10)")
            elif cls_submitted not in self.VALID_CLASSIFICATIONS:
                reward -= 0.10
                parts.append(f"Invalid classification '{cls_submitted}' (-0.10)")
            elif cls_submitted == gt["classification"]:
                reward += 0.25
                parts.append(f"Classification '{cls_submitted}' ✓ (+0.25)")
            else:
                parts.append(f"Classification '{cls_submitted}' ✗ (expected '{gt['classification']}')")

            # Urgency
            if not urg_submitted:
                reward -= 0.10
                parts.append("No urgency submitted (-0.10)")
            elif urg_submitted not in self.VALID_URGENCIES:
                reward -= 0.10
                parts.append(f"Invalid urgency '{urg_submitted}' (-0.10)")
            elif urg_submitted == gt["urgency"]:
                reward += 0.15
                parts.append(f"Urgency '{urg_submitted}' ✓ (+0.15)")
            else:
                parts.append(f"Urgency '{urg_submitted}' ✗ (expected '{gt['urgency']}')")

            return round(reward, 4), " | ".join(parts)

        else:  # step == 2
            quality = self._score_response(action.response_draft, gt)
            reward = round(quality * 0.50, 4)
            msg = f"Response quality: {quality:.2f}/1.00 → reward +{reward:.2f}/0.50"
            return reward, msg

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _char_trigram_overlap(self, text1: str, text2: str) -> float:
        """
        Jaccard similarity of character trigrams between two texts.
        Returns 0.0–1.0. Rewards vocabulary specificity in responses.
        """
        def trigrams(s: str):
            s = s.lower().strip()
            return {s[i: i + 3] for i in range(len(s) - 2)} if len(s) >= 3 else set()

        t1, t2 = trigrams(text1), trigrams(text2)
        if not t1 or not t2:
            return 0.0
        return len(t1 & t2) / len(t1 | t2)

    # Response quality scorer ──────────────────────────────────────────────────

    def _score_response(self, response: Optional[str], gt: Dict[str, Any]) -> float:
        """
        Score a customer support response draft from 0.0 to 1.0.

        Rubric (deterministic, keyword-based):
          0.10  — Greeting (hello / hi / dear / thank you)
          0.10  — Empathy / apology (sorry / apologise / understand / regret)
          0.25  — Issue acknowledgment (matches ticket-specific keywords)
          0.20  — Resolution / next-steps language
          0.10  — Commitment or timeline (e.g. "within 24 hours", "immediately")
          0.15  — Adequate length (≥ 100 chars = professional; ≥ 40 = partial)
          0.10  — Professional tone (no rude / dismissive language)

        Penalty:
          -0.20 — Response is shorter than 20 characters (too short to be useful)
          -0.10 — Response simply echoes the ticket subject verbatim
        """
        if not response or len(response.strip()) < 10:
            return 0.0

        text = response.strip()
        r = text.lower()
        score = 0.0

        # Too short to be a real response
        if len(text) < 20:
            return -0.20

        # Greeting
        if any(g in r for g in ["hello", "hi ", "hi,", "dear ", "thank you for", "thanks for"]):
            score += 0.10

        # Empathy / apology
        if any(e in r for e in ["sorry", "apologis", "apologiz", "understand", "regret", "sincerely"]):
            score += 0.10

        # Issue acknowledgment — ticket-specific keywords
        issue_kws = gt.get("issue_keywords", [])
        matched_kws = sum(1 for kw in issue_kws if kw.lower() in r) if issue_kws else 0
        if matched_kws >= 2:
            score += 0.25
        elif matched_kws == 1:
            score += 0.12

        # Resolution / action language
        resolution = [
            "resolve", "fix", "help", "assist", "solution", "escalat",
            "investigate", "look into", "next step", "guide", "refund",
            "restore", "reset", "update", "reverse", "correct", "credit",
            "engineer", "team", "follow up", "follow-up", "working on",
            "priority", "urgent", "immediately", "right away",
        ]
        matched_res = sum(1 for w in resolution if w in r)
        if matched_res >= 2:
            score += 0.20
        elif matched_res == 1:
            score += 0.10

        # Commitment or timeline
        timeline = [
            "within 24", "within 48", "within 1 hour", "within an hour",
            "immediately", "right away", "as soon as", "by end of day",
            "today", "shortly", "asap", "promptly",
        ]
        if any(t in r for t in timeline):
            score += 0.10

        # Length quality
        if len(text) >= 100:
            score += 0.15
        elif len(text) >= 40:
            score += 0.07

        # Professionalism (no rude / dismissive language)
        rude = ["stupid", "idiot", "hate", "worst", "ridiculous", "incompetent",
                "not my problem", "not our fault", "deal with it"]
        if not any(w in r for w in rude):
            score += 0.10

        # Penalty: response just echoes the subject line verbatim
        subject = gt.get("subject", "").lower()
        if subject and len(subject) > 10 and subject in r:
            score -= 0.10

        # Specificity bonus: character trigram overlap with issue keywords
        # Rewards responses that use vocabulary drawn from the actual ticket content
        issue_reference = " ".join(gt.get("issue_keywords", []))
        if issue_reference and len(text) >= 30:
            overlap = self._char_trigram_overlap(text, issue_reference)
            score += min(overlap * 0.15, 0.08)  # up to +0.08 bonus

        return round(min(max(score, -0.20), 1.0), 4)
