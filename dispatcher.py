import os
import anthropic
from sec_api import QueryApi, ExtractorApi

# 1. Access the Vault (GitHub Secrets)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
SEC_API_KEY = os.getenv("SEC_API_KEY")

# 2. Initialize Clients
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
sec_query = QueryApi(api_key=SEC_API_KEY)
sec_extractor = ExtractorApi(api_key=SEC_API_KEY)

# 3. Target Telemetry (Copper Skin)
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
        print("📭 No new behavioral friction detected in target tickers today.")
        return

    for filing in response['filings']:
        ticker = filing['ticker']
        url = filing['linkToFilingDetails']
        filed_date = filing['filedAt'][:10]
        
        try:
            content = sec_extractor.get_section(url, "8-1", "text")
            if not content or len(content) < 100:
                content = "Filing metadata suggests administrative shift. Context restricted."
        except:
            content = "Filing body context unavailable for automated extraction."

        print(f"🧠 Claude Audit: Analyzing {ticker} under ZSP v2.1...")
        
        try:
            # Protocol Execution
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022", 
                max_tokens=4000,
                messages=[{
                    "role": "user", 
                    "content": (
                        f"Apply Zavala Sovereignty Protocol (ZSP) v2.1 to this {ticker} filing. \n\n"
                        "ANALYSIS:\n"
                        "1. Map the 'Bridge' to physical supply chain friction.\n"
                        "2. State: CONDUCTOR, INSULATOR, or CORRODED.\n"
                        "3. Resistance Index (Stage 1-4).\n\n"
                        f"DATA SOURCE:\n{content}"
                    )
                }]
            )
            
            # Save the Ledger
            os.makedirs("audits", exist_ok=True)
            filename = f"audits/{ticker}_{filed_date}.md"
            with open(filename, "w") as f:
                f.write(message.content[0].text)
            print(f"✅ Audit Saved: {filename}")
            
        except Exception as e:
            print(f"❌ Claude Call Failed for {ticker}: {e}")

if __name__ == "__main__":
    run_zsp_audit()
