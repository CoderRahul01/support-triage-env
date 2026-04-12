"""Pydantic models for the Enterprise Support Operations Benchmark (ESOB)."""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

try:
    from openenv.core.env_server.types import Action, Observation, State
except ImportError:
    # Fallback for local dev without openenv-core installed
    class Action(BaseModel):  # type: ignore[no-redef]
        pass

    class Observation(BaseModel):  # type: ignore[no-redef]
        done: bool = False
        reward: Optional[float] = None

    class State(BaseModel):  # type: ignore[no-redef]
        pass


class SupportAction(Action):
    """
    Action submitted by the agent in the Enterprise Support Operations Benchmark.

    Only fill the fields relevant to the current task step.
    The task_description in the Observation tells you exactly what to submit.
    """

    # Used in: classify_ticket step 1 | draft_response step 1 | resolve_ticket step 2
    classification: Optional[str] = Field(
        default=None,
        description="Category: 'billing' | 'technical' | 'account' | 'general'",
    )

    # Used in: classify_ticket step 2 | draft_response step 2
    urgency: Optional[str] = Field(
        default=None,
        description="Urgency: 'low' | 'medium' | 'high' | 'critical'",
    )

    # Used in: draft_response step 3
    response_draft: Optional[str] = Field(
        default=None,
        description="Full professional reply to send to the customer",
    )

    # Used in: triage_queue step 1
    ticket_classifications: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="[{ticket_id, classification, urgency}, ...] for ALL tickets in the queue",
    )

    # Used in: triage_queue step 1 — SLA-aware processing order (most urgent first)
    processing_order: Optional[List[str]] = Field(
        default=None,
        description=(
            "Ordered list of ticket_ids representing the proposed processing priority "
            "(index 0 = handle first). Ranked by SLA deadline_minutes to minimise total SLA breaches."
        ),
    )

    # Used in: triage_queue step 2
    escalate_ticket_id: Optional[str] = Field(
        default=None,
        description="ID of the ticket that needs immediate escalation",
    )
    escalation_response: Optional[str] = Field(
        default=None,
        description="Full response draft for the escalated ticket",
    )

    # Used in: resolve_ticket step 1
    clarification_request: Optional[str] = Field(
        default=None,
        description="A specific clarifying question to ask the customer (resolve_ticket step 1)",
    )

    # Used in: resolve_ticket step 2 — resolution plan submitted before customer reacts
    resolution_plan: Optional[str] = Field(
        default=None,
        description=(
            "Resolution plan for the customer's issue: state the specific action you will take, "
            "include a concrete timeline commitment, and express empathy. "
            "Used in resolve_ticket step 2."
        ),
    )

    # Used in: resolve_ticket step 3 — final closure after customer reaction is revealed
    closure_response: Optional[str] = Field(
        default=None,
        description=(
            "Final closure response acknowledging the customer's reaction to your resolution plan. "
            "Adapt tone based on whether the customer is satisfied or escalating."
        ),
    )


class TicketInfo(BaseModel):
    """A single customer support ticket."""

    ticket_id: str
    subject: str
    content: str
    customer_name: str
    customer_email: str
    # SLA deadline in minutes from now — populated for triage_queue tasks
    deadline_minutes: Optional[int] = Field(
        default=None,
        description="SLA deadline: minutes from now before this ticket breaches service level",
    )


class SupportObservation(Observation):
    """What the agent sees after each reset() or step()."""

    task_name: str = ""
    ticket: Optional[TicketInfo] = None
    ticket_queue: Optional[List[TicketInfo]] = None
    task_description: str = ""
    step: int = 0
    max_steps: int = 3
    last_action_result: Optional[str] = None
    score: float = 0.0
    reward: Optional[float] = None
    revealed_info: Optional[str] = Field(
        default=None,
        description="Extra context revealed after a clarification request (resolve_ticket task)",
    )
    # resolve_ticket: customer reply revealed after step 1
    customer_reply: Optional[str] = Field(
        default=None,
        description="Customer's reply to the agent's clarifying question (resolve_ticket step 2+)",
    )
    # resolve_ticket: customer reaction revealed after step 2 (resolution plan)
    customer_reaction: Optional[str] = Field(
        default=None,
        description=(
            "Customer's reaction to the agent's resolution plan — either satisfied or escalating. "
            "Revealed at step 3 of resolve_ticket. Agent must acknowledge this in closure_response."
        ),
    )
    metadata: Dict[str, Any] = {}


class SupportState(State):
    """Internal episode state (returned by GET /state)."""

    episode_id: str = ""
    task_name: str = ""
    ticket: Optional[TicketInfo] = None
    ticket_queue: Optional[List[TicketInfo]] = None
    step: int = 0
    max_steps: int = 3
    done: bool = False
    score: float = 0.0
    ground_truth: Dict[str, Any] = {}
    queue_ground_truth: List[Dict[str, Any]] = []
    # resolve_ticket-specific fields
    full_content: Optional[str] = None
    customer_reply: Optional[str] = None
    clarification_keywords: List[str] = []
    clarification_done: bool = False
    # resolve_ticket negotiation fields (new)
    required_resolution_keywords: List[str] = []
    satisfied_reply: Optional[str] = None
    escalating_reply: Optional[str] = None
    customer_reaction: Optional[str] = None        # generated after step 1, shown in step 2 obs
    customer_reaction_type: Optional[str] = None   # "satisfied" | "escalating"
    clarification_field: Optional[str] = None
