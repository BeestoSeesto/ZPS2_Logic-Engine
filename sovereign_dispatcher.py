import os
import re
import glob
import anthropic
from datetime import date

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

DISPATCHER_PROMPT = """
You are the Sovereign Dispatcher of ZSP v2.1. 
Analyze the pattern of signals ACROSS the provided reports to detect cross-domain convergence.
Constraint: Read the pattern across reports. The convergence IS the signal.
"""

def load_reports():
    today = date.today().strftime("%Y-%m-%d")
    reports = {}
    files = glob.glob(f"audits/*_{today}.md")
    
    if not files:
        files = sorted(glob.glob("audits/*.md"), key=os.path.getmtime, reverse=True)[:5]
    
    for filepath in files:
        with open(filepath, "r") as f:
            reports[os.path.basename(filepath)] = f.read()
    return reports

def run_sovereign_dispatcher():
    print("🛰️ SOVEREIGN DISPATCHER: Initiating analysis...")
    reports = load_reports()
    
    if not reports:
        print("📭 No reports found.")
        return

    combined_input = f"Analyze these {len(reports)} reports for convergence:\n\n"
    for name, content in reports.items():
        combined_input += f"--- REPORT: {name} ---\n{content}\n\n"

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        system=DISPATCHER_PROMPT,
        messages=[{"role": "user", "content": combined_input}]
    )

    os.makedirs("dispatches", exist_ok=True)
    today = date.today().strftime("%Y-%m-%d")
    with open(f"dispatches/SOVEREIGN_DISPATCH_{today}.md", "w") as f:
        f.write(message.content[0].text)
    
    print(f"✅ Dispatch complete: SOVEREIGN_DISPATCH_{today}.md")

if __name__ == "__main__":
    run_sovereign_dispatcher()
