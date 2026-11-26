"""A2A server helper: turns a plain `handle(text) -> str` function into an A2A server."""
import uvicorn
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from a2a.utils import new_agent_text_message


class SimpleExecutor(AgentExecutor):
    def __init__(self, handler):
        self.handler = handler

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        text = context.get_user_input()
        await event_queue.enqueue_event(new_agent_text_message(self.handler(text)))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError("cancel not supported")


def serve(handler, *, name: str, description: str, skill_id: str, skill_desc: str, port: int):
    card = AgentCard(
        name=name,
        description=description,
        url=f"http://localhost:{port}/",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=False),
        skills=[AgentSkill(id=skill_id, name=skill_id, description=skill_desc, tags=[skill_id])],
    )
    app = A2AStarletteApplication(
        agent_card=card,
        http_handler=DefaultRequestHandler(
            agent_executor=SimpleExecutor(handler), task_store=InMemoryTaskStore()
        ),
    )
    uvicorn.run(app.build(), host="127.0.0.1", port=port)
