"""
Synthetic support ticket data with deterministic ground-truth labels.
All 15 tickets cover real-world scenarios across 4 categories.
3 pre-built queues are used for the triage_queue task.
"""
from typing import Any, Dict, List

TICKETS: List[Dict[str, Any]] = [
    {
        "ticket_id": "TKT-001",
        "subject": "Wrong charge on my invoice",
        "content": (
            "Hello, I was charged $250 this month but my subscription plan is $99/month. "
            "This is the second time this has happened. I need an immediate refund "
            "and an explanation. My account email is priya@example.com."
        ),
        "customer_name": "Priya Sharma",
        "customer_email": "priya@example.com",
        "ground_truth": {
            "classification": "billing",
            "urgency": "high",
            "issue_keywords": ["charge", "invoice", "refund", "overcharg", "billed", "amount"],
        },
    },
    {
        "ticket_id": "TKT-002",
        "subject": "App keeps crashing on startup",
        "content": (
            "Hi team, every time I open the app on my iPhone 15 it crashes immediately. "
            "I tried reinstalling but the issue persists. My whole team of 8 people "
            "is affected and we cannot do our work today. This is urgent!"
        ),
        "customer_name": "James Chen",
        "customer_email": "james.chen@techcorp.io",
        "ground_truth": {
            "classification": "technical",
            "urgency": "high",
            "issue_keywords": ["crash", "install", "app", "team", "bug", "work"],
        },
    },
    {
        "ticket_id": "TKT-003",
        "subject": "How do I export my data?",
        "content": (
            "Hi, I'm trying to export all my project data as a CSV file. "
            "I have looked through the settings but cannot find the export option. "
            "Could you guide me through the steps?"
        ),
        "customer_name": "Anika Patel",
        "customer_email": "anika@startup.in",
        "ground_truth": {
            "classification": "general",
            "urgency": "low",
            "issue_keywords": ["export", "data", "csv", "settings", "option", "guide"],
        },
    },
    {
        "ticket_id": "TKT-004",
        "subject": "Cannot reset my password — presentation in 2 hours",
        "content": (
            "I have been trying to reset my password for the past hour. "
            "I am not receiving the reset email. I checked my spam folder too. "
            "I need access to my account right away — I have a critical client "
            "presentation in 2 hours and all my files are in the system."
        ),
        "customer_name": "Ravi Kumar",
        "customer_email": "ravi.kumar@enterprise.com",
        "ground_truth": {
            "classification": "account",
            "urgency": "critical",
            "issue_keywords": ["password", "reset", "email", "access", "account", "login"],
        },
    },
    {
        "ticket_id": "TKT-005",
        "subject": "Switching from annual to monthly plan",
        "content": (
            "Hi, my annual subscription renews next month. "
            "I want to switch to the monthly plan. "
            "Will I be charged a cancellation fee? What happens to my data?"
        ),
        "customer_name": "Sophie Martin",
        "customer_email": "sophie@designco.fr",
        "ground_truth": {
            "classification": "billing",
            "urgency": "low",
            "issue_keywords": ["subscription", "renew", "plan", "cancel", "fee", "monthly"],
        },
    },
    {
        "ticket_id": "TKT-006",
        "subject": "API returning 403 Forbidden — production launch tomorrow",
        "content": (
            "We are integrating your API with our production system. "
            "We keep getting a 403 Forbidden error on the /data endpoint "
            "even with the correct API key. Our product launch is tomorrow morning "
            "and this is completely blocking us."
        ),
        "customer_name": "Elena Kovac",
        "customer_email": "elena@devteam.eu",
        "ground_truth": {
            "classification": "technical",
            "urgency": "critical",
            "issue_keywords": ["api", "403", "forbidden", "error", "endpoint", "key", "launch"],
        },
    },
    {
        "ticket_id": "TKT-007",
        "subject": "Need copies of all invoices for tax filing",
        "content": (
            "Could you send me copies of all my invoices from January to March 2025? "
            "I need them for my annual tax filing. "
            "My account is under the email address below."
        ),
        "customer_name": "David Wong",
        "customer_email": "david.wong@accounting.hk",
        "ground_truth": {
            "classification": "billing",
            "urgency": "low",
            "issue_keywords": ["invoice", "copy", "tax", "january", "march", "2025"],
        },
    },
    {
        "ticket_id": "TKT-008",
        "subject": "2FA locked me out after getting a new phone",
        "content": (
            "I got a new phone and now I cannot log in because two-factor authentication "
            "is sending codes to my old phone number, which I no longer have. "
            "I run a team of 20 people and none of them can access shared resources now."
        ),
        "customer_name": "Fatima Al-Rashid",
        "customer_email": "fatima@enterprise.ae",
        "ground_truth": {
            "classification": "account",
            "urgency": "high",
            "issue_keywords": ["2fa", "two-factor", "phone", "locked", "account", "recover", "access"],
        },
    },
    {
        "ticket_id": "TKT-009",
        "subject": "Feature request: dark mode for the dashboard",
        "content": (
            "I love your product but really wish there was a dark mode option. "
            "I use the dashboard for many hours a day and the bright white "
            "background is hard on my eyes. Any plans to add this feature?"
        ),
        "customer_name": "Marcus Lee",
        "customer_email": "marcus@design.sg",
        "ground_truth": {
            "classification": "general",
            "urgency": "low",
            "issue_keywords": ["dark mode", "feature", "dashboard", "eyes", "request"],
        },
    },
    {
        "ticket_id": "TKT-010",
        "subject": "Data import failing with error 500 — blocking onboarding",
        "content": (
            "Every time we try to import our customer dataset (35,000 rows) "
            "we get an Internal Server Error after about 2 minutes. "
            "We have tried smaller batches but still get the same error. "
            "This is completely blocking our enterprise customer onboarding."
        ),
        "customer_name": "Chen Wei",
        "customer_email": "chen.wei@dataops.cn",
        "ground_truth": {
            "classification": "technical",
            "urgency": "high",
            "issue_keywords": ["import", "error", "500", "dataset", "batch", "server", "onboarding"],
        },
    },
    {
        "ticket_id": "TKT-011",
        "subject": "Charged after cancellation — demanding full refund",
        "content": (
            "I cancelled my subscription on March 1st but I was still charged on March 5th. "
            "This is an unauthorized charge. I want a full refund immediately "
            "and written confirmation that my account is fully cancelled. "
            "If this is not resolved today I will dispute the charge with my bank."
        ),
        "customer_name": "Olivia Brown",
        "customer_email": "olivia.brown@personal.co.uk",
        "ground_truth": {
            "classification": "billing",
            "urgency": "critical",
            "issue_keywords": ["cancel", "charge", "refund", "unauthorized", "subscription", "dispute"],
        },
    },
    {
        "ticket_id": "TKT-012",
        "subject": "How to add more users to our current plan?",
        "content": (
            "We are a team of 12 and our current plan allows 10 users. "
            "How can I upgrade to add 2 more seats? "
            "Will the price change immediately or at the next billing cycle?"
        ),
        "customer_name": "Arjun Mehta",
        "customer_email": "arjun@startup.in",
        "ground_truth": {
            "classification": "billing",
            "urgency": "medium",
            "issue_keywords": ["users", "seats", "upgrade", "plan", "billing", "price"],
        },
    },
    {
        "ticket_id": "TKT-013",
        "subject": "Dashboard extremely slow — 15-20 second load times",
        "content": (
            "The dashboard has been extremely slow for the past week. "
            "Pages take 15 to 20 seconds to load. I am on a 1Gbps connection "
            "and the issue affects all our team members across different locations."
        ),
        "customer_name": "Yuki Tanaka",
        "customer_email": "yuki@corp.jp",
        "ground_truth": {
            "classification": "technical",
            "urgency": "medium",
            "issue_keywords": ["slow", "dashboard", "performance", "load", "speed", "team"],
        },
    },
    {
        "ticket_id": "TKT-014",
        "subject": "Need to update company billing address",
        "content": (
            "We have moved offices and need to update the billing address on our account. "
            "New address: 123 Tech Park, Whitefield, Bangalore 560066, India. "
            "Please update this so our invoices are correct."
        ),
        "customer_name": "Rahul Gupta",
        "customer_email": "rahul@startup.in",
        "ground_truth": {
            "classification": "billing",
            "urgency": "low",
            "issue_keywords": ["billing", "address", "update", "company", "invoice"],
        },
    },
    {
        "ticket_id": "TKT-015",
        "subject": "Platform emails landing in customer spam folders",
        "content": (
            "The automated transactional emails sent from your platform "
            "to our end customers are consistently going to spam. "
            "This is severely impacting our customer communication and retention. "
            "We need this resolved as a priority."
        ),
        "customer_name": "Nadia Hassan",
        "customer_email": "nadia@ecommerce.eg",
        "ground_truth": {
            "classification": "technical",
            "urgency": "high",
            "issue_keywords": ["email", "spam", "automated", "customer", "communication", "delivery"],
        },
    },
]


