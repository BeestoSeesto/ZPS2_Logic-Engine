import os
import anthropic
from sec_api import QueryApi, ExtractorApi

# 1. Access the Vault
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
SEC_API_KEY = os.getenv("SEC_API_KEY")

# 2. Initialize Clients
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
sec_query = QueryApi(api_key=SEC_API_KEY)
sec_extractor = ExtractorApi(api_key=SEC_API_KEY)

# 3. Target Telemetry
TARGETS = ["FCX", "RIO", "BHP"]

def run_zsp_audit():
    print("📡 ZSP v2.1: Scanning SEC Telemetry...")
    
    query = {
        "query": f"ticker:({' OR '.join(TARGETS)}) AND formType:\"8-K\" AND filedAt:[now-1d TO now]",
        "from": "0", "size": "5", "sort": [{"filedAt": {"order": "desc"}}]
    }
    
    try:
        response = sec_query.get_filings(query)
    except Exception as e:
        print(f"❌ SEC Query Failed: {e}")
        return

    if not response.get('filings'):
        print("📭 No new behavioral friction detected.")
        return

    for filing in response['filings']:
        ticker = filing['ticker']
        url = filing['linkToFilingDetails']
        
        try:
            content = sec_extractor.get_section(url, "8-1", "text")
        except:
            content = "Filing metadata available, manual bridge required."

        print(f"🧠 Claude 4.6 Opus: Auditing {ticker}...")
        
        # 4. The Logic Call (2026 Stable Syntax)
        try:
            audit = client.messages.create(
                model="claude-3-5-sonnet-20241022", # Sonnet for first-run stability
                max_tokens=4000,
                messages=[{"role": "user", "content": f"Apply ZSP v2.1 to this {ticker} filing: {content}"}]
            )
            
            os.makedirs("audits", exist_ok=True)
            with open(f"audits/{ticker}_{filing['filedAt'][:10]}.md", "w") as f:
                f.write(audit.content[0].text)
            print(f"✅ Audit Saved for {ticker}")
        except Exception as e:
            print(f"❌ Claude Call Failed: {e}")

if __name__ == "__main__":
    run_zsp_audit()
