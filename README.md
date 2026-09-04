## Inspiration
As AI agents gain direct access to databases via tools and function-calling, prompts become executable code. This opens up a dangerous attack vector. Our team looked at the data and found a massive vulnerability gap:
* **The Exploit:** The **OWASP Top 10 for LLMs** ranks Prompt Injection (LLM01) as the #1 active threat. Attackers easily trick AI agents into running unauthorized backend commands.
* **The Detection Void:** The **IBM Cost of a Data Breach Report** shows organizations take an average of **over 200 days to detect a breach**. For an AI agent, an entire database can be stolen in seconds.
* **Alert Fatigue:** **Gartner** research reveals that **62% of security alerts are missed** or ignored due to noisy Slack and email channels. 

We built **VibeGuard** because passive dashboards and easy-to-mute browser alerts cannot stop a live breach. Security teams need an immediate, un-ignorable defense circuit breaker.

## What it does
VibeGuard acts as an inline circuit breaker for AI applications. The moment it detects a prompt-injection attack or an unauthorized data-dump attempt, it instantly freezes the API stream (`HTTP 423 Locked`), completely cutting off the attacker. 

Simultaneously, it bypasses noisy digital channels and triggers a physical phone call to the system admin via **CALL-E**. A synthetic voice delivers a "hackish" terminal alert ("Error 404: Malicious payload intercepted on Agent 4"). The admin can then triage the live infrastructure directly from their phone's keypad—pressing `1` to instantly isolate the database via Supabase Row-Level Security (RLS) or `2` to revoke the hijacked agent's authentication token.

## How we built it
We engineered a working prototype focused on speed and reliable out-of-band communication:
* **FastAPI Middleware:** Built a low-latency proxy layer that screens inbound prompts, tracks semantic shifts, and enforces the `HTTP 423` stream-freeze state machine.
* **CALL-E Integration:** Configured webhook handlers to compile type-safe responses that trigger physical phone calls and speak in clean, machine-like terminal terminology.
* **Supabase Backend:** Hooked the phone's DTMF keypad responses directly into live cloud database actions, allowing a physical button press to execute precise SQL policies.

## Challenges we ran into
* **State Syncing Over Split Channels:** Bridging an open, asynchronous API web stream with a physical phone line was difficult. If an automated script exfiltrates data at rapid speeds, it can finish before a human answers the phone. We solved this by implementing an immediate *local in-memory stream freeze* while the human makes the permanent infrastructure decision via the phone line.
* **Telephony Hook Latency:** Ensuring that parsing keypad tones from a mobile device reliably translated back into cloud database changes within milliseconds required stripping our webhook layer of heavy dependencies and keeping processing code minimal and fast.

## Accomplishments that we're proud of
* **True Out-of-Band Defense:** We successfully bridged physical telephony infrastructure with automated cloud security policies. 
* **Zero-Downtime Triage:** We proved that you can isolate compromised components and secure data mid-attack without taking down the entire enterprise backend application.
* **Bulletproof Core:** We verified our prototype structure with static analysis tools to ensure the webhook handlers are reliable and type-safe during live mitigation events.

## What we learned
* **The Power of Physical Alerts:** Shifting critical alerts entirely outside the browser window changes response rates. A ringing phone on a desk commands immediate operational attention.
* **Strict Type Safety is Essential:** When an infrastructure freeze relies on a physical keypad press, validation checks cannot fail after the call connects. Using strong typing to catch bugs before runtime is a requirement, not an option.

## What's next for VibeGuard
* **Edge Deployment:** Move the FastAPI middleware logic to edge workers to minimize latency even further.
* **Dynamic Thresholding:** Implement lightweight, local vector embeddings to calculate multi-dimensional semantic drift dynamically rather than relying on fixed classification patterns.
* **Multi-Admin Escalation Trees:** Build a failover routing system so that if the primary administrator misses the CALL-E security phone call, it automatically dials the rest of the DevOps team in order of priority.
