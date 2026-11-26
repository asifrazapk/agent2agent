"""Web chatbot front-end. Each message triggers agent-to-agent (A2A) calls to the hotel
and transport agents. Message format: "<origin> to <destination> [N nights]".

Run: python -m trip_planner.chatbot   then open http://localhost:8000
"""
import asyncio
import re

import uvicorn
from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route

from trip_planner.a2a_client import HOTEL_URL, TRANSPORT_URL, ask_agent

PATTERN = re.compile(r"(?P<o>[a-zA-Z]+)\s+to\s+(?P<d>[a-zA-Z]+)(?:.*?(?P<n>\d+)\s*night)?", re.I)
HELP = ('Try: "Karachi to Lahore 3 nights", "Lahore to Islamabad 2 nights" '
        'or "Islamabad to Murree 4 nights".')


async def reply(message: str) -> str:
    m = PATTERN.search(message)
    if not m:
        return "Tell me where you want to go. " + HELP
    origin, dest, nights = m["o"], m["d"], int(m["n"] or 2)
    try:
        transport, hotels = await asyncio.gather(
            ask_agent(TRANSPORT_URL, {"origin": origin, "destination": dest}),
            ask_agent(HOTEL_URL, {"destination": dest, "nights": nights}),
        )
    except Exception as e:  # agents not running, etc.
        return f"Could not reach the agents ({type(e).__name__}). Are both agent servers running?"
    return f"{transport}\n\n{hotels}"


async def chat(request):
    body = await request.json()
    return JSONResponse({"reply": await reply(body.get("message", ""))})


async def index(request):
    return HTMLResponse(PAGE)


PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>Trip Planner Chat</title>
<style>
body{font-family:system-ui,sans-serif;max-width:640px;margin:2rem auto;padding:0 1rem}
#log{border:1px solid #ccc;border-radius:8px;height:420px;overflow-y:auto;padding:.75rem}
.m{margin:.4rem 0;padding:.5rem .75rem;border-radius:8px;white-space:pre-wrap;max-width:85%}
.u{background:#dbeafe;margin-left:auto}.b{background:#f1f5f9}
form{display:flex;gap:.5rem;margin-top:.75rem}input{flex:1;padding:.6rem}button{padding:.6rem 1rem}
</style></head><body><h2>Trip Planner Chat</h2><div id="log"></div>
<form id="f"><input id="t" placeholder="Karachi to Lahore 3 nights" autocomplete="off"><button>Send</button></form>
<script>
const log=document.getElementById('log');
function add(c,t){const d=document.createElement('div');d.className='m '+c;d.textContent=t;log.appendChild(d);log.scrollTop=log.scrollHeight}
add('b','Hi! Ask me like: Karachi to Lahore 3 nights');
async function send(v){add('u',v);
 const r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:v})});
 add('b',(await r.json()).reply)}
document.getElementById('f').onsubmit=e=>{e.preventDefault();
 const i=document.getElementById('t'),v=i.value.trim();if(!v)return;i.value='';send(v)};
const q=new URLSearchParams(location.search).get('q');if(q)send(q);  // /?q=... asks immediately
</script></body></html>"""

app = Starlette(routes=[Route("/", index), Route("/chat", chat, methods=["POST"])])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
