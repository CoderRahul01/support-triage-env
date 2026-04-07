"""
Synthetic support ticket data with deterministic ground-truth labels.
30 tickets covering real-world scenarios across 4 categories,
including ambiguous cases that challenge frontier models.
6 pre-built queues used for the triage_queue task.
"""
from typing import Any, Dict, List

TICKETS: List[Dict[str, Any]] = [
    # ── Original 15 ──────────────────────────────────────────────────────────
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

    # ── New tickets — harder, more ambiguous ──────────────────────────────────
    {
        "ticket_id": "TKT-016",
        "subject": "Production database showing corruption errors — data loss imminent",
        "content": (
            "Our production database is throwing corruption errors and some records "
            "are already missing from the last 6 hours. This affects 50,000 active users. "
            "We need an emergency engineer on this immediately. "
            "Every minute of delay risks permanent data loss."
        ),
        "customer_name": "Liam O'Brien",
        "customer_email": "liam@scaleup.ie",
        "ground_truth": {
            "classification": "technical",
            "urgency": "critical",
            "issue_keywords": ["database", "corruption", "data loss", "production", "records", "emergency"],
        },
    },
    {
        "ticket_id": "TKT-017",
        "subject": "Account suspended without warning — hospital system down",
        "content": (
            "Our hospital's patient management system is connected to your platform via API. "
            "Our account was suspended this morning without any prior notice. "
            "Clinical staff cannot access patient records. "
            "This is a medical emergency situation — please restore access immediately."
        ),
        "customer_name": "Dr. Sarah Okonkwo",
        "customer_email": "s.okonkwo@cityhospital.ng",
        "ground_truth": {
            "classification": "account",
            "urgency": "critical",
            "issue_keywords": ["suspended", "hospital", "patient", "access", "medical", "clinical", "records"],
        },
    },
    {
        "ticket_id": "TKT-018",
        "subject": "Interested in enterprise pricing for 500+ seats",
        "content": (
            "Hi, we are a Fortune 500 company evaluating your platform for company-wide deployment. "
            "We would need approximately 500-700 seats. "
            "Can you share your enterprise pricing and connect us with a sales representative?"
        ),
        "customer_name": "Michael Torres",
        "customer_email": "m.torres@fortune500.com",
        "ground_truth": {
            "classification": "general",
            "urgency": "medium",
            "issue_keywords": ["enterprise", "pricing", "seats", "sales", "company", "deployment"],
        },
    },
    {
        "ticket_id": "TKT-019",
        "subject": "Duplicate payment — charged twice for same invoice",
        "content": (
            "Your system processed my payment twice for invoice #INV-2025-0892. "
            "I have been charged $1,200 twice ($2,400 total) on my corporate card. "
            "I need one charge reversed immediately as this is causing issues with our finance team."
        ),
        "customer_name": "Beatrice Osei",
        "customer_email": "b.osei@corpfinance.gh",
        "ground_truth": {
            "classification": "billing",
            "urgency": "high",
            "issue_keywords": ["duplicate", "payment", "charged", "invoice", "refund", "finance", "reversed"],
        },
    },
    {
        "ticket_id": "TKT-020",
        "subject": "Cannot log in after mandatory password reset",
        "content": (
            "You sent a mandatory password reset email. I reset my password but now "
            "the system says my credentials are invalid. I have tried 5 times and "
            "my account is now locked. I have a board presentation starting in 45 minutes."
        ),
        "customer_name": "Alexander Petrov",
        "customer_email": "a.petrov@boardroom.ru",
        "ground_truth": {
            "classification": "account",
            "urgency": "critical",
            "issue_keywords": ["login", "password", "locked", "credentials", "account", "access", "board"],
        },
    },
    {
        "ticket_id": "TKT-021",
        "subject": "Salesforce integration stopped syncing — sales data stale",
        "content": (
            "Our Salesforce CRM integration stopped syncing 3 days ago. "
            "Our sales team is working from stale data and we have closed deals "
            "that are not showing up in the platform. Quarter-end is this Friday."
        ),
        "customer_name": "Jessica Park",
        "customer_email": "j.park@salesteam.us",
        "ground_truth": {
            "classification": "technical",
            "urgency": "high",
            "issue_keywords": ["salesforce", "integration", "sync", "data", "sales", "quarter"],
        },
    },
    {
        "ticket_id": "TKT-022",
        "subject": "Need VAT invoice for EU compliance audit",
        "content": (
            "We are undergoing a compliance audit in Germany and our auditors require "
            "VAT-compliant invoices for all our 2024 payments. "
            "Your current invoices do not include our VAT number or the required EU format. "
            "Audit deadline is in 10 days."
        ),
        "customer_name": "Klaus Wagner",
        "customer_email": "k.wagner@audit.de",
        "ground_truth": {
            "classification": "billing",
            "urgency": "medium",
            "issue_keywords": ["vat", "invoice", "compliance", "audit", "germany", "eu", "format"],
        },
    },
    {
        "ticket_id": "TKT-023",
        "subject": "Webhook delivery failing — payments not being processed",
        "content": (
            "Your webhooks have been returning 502 errors for the past 4 hours. "
            "Our payment processor relies on these webhooks to confirm transactions. "
            "We have had approximately 340 failed payment confirmations. "
            "Customers are being charged but not getting access."
        ),
        "customer_name": "Carlos Reyes",
        "customer_email": "c.reyes@paytech.mx",
        "ground_truth": {
            "classification": "technical",
            "urgency": "critical",
            "issue_keywords": ["webhook", "502", "payment", "transaction", "failed", "error", "confirm"],
        },
    },
    {
        "ticket_id": "TKT-024",
        "subject": "How to migrate data to new workspace?",
        "content": (
            "Our company is restructuring and we need to split one workspace into two. "
            "We have about 5,000 projects and 200 users that need to be migrated. "
            "Is there a bulk migration tool? What is the recommended process?"
        ),
        "customer_name": "Priyanka Nair",
        "customer_email": "p.nair@restructure.in",
        "ground_truth": {
            "classification": "general",
            "urgency": "medium",
            "issue_keywords": ["migrate", "workspace", "projects", "users", "bulk", "split"],
        },
    },
    {
        "ticket_id": "TKT-025",
        "subject": "Suspicious login from foreign IP — possible breach",
        "content": (
            "I received an alert that someone logged into my account from an IP in Belarus. "
            "I am based in Canada and have never accessed from there. "
            "I immediately changed my password but I'm concerned my data may be compromised. "
            "Can you investigate and tell me what data was accessed?"
        ),
        "customer_name": "Emma Delacroix",
        "customer_email": "e.delacroix@consulting.ca",
        "ground_truth": {
            "classification": "account",
            "urgency": "critical",
            "issue_keywords": ["suspicious", "login", "breach", "ip", "security", "compromised", "unauthorised"],
        },
    },
    {
        "ticket_id": "TKT-026",
        "subject": "Monthly report not generating — management review tomorrow",
        "content": (
            "The automated monthly performance report failed to generate this month. "
            "I tried manually triggering it but get an error: 'Report generation timeout'. "
            "My management team review is tomorrow morning and they need this data."
        ),
        "customer_name": "Samuel Adeyemi",
        "customer_email": "s.adeyemi@corp.ng",
        "ground_truth": {
            "classification": "technical",
            "urgency": "high",
            "issue_keywords": ["report", "generate", "timeout", "error", "management", "automated"],
        },
    },
    {
        "ticket_id": "TKT-027",
        "subject": "Charged in USD instead of GBP",
        "content": (
            "My account is set to GBP but I was charged in USD this month. "
            "Due to the exchange rate, I was effectively overcharged by about 22%. "
            "Please correct the currency and refund the difference."
        ),
        "customer_name": "Oliver Hartley",
        "customer_email": "o.hartley@media.co.uk",
        "ground_truth": {
            "classification": "billing",
            "urgency": "medium",
            "issue_keywords": ["currency", "usd", "gbp", "exchange", "overcharged", "refund"],
        },
    },
    {
        "ticket_id": "TKT-028",
        "subject": "How to configure SSO with Okta?",
        "content": (
            "We want to set up Single Sign-On using Okta for our enterprise account. "
            "I have found the SSO settings but the SAML configuration is not clear. "
            "Do you have step-by-step documentation? Is this supported on our current plan?"
        ),
        "customer_name": "Tanvir Ahmed",
        "customer_email": "t.ahmed@enterprise.pk",
        "ground_truth": {
            "classification": "general",
            "urgency": "low",
            "issue_keywords": ["sso", "okta", "saml", "single sign-on", "configure", "enterprise"],
        },
    },
    {
        "ticket_id": "TKT-029",
        "subject": "SSL certificate expired — site showing security warning",
        "content": (
            "The SSL certificate on our embedded widget expired this morning. "
            "Our customers are seeing browser security warnings when visiting our checkout page. "
            "This is causing abandoned carts and revenue loss. "
            "We need this fixed in the next hour or we will be forced to take the site down."
        ),
        "customer_name": "Mei Suzuki",
        "customer_email": "m.suzuki@ecommerce.jp",
        "ground_truth": {
            "classification": "technical",
            "urgency": "critical",
            "issue_keywords": ["ssl", "certificate", "expired", "security", "checkout", "revenue", "warning"],
        },
    },
    {
        "ticket_id": "TKT-030",
        "subject": "Accidentally deleted entire project — need recovery",
        "content": (
            "I accidentally deleted our main project which contains 18 months of work. "
            "It happened about 10 minutes ago. I did not have a backup. "
            "Please tell me if there is any way to recover this. "
            "The project name was 'Q4-2024-Campaign' under my account."
        ),
        "customer_name": "Gabriela Santos",
        "customer_email": "g.santos@agency.br",
        "ground_truth": {
            "classification": "account",
            "urgency": "critical",
            "issue_keywords": ["deleted", "project", "recover", "backup", "lost", "data", "restore"],
        },
    },
]


