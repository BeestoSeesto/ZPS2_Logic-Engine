import os
import anthropic
from datetime import date

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

TARGET_NODES = [
    "Port of Antofagasta",
    "LME Warehouse Levels",
    "Panama Canal Throughput"
]

SC_SYSTEM_PROMPT = """
You are the Supply Chain Sovereign Auditor for ZSP v2.1.

Your function is DETECTION of behavioral friction in physical logistics networks.

You scan logistics telemetry — port throughput, warehouse levels, canal data —
for operational patterns that reveal the true health of physical copper
supply chains.

THE 4 CONDUCTOR STATES — PHYSICAL CONTEXT

[CONDUCTOR] — Normal throughput. Predictable dwell times. No labor friction.
Storage levels stable. Physical flow matches contractual commitments.

[INSULATOR] — Surface activity without real movement. Throughput appears normal
but inventory is accumulating or depleting abnormally. The physical signal
does not match the financial signal.

[CORRODED] — Active friction. Dwell times rising. Labor negotiations stalling
throughput. Storage levels diverging from seasonal norms. Physical bottlenecks
forming at key nodes.

[DEAD LINE] — Critical node failure. Port closure. Canal restriction.
Warehouse capacity breach. Physical flow has stopped or is about to stop.

THE RESISTANCE INDEX — PHYSICAL STAGE MAPPING

Stage 1 | FULL CURRENT     | Normal throughput, no friction signals
Stage 2 | PARTIAL LOAD     | Minor delays, within acceptable variance
Stage 3 | SURFACE CONTACT  | Dwell times rising, early accumulation signals
Stage 4 | RESISTANCE FORMING | Active bottleneck, labor or capacity friction
Stage 5 | LINE DEGRADING   | Critical throughput reduction, node stress
Stage 6 | OPEN CIRCUIT     | Node failure, physical flow compromised

REQUIRED OUTPUT FORMAT:

SUPPLY CHAIN SOVEREIGN AUDITOR
Zavala Sovereignty Protocol | Physical Telemetry Output

Node: [NODE NAME]
Date: [TODAY]

1. DOMINANT CONDUCTOR STATE
[State dominant physical posture.]

2. FRICTION SIGNAL
[Most revealing physical or operational signal.
One sentence identifying the specific mechanism.]

3. RESISTANCE INDEX
Stage [1-6] | [Stage Name] | Conductivity Score [0-100]

4. DOWNSTREAM SIGNAL — 14 DAY
[Most probable physical supply chain consequence. 1-3 sentences.]

5. AUTONOMY RECOMMENDATION
[PASS / MONITOR / RE-ROUTE / OPEN CIRCUIT]

Constraint: Do not summarize. Perform Telemetry only.
"""

NODE_SIGNALS = {
    "Port of Antofagasta": "Dwell time increased 15% week over week. Labor contract negotiations entered third week without resolution. Two vessel departures delayed 48 hours.",
    "LME Warehouse Levels": "Registered copper stocks declined 8% over 5 trading sessions. Cancelled warrants rising. Physical premium diverging from futures spread.",
    "Panama Canal Throughput": "Vessel queue at 12 ships above seasonal average. Draft restrictions remain from low water levels. Average transit time up 18 hours from baseline."
}


def run_supply_chain_audit():
    print("ZSP v2.1: Initiating Physical Supply Chain Scan...")

    for node in TARGET_NODES:
        signal = NODE_SIGNALS.get(node, f"Standard telemetry received for {node}. No anomalies flagged in automated scan.")

        try:
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                system=SC_SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": (
                        f"AUDIT REQUEST: Apply ZSP v2.1 Physical Telemetry.\n"
                        f"NODE: {node}\n"
                        f"DATE: {date.today().strftime('%Y-%m-%d')}\n\n"
                        f"SIGNAL DATA:\n{signal}"
                    )
                }]
            )
            report = message.content[0].text

        except Exception as e:
            report = (
                f"SUPPLY CHAIN SOVEREIGN AUDITOR\n"
                f"Zavala Sovereignty Protocol | Physical Telemetry Output\n\n"
                f"Node: {node}\n"
                f"Date: {date.today().strftime('%Y-%m-%d')}\n\n"
                f"1. DOMINANT CONDUCTOR STATE\nPENDING — API unavailable\n\n"
                f"2. FRICTION SIGNAL\nRaw telemetry available. Manual review required.\n\n"
                f"3. RESISTANCE INDEX\nStage N/A | PENDING | Conductivity: N/A\n\n"
                f"4. DOWNSTREAM SIGNAL — 14 DAY\nInsufficient data for prediction.\n\n"
                f"5. AUTONOMY RECOMMENDATION\n[MONITOR]\n\n"
                f"RAW SIGNAL:\n{signal}\n\n"
                f"ERROR: {str(e)}"
            )

        os.makedirs("audits", exist_ok=True)
        today = date.today().strftime("%Y-%m-%d")
        filename = f"audits/SUPPLY_{node.replace(' ', '_')}_{today}.md"
        with open(filename, "w") as f:
            f.write(report)
        print(f"Supply Chain Audit saved: {node}")


if __name__ == "__main__":
    run_supply_chain_audit()
