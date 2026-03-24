import os
import anthropic
from sec_api import QueryApi, ExtractorApi

# 1. Access the Vault (GitHub Secrets)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
SEC_API_KEY = os.getenv("SEC_API_KEY")

# 2. Initialize 2026-Spec Clients
# Note: The SDK automatically reads the environment variable
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
sec_query = QueryApi(api_key=SEC_API_KEY)
sec_extractor = ExtractorApi(api_key=SEC_API_KEY)

# 3. Target Telemetry (The "Copper Skin")
TARGETS = ["FCX", "RIO", "BHP"] 

def run_zsp_audit():
    print("📡 ZSP v2.1: Scanning SEC Telemetry...")
    
    # Query for 8-K filings from the last 24 hours
    query = {
        "query": f"ticker:({' OR '.join(TARGETS)}) AND formType:\"8-K\" AND filedAt:[now-1d TO now]",
        "from": "0", "size": "5", "sort": [{"filedAt": {"order": "desc"}}]
    }
    
    response = sec_query.get_filings(query)
    
    if not response['filings']:
        print("📭 No new behavioral friction detected in target tickers.")
        return

    for filing in response['filings']:
        ticker = filing['ticker']
        url = filing['linkToFilingDetails']
        
        # Extract Item 8.01 (Other Events) - the core of corporate "Behavioral Physics"
        try:
            content = sec_extractor.get_section(url, "8-1", "text")
        except Exception:
            content = "Filing metadata available, full text extraction requires manual bridge."

        print(f"🧠 Claude 4.6 Opus: Initiating Adaptive Thinking Audit for {ticker}...")
        
        # 4. The "Architect" Logic Call
        # We enable 'adaptive' thinking so Claude decides how deep the reasoning needs to go.
        # We use 'max' effort for Opus 4.6 to ensure no edge cases are missed.
        audit = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=20000, # Large buffer for deep reasoning + report
            thinking={
                "type": "adaptive" 
            },
            # 'max' effort is the 250k differentiator for Opus 4.6
