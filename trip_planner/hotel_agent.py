"""Hotel agent (A2A server, port 9001). Input: JSON {"destination": str, "nights": int}."""
import json

from trip_planner.a2a_server import serve

# Mock data: price per night in PKR
HOTELS = {
    "lahore": [("Walled City Guesthouse", 4000, "budget"), ("Hospitality Inn", 12000, "mid"), ("Pearl Continental Lahore", 35000, "luxury")],
    "islamabad": [("Margalla View Lodge", 5000, "budget"), ("Envoy Continental", 14000, "mid"), ("Serena Hotel Islamabad", 45000, "luxury")],
    "murree": [("Mall Road Inn", 4500, "budget"), ("Pine Hills Resort", 11000, "mid"), ("PC Bhurban", 40000, "luxury")],
}


def handle(text: str) -> str:
    try:
        req = json.loads(text)
        dest, nights = req["destination"].strip().lower(), int(req["nights"])
    except (ValueError, KeyError, TypeError):
        return 'Send JSON like {"destination": "Lahore", "nights": 3}'

    options = HOTELS.get(dest)
    if not options:
        return f"No hotels found for '{dest}'. Known: {', '.join(HOTELS)}"

    lines = [f"Hotels in {dest.title()} for {nights} night(s):"]
    for name, price, tier in options:
        lines.append(f"- {name} ({tier}): PKR {price:,}/night, total PKR {price * nights:,}")
    return "\n".join(lines)


if __name__ == "__main__":
    serve(
        handle,
        name="hotel-agent",
        description="Finds hotel options and total stay cost for a destination.",
        skill_id="find_hotels",
        skill_desc="List hotels with per-night and total price",
        port=9001,
    )
