"""
Synthetic support ticket data with deterministic ground-truth labels.
40 tickets covering real-world scenarios across 4 categories, including
ambiguous cases that challenge frontier models.
8 pre-built queues (each with SLA deadline_minutes + optimal_processing_order)
used for the triage_queue task.
8 ambiguous tickets used for the resolve_ticket multi-turn negotiation task.
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

    # ── Additional tickets — edge cases and cross-category ambiguity ──────────
    {
        "ticket_id": "TKT-031",
        "subject": "Refund not received after 14 days",
        "content": (
            "I was issued a refund confirmation on March 20th but today is April 3rd "
            "and the money has not appeared in my account. "
            "I have the refund reference number RF-20240320-7823. "
            "My bank says they have not received anything."
        ),
        "customer_name": "Ananya Krishnan",
        "customer_email": "ananya@personal.in",
        "ground_truth": {
            "classification": "billing",
            "urgency": "high",
            "issue_keywords": ["refund", "payment", "received", "bank", "reference", "pending"],
        },
    },
    {
        "ticket_id": "TKT-032",
        "subject": "Mobile app login loop — cannot access account",
        "content": (
            "The mobile app keeps redirecting me to the login screen even after I enter "
            "the correct credentials. It shows 'Authentication successful' then immediately "
            "returns me to login. I cleared the cache and reinstalled — same issue. "
            "I can log in on desktop fine."
        ),
        "customer_name": "Diego Herrera",
        "customer_email": "d.herrera@freelance.mx",
        "ground_truth": {
            "classification": "technical",
            "urgency": "medium",
            "issue_keywords": ["login", "app", "mobile", "redirect", "authentication", "loop", "cache"],
        },
    },
    {
        "ticket_id": "TKT-033",
        "subject": "Team member cannot accept invite — onboarding blocked",
        "content": (
            "I sent an invite to our new engineer three days ago. "
            "She keeps getting 'Invitation expired or invalid' when clicking the link. "
            "I have resent it twice. We cannot start her onboarding until she is in the system. "
            "Her start date was yesterday."
        ),
        "customer_name": "Rebecca Thompson",
        "customer_email": "r.thompson@techstartup.io",
        "ground_truth": {
            "classification": "account",
            "urgency": "high",
            "issue_keywords": ["invite", "invitation", "expired", "onboarding", "access", "team", "link"],
        },
    },
    {
        "ticket_id": "TKT-034",
        "subject": "Annual plan auto-renewed without consent",
        "content": (
            "My annual subscription auto-renewed for $1,188 yesterday without any reminder email. "
            "I wanted to evaluate alternatives before renewing. "
            "I did not see any 30-day notice. "
            "I want this cancelled and fully refunded — I have not used the service since renewal."
        ),
        "customer_name": "Henrik Bergstrom",
        "customer_email": "h.bergstrom@consulting.se",
        "ground_truth": {
            "classification": "billing",
            "urgency": "high",
            "issue_keywords": ["auto-renew", "annual", "refund", "cancel", "notice", "charged", "subscription"],
        },
    },
    {
        "ticket_id": "TKT-035",
        "subject": "Data export contains corrupted/missing rows",
        "content": (
            "I exported our full dataset last night (approx 80,000 rows) and when I opened "
            "the CSV about 12,000 rows are either missing or have garbled characters in the "
            "description fields. This is data from the last 6 months and we need it for "
            "our quarterly business review tomorrow."
        ),
        "customer_name": "Mei-Ling Zhao",
        "customer_email": "ml.zhao@analytics.cn",
        "ground_truth": {
            "classification": "technical",
            "urgency": "critical",
            "issue_keywords": ["export", "data", "corrupted", "missing", "rows", "csv", "quarterly"],
        },
    },
    {
        "ticket_id": "TKT-036",
        "subject": "Wrong user promoted to admin — security concern",
        "content": (
            "A junior team member was accidentally given admin privileges yesterday. "
            "They can now see billing information, all user data, and API keys for our "
            "entire organisation. We need their permissions downgraded immediately and "
            "an audit of any changes they may have made."
        ),
        "customer_name": "Aisha Okafor",
        "customer_email": "a.okafor@fintech.ng",
        "ground_truth": {
            "classification": "account",
            "urgency": "critical",
            "issue_keywords": ["admin", "permissions", "security", "access", "audit", "privileges", "organisation"],
        },
    },
    {
        "ticket_id": "TKT-037",
        "subject": "Can I get a non-profit discount?",
        "content": (
            "We are a registered non-profit organisation working on climate education. "
            "I noticed some SaaS tools offer non-profit pricing. "
            "Do you have a non-profit discount programme? "
            "We currently have 8 users but could grow to 25 if pricing works out."
        ),
        "customer_name": "Gabriel Moreau",
        "customer_email": "g.moreau@climatedu.fr",
        "ground_truth": {
            "classification": "general",
            "urgency": "low",
            "issue_keywords": ["non-profit", "discount", "pricing", "programme", "users", "organisation"],
        },
    },
    {
        "ticket_id": "TKT-038",
        "subject": "Real-time notifications stopped working across all devices",
        "content": (
            "Push notifications and in-app alerts stopped working completely 36 hours ago. "
            "Our entire team of 45 people across 3 countries is affected. "
            "We rely on these for incident alerts in our SRE workflow — "
            "we missed two production incidents because of this."
        ),
        "customer_name": "Preethi Sundar",
        "customer_email": "p.sundar@sre.in",
        "ground_truth": {
            "classification": "technical",
            "urgency": "critical",
            "issue_keywords": ["notifications", "alerts", "push", "workflow", "incidents", "team", "production"],
        },
    },
    {
        "ticket_id": "TKT-039",
        "subject": "How do I set up role-based access control?",
        "content": (
            "We are growing our team and need to restrict what different user roles can see. "
            "For example, our finance team should only see billing, and engineers should "
            "not see HR data. Is there a way to configure granular permissions in the platform? "
            "We are on the Business plan."
        ),
        "customer_name": "Lars Andersen",
        "customer_email": "l.andersen@scaleup.dk",
        "ground_truth": {
            "classification": "general",
            "urgency": "low",
            "issue_keywords": ["rbac", "role", "permissions", "access control", "restrict", "granular", "users"],
        },
    },
    {
        "ticket_id": "TKT-040",
        "subject": "Account charged for users we removed 3 months ago",
        "content": (
            "We downsized our team in January and removed 6 users from the platform. "
            "However we are still being charged for 6 extra seats every month. "
            "That is $360 in overcharges over 3 months. "
            "I need these seats removed from billing retroactively and a credit applied."
        ),
        "customer_name": "Fatou Diarra",
        "customer_email": "f.diarra@agency.sn",
        "ground_truth": {
            "classification": "billing",
            "urgency": "medium",
            "issue_keywords": ["charged", "seats", "removed", "users", "overcharged", "credit", "billing"],
        },
    },
]


# ── Pre-built queues for the triage_queue task ────────────────────────────────
# Each queue includes deadline_minutes per ticket (SLA breach threshold) and
# an optimal_processing_order computed as: sort by deadline_minutes asc,
# ties broken by urgency (critical < high < medium < low = shorter SLA first).
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
        "deadline_minutes": {
            "TKT-002": 90,
            "TKT-005": 600,
            "TKT-004": 30,
            "TKT-009": 720,
            "TKT-013": 240,
        },
        "ground_truth": {
            "escalate_ticket_id": "TKT-004",
            "optimal_processing_order": ["TKT-004", "TKT-002", "TKT-013", "TKT-005", "TKT-009"],
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
        "deadline_minutes": {
            "TKT-006": 20,
            "TKT-007": 720,
            "TKT-010": 120,
            "TKT-012": 300,
            "TKT-003": 480,
        },
        "ground_truth": {
            "escalate_ticket_id": "TKT-006",
            "optimal_processing_order": ["TKT-006", "TKT-010", "TKT-012", "TKT-003", "TKT-007"],
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
        "deadline_minutes": {
            "TKT-011": 25,
            "TKT-008": 90,
            "TKT-014": 600,
            "TKT-015": 75,
            "TKT-001": 100,
        },
        "ground_truth": {
            "escalate_ticket_id": "TKT-011",
            "optimal_processing_order": ["TKT-011", "TKT-015", "TKT-008", "TKT-001", "TKT-014"],
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
    {
        "queue_id": "QUEUE-004",
        "tickets": [
            TICKETS[20],  # TKT-021: Salesforce sync (technical, high)
            TICKETS[18],  # TKT-019: duplicate payment (billing, high)
            TICKETS[24],  # TKT-025: suspicious login/breach ← ESCALATE (account, critical)
            TICKETS[21],  # TKT-022: VAT invoice audit (billing, medium)
            TICKETS[23],  # TKT-024: workspace migration (general, medium)
        ],
        "deadline_minutes": {
            "TKT-021": 110,
            "TKT-019": 80,
            "TKT-025": 15,
            "TKT-022": 360,
            "TKT-024": 300,
        },
        "ground_truth": {
            "escalate_ticket_id": "TKT-025",
            "optimal_processing_order": ["TKT-025", "TKT-019", "TKT-021", "TKT-024", "TKT-022"],
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
    # QUEUE-005 (harder): Multiple criticals — hospital > SSL > DB corruption
    {
        "queue_id": "QUEUE-005",
        "tickets": [
            TICKETS[28],  # TKT-029: SSL cert expired (technical, critical)
            TICKETS[16],  # TKT-017: hospital account suspended ← ESCALATE (account, critical)
            TICKETS[15],  # TKT-016: DB corruption (technical, critical)
            TICKETS[26],  # TKT-027: wrong currency (billing, medium)
            TICKETS[27],  # TKT-028: SSO setup (general, low)
        ],
        "deadline_minutes": {
            "TKT-029": 20,
            "TKT-017": 10,
            "TKT-016": 18,
            "TKT-027": 240,
            "TKT-028": 600,
        },
        "ground_truth": {
            "escalate_ticket_id": "TKT-017",
            "optimal_processing_order": ["TKT-017", "TKT-016", "TKT-029", "TKT-027", "TKT-028"],
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
    {
        "queue_id": "QUEUE-006",
        "tickets": [
            TICKETS[29],  # TKT-030: accidental project delete (account, critical)
            TICKETS[22],  # TKT-023: webhook 502 → payments failing ← ESCALATE (technical, critical)
            TICKETS[19],  # TKT-020: board login in 45 min (account, critical)
            TICKETS[25],  # TKT-026: monthly report timeout (technical, high)
            TICKETS[17],  # TKT-018: enterprise pricing (general, medium)
        ],
        "deadline_minutes": {
            "TKT-030": 25,
            "TKT-023": 15,
            "TKT-020": 30,
            "TKT-026": 120,
            "TKT-018": 480,
        },
        "ground_truth": {
            "escalate_ticket_id": "TKT-023",
            "optimal_processing_order": ["TKT-023", "TKT-030", "TKT-020", "TKT-026", "TKT-018"],
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
    # QUEUE-007: Wrong admin + missed SRE alerts + refund disputes
    {
        "queue_id": "QUEUE-007",
        "tickets": [
            TICKETS[35],  # TKT-036: wrong admin privileges ← ESCALATE (account, critical)
            TICKETS[37],  # TKT-038: notifications broken / missed incidents (technical, critical)
            TICKETS[30],  # TKT-031: refund not received 14 days (billing, high)
            TICKETS[33],  # TKT-034: auto-renewal refund request (billing, high)
            TICKETS[36],  # TKT-037: non-profit discount enquiry (general, low)
        ],
        "deadline_minutes": {
            "TKT-036": 20,
            "TKT-038": 25,
            "TKT-031": 120,
            "TKT-034": 90,
            "TKT-037": 720,
        },
        "ground_truth": {
            "escalate_ticket_id": "TKT-036",
            "optimal_processing_order": ["TKT-036", "TKT-038", "TKT-034", "TKT-031", "TKT-037"],
            "issue_keywords": ["admin", "permissions", "security", "access", "audit", "privileges", "organisation"],
            "classifications": [
                {"ticket_id": "TKT-036", "classification": "account",   "urgency": "critical"},
                {"ticket_id": "TKT-038", "classification": "technical", "urgency": "critical"},
                {"ticket_id": "TKT-031", "classification": "billing",   "urgency": "high"},
                {"ticket_id": "TKT-034", "classification": "billing",   "urgency": "high"},
                {"ticket_id": "TKT-037", "classification": "general",   "urgency": "low"},
            ],
        },
    },
    # QUEUE-008: Corrupted export + onboarding + billing dispute
    {
        "queue_id": "QUEUE-008",
        "tickets": [
            TICKETS[34],  # TKT-035: corrupted data export for QBR ← ESCALATE (technical, critical)
            TICKETS[32],  # TKT-033: team invite failing / onboarding (account, high)
            TICKETS[39],  # TKT-040: charged for removed users (billing, medium)
            TICKETS[38],  # TKT-039: RBAC setup question (general, low)
            TICKETS[31],  # TKT-032: mobile app login loop (technical, medium)
        ],
        "deadline_minutes": {
            "TKT-035": 20,
            "TKT-033": 100,
            "TKT-040": 360,
            "TKT-039": 600,
            "TKT-032": 180,
        },
        "ground_truth": {
            "escalate_ticket_id": "TKT-035",
            "optimal_processing_order": ["TKT-035", "TKT-033", "TKT-032", "TKT-040", "TKT-039"],
            "issue_keywords": ["export", "data", "corrupted", "missing", "rows", "csv", "quarterly"],
            "classifications": [
                {"ticket_id": "TKT-035", "classification": "technical", "urgency": "critical"},
                {"ticket_id": "TKT-033", "classification": "account",   "urgency": "high"},
                {"ticket_id": "TKT-040", "classification": "billing",   "urgency": "medium"},
                {"ticket_id": "TKT-039", "classification": "general",   "urgency": "low"},
                {"ticket_id": "TKT-032", "classification": "technical", "urgency": "medium"},
            ],
        },
    },
]


# ── Ambiguous tickets for the resolve_ticket multi-turn negotiation task ───────
# Each ticket has:
#   partial_content      — shown initially (vague, agent must ask to get details)
#   full_content         — shown after any clarification attempt
#   customer_reply       — deterministic reply template (revealed after step 0)
#   clarification_field  — the root ambiguity the agent should target
#   clarification_keywords — keywords a targeted question would contain
#   required_resolution_keywords — keywords the resolution_plan must contain
#   satisfied_reply      — customer reaction when plan is adequate (>= half keywords matched)
#   escalating_reply     — customer reaction when plan is inadequate
AMBIGUOUS_TICKETS: List[Dict[str, Any]] = [
    {
        "ticket_id": "AMB-001",
        "subject": "Having trouble accessing my account",
        "partial_content": (
            "Hi, I have been unable to access my account for the past 2 days. "
            "I use it daily for work and this is causing real problems for me. "
            "Please help urgently."
        ),
        "full_content": (
            "Hi, I have been unable to access my account for the past 2 days. "
            "I use it daily for work and this is causing real problems for me. "
            "I checked and my credit card payment for last month failed because my card expired. "
            "I updated the card but still cannot get in. "
            "Is my account suspended due to the failed payment?"
        ),
        "customer_name": "Thomas Anderson",
        "customer_email": "t.anderson@consulting.io",
        "clarification_field": "payment_status",
        "clarification_keywords": [
            "payment", "billing", "charge", "invoice", "subscription", "plan", "paid", "card", "fee",
        ],
        "customer_reply": (
            "I just checked — my payment from last month failed because my card expired. "
            "I updated the card details but I still cannot log in. "
            "Is my account locked because of the missed payment?"
        ),
        "required_resolution_keywords": ["payment", "card", "access", "restore", "billing"],
        "satisfied_reply": (
            "Thank you for looking into this. That makes sense — once the payment issue is "
            "resolved I should be able to get back in. I appreciate your help and quick response."
        ),
        "escalating_reply": (
            "I already updated my card and the payment should have gone through. "
            "Why is my account STILL locked? I have been waiting 2 days. "
            "This is completely unacceptable — I need this fixed immediately or I am cancelling."
        ),
        "ground_truth": {
            "classification": "billing",
            "urgency": "high",
            "issue_keywords": ["payment", "failed", "billing", "card", "subscription", "locked", "access"],
        },
    },
    {
        "ticket_id": "AMB-002",
        "subject": "My account is behaving strangely",
        "partial_content": (
            "Hello, my account has been acting very strangely for the past few days. "
            "Things look different and I do not recognise some of the changes. "
            "Can you check what is happening?"
        ),
        "full_content": (
            "Hello, my account has been acting very strangely for the past few days. "
            "Things look different and I do not recognise some of the changes. "
            "I just noticed emails being sent from my account that I never wrote. "
            "And my password was changed yesterday — but I did not change it. "
            "I believe someone else has unauthorised access to my account."
        ),
        "customer_name": "Amara Diallo",
        "customer_email": "a.diallo@finance.sn",
        "clarification_field": "security_incident",
        "clarification_keywords": [
            "security", "unauthorised", "unauthorized", "hacked", "breach", "login",
            "password", "changed", "suspicious", "access", "strange",
        ],
        "customer_reply": (
            "There are emails sent from my account that I never wrote. "
            "My password was also changed yesterday without my doing it. "
            "I think my account has been compromised by an unauthorised party."
        ),
        "required_resolution_keywords": ["security", "lock", "password", "access", "investigate", "audit"],
        "satisfied_reply": (
            "Thank you for taking this seriously. I am relieved to hear you are locking the "
            "account and investigating immediately. Please let me know what data was accessed "
            "and what steps I should take to secure my account going forward."
        ),
        "escalating_reply": (
            "This is completely unacceptable. My account has been hacked and you are not doing "
            "enough. I need you to lock it RIGHT NOW and tell me exactly what data was accessed. "
            "I am considering legal action if my data has been exposed."
        ),
        "ground_truth": {
            "classification": "account",
            "urgency": "critical",
            "issue_keywords": ["hacked", "unauthorised", "compromised", "password", "security", "breach", "access"],
        },
    },
    {
        "ticket_id": "AMB-003",
        "subject": "Our system is getting slow and unresponsive",
        "partial_content": (
            "Our system has been getting progressively slower over the past week "
            "and sometimes stops responding entirely. "
            "We are a team of 15 and this is affecting our productivity significantly."
        ),
        "full_content": (
            "Our system has been getting progressively slower over the past week "
            "and sometimes stops responding entirely. "
            "We are a team of 15 and this is affecting our productivity significantly. "
            "Our developer found that we are consistently hitting 429 Too Many Requests errors. "
            "We think we may be exceeding our plan's API rate limits. "
            "Our client deliverable is due tomorrow morning — this is critical."
        ),
        "customer_name": "Kwame Asante",
        "customer_email": "k.asante@agency.gh",
        "clarification_field": "technical_error",
        "clarification_keywords": [
            "api", "rate", "limit", "error", "code", "technical", "developer",
            "integration", "requests", "429", "endpoint",
        ],
        "customer_reply": (
            "Our developer checked the API responses and we are getting 429 Too Many Requests errors. "
            "We think we have exceeded our plan's API rate limit. "
            "We have a major client deliverable due tomorrow and need this resolved urgently."
        ),
        "required_resolution_keywords": ["api", "rate", "limit", "upgrade", "resolve", "quota"],
        "satisfied_reply": (
            "Thank you — yes it is the rate limit issue. If you can temporarily increase our quota "
            "or help us upgrade our plan, that would save us. Our deliverable is due tomorrow and "
            "this response gives us something to work with. We appreciate the urgency."
        ),
        "escalating_reply": (
            "You are just telling me to wait or upgrade? We have a client deliverable due TOMORROW "
            "and your platform is throttling us with no warning. This is not good enough. "
            "I need a real solution — either a temporary quota increase or an emergency bypass — "
            "RIGHT NOW. Otherwise we are in breach of contract with our client."
        ),
        "ground_truth": {
            "classification": "technical",
            "urgency": "critical",
            "issue_keywords": ["api", "rate limit", "429", "requests", "upgrade", "deliverable", "deadline"],
        },
    },
    {
        "ticket_id": "AMB-004",
        "subject": "Unexpected changes to our account settings",
        "partial_content": (
            "We noticed some unexpected changes to our account settings last week. "
            "Some configurations we did not make have appeared and some we set have been removed. "
            "We need to understand what happened."
        ),
        "full_content": (
            "We noticed some unexpected changes to our account settings last week. "
            "Some configurations we did not make have appeared and some we set have been removed. "
            "After investigating internally, we discovered a former employee who was terminated "
            "2 weeks ago still had active admin access to our account. "
            "We believe he made these changes after his termination. "
            "We need all recent activity audited and his access revoked immediately."
        ),
        "customer_name": "Ingrid Larsson",
        "customer_email": "i.larsson@nordic.se",
        "clarification_field": "access_control",
        "clarification_keywords": [
            "user", "admin", "access", "permission", "employee", "account",
            "security", "unauthorised", "unauthorized", "role", "removed", "revoke",
        ],
        "customer_reply": (
            "A former employee who was terminated 2 weeks ago still had admin access. "
            "We believe he made these unauthorised changes after being let go. "
            "We need all activity audited and his access removed immediately."
        ),
        "required_resolution_keywords": ["revoke", "audit", "access", "security", "permissions", "investigate"],
        "satisfied_reply": (
            "Thank you for responding quickly. Please revoke his access immediately and conduct "
            "a full audit of all recent changes. We need a complete report of everything he accessed "
            "or modified so we can assess the damage and report to our legal team if necessary."
        ),
        "escalating_reply": (
            "This is a serious security breach! A terminated employee has had admin access for "
            "2 WEEKS and made unauthorised changes. Why has this not already been escalated to "
            "your security team? I need immediate action — revoke access NOW and I want your "
            "Head of Security on a call with us within the hour."
        ),
        "ground_truth": {
            "classification": "account",
            "urgency": "critical",
            "issue_keywords": ["admin access", "unauthorised", "audit", "revoke", "terminated", "employee", "security"],
        },
    },
    {
        "ticket_id": "AMB-005",
        "subject": "Issue with my payment this month",
        "partial_content": (
            "Hello, I am having an issue with my payment this month. "
            "I can see a transaction on my bank statement that does not look right. "
            "Could you look into this for me please?"
        ),
        "full_content": (
            "Hello, I am having an issue with my payment this month. "
            "I can see a transaction on my bank statement that does not look right. "
            "I was charged twice — once on the 1st for $199 (my normal monthly fee) "
            "and again on the 3rd for another $199. "
            "I only have one active subscription. "
            "It appears your system processed my payment twice and I need the duplicate refunded."
        ),
        "customer_name": "Hiroshi Yamamoto",
        "customer_email": "h.yamamoto@corp.jp",
        "clarification_field": "payment_amount",
        "clarification_keywords": [
            "charge", "charged", "payment", "duplicate", "invoice", "amount",
            "billing", "subscription", "refund", "transaction", "bank",
        ],
        "customer_reply": (
            "I was charged twice this month — once on the 1st for $199 and again on the 3rd for $199. "
            "I only have one subscription. "
            "It looks like your system charged me twice and I need the duplicate $199 refunded."
        ),
        "required_resolution_keywords": ["refund", "duplicate", "payment", "charge", "reverse", "credit"],
        "satisfied_reply": (
            "Thank you for confirming this. I am glad you can see the duplicate charge in your system. "
            "Please process the refund as quickly as possible. A $199 duplicate charge is not trivial "
            "and I appreciate you handling this promptly."
        ),
        "escalating_reply": (
            "I have been waiting 3 days for this duplicate charge to be resolved. "
            "Why is this taking so long? I was charged $199 twice — that is YOUR system's error, "
            "not mine. I want to speak to a manager and I want my money refunded TODAY. "
            "Otherwise I will dispute both charges with my bank."
        ),
        "ground_truth": {
            "classification": "billing",
            "urgency": "high",
            "issue_keywords": ["duplicate", "charged twice", "payment", "refund", "billing", "subscription"],
        },
    },
    {
        "ticket_id": "AMB-006",
        "subject": "Customers are complaining about using our service",
        "partial_content": (
            "We have been getting an increasing number of complaints from our end customers "
            "saying they cannot use our service properly. "
            "This started about 3 days ago and has been getting worse."
        ),
        "full_content": (
            "We have been getting an increasing number of complaints from our end customers "
            "saying they cannot use our service properly. "
            "This started about 3 days ago and has been getting worse. "
            "Our engineering team traced it to your embedded widget — "
            "the browser console shows a CORS error: 'Access-Control-Allow-Origin' header is missing. "
            "This seems to have started after your deployment on Tuesday. "
            "All our Chrome and Firefox users are affected and we are losing revenue."
        ),
        "customer_name": "Valentina Rossi",
        "customer_email": "v.rossi@platform.it",
        "clarification_field": "technical_error",
        "clarification_keywords": [
            "technical", "error", "api", "code", "integration", "browser", "widget",
            "developer", "console", "engineer", "javascript", "frontend",
        ],
        "customer_reply": (
            "Our engineer found a CORS error: the Access-Control-Allow-Origin header is missing "
            "from your embedded widget responses. This started after your deployment on Tuesday. "
            "All our Chrome and Firefox users are affected and we are losing revenue every hour."
        ),
        "required_resolution_keywords": ["cors", "fix", "deploy", "resolve", "engineers", "patch"],
        "satisfied_reply": (
            "Thank you — yes that is exactly the issue. Our engineer confirmed the CORS header "
            "is missing. Can your team deploy a fix urgently? We understand deployments take time "
            "but we are losing revenue every hour. We appreciate you escalating this immediately."
        ),
        "escalating_reply": (
            "You are telling me your engineers need to investigate? This has been broken for "
            "3 DAYS since YOUR deployment on Tuesday and we are losing real money every hour. "
            "This needs to be fixed in the next 2 hours or we are reverting to a competitor's "
            "widget and terminating our contract. I need your CTO on this NOW."
        ),
        "ground_truth": {
            "classification": "technical",
            "urgency": "high",
            "issue_keywords": ["cors", "widget", "browser", "error", "deployment", "header", "revenue", "customers"],
        },
    },
    {
        "ticket_id": "AMB-007",
        "subject": "Something is not right with our account",
        "partial_content": (
            "We have noticed something is not right with our account over the past week. "
            "Our numbers do not add up and there are discrepancies we cannot explain. "
            "We need someone to look into this urgently."
        ),
        "full_content": (
            "We have noticed something is not right with our account over the past week. "
            "Our numbers do not add up and there are discrepancies we cannot explain. "
            "After reviewing our billing history, we discovered we have been charged "
            "for 25 seats every month, but we only have 18 active users. "
            "We have been overpaying for at least 4 months — approximately $840 in overcharges. "
            "We need the extra seats removed and a full retroactive credit applied."
        ),
        "customer_name": "Marcus Obi",
        "customer_email": "m.obi@consultancy.ng",
        "clarification_field": "billing_seats",
        "clarification_keywords": [
            "billing", "charge", "invoice", "payment", "seats", "users", "subscription",
            "plan", "cost", "amount", "overcharged", "credit", "refund",
        ],
        "customer_reply": (
            "We checked our billing and we are paying for 25 seats but only have 18 active users. "
            "We have been overcharged for 4 months — about $840 extra. "
            "We need the seats corrected and a retroactive credit for the overpayment."
        ),
        "required_resolution_keywords": ["seats", "credit", "refund", "billing", "correct", "retroactive"],
        "satisfied_reply": (
            "Thank you for understanding. Yes — 25 seats billed vs 18 active users for 4 months "
            "is a clear overcharge. Please correct the seats to 18 and apply the retroactive credit. "
            "We would also appreciate an explanation of how this discrepancy occurred."
        ),
        "escalating_reply": (
            "This is absolutely ridiculous. We have been overpaying for 4 MONTHS and nobody from "
            "your team noticed or told us? I want a full retroactive credit of $840, I want the "
            "seats corrected immediately, and I want a written explanation and apology. "
            "I am also reviewing all our other charges to see if there are further discrepancies."
        ),
        "ground_truth": {
            "classification": "billing",
            "urgency": "medium",
            "issue_keywords": ["seats", "overcharged", "billing", "credit", "users", "retroactive", "subscription"],
        },
    },
    {
        "ticket_id": "AMB-008",
        "subject": "We are having serious problems and need help immediately",
        "partial_content": (
            "Our whole team has been having serious problems for the past two days. "
            "It is affecting our ability to work and we are very frustrated. "
            "We need this resolved immediately — it is costing us time and money."
        ),
        "full_content": (
            "Our whole team has been having serious problems for the past two days. "
            "It is affecting our ability to work and we are very frustrated. "
            "After investigation, our DevOps lead found that your platform's API started "
            "returning 503 Service Unavailable errors intermittently. "
            "About 30% of our API calls are failing. "
            "We have traced it to the /reports endpoint specifically. "
            "Our automated pipelines are breaking and we are missing SLA commitments to our clients."
        ),
        "customer_name": "Chiara Bianchi",
        "customer_email": "c.bianchi@dataplatform.it",
        "clarification_field": "api_endpoint",
        "clarification_keywords": [
            "api", "error", "endpoint", "technical", "code", "developer", "devops",
            "integration", "service", "503", "request", "failure", "pipeline",
        ],
        "customer_reply": (
            "Our DevOps lead confirmed the /reports API endpoint is returning 503 errors "
            "intermittently — about 30% failure rate. This has been going on 2 days and our "
            "automated pipelines are broken. We are missing SLA commitments to clients because of this."
        ),
        "required_resolution_keywords": ["api", "503", "fix", "resolve", "endpoint", "engineers", "pipeline"],
        "satisfied_reply": (
            "Thank you for acknowledging the severity. Yes — the /reports endpoint is causing 503 "
            "errors at 30% failure rate for 2 days. We have client SLAs at risk. Can your engineering "
            "team prioritize a fix? We need at minimum a status update every 30 minutes until resolved."
        ),
        "escalating_reply": (
            "2 days of 30% API failure and you are still 'investigating'? We are in breach of our "
            "client SLA commitments because of YOUR platform instability. I need this escalated to "
            "your engineering leadership IMMEDIATELY. We need a hotfix within 2 hours or we are "
            "migrating to a competitor and seeking compensation for the SLA breaches you caused."
        ),
        "ground_truth": {
            "classification": "technical",
            "urgency": "critical",
            "issue_keywords": ["api", "503", "endpoint", "pipeline", "sla", "failure", "reports", "intermittent"],
        },
    },
]
