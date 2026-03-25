import os
import anthropic
from datetime import date

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
TARGETS = ["Freeport-McMoRan", "Rio_Tinto", "BHP_Group"]

DOCKET_PROMPT = "You are the Legal Sovereign Auditor. Apply ZSP v2.1 to this court filing text. Output: State, Legal Friction, Resistance Index, 14-day Risk."

def run_docket_audit():
    for company in TARGETS:
        # Mocking the fetch for the build test - Real API integration next
        mock_text = f"Motion to Dismiss for {company}: Force Majeure cited regarding supply constraints."
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            system=DOCKET_PROMPT,
            messages=[{"role": "user", "content": f"COMPANY: {company}\nTEXT: {mock_text}"}]
        )
        
        os.makedirs("audits", exist_ok=True)
        with open(f"audits/LEGAL_{company}_{date.today()}.md", "w") as f:
            f.write(message.content[0].text)
        print(f"Legal Audit Saved: {company}")

if __name__ == "__main__":
    run_docket_audit()
