import os
import anthropic
from datetime import date
from sec_api import QueryApi, ExtractorApi

# API Keys
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
sec_query = QueryApi(api_key=os.getenv("SEC_API_KEY"))
sec_extractor = ExtractorApi(api_key=os.getenv("SEC_API_KEY"))

TARGETS = ["FCX", "RIO", "BHP"]

ZSP_PROMPT = "You are the Copper Sovereign Auditor. Apply ZSP v2.1 to this SEC text. Output: State, Friction Signal, Resistance Index, 14-day Window."

def run_zsp_audit():
    query = {"query": f"ticker:({' OR '.join(TARGETS)}) AND formType:\"8-K\" AND filedAt:[now-1d TO now]", "size": "5"}
    response = sec_query.get_filings(query)
    
    if not response.get('filings'): return print("No new SEC filings.")

    for filing in response['filings']:
        ticker = filing['ticker']
        content = sec_extractor.get_section(filing['linkToFilingDetails'], "8-1", "text")
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            system=ZSP_PROMPT,
            messages=[{"role": "user", "content": f"TICKER: {ticker}\nTEXT: {content}"}]
        )
        
        os.makedirs("audits", exist_ok=True)
        with open(f"audits/SEC_{ticker}_{date.today()}.md", "w") as f:
            f.write(message.content[0].text)
        print(f"SEC Audit Saved: {ticker}")

if __name__ == "__main__":
    run_zsp_audit()
