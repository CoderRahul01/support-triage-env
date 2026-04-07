"""Pydantic models for the Support Triage Environment."""
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
    Action submitted by the agent in the Support Triage environment.

    Only fill the fields relevant to the current task step.
    The task_description in the Observation tells you exactly what to submit.
    """

    # Used in: classify_ticket step 1 | draft_response step 1 | resolve_ticket step 2
    classification: Optional[str] = Field(
        default=None,
        description="Category: 'billing' | 'technical' | 'account' | 'general'",
    )

    # Used in: classify_ticket step 2 | draft_response step 2 | resolve_ticket step 2
    urgency: Optional[str] = Field(
        default=None,
        description="Urgency: 'low' | 'medium' | 'high' | 'critical'",
    )

    # Used in: draft_response step 3 | resolve_ticket step 3
    response_draft: Optional[str] = Field(
        default=None,
        description="Full professional reply to send to the customer",
    )

    # Used in: triage_queue step 1
    ticket_classifications: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="[{ticket_id, classification, urgency}, ...] for ALL tickets",
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
        description="A specific clarifying question to ask the customer (resolve_ticket task only)",
    )


class TicketInfo(BaseModel):
    """A single customer support ticket."""

    ticket_id: str
    subject: str
    content: str
    customer_name: str
    customer_email: str


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
