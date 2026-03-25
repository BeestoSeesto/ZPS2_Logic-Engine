import os
import glob
import anthropic
from datetime import date

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

DISPATCH_PROMPT = "You are the Sovereign Dispatcher. Read the reports and detect CROSS-DOMAIN CONVERGENCE (SEC vs Legal)."

def run_sovereign_dispatcher():
    files = glob.glob("audits/*.md")
    if not files: return print("No reports to analyze.")

    combined = ""
    for f in files:
        with open(f, "r") as report: combined += f"\n--- {f} ---\n{report.read()}"

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        system=DISPATCH_PROMPT,
        messages=[{"role": "user", "content": combined}]
    )

    os.makedirs("dispatches", exist_ok=True)
    with open(f"dispatches/SOVEREIGN_DISPATCH_{date.today()}.md", "w") as f:
        f.write(message.content[0].text)
    print("Sovereign Dispatch Complete.")

if __name__ == "__main__":
    run_sovereign_dispatcher()
