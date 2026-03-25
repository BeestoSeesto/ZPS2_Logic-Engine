import os
import re
import anthropic
from datetime import datetime, date
from sec_api import QueryApi, ExtractorApi

# 1. Configuration & API Access
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
SEC_API_KEY = os.getenv("SEC_API_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
sec_query = QueryApi(api_key=SEC_API_KEY)
sec_extractor = ExtractorApi(api_key=SEC_API_KEY)

TARGETS = ["FCX", "RIO", "BHP"]

ZSP_SYSTEM_PROMPT = """
You are the Copper Sovereign Auditor, operating under Zavala Sovereignty Protocol (ZSP) v2.1.
Perform Behavioral Telemetry on the provided text.

REQUIRED OUTPUT FORMAT:
1. DOMINANT CONDUCTOR STATE: [CONDUCTOR/INSULATOR/CORRODED/DEAD LINE]
2. FRICTION SIGNAL: [Quote + Mechanism]
3. RESISTANCE INDEX: Stage [1-6] | Conductivity Score [0-100]
4. DOWNSTREAM SIGNAL — 14 DAY: [Prediction]
5. AUTONOMY RECOMMENDATION: [PASS/MONITOR/RE-ROUTE/OPEN CIRCUIT]
"""

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
            content = "Summary: Operational shift detected. Full context in SEC archives."

        print(f"🧠 ZSP Auditor: Running telemetry on {ticker}...")

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            system=ZSP_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": f"TICKER: {ticker}\nTEXT:\n{content}"}]
        )

        raw_response = message.content[0].text
        os.makedirs("audits", exist_ok=True)
        with open(f"audits/{ticker}_{filed_date}.md", "w") as f:
            f.write(raw_response)
        print(f"✅ Audit saved for {ticker}")

if __name__ == "__main__":
    run_zsp_audit()
