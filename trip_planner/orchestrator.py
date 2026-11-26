"""CLI orchestrator: asks both agents over A2A (in parallel) and prints a combined plan.

Usage: python -m trip_planner.orchestrator <origin> <destination> <nights>
Example: python -m trip_planner.orchestrator Karachi Lahore 3
"""
import asyncio
import sys

from trip_planner.a2a_client import HOTEL_URL, TRANSPORT_URL, ask_agent


async def main(origin: str, destination: str, nights: int) -> None:
    transport, hotels = await asyncio.gather(
        ask_agent(TRANSPORT_URL, {"origin": origin, "destination": destination}),
        ask_agent(HOTEL_URL, {"destination": destination, "nights": nights}),
    )
    print(f"=== Trip plan: {origin} -> {destination}, {nights} nights ===\n")
    print(transport, "\n")
    print(hotels)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    asyncio.run(main(sys.argv[1], sys.argv[2], int(sys.argv[3])))
