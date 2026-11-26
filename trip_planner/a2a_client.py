"""A2A client helper: discover an agent via its card and send it one message."""
import json
from uuid import uuid4

import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import MessageSendParams, SendMessageRequest

HOTEL_URL = "http://localhost:9001"
TRANSPORT_URL = "http://localhost:9002"


async def ask_agent(base_url: str, payload: dict) -> str:
    """Send `payload` (as JSON text) to the agent at `base_url` and return its text reply."""
    async with httpx.AsyncClient(timeout=30) as http:
        card = await A2ACardResolver(httpx_client=http, base_url=base_url).get_agent_card()
        client = A2AClient(httpx_client=http, agent_card=card)
        request = SendMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(
                message={
                    "role": "user",
                    "parts": [{"kind": "text", "text": json.dumps(payload)}],
                    "messageId": uuid4().hex,
                }
            ),
        )
        response = await client.send_message(request)
        result = response.root.result  # a Message for these simple agents
        return "\n".join(p.root.text for p in result.parts if p.root.kind == "text")
