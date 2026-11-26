"""Transport agent (A2A server, port 9002). Input: JSON {"origin": str, "destination": str}."""
import json

from trip_planner.a2a_server import serve

# Mock data: (mode, one-way price in PKR, hours)
ROUTES = {
    ("karachi", "lahore"): [("Train", 5500, 18), ("Bus", 6000, 17), ("Flight", 22000, 1.8)],
    ("lahore", "islamabad"): [("Train", 1800, 5.5), ("Bus", 2200, 4.5), ("Flight", 14000, 1.0)],
    ("islamabad", "murree"): [("Bus", 600, 1.5), ("Cab", 4500, 1.2)],
}


def handle(text: str) -> str:
    try:
        req = json.loads(text)
        origin, dest = req["origin"].strip().lower(), req["destination"].strip().lower()
    except (ValueError, KeyError, TypeError):
        return 'Send JSON like {"origin": "Karachi", "destination": "Lahore"}'

    options = ROUTES.get((origin, dest))
    if not options:
        known = ", ".join(f"{o.title()}->{d.title()}" for o, d in ROUTES)
        return f"No route {origin.title()}->{dest.title()}. Known: {known}"

    lines = [f"Transport {origin.title()} -> {dest.title()} (round trip = 2x):"]
    for mode, price, hours in options:
        lines.append(f"- {mode}: PKR {price:,} one-way, PKR {price * 2:,} round trip, ~{hours}h")
    return "\n".join(lines)


if __name__ == "__main__":
    serve(
        handle,
        name="transport-agent",
        description="Finds travel modes, duration and cost between two cities.",
        skill_id="find_transport",
        skill_desc="List transport options with price and duration",
        port=9002,
    )