# ── Pre-built queues for the triage_queue task ─────────────────────────────────
TICKET_QUEUES: List[Dict[str, Any]] = [
    {
        "queue_id": "QUEUE-001",
        "tickets": [
            TICKETS[1],   # TKT-002: app crash (technical, high)
            TICKETS[4],   # TKT-005: plan switch (billing, low)
            TICKETS[3],   # TKT-004: password + presentation ← ESCALATE (account, critical)
            TICKETS[8],   # TKT-009: dark mode (general, low)
            TICKETS[12],  # TKT-013: slow dashboard (technical, medium)
        ],
        "ground_truth": {
            "escalate_ticket_id": "TKT-004",
            "issue_keywords": ["password", "reset", "access", "presentation", "urgent", "account"],
            "classifications": [
                {"ticket_id": "TKT-002", "classification": "technical", "urgency": "high"},
                {"ticket_id": "TKT-005", "classification": "billing",   "urgency": "low"},
                {"ticket_id": "TKT-004", "classification": "account",   "urgency": "critical"},
                {"ticket_id": "TKT-009", "classification": "general",   "urgency": "low"},
                {"ticket_id": "TKT-013", "classification": "technical", "urgency": "medium"},
            ],
        },
    },
    {
        "queue_id": "QUEUE-002",
        "tickets": [
            TICKETS[5],   # TKT-006: API 403 launch tomorrow ← ESCALATE (technical, critical)
            TICKETS[6],   # TKT-007: invoice copies (billing, low)
            TICKETS[9],   # TKT-010: import error (technical, high)
            TICKETS[11],  # TKT-012: add users (billing, medium)
            TICKETS[2],   # TKT-003: export question (general, low)
        ],
        "ground_truth": {
            "escalate_ticket_id": "TKT-006",
            "issue_keywords": ["api", "403", "forbidden", "launch", "production", "error"],
            "classifications": [
                {"ticket_id": "TKT-006", "classification": "technical", "urgency": "critical"},
                {"ticket_id": "TKT-007", "classification": "billing",   "urgency": "low"},
                {"ticket_id": "TKT-010", "classification": "technical", "urgency": "high"},
                {"ticket_id": "TKT-012", "classification": "billing",   "urgency": "medium"},
                {"ticket_id": "TKT-003", "classification": "general",   "urgency": "low"},
            ],
        },
    },
    {
        "queue_id": "QUEUE-003",
        "tickets": [
            TICKETS[10],  # TKT-011: charged after cancel ← ESCALATE (billing, critical)
            TICKETS[7],   # TKT-008: 2FA lockout (account, high)
            TICKETS[13],  # TKT-014: billing address (billing, low)
            TICKETS[14],  # TKT-015: emails in spam (technical, high)
            TICKETS[0],   # TKT-001: wrong charge (billing, high)
        ],
        "ground_truth": {
            "escalate_ticket_id": "TKT-011",
            "issue_keywords": ["cancel", "charge", "refund", "unauthorized", "subscription", "dispute"],
            "classifications": [
                {"ticket_id": "TKT-011", "classification": "billing",   "urgency": "critical"},
                {"ticket_id": "TKT-008", "classification": "account",   "urgency": "high"},
                {"ticket_id": "TKT-014", "classification": "billing",   "urgency": "low"},
                {"ticket_id": "TKT-015", "classification": "technical", "urgency": "high"},
                {"ticket_id": "TKT-001", "classification": "billing",   "urgency": "high"},
            ],
        },
    },
]
