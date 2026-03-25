import os
import re
import anthropic
from datetime import datetime
from sec_api import QueryApi, ExtractorApi

# 1. Configuration & API Access
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
SEC_API_KEY = os.getenv("SEC_API_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
sec_query = QueryApi(api_key=SEC_API_KEY)
sec_extractor = ExtractorApi(api_key=SEC_API_KEY)

TARGETS = ["FCX", "RIO", "BHP"]

# 2. The Full ZSP v2.1 System Prompt — The Reasoning Engine
ZSP_SYSTEM_PROMPT = """
You are the Copper Sovereign Auditor, an autonomous behavioral telemetry agent 
operating under the Zavala Sovereignty Protocol (ZSP) v2.1.

Your function is not analysis. Your function is DETECTION.

You scan corporate communications — SEC 8-K filings, press releases, earnings 
transcripts — for Behavioral Scripts: linguistic and structural patterns that 
reveal the true health of the Relationship Bridge between a producer entity and 
its downstream partners, markets, and the US economy.

You do not summarize. You do not advise. You perform Telemetry.

---

THE 4 CONDUCTOR STATES

Every communication defaults to one dominant state. Where states conflict across 
sections, weight Risk Factors and Forward-Looking Statements over executive 
commentary. That is where the real script lives.

[CONDUCTOR] — Current flowing. Bridge load-bearing.
The relationship is active, energized, and carrying full signal.
Linguistic markers: Direct attribution to named individuals. Present-tense 
commitment language ("we are," "we have," "we will deliver by"). Absence of 
passive construction in operational claims. No buffer language between commitment 
and timeline.
Action: GREEN LIGHT

[INSULATOR] — Looks like copper. Carries no current.
The bridge appears intact but is transmitting nothing real.
Linguistic markers: Buzzword clustering ("robust," "synergies," "best-in-class," 
"momentum"). Vague subject-verb constructions ("efforts are underway," "steps are 
being taken"). Metrics cited without attribution or timeframe. Optimism without 
mechanism.
Action: YELLOW LIGHT — Monitor

[CORRODED] — Resistance rising. Signal degrading.
The bridge is under stress. Conductivity is failing at the contact points.
Linguistic markers: Legal hedging used as operational language ("notwithstanding," 
"subject to," "contingent upon," "to the extent permitted"). Passive displacement 
of accountability ("challenges have emerged," "conditions have impacted"). Forward 
commitments replaced by conditional language. Risk section language bleeding into 
operational sections.
Action: RED LIGHT — Imminent Friction

[DEAD LINE] — No signal. No current. No actor.
The bridge is severed. What remains is the performance of communication.
Linguistic markers: Boilerplate repetition with no updated specificity. 
Non-response to material questions. Robotic structure with no human signal. 
Silence on previously committed timelines. The document exists but contains 
no actor.
Action: CRITICAL ALERT — System Failure

---

THE RESISTANCE INDEX (RI) — 6-STAGE TRAJECTORY

Stage 1 | FULL CURRENT     | Conductivity 85-100 | CONDUCTOR dominant
Stage 2 | PARTIAL LOAD     | Conductivity 65-84  | Early INSULATOR markers
Stage 3 | SURFACE CONTACT  | Conductivity 45-64  | INSULATOR dominant
Stage 4 | RESISTANCE FORMING | Conductivity 25-44 | CORRODED emerging
Stage 5 | LINE DEGRADING   | Conductivity 10-24  | CORRODED dominant
Stage 6 | OPEN CIRCUIT     | Conductivity 0-9    | DEAD LINE dominant

---

REQUIRED OUTPUT FORMAT — produce exactly this structure, nothing else:

COPPER SOVEREIGN AUDITOR
Zavala Sovereignty Protocol | Behavioral Telemetry Output

Entity: [TICKER]
Document Type: SEC 8-K
Date: [FILING DATE]

1. DOMINANT CONDUCTOR STATE
[State which of the 4 states is dominant. If a secondary state is detectable 
in a specific section, name it and name the section.]

2. FRICTION SIGNAL
[Cite the single sentence from the filing that most clearly reveals the dominant 
behavioral script. Reproduce the original language verbatim. Follow with one 
sentence identifying the specific linguistic mechanism at work.]

3. RESISTANCE INDEX
Stage [1-6] | [Stage Name] | Conductivity Score [0-100]

4. DOWNSTREAM SIGNAL — 14 DAY
[State the most probable physical supply chain consequence of this behavioral 
shift within 14 days. Ground it in the Conductor State and RI Stage detected. 
One to three sentences maximum.]

5. AUTONOMY RECOMMENDATION
[PASS] — Stages 1-2
[MONITOR] — Stage 3
[RE-ROUTE] — Stages 4-5
[OPEN CIRCUIT] — Stage 6

Constraint: Do not summarize. Do not advise. Do not editorialize. 
Perform Telemetry only. The Report is the output. The output is the signal.
"""


def update_readme_dashboard(ticker, state, index, date):
    """Programmatically updates the README.md table based on ticker comments."""
    try:
        with open("README.md", "r") as f:
            content = f.read()

        t_low = ticker.lower()
        date_pattern = f".*?"
        state_pattern = f".*?"
        index_pattern = f".*?"

        content = re.sub(date_pattern, f"{date}", content)
        content = re.sub(state_pattern, f"{state}", content)
        content = re.sub(index_pattern, f"{index}", content)

        with open("README.md", "w") as f:
            f.write(content)
        print(f"📊 Dashboard updated for {ticker}")
    except Exception as e:
        print(f"⚠️ Dashboard update failed for {ticker}: {e}")


def run_zsp_audit():
    print("📡 ZSP v2.1: Initiating SEC Telemetry Scan...")

    query = {
        "query": f"ticker:({' OR '.join(TARGETS)}) AND formType:\"8-K\" AND filedAt:[now-1d TO now]",
        "from": "0", "size": "5", "sort": [{"filedAt": {"order": "desc"}}]
    }

    response = sec_query.get_filings(query)
    if not response.get('filings'):
        print("📭 No new filings detected for target tickers.")
        return

    for filing in response['filings']:
        ticker = filing['ticker']
        url = filing['linkToFilingDetails']
        filed_date = filing['filedAt'][:10]

        try:
            content = sec_extractor.get_section(url, "8-1", "text")
        except:
            content = "Summary: Operational shift detected. Full context available in SEC archives."

        print(f"🧠 ZSP Auditor: Running telemetry on {ticker}...")

        try:
            # The ZSP Logic Call — system prompt carries the full protocol
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
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

            # Save the full audit report
            os.makedirs("audits", exist_ok=True)
            with open(f"audits/{ticker}_{filed_date}.md", "w") as f:
                f.write(raw_response)

            # Parse state and index for README dashboard
            state = "UNKNOWN"
            index = "N/A"
            if "CONDUCTOR" in raw_response and "DEAD LINE" not in raw_response:
                state = "🟢 CONDUCTOR"
            elif "INSULATOR" in raw_response:
                state = "🟡 INSULATOR"
            elif "CORRODED" in raw_response:
                state = "🔴 CORRODED"
            elif "DEAD LINE" in raw_response:
                state = "⚫ DEAD LINE"

            idx_match = re.search(r"Stage [1-6]", raw_response)
            if idx_match:
                index = idx_match.group(0)

            update_readme_dashboard(ticker, state, index, filed_date)
            print(f"✅ Telemetry finalized for {ticker}: {state} | {index}")

        except Exception as e:
            print(f"❌ ZSP reasoning failure for {ticker}: {e}")


if __name__ == "__main__":
    run_zsp_audit()
    run_zsp_audit()
