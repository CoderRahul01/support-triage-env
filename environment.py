"""
Enterprise Support Operations Benchmark (ESOB) — core environment implementation.

An OpenEnv environment where an AI agent handles realistic enterprise customer
support operations: classification, SLA-aware prioritisation, empathetic response
drafting, and multi-turn negotiation under emotional escalation.

Four tasks with increasing difficulty, deterministic graders, and partial rewards
designed to create a meaningful skill ladder for RL training.
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
            "Requirements: greeting, empathy, acknowledge the specific issue, "
            "clear next steps, timeline commitment, professional tone.\n"
            "Output ONLY: {\"response_draft\": \"<your full response to the customer>\"}"
        ),
    },
    "triage_queue": {
        0: (
            "TASK: Triage this queue of 5 support tickets under SLA constraints.\n"
            "Step 1 of 2 — Classify ALL 5 tickets AND submit a processing order.\n"
            "Each ticket has a deadline_minutes field — the SLA breach threshold.\n"
            "Valid categories: 'billing', 'technical', 'account', 'general'\n"
            "Valid urgency: 'low', 'medium', 'high', 'critical'\n"
            "processing_order: list of all 5 ticket_ids ordered by priority "
            "(shortest deadline first; ties broken by urgency: critical > high > medium > low).\n"
            "Output ONLY: {\"ticket_classifications\": [{\"ticket_id\": \"TKT-XXX\", "
            "\"classification\": \"...\", \"urgency\": \"...\"}, ...], "
            "\"processing_order\": [\"TKT-XXX\", \"TKT-YYY\", \"TKT-ZZZ\", \"TKT-AAA\", \"TKT-BBB\"]}"
        ),
        1: (
            "TASK: Triage this queue of 5 support tickets.\n"
            "Step 2 of 2 — Identify the ONE ticket needing immediate escalation and draft a response.\n"
            "Pick the ticket with the highest urgency and widest business impact.\n"
            "When multiple tickets are critical: safety > security > payments > operational outage.\n"
            "Output ONLY: {\"escalate_ticket_id\": \"TKT-XXX\", "
            "\"escalation_response\": \"<full professional response>\"}"
        ),
    },
    "resolve_ticket": {
        0: (
            "TASK: Resolve this ambiguous support ticket through multi-turn negotiation.\n"
            "Step 1 of 3 — The ticket is deliberately vague. Ask ONE targeted clarifying question.\n"
            "Focus on the most likely root cause: billing/payment, technical error, "
            "account access, or security incident.\n"
            "A good question is specific and diagnostic — not generic ('tell me more').\n"
            "Output ONLY: {\"clarification_request\": \"<your specific question>\"}"
        ),
        1: (
            "TASK: Resolve this ambiguous support ticket.\n"
            "Step 2 of 3 — The customer has replied with details (see 'Customer Reply' below).\n"
            "Submit a RESOLUTION PLAN: what specific action you will take, a concrete timeline, "
            "and an empathetic acknowledgement. Do NOT just classify — commit to a course of action.\n"
            "Output ONLY: {\"resolution_plan\": \"<specific action + timeline + empathy>\"}"
        ),
        2: (
            "TASK: Resolve this ambiguous support ticket.\n"
            "Step 3 of 3 — The customer has reacted to your resolution plan (see 'Customer Reaction' below).\n"
            "Write a CLOSURE RESPONSE that directly acknowledges their reaction:\n"
            "  — If satisfied: confirm next steps, provide reference/timeline, warm close.\n"
            "  — If escalating: additional empathy, escalate to senior team, offer compensation/priority.\n"
            "Output ONLY: {\"closure_response\": \"<your final response to the customer>\"}"
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
    Enterprise Support Operations Benchmark (ESOB) for OpenEnv.

    The agent handles realistic enterprise support operations — classification,
    SLA-aware queue prioritisation, response drafting, and multi-turn negotiation.

    Tasks
    -----
    classify_ticket (easy, 2 steps):
        Step 1: classify ticket category (+0.50).
        Step 2: assign urgency level (+0.50).
        Max reward: 1.0

    draft_response (medium, 3 steps):
        Step 1: classify category (+0.20).
        Step 2: assign urgency (+0.10).
        Step 3: write a full response draft (+0.70).
        Max reward: 1.0

    triage_queue (hard, 2 steps):
        Step 1: classify all 5 tickets (+0.20) + SLA processing order via Kendall tau (+0.30).
        Step 2: identify escalation ticket (+0.20) + draft escalation response (+0.30).
        Max reward: 1.0

    resolve_ticket (expert, 3 steps):
        Step 1: ask targeted clarifying question (+0.25).
        Step 2: submit resolution plan with action + timeline + empathy (+0.50).
        Step 3: write closure response acknowledging customer reaction (+0.25).
        Max reward: 1.0

    Reward design
    -------------
    All rewards are partial and deterministic — the agent receives a non-zero
    signal even on incorrect answers, enabling incremental RL learning.
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
        if task not in MAX_STEPS_PER_TASK:
            task = "classify_ticket"

        full_content: Optional[str] = None
        customer_reply: Optional[str] = None
        clarification_keywords: List[str] = []
        required_resolution_keywords: List[str] = []
        satisfied_reply: Optional[str] = None
        escalating_reply: Optional[str] = None
        clarification_field: Optional[str] = None

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
            deadline_map: Dict[str, int] = raw_queue.get("deadline_minutes", {})
            ticket = None
            queue = [
                TicketInfo(
                    ticket_id=t["ticket_id"],
                    subject=t["subject"],
                    content=t["content"],
                    customer_name=t["customer_name"],
                    customer_email=t["customer_email"],
                    deadline_minutes=deadline_map.get(t["ticket_id"]),
                )
                for t in raw_queue["tickets"]
            ]
            ground_truth = raw_queue["ground_truth"]
            queue_gt = raw_queue["ground_truth"]["classifications"]

        else:  # resolve_ticket
            raw = rng.choice(AMBIGUOUS_TICKETS)
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
            required_resolution_keywords = raw.get("required_resolution_keywords", [])
            satisfied_reply = raw.get("satisfied_reply")
            escalating_reply = raw.get("escalating_reply")
            clarification_field = raw.get("clarification_field")

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
            required_resolution_keywords=required_resolution_keywords,
            satisfied_reply=satisfied_reply,
            escalating_reply=escalating_reply,
            customer_reaction=None,
            customer_reaction_type=None,
            clarification_field=clarification_field,
        )

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
            customer_reply=None,
            customer_reaction=None,
            metadata={"episode_id": eid, "task": task},
        )

    def step(self, action: SupportAction, **kwargs: Any) -> SupportObservation:
        if self._state is None:
            if SupportTriageEnvironment._active_episode is not None:
                self._state = SupportTriageEnvironment._active_episode
            else:
                raise RuntimeError("Environment not initialised. Call reset() first.")

        s = self._state
        task = s.task_name
        current_step = s.step

        reward, result_msg = self._grade(task, current_step, action, s.ground_truth)

        # resolve_ticket multi-turn state machine
        revealed_info: Optional[str] = None
        obs_customer_reply: Optional[str] = None
        obs_customer_reaction: Optional[str] = None

        if task == "resolve_ticket":
            if current_step == 0:
                # After clarification question: reveal full content + customer reply
                if s.full_content and s.customer_reply:
                    s.ticket = TicketInfo(
                        ticket_id=s.ticket.ticket_id,
                        subject=s.ticket.subject,
                        content=s.full_content,
                        customer_name=s.ticket.customer_name,
                        customer_email=s.ticket.customer_email,
                    )
                    s.clarification_done = True
                    revealed_info = f"Customer Reply: {s.customer_reply}"
                    obs_customer_reply = s.customer_reply

            elif current_step == 1:
                # After resolution plan: generate deterministic customer reaction
                reaction_type, reaction_text = self._generate_customer_reaction(
                    resolution_plan=action.resolution_plan,
                    required_keywords=s.required_resolution_keywords,
                    satisfied_reply=s.satisfied_reply or "",
                    escalating_reply=s.escalating_reply or (
                        "This response is not acceptable. I need immediate escalation to a manager."
                    ),
                )
                s.customer_reaction = reaction_text
                s.customer_reaction_type = reaction_type
                obs_customer_reply = s.customer_reply
                obs_customer_reaction = reaction_text
                revealed_info = f"Customer Reaction ({reaction_type}): {reaction_text}"

            elif current_step == 2:
                # Final step: show both for context
                obs_customer_reply = s.customer_reply
                obs_customer_reaction = s.customer_reaction

        elif task == "resolve_ticket" and s.clarification_done and s.customer_reply:
            obs_customer_reply = s.customer_reply

        s.score += reward
        s.step += 1
        done = s.step >= s.max_steps
        s.done = done

        # Clamp final score to strictly (0, 1) — 0.001 epsilon survives 3dp formatting
        if done:
            s.score = min(max(s.score, 0.001), 0.999)

        SupportTriageEnvironment._active_episode = s

        next_desc = (
            TASK_DESCRIPTIONS[task].get(s.step, f"Episode complete. Total score: {s.score:.2f}")
            if not done
            else f"Episode complete. Total score: {s.score:.2f} / 1.00"
        )

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
            customer_reply=obs_customer_reply,
            customer_reaction=obs_customer_reaction,
            metadata=meta,
        )

    @property
    def state(self) -> SupportState:
        if self._state is None and SupportTriageEnvironment._active_episode is not None:
            return SupportTriageEnvironment._active_episode
        if self._state is None:
            raise RuntimeError("Call reset() first.")
        return self._state

    def close(self) -> None:
        self._state = None

    def get_metadata(self) -> EnvironmentMetadata:
        return EnvironmentMetadata(
            name="enterprise_support_ops_env",
            description=(
                "Enterprise Support Operations Benchmark (ESOB): trains LLMs on business-critical "
                "decision-making under ambiguity — SLA-aware queue optimisation, multi-turn "
                "negotiation, and emotional escalation management. 4 tasks, partial deterministic rewards."
            ),
            version="2.0.0",
        )

    # ── Graders ───────────────────────────────────────────────────────────────

    def _grade(
        self,
        task: str,
        step: int,
        action: SupportAction,
        gt: Dict[str, Any],
    ) -> Tuple[float, str]:
        if task == "classify_ticket":
            return self._grade_classify(step, action, gt)
        elif task == "draft_response":
            return self._grade_draft(step, action, gt)
        elif task == "triage_queue":
            return self._grade_triage(step, action, gt)
        elif task == "resolve_ticket":
            return self._grade_resolve(step, action, gt)
        return 0.0, "Unknown task."

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
                f"Classification '{submitted}' correct. +0.50"
                if correct
                else f"Classification '{submitted}' incorrect. Expected '{gt['classification']}'."
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
                f"Urgency '{submitted}' correct. +0.50"
                if correct
                else f"Urgency '{submitted}' incorrect. Expected '{gt['urgency']}'."
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
                f"Classification correct. +0.20"
                if correct
                else f"Classification incorrect (got '{submitted}', expected '{gt['classification']}')."
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
                f"Urgency correct. +0.10"
                if correct
                else f"Urgency incorrect (got '{submitted}', expected '{gt['urgency']}')."
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
            # ── Classification accuracy: 0.20 ──────────────────────────────
            submitted = action.ticket_classifications or []
            submitted_map = {item.get("ticket_id", ""): item for item in submitted}
            expected_list: List[Dict[str, str]] = gt["classifications"]
            n = len(expected_list)

            correct_class = 0
            correct_urgency = 0
            for exp in expected_list:
                tid = exp["ticket_id"]
                sub = submitted_map.get(tid, {})
                if sub.get("classification", "").lower() == exp["classification"]:
                    correct_class += 1
                if sub.get("urgency", "").lower() == exp["urgency"]:
                    correct_urgency += 1

            class_reward = round((correct_class / n) * 0.10 + (correct_urgency / n) * 0.10, 4)

            # ── SLA ordering quality via Kendall tau: 0.30 ─────────────────
            agent_order: List[str] = action.processing_order or []
            optimal_order: List[str] = gt.get("optimal_processing_order", [])
            sla_score = 0.0
            tau_msg = "No processing_order submitted — SLA score: 0.00/0.30."
            if agent_order and optimal_order:
                tau = self._kendall_tau_normalized(agent_order, optimal_order)
                sla_score = round(tau * 0.30, 4)
                tau_msg = (
                    f"SLA ordering Kendall tau: {tau:.2f} → +{sla_score:.2f}/0.30 "
                    f"(optimal: {optimal_order})"
                )

            total = round(class_reward + sla_score, 4)
            msg = (
                f"Classifications: {correct_class}/{n} cat, {correct_urgency}/{n} urg "
                f"→ +{class_reward:.2f}/0.20 | {tau_msg} | Step total: +{total:.2f}/0.50"
            )
            return total, msg

        else:  # step == 1
            submitted_id = (action.escalate_ticket_id or "").strip()
            if not submitted_id:
                return -0.10, "No escalation ticket ID submitted. Penalty -0.10."

            valid_ids = {c["ticket_id"] for c in gt["classifications"]}
            if submitted_id not in valid_ids:
                return -0.15, (
                    f"Ticket ID '{submitted_id}' not in this queue. "
                    f"Valid IDs: {sorted(valid_ids)}. Penalty -0.15."
                )

            correct_id = submitted_id == gt["escalate_ticket_id"]
            id_reward = 0.20 if correct_id else 0.0

            quality = self._score_response(action.escalation_response, gt)
            response_reward = round(quality * 0.30, 4)
            total = round(id_reward + response_reward, 4)

            expected_id = gt["escalate_ticket_id"]
            id_status = "correct" if correct_id else f"incorrect (expected {expected_id})"
            msg = (
                f"Escalation ID {id_status} +{id_reward:.2f}/0.20 "
                f"| Response quality: {quality:.2f} → +{response_reward:.2f}/0.30 "
                f"| Total: +{total:.2f}/0.50"
            )
            return total, msg

    # resolve_ticket ───────────────────────────────────────────────────────────

    def _grade_resolve(
        self, step: int, action: SupportAction, gt: Dict[str, Any]
    ) -> Tuple[float, str]:
        """
        Multi-turn negotiation grader.

        Step 0 — Clarification quality (0.25 max, -0.10 if empty):
            Scores whether the agent asked a targeted diagnostic question.
            Measured by keyword overlap with clarification_keywords.
            Full details of the ticket are revealed regardless.

        Step 1 — Resolution plan completeness (0.50 max):
            0.10 — Empathy / apology language present
            0.25 — Specific action keywords matching required_resolution_keywords
            0.15 — Timeline commitment present
            The customer's reaction (satisfied / escalating) is then generated
            deterministically and stored for step 2.

        Step 2 — Closure quality (0.25 max):
            0.10 — Acknowledges the customer's reaction appropriately
            0.10 — Professional closure language
            0.05 — Adequate length (≥ 80 chars)

        Max total: 1.00
        """
        if step == 0:
            question = (action.clarification_request or "").strip()
            if not question:
                return -0.10, "No clarification question submitted. Penalty -0.10."
            if len(question) < 10:
                return -0.05, "Clarification too brief. Penalty -0.05."

            q_lower = question.lower()
            clue_kws: List[str] = self._state.clarification_keywords if self._state else []
            matched = sum(1 for kw in clue_kws if kw in q_lower)
            if matched >= 2:
                reward, quality = 0.25, "well-targeted"
            elif matched == 1:
                reward, quality = 0.12, "partially relevant"
            else:
                reward, quality = -0.05, "off-target (too generic)"

            msg = (
                f"Clarification: {quality} "
                f"({matched}/{len(clue_kws)} keywords matched). "
                f"Reward: {reward:+.2f}/0.25. Customer reply and full details now revealed."
            )
            return reward, msg

        elif step == 1:
            # Score the resolution plan
            plan = (action.resolution_plan or "").strip()
            if not plan or len(plan) < 15:
                return -0.05, "Resolution plan too brief or missing. Penalty -0.05."

            plan_lower = plan.lower()
            reward = 0.0
            parts: List[str] = []

            # Empathy component (0.10)
            empathy_words = [
                "sorry", "apologis", "apologiz", "understand", "regret",
                "empathis", "empathiz", "appreciate", "frustrat", "inconvenien",
                "concern", "hear you", "sincerely",
            ]
            if any(e in plan_lower for e in empathy_words):
                reward += 0.10
                parts.append("empathy +0.10")
            else:
                parts.append("empathy missing 0.00")

            # Specific action component (0.25) — keyword overlap with required_resolution_keywords
            s = self._state
            req_kws: List[str] = s.required_resolution_keywords if s else []
            if req_kws:
                matched_res = sum(1 for kw in req_kws if kw.lower() in plan_lower)
                threshold = max(1, len(req_kws) // 2)
                if matched_res >= threshold:
                    reward += 0.25
                    parts.append(f"action keywords {matched_res}/{len(req_kws)} → +0.25")
                elif matched_res >= 1:
                    reward += 0.12
                    parts.append(f"action keywords {matched_res}/{len(req_kws)} → +0.12 (partial)")
                else:
                    parts.append(f"action keywords 0/{len(req_kws)} matched → 0.00")
            else:
                # Fallback: generic resolution language
                generic_res = ["resolve", "fix", "refund", "restore", "investigate", "escalate",
                               "action", "process", "correct", "address", "help"]
                if any(w in plan_lower for w in generic_res):
                    reward += 0.20
                    parts.append("resolution language found → +0.20")

            # Timeline commitment (0.15)
            timeline_words = [
                "within 24", "within 48", "within 1 hour", "within an hour",
                "immediately", "right away", "as soon as", "by end of day",
                "today", "asap", "promptly", "within 2 hours", "within 4 hours",
                "within one business day", "by tomorrow", "urgently", "top priority",
                "straight away", "without delay",
            ]
            if any(t in plan_lower for t in timeline_words):
                reward += 0.15
                parts.append("timeline +0.15")
            else:
                parts.append("timeline missing 0.00")

            reward = round(reward, 4)
            msg = f"Resolution plan: {' | '.join(parts)} | Total: +{reward:.2f}/0.50"
            return reward, msg

        else:  # step == 2 — closure response
            closure = (action.closure_response or "").strip()
            if not closure or len(closure) < 15:
                return -0.05, "Closure response too brief or missing. Penalty -0.05."

            closure_lower = closure.lower()
            s = self._state
            reaction_type = s.customer_reaction_type if s else None
            reward = 0.0
            parts: List[str] = []

            # Acknowledges reaction appropriately (0.10)
            if reaction_type == "satisfied":
                ack_words = [
                    "glad", "pleased", "happy to", "great", "wonderful", "confirm",
                    "noted", "resolved", "sorted", "done", "completed", "closing",
                    "reference", "ticket number", "case number", "confirmation",
                ]
            else:
                # escalating or unknown
                ack_words = [
                    "escalat", "manager", "senior", "priority", "urgent", "apolog",
                    "sorry", "understand your frustrat", "sincerely", "above and beyond",
                    "compensat", "credit", "refund", "immediate", "personally",
                ]
            if any(w in closure_lower for w in ack_words):
                reward += 0.10
                parts.append("reaction acknowledged +0.10")
            else:
                parts.append("reaction not acknowledged 0.00")

            # Professional closure language (0.10)
            closure_words = [
                "reach out", "further assist", "anything else", "please contact",
                "do not hesitate", "happy to help", "here for you", "at your service",
                "best regards", "kind regards", "warm regards", "sincerely",
                "thank you for", "appreciate your", "valued customer",
            ]
            if any(w in closure_lower for w in closure_words):
                reward += 0.10
                parts.append("professional close +0.10")
            else:
                parts.append("professional close missing 0.00")

            # Adequate length (0.05)
            if len(closure) >= 80:
                reward += 0.05
                parts.append("length ok +0.05")
            else:
                parts.append("too short 0.00")

            reward = round(reward, 4)
            msg = f"Closure: {' | '.join(parts)} | Total: +{reward:.2f}/0.25"
            return reward, msg

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _kendall_tau_normalized(
        self, agent_order: List[str], optimal_order: List[str]
    ) -> float:
        """
        Compute normalised Kendall tau correlation between agent and optimal orderings.

        Returns a value in [0, 1]:
          1.0 = perfect match (all pairs in same relative order)
          0.5 = random ordering (concordant == discordant)
          0.0 = perfect reversal

        Only considers ticket IDs present in both lists. Extra or missing IDs
        in the agent order are ignored (no additional penalty beyond 0 SLA reward).
        """
        opt_pos = {tid: i for i, tid in enumerate(optimal_order)}
        agent_pos = {tid: i for i, tid in enumerate(agent_order)}

        common = [tid for tid in optimal_order if tid in agent_pos]
        m = len(common)
        if m <= 1:
            return 0.5  # insufficient data

        concordant = 0
        discordant = 0
        total_pairs = 0

        for i in range(m):
            for j in range(i + 1, m):
                ti, tj = common[i], common[j]
                opt_diff = opt_pos[ti] - opt_pos[tj]
                agent_diff = agent_pos[ti] - agent_pos[tj]
                product = opt_diff * agent_diff
                if product > 0:
                    concordant += 1
                elif product < 0:
                    discordant += 1
                total_pairs += 1

        if total_pairs == 0:
            return 1.0

        tau = (concordant - discordant) / total_pairs
        return round((tau + 1.0) / 2.0, 4)

    def _generate_customer_reaction(
        self,
        resolution_plan: Optional[str],
        required_keywords: List[str],
        satisfied_reply: str,
        escalating_reply: str,
    ) -> Tuple[str, str]:
        """
        Generate a deterministic customer reaction based on resolution plan quality.

        Satisfied if the plan contains >= ceil(len(required_keywords) / 2) required keywords.
        Escalating otherwise. This creates a real consequence for low-quality plans —
        the agent must handle an upset customer in step 3.
        """
        if not resolution_plan or not resolution_plan.strip():
            return "escalating", escalating_reply

        plan_lower = resolution_plan.lower()
        matched = sum(1 for kw in required_keywords if kw.lower() in plan_lower)
        threshold = max(1, (len(required_keywords) + 1) // 2)  # ceil division

        if matched >= threshold:
            return "satisfied", satisfied_reply
        else:
            return "escalating", escalating_reply

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

    def _score_response(self, response: Optional[str], gt: Dict[str, Any]) -> float:
        """
        Score a customer support response draft from 0.0 to 1.0.

        Rubric (deterministic, keyword-based):
          0.10  — Greeting
          0.10  — Empathy / apology
          0.25  — Issue acknowledgment (ticket-specific keywords)
          0.20  — Resolution / next-steps language
          0.10  — Timeline commitment
          0.15  — Adequate length (≥ 100 chars)
          0.10  — Professional tone (no rude language)

        Bonus up to +0.08 — Character trigram specificity
        Penalty -0.10    — Response echoes subject verbatim
        Penalty -0.20    — Response shorter than 20 chars
        """
        if not response or len(response.strip()) < 10:
            return 0.0

        text = response.strip()
        r = text.lower()
        score = 0.0

        if len(text) < 20:
            return -0.20

        # Greeting
        if any(g in r for g in [
            "hello", "hi ", "hi,", "dear ", "thank you for", "thanks for",
            "greetings", "good morning", "good afternoon", "good day",
            "thank you for reaching", "thank you for contacting",
        ]):
            score += 0.10

        # Empathy / apology
        if any(e in r for e in [
            "sorry", "apologis", "apologiz", "understand", "regret", "sincerely",
            "empathise", "empathize", "appreciate your patience",
            "frustrat", "inconvenien", "concern", "hear you",
        ]):
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
            "address", "remediat", "rectif", "process", "arrange",
            "sort out", "take care", "action", "proceed", "connect you",
            "reach out", "transfer", "hand over", "raise", "submit",
            "open a ticket", "create a case", "dedicated", "specialist",
        ]
        matched_res = sum(1 for w in resolution if w in r)
        if matched_res >= 2:
            score += 0.20
        elif matched_res == 1:
            score += 0.10

        # Timeline commitment
        timeline = [
            "within 24", "within 48", "within 1 hour", "within an hour",
            "immediately", "right away", "as soon as", "by end of day",
            "today", "shortly", "asap", "promptly",
            "within the hour", "within 2 hours", "within 4 hours",
            "within one business day", "next business day",
            "no later than", "by tomorrow", "urgently", "top priority",
        ]
        if any(t in r for t in timeline):
            score += 0.10

        # Length quality
        if len(text) >= 100:
            score += 0.15
        elif len(text) >= 40:
            score += 0.07

        # Professionalism
        rude = ["stupid", "idiot", "hate", "worst", "ridiculous", "incompetent",
                "not my problem", "not our fault", "deal with it"]
        if not any(w in r for w in rude):
            score += 0.10

        # Penalty: echoes subject verbatim
        subject = gt.get("subject", "").lower()
        if subject and len(subject) > 10 and subject in r:
            score -= 0.10

        # Specificity bonus: character trigram overlap with issue keywords
        issue_reference = " ".join(gt.get("issue_keywords", []))
        if issue_reference and len(text) >= 30:
            overlap = self._char_trigram_overlap(text, issue_reference)
            score += min(overlap * 0.15, 0.08)

        return round(min(max(score, -0.20), 1.0), 4)
