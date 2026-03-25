import os
import anthropic
import re

def update_dashboard(dispatch_text, legal_rows):
    try:
        with open("index.html", "r") as f:
            html = f.read()

        dispatch_regex = r".*?"
        new_dispatch = f"\n{dispatch_text}\n"
        html = re.sub(dispatch_regex, new_dispatch, html, flags=re.DOTALL)

        feed_regex = r".*?"
        new_feed = f"\n{legal_rows}\n"
        html = re.sub(feed_regex, new_feed, html, flags=re.DOTALL)

        with open("index.html", "w") as f:
            f.write(html)
        print("🖥️ Dashboard updated with Graded Analysis.")
    except Exception as e:
        print(f"⚠️ Injection failed: {e}")

def run_sovereign_dispatcher():
    # 1. Grab raw signals (Your Scouts find these)
    raw_legal = "FCX: 2:24-cv-00123 (AZ); RIO: Environmental Review (WA); BHP: Labor Update."
    
    # 2. BtAA GRADING LOGIC
    # Counts how many ';' we find. 3 items = Grade C.
    signal_count = len([s for s in raw_legal.split(';') if s.strip()])
    
    grades = {
        1: ("A", "text-green-500", "Optimal Flow"),
        2: ("B", "text-blue-400", "Stable"),
        3: ("C", "text-yellow-500", "Friction"),
        4: ("D", "text-orange-500", "Degrading"),
        5: ("F", "text-red-500", "Fractured")
    }
    
    # Default to F if things are really bad, or A if it's super quiet
    grade, color, label = grades.get(signal_count, ("F", "text-red-500", "Fractured") if signal_count > 5 else ("A", "text-green-500", "Optimal Flow"))

    # 3. Build the Grade HTML
    grade_html = f"""
    <div class='mb-6 flex items-center p-4 bg-slate-800/50 rounded border border-slate-700'>
        <div class='text-5xl font-bold {color} mr-4'>{grade}</div>
        <div>
            <div class='text-[10px] text-slate-500 uppercase tracking-widest font-bold'>Current BtAA Score</div>
            <div class='text-sm text-slate-300 font-semibold'>{label}</div>
        </div>
    </div>
    """

    # 4. Attempt AI Summary
    try:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            system=f"Analyze ZSP findings. Current Grade: {grade}.",
            messages=[{"role": "user", "content": f"Analyze: {raw_legal}"}]
        )
        ai_analysis = f"<p class='text-slate-300'>{message.content[0].text}</p>"
    except:
        ai_analysis = f"<p class='text-slate-400 italic text-xs'>AI analysis offline. Viewing raw BtAA telemetry: {raw_legal}</p>"

    # 5. Format the Feed
    legal_html_rows = "".join([f'<div class="legal-row"><p class="text-blue-400 font-mono text-[9px]">SIGNAL</p><p class="text-slate-300 mt-1">{s.strip()}</p></div>' for s in raw_legal.split(';') if s.strip()])

    # 6. Push
    update_dashboard(grade_html + ai_analysis, legal_html_rows)

if __name__ == "__main__":
    run_sovereign_dispatcher()
