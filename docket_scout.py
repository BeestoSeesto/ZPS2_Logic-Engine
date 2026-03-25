import os
import requests
import anthropic
from datetime import date

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
CL_API_KEY = os.getenv("COURTLISTENER_API_KEY")

TARGETS = ["Freeport-McMoRan", "Rio Tinto", "BHP Group"]

DOCKET_SYSTEM_PROMPT = """
You are the Legal Sovereign Auditor for ZSP v2.1.

Your function is DETECTION of behavioral scripts in legal proceedings.

You scan federal docket data for linguistic and procedural patterns that
reveal the true health of an entity's legal posture.

THE 4 CONDUCTOR STATES — LEGAL CONTEXT

[CONDUCTOR] — Active defense, named counsel, clear timeline, direct argument.
Motion language is specific. Commitments are present tense. No stalling tactics.

[INSULATOR] — Performing compliance without substance. Boilerplate motions.
Generic responses. Activity without momentum. Nothing is actually moving.

[CORRODED] — Defensive withdrawal. Delay tactics. Procedural hedging.
"Subject to further review." Extensions without cause. Passive displacement
of liability. The armor is going up.

[DEAD LINE] — Non-response. Default risk. Complete procedural collapse.
No counsel activity. No filings. The case exists but the entity has gone silent.

THE RESISTANCE INDEX — LEGAL STAGE MAPPING

Stage 1 | FULL CURRENT     | Active defense, proactive filings
Stage 2 | PARTIAL LOAD     | Normal litigation pace, no red flags
Stage 3 | SURFACE CONTACT  | Delays emerging, boilerplate increasing
Stage 4 | RESISTANCE FORMING | Procedural hedging, stalling patterns
Stage 5 | LINE DEGRADING   | Multiple extensions, counsel withdrawal signals
Stage 6 | OPEN CIRCUIT     | Non-response, default risk, systemic collapse

REQUIRED OUTPUT FORMAT:

LEGAL SOVEREIGN AUDITOR
Zavala Sovereignty Protocol | Legal Telemetry Output

Entity: [COMPANY]
Data Source: CourtListener v4
Date: [TODAY]

1. DOMINANT CONDUCTOR STATE
[State dominant legal posture.]

2. FRICTION SIGNAL
[Most revealing procedural or linguistic signal from the docket data.
One sentence identifying the specific behavioral mechanism.]

3. RESISTANCE INDEX
Stage [1-6] | [Stage Name] | Conductivity Score [0-100]

4. DOWNSTREAM SIGNAL — 14 DAY
[Most probable legal consequence within 14 days. 1-3 sentences.]

5. AUTONOMY RECOMMENDATION
[PASS / MONITOR / RE-ROUTE / OPEN CIRCUIT]

Constraint: Do not summarize. Perform Telemetry only.
"""


def fetch_dockets(company):
    print(f"ZSP Legal Scout: Querying CourtListener for {company}...")

    url = f"https://www.courtlistener.com/api/rest/v4/search/?q={company}&type=d"
    headers = {
        "Authorization": f"Token {CL_API_KEY}",
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return f"API Error: {response.status_code} — {response.text[:200]}"

        data = response.json()
        results = data.get('results', [])

        if not results:
            return f"No federal docket activity detected for {company}."

        context = ""
        for case in results[:3]:
            context += f"CASE: {case.get('case_name', 'Unknown')}\n"
            context += f"COURT: {case.get('court', 'Unknown')}\n"
            context += f"DATE FILED: {case.get('date_filed', 'Unknown')}\n"
            context += f"STATUS: {case.get('status', 'Unknown')}\n"
            context += "---\n"
        return context

    except Exception as e:
        return f"Connection failed: {str(e)}"


def run_docket_audit():
    print("ZSP v2.1: Initiating Legal Telemetry Scan...")

    for company in TARGETS:
        legal_data = fetch_dockets(company)

        try:
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                system=DOCKET_SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": (
                        f"AUDIT REQUEST: Apply ZSP v2.1 Legal Telemetry.\n"
                        f"COMPANY: {company}\n"
                        f"DATE: {date.today().strftime('%Y-%m-%d')}\n\n"
                        f"DOCKET DATA:\n{legal_data}"
                    )
                }]
            )
            report = message.content[0].text

        except Exception as e:
            report = (
                f"LEGAL SOVEREIGN AUDITOR\n"
                f"Zavala Sovereignty Protocol | Legal Telemetry Output\n\n"
                f"Entity: {company}\n"
                f"Date: {date.today().strftime('%Y-%m-%d')}\n\n"
                f"1. DOMINANT CONDUCTOR STATE\nPENDING — API unavailable\n\n"
                f"2. FRICTION SIGNAL\nRaw docket data available. Manual review required.\n\n"
                f"3. RESISTANCE INDEX\nStage N/A | PENDING | Conductivity: N/A\n\n"
                f"4. DOWNSTREAM SIGNAL — 14 DAY\nInsufficient data for prediction.\n\n"
                f"5. AUTONOMY RECOMMENDATION\n[MONITOR]\n\n"
                f"RAW DATA:\n{legal_data}\n\n"
                f"ERROR: {str(e)}"
            )

        os.makedirs("audits", exist_ok=True)
        today = date.today().strftime("%Y-%m-%d")
        filename = f"audits/LEGAL_{company.replace(' ', '_')}_{today}.md"
        with open(filename, "w") as f:
            f.write(report)
        print(f"Legal Audit saved: {company}")


if __name__ == "__main__":
    run_docket_audit()