# ── Pre-built queues for the triage_queue task ─────────────────────────────────
TICKET_QUEUES: List[Dict[str, Any]] = [
    # QUEUE-001: One obvious critical (account), rest routine
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
    # QUEUE-002: Critical is a launch blocker (technical)
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
    # QUEUE-003: Billing dispute as critical
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
    # QUEUE-004 (harder): Two "high" tickets + one critical security breach
    # Agent must reason: security breach > revenue loss > data sync
    {
        "queue_id": "QUEUE-004",
        "tickets": [
            TICKETS[20],  # TKT-021: Salesforce sync (technical, high)
            TICKETS[18],  # TKT-019: duplicate payment (billing, high)
            TICKETS[24],  # TKT-025: suspicious login/breach ← ESCALATE (account, critical)
            TICKETS[21],  # TKT-022: VAT invoice audit (billing, medium)
            TICKETS[23],  # TKT-024: workspace migration (general, medium)
        ],
        "ground_truth": {
            "escalate_ticket_id": "TKT-025",
            "issue_keywords": ["suspicious", "login", "breach", "ip", "security", "compromised"],
            "classifications": [
                {"ticket_id": "TKT-021", "classification": "technical", "urgency": "high"},
                {"ticket_id": "TKT-019", "classification": "billing",   "urgency": "high"},
                {"ticket_id": "TKT-025", "classification": "account",   "urgency": "critical"},
                {"ticket_id": "TKT-022", "classification": "billing",   "urgency": "medium"},
                {"ticket_id": "TKT-024", "classification": "general",   "urgency": "medium"},
            ],
        },
    },
    # QUEUE-005 (harder): Multiple criticals — agent must choose the one with widest impact
    # Hospital account suspension > SSL cert > DB corruption
    # Correct: hospital (lives at risk > revenue > data)
    {
        "queue_id": "QUEUE-005",
        "tickets": [
            TICKETS[28],  # TKT-029: SSL cert expired (technical, critical)
            TICKETS[16],  # TKT-017: hospital account suspended ← ESCALATE (account, critical)
            TICKETS[15],  # TKT-016: DB corruption (technical, critical)
            TICKETS[26],  # TKT-027: wrong currency (billing, medium)
            TICKETS[27],  # TKT-028: SSO setup (general, low)
        ],
        "ground_truth": {
            "escalate_ticket_id": "TKT-017",
            "issue_keywords": ["hospital", "patient", "suspended", "medical", "clinical", "access"],
            "classifications": [
                {"ticket_id": "TKT-029", "classification": "technical", "urgency": "critical"},
                {"ticket_id": "TKT-017", "classification": "account",   "urgency": "critical"},
                {"ticket_id": "TKT-016", "classification": "technical", "urgency": "critical"},
                {"ticket_id": "TKT-027", "classification": "billing",   "urgency": "medium"},
                {"ticket_id": "TKT-028", "classification": "general",   "urgency": "low"},
            ],
        },
    },
    # QUEUE-006 (hardest): Webhook killing payments + data loss + board login
    # Agent must prioritise: webhook (340 failed payments, ongoing) > board login (45 min) > project delete
    {
        "queue_id": "QUEUE-006",
        "tickets": [
            TICKETS[29],  # TKT-030: accidental project delete (account, critical)
            TICKETS[22],  # TKT-023: webhook 502 → payments failing ← ESCALATE (technical, critical)
            TICKETS[19],  # TKT-020: board login in 45 min (account, critical)
            TICKETS[25],  # TKT-026: monthly report timeout (technical, high)
            TICKETS[17],  # TKT-018: enterprise pricing (general, medium)
        ],
        "ground_truth": {
            "escalate_ticket_id": "TKT-023",
            "issue_keywords": ["webhook", "502", "payment", "transaction", "failed", "confirm", "customers"],
            "classifications": [
                {"ticket_id": "TKT-030", "classification": "account",   "urgency": "critical"},
                {"ticket_id": "TKT-023", "classification": "technical", "urgency": "critical"},
                {"ticket_id": "TKT-020", "classification": "account",   "urgency": "critical"},
                {"ticket_id": "TKT-026", "classification": "technical", "urgency": "high"},
                {"ticket_id": "TKT-018", "classification": "general",   "urgency": "medium"},
            ],
        },
    },
]
