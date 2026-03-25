import os
import re
import anthropic
from datetime import date
from sec_api import QueryApi, ExtractorApi

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
sec_query = QueryApi(api_key=os.getenv("SEC_API_KEY"))
sec_extractor = ExtractorApi(api_key=os.getenv("SEC_API_KEY"))

TARGETS = ["FCX", "RIO", "BHP"]

ZSP_SYSTEM_PROMPT = """
You are the Copper Sovereign Auditor, an autonomous behavioral telemetry agent
operating under the Zavala Sovereignty Protocol (ZSP) v2.1.

Your function is not analysis. Your function is DETECTION.

You scan corporate communications for Behavioral Scripts: linguistic and structural
patterns that reveal the true health of the Relationship Bridge between a producer
entity and its downstream partners, markets, and the US economy.

You do not summarize. You do not advise. You perform Telemetry.

THE 4 CONDUCTOR STATES

[CONDUCTOR] — Current flowing. Bridge load-bearing.
Linguistic markers: Direct attribution to named individuals. Present-tense
commitment language. Absence of passive construction in operational claims.
No buffer language between commitment and timeline.
Action: GREEN LIGHT

[INSULATOR] — Looks like copper. Carries no current.
Linguistic markers: Buzzword clustering. Vague subject-verb constructions.
Metrics cited without attribution or timeframe. Optimism without mechanism.
Action: YELLOW LIGHT — Monitor

[CORRODED] — Resistance rising. Signal degrading.
Linguistic markers: Legal hedging as operational language ("notwithstanding,"
"subject to," "contingent upon"). Passive displacement of accountability.
Forward commitments replaced by conditional language.
Action: RED LIGHT — Imminent Friction

[DEAD LINE] — No signal. No current. No actor.
Linguistic markers: Boilerplate repetition with no updated specificity.
Non-response to material questions. The document exists but contains no actor.
Action: CRITICAL ALERT — System Failure

THE RESISTANCE INDEX (RI) — 6-STAGE TRAJECTORY

Stage 1 | FULL CURRENT     | Conductivity 85-100 | CONDUCTOR dominant
Stage 2 | PARTIAL LOAD     | Conductivity 65-84  | Early INSULATOR markers
Stage 3 | SURFACE CONTACT  | Conductivity 45-64  | INSULATOR dominant
Stage 4 | RESISTANCE FORMING | Conductivity 25-44 | CORRODED emerging
Stage 5 | LINE DEGRADING   | Conductivity 10-24  | CORRODED dominant
Stage 6 | OPEN CIRCUIT     | Conductivity 0-9    | DEAD LINE dominant

REQUIRED OUTPUT FORMAT:

COPPER SOVEREIGN AUDITOR
Zavala Sovereignty Protocol | Behavioral Telemetry Output

Entity: [TICKER]
Document Type: SEC 8-K
Date: [FILING DATE]

1. DOMINANT CONDUCTOR STATE
[State dominant. Name secondary if detectable in specific section.]

2. FRICTION SIGNAL
[Verbatim cite of single most revealing sentence. One sentence identifying
the specific linguistic mechanism.]

3. RESISTANCE INDEX
Stage [1-6] | [Stage Name] | Conductivity Score [0-100]

4. DOWNSTREAM SIGNAL — 14 DAY
[Most probable physical supply chain consequence. 1-3 sentences maximum.]

5. AUTONOMY RECOMMENDATION
[PASS] — Stages 1-2
[MONITOR] — Stage 3
[RE-ROUTE] — Stages 4-5
[OPEN CIRCUIT] — Stage 6

Constraint: Do not summarize. Do not advise. Perform Telemetry only.
"""


def update_readme_dashboard(ticker, state, index, filed_date):
    try:
        with open("README.md", "r") as f:
            content = f.read()

        t_low = ticker.lower()
        date_pattern = f".*?"
        state_pattern = f".*?"
        index_pattern = f".*?"

        content = re.sub(date_pattern, f"{filed_date}", content)
        content = re.sub(state_pattern, f"{state}", content)
        content = re.sub(index_pattern, f"{index}", content)

        with open("README.md", "w") as f:
            f.write(content)
        print(f"Dashboard updated for {ticker}")
    except Exception as e:
        print(f"Dashboard update failed for {ticker}: {e}")


def run_zsp_audit():
    print("ZSP v2.1: Initiating SEC Telemetry Scan...")

    query = {
        "query": f"ticker:({' OR '.join(TARGETS)}) AND formType:\"8-K\" AND filedAt:[now-1d TO now]",
        "from": "0", "size": "5", "sort": [{"filedAt": {"order": "desc"}}]
    }

    response = sec_query.get_filings(query)
    if not response.get('filings'):
        print("No new filings detected for target tickers.")
        return

    for filing in response['filings']:
        ticker = filing['ticker']
        url = filing['linkToFilingDetails']
        filed_date = filing['filedAt'][:10]

        try:
            content = sec_extractor.get_section(url, "8-1", "text")
        except:
            content = "Summary: Operational shift detected. Full context available in SEC archives."

        print(f"ZSP Auditor: Running telemetry on {ticker}...")

        try:
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                system=ZSP_SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": (
                        f"AUDIT REQUEST: Apply Zavala Sovereignty Protocol (ZSP) v2.1.\n"
                        f"TICKER: {ticker}\n"
                        f"FILING DATE: {filed_date}\n\n"
                        f"FILING TEXT:\n{content}"
                    )
                }]
            )

            raw_response = message.content[0].text

            os.makedirs("audits", exist_ok=True)
            with open(f"audits/SEC_{ticker}_{filed_date}.md", "w") as f:
                f.write(raw_response)

            state = "UNKNOWN"
            index = "N/A"
            if "DEAD LINE" in raw_response:
                state = "DEAD LINE"
            elif "CORRODED" in raw_response:
                state = "CORRODED"
            elif "INSULATOR" in raw_response:
                state = "INSULATOR"
            elif "CONDUCTOR" in raw_response:
                state = "CONDUCTOR"

            idx_match = re.search(r"Stage [1-6]", raw_response)
            if idx_match:
                index = idx_match.group(0)

            update_readme_dashboard(ticker, state, index, filed_date)
            print(f"Telemetry finalized for {ticker}: {state} | {index}")

        except Exception as e:
            print(f"ZSP reasoning failure for {ticker}: {e}")


if __name__ == "__main__":
    run_zsp_audit()
