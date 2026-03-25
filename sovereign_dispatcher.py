import os
import anthropic
import re

# ... (Previous API setup code remains the same)

def update_dashboard_html(legal_context):
    """Injects the latest legal telemetry into index.html"""
    try:
        with open("index.html", "r") as f:
            content = f.read()

        # Find the Litigation Feed section and update the rows
        # This replaces the placeholder text with the actual case data
        new_row_content = f"""
                        <div class="legal-row">
                            <p class="text-blue-400 font-bold font-mono text-xs uppercase">Latest Audit Signal</p>
                            <p class="text-slate-300 mt-1 text-[10px]">{legal_context[:150]}...</p>
                        </div>"""
        
        # Simple regex to find the section and replace it
        pattern = r'<div class="text-\[11px\] space-y-2">.*?</div>'
        updated_content = re.sub(pattern, f'<div class="text-[11px] space-y-2">{new_row_content}</div>', content, flags=re.DOTALL)

        with open("index.html", "w") as f:
            f.write(updated_content)
        print("🖥️ Dashboard HTML updated with latest litigation telemetry.")
    except Exception as e:
        print(f"⚠️ Dashboard update failed: {e}")

def run_sovereign_dispatcher():
    # ... (Your existing logic to read audits and call Claude)
    
    # MOCK DATA FOR THE INJECTOR (In case Claude is still cooling down)
    # Once Claude runs, we will use the actual 'message.content' here
    sample_legal_signal = "FCX: 22-cv-0145; New environmental motion filed in AZ District. RIO: Labor arbitration update in WA."
    
    update_dashboard_html(sample_legal_signal)

if __name__ == "__main__":
    run_sovereign_dispatcher()
