import os
import anthropic
from datetime import date

# Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

TARGETS = ["Freeport-McMoRan", "Rio Tinto", "BHP Group"]

DOCKET_SYSTEM_PROMPT = """
You are the Legal Sovereign Auditor. You analyze court motions and legal filings.
Apply ZSP v2.1 to detect Behavioral Atrophy.

REQUIRED OUTPUT FORMAT:
1. DOMINANT CONDUCTOR STATE: [CONDUCTOR/INSULATOR/CORRODED/DEAD LINE]
2. LEGAL FRICTION SIGNAL: [Quote from motion + Mechanism]
3. RESISTANCE INDEX: Stage [1-6]
4. PREDICTIVE LITIGATION RISK: [14-day outlook]
"""

def run_docket_audit():
    print("⚖️ ZSP v2.1: Initiating Legal Docket Scan...")
    
    # For now, we simulate the 'Content' fetch. 
    # In the next iteration, we'll hook this to a CourtListener/PACER API.
    for company in TARGETS:
        print(f"🔍 Scanning Dockets for {company}...")
        
        # Simulated content for the build test
        mock_legal_text = f"Motion to Dismiss filed by {company} regarding supply chain nondisclosure. 'Defendant asserts that any alleged delays are subject to force majeure protections...'"

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            system=DOCKET_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": f"COMPANY: {company}\nMOTION TEXT:\n{mock_legal_text}"}]
        )

        raw_response = message.content[0].text
        os.makedirs("audits", exist_ok=True)
        today = date.today().strftime("%Y-%m-%d")
        
        with open(f"audits/LEGAL_{company.replace(' ', '_')}_{today}.md", "w") as f:
            f.write(raw_response)
        print(f"✅ Legal Audit saved for {company}")

if __name__ == "__main__":
    run_docket_audit()
