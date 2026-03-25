import os
import requests
import anthropic
from datetime import date, timedelta

# Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CL_API_KEY = os.getenv("COURTLISTENER_API_KEY")
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# The Big Three Copper Targets
TARGETS = ["Freeport-McMoRan", "Rio Tinto", "BHP Group"]

DOCKET_SYSTEM_PROMPT = """
You are the Legal Sovereign Auditor for ZSP v2.1.
Analyze the provided Federal Docket search results from CourtListener v4.
Identify "Insulator" (stalling) or "Corroded" (failure) behavior in litigation.
"""

def fetch_real_dockets(company):
    print(f"⚖️ ZSP v4.3: Querying CourtListener for {company}...")
    
    # Using the search endpoint as suggested in the v4 docs
    # Filtering for dockets ('type=d')
    url = f"https://www.courtlistener.com/api/rest/v4/search/?q={company}&type=d"
    
    # Requirement: "Authorization: Token <your_token>"
    headers = {
        "Authorization": f"Token {CL_API_KEY}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return f"API Error: {response.status_code}"
            
        data = response.json()
        results = data.get('results', [])
        
        if not results:
            return f"No recent federal filings detected for {company}."
        
        # Pull top 3 most recent cases
        context = ""
        for case in results[:3]:
            context += f"CASE: {case.get('case_name')}\nCOURT: {case.get('court')}\nDATE: {case.get('date_filed')}\n---\n"
        return context
        
    except Exception as e:
        return f"Connection Failed: {str(e)}"

def run_docket_audit():
    for company in TARGETS:
        legal_telemetry = fetch_real_dockets(company)
        
        # Analyze with Claude
        # (This will resume working once your credits reset)
        try:
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                system=DOCKET_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": f"DATA SOURCE: CourtListener v4\nCOMPANY: {company}\nTEXT:\n{legal_telemetry}"}]
            )
            report = message.content[0].text
        except:
            report = f"STATE: PENDING\nREASON: API Credit Reset Required.\nRAW DATA: {legal_telemetry}"

        os.makedirs("audits", exist_ok=True)
        today = date.today().strftime("%Y-%m-%d")
        with open(f"audits/LEGAL_{company.replace(' ', '_')}_{today}.md", "w") as f:
            f.write(report)
        print(f"✅ Legal Audit saved for {company}")

if __name__ == "__main__":
    run_docket_audit()
