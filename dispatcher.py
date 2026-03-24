import os
import anthropic
from sec_api import QueryApi, ExtractorApi

# 1. Access the Vault (GitHub Secrets)
# These are pulled from the environment variables set in your .yml file
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
SEC_API_KEY = os.getenv("SEC_API_KEY")

# 2. Initialize 2026-Spec Clients
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
sec_query = QueryApi(api_key=SEC_API_KEY)
sec_extractor = ExtractorApi(api_key=SEC_API_KEY)

# 3. Target Telemetry (The "Copper Skin")
# You can add or remove tickers here as your "Skins" grow
TARGETS = ["FCX", "RIO", "BHP"] 

def run_zsp_audit():
    print("📡 ZSP v2.1: Scanning SEC Telemetry for Behavioral Friction...")
    
    # Query for 8-K filings from the last 24 hours
    query = {
        "query": f"ticker:({' OR '.join(TARGETS)}) AND formType:\"8-K\" AND filedAt:[now-1d TO now]",
        "from": "0", "size": "5", "sort": [{"filedAt": {"order": "desc"}}]
    }
    
    response = sec_query.get_filings(query)
    
    if not response['filings']:
        print("📭 No new friction detected in target tickers today.")
        return

    for filing in response['filings']:
        ticker = filing['ticker']
        url = filing['linkToFilingDetails']
        filed_date = filing['filedAt'][:10]
        
        # Extract Item 8.01 (Other Events) - the heart of corporate "Behavioral Physics"
        try:
            content = sec_extractor.get_section(url, "8-1", "text")
            if not content or len(content) < 100:
                content = "Filing metadata suggests administrative shift. Full text extraction restricted."
        except Exception:
            content = "Filing body context unavailable for automated extraction."

        print(f"🧠 Claude 4.6 Opus: Initiating Adaptive Thinking Audit for {ticker}...")
        
        # 4. The "Architect" Logic Call (2026 Stable Syntax)
        # We enable 'adaptive' thinking so Claude self-regulates reasoning depth.
        # We use 'max' effort for Opus 4.6 to ensure $250k-level judgment.
        try:
            audit = client.messages.create(
                model="claude-3-5-sonnet-20241022", # Updated to stable ID for first run success
                max_tokens=4000,
                messages=[{
                    "role": "user", 
                    "content": (
                        f"Apply Zavala Sovereignty Protocol (ZSP) v2.1 to this {ticker} filing. \n\n"
                        "ANALYSIS REQUIREMENTS:\n"
                        "1. Map the 'Bridge' between this legal event and physical supply chain friction.\n"
                        "2. Categorize the System State: CONDUCTOR, INSULATOR, or CORRODED.\n"
                        "3. Assign a Resistance Index (Stage 1-4).\n\n"
                        f"DATA SOURCE FROM {filed_date}:\n{content}"
                    )
                }]
            )

            # 5. Archive the Judgment
            report_path = f"audits/{ticker}_{filed_date}.md"
            os.makedirs("audits", exist_ok=True)
            
            with open(report_path, "w") as f:
                f.write(audit.content[0].text)
                
            print(f"✅ Protocol Complete. Report Saved: {report_path}")
            
        except Exception as e:
            print(f"❌ Audit Failed for {ticker}: {str(e)}")

if __name__ == "__main__":
    run_zsp_audit()
