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

def update_readme_dashboard(ticker, state, index, date):
    """Programmatically updates the README.md table based on ticker comments."""
    try:
        with open("README.md", "r") as f:
            content = f.read()

        t_low = ticker.lower()
        # Regex patterns to find content between the hidden comment tags
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
        
        # Section 8-1 is typically the 'Other Events' section in an 8-K
        try:
            content = sec_extractor.get_section(url, "8-1", "text")
        except:
            content = "Summary: Operational shift detected. Full context available in SEC archives."

        print(f"🧠 Claude 4.6 Audit: Processing {ticker}...")
        
        try:
            # The 'Thinking' call for 2026 Sovereign Auditing
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022", # Stable 2026 endpoint
                max_tokens=4000,
                messages=[{
                    "role": "user", 
                    "content": (
                        f"AUDIT REQUEST: Apply Zavala Sovereignty Protocol (ZSP) v2.1 to {ticker}.\n"
                        f"FILING DATE: {filed_date}\n"
                        f"TEXT: {content}\n\n"
                        "REQUIRED OUTPUT FORMAT:\n"
                        "STATE: [CONDUCTOR/INSULATOR/CORRODED]\n"
                        "INDEX: [Stage 1-4]\n"
                        "BRIEF: [2-sentence ZSP mapping]"
                    )
                }]
            )
            
            raw_response = message.content[0].text
            
            # Save the raw audit to /audits folder
            os.makedirs("audits", exist_ok=True)
            with open(f"audits/{ticker}_{filed_date}.md", "w") as f:
                f.write(raw_response)

            # Extract data for the README Dashboard
            # Simple parsing for the automated table update
            state = "UNKNOWN"
            index = "N/A"
            if "CONDUCTOR" in raw_response: state = "🟢 CONDUCTOR"
            elif "INSULATOR" in raw_response: state = "🟡 INSULATOR"
            elif "CORRODED" in raw_response: state = "🔴 CORRODED"
            
            # Basic index extraction
            idx_match = re.search(r"Stage [1-4]", raw_response)
            if idx_match: index = idx_match.group(0)

            update_readme_dashboard(ticker, state, index, filed_date)
            print(f"✅ Audit finalized for {ticker}")
            
        except Exception as e:
            print(f"❌ Claude reasoning failure: {e}")

if __name__ == "__main__":
    run_zsp_audit()
