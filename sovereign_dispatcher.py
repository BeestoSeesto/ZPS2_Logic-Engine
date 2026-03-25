def run_sovereign_dispatcher():
    # 1. Grab raw telemetry
    raw_legal = "FCX: 2:24-cv-00123 (AZ); RIO: Environmental Review (WA); BHP: Labor Update."
    
    # 2. BtAA SCORING LOGIC (8th Grade Level)
    # We count how many "bad" signals we found. More signals = worse grade.
    signal_count = len(raw_legal.split(';'))
    
    if signal_count <= 1:
        grade = "A"
        color = "text-green-500"
    elif signal_count == 2:
        grade = "B"
        color = "text-blue-400"
    elif signal_count == 3:
        grade = "C"
        color = "text-yellow-500"
    elif signal_count == 4:
        grade = "D"
        color = "text-orange-500"
    else:
        grade = "F"
        color = "text-red-500"

    # 3. Attempt AI Analysis (The Brain)
    try:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            system=f"Analyze ZSP v2.1 findings. The current BtAA Grade is {grade}.",
            messages=[{"role": "user", "content": f"Analyze: {raw_legal}"}]
        )
        final_dispatch = message.content[0].text
    except Exception as e:
        final_dispatch = f"AI ANALYSIS PENDING. RAW TELEMETRY: {raw_legal}"

    # 4. Add the Grade to the Dispatch Text
    # This puts the big letter right at the top of your analysis box
    graded_dispatch = f"<div class='mb-4'><span class='text-4xl font-bold {color}'>{grade}</span> <span class='text-slate-500 ml-2 uppercase text-xs font-mono'>Current BtAA Score</span></div>" + final_dispatch

    # 5. Format the Side Feed Rows
    legal_html_rows = ""
    for entry in raw_legal.split(';'):
        legal_html_rows += f"""
        <div class="legal-row">
            <p class="text-blue-400 font-bold font-mono uppercase text-[9px]">SIGNAL DETECTED</p>
            <p class="text-slate-300 mt-1">{entry.strip()}</p>
        </div>"""

    # 6. Push to Dashboard
    update_dashboard(graded_dispatch, legal_html_rows)
