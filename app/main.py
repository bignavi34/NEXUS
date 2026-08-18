from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.agents.core import build_agent

from fastapi.middleware.cors import CORSMiddleware
agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):

    global agent

    print("\n==============================")
    print("Starting NEXUS")
    print("==============================")

    try:
        print("Building agent...")

        agent = await build_agent()

        print("AGENT OBJECT:", agent)
        print("AGENT TYPE:", type(agent))
        print("AGENT ID:", id(agent))

        if agent is None:
            print("ERROR: build_agent() returned None")
        else:
            print("NEXUS agent ready.")

    except Exception as e:

        print("\n==============================")
        print("NEXUS STARTUP ERROR")
        print("==============================")

        import traceback
        traceback.print_exc()

        agent = None

    yield

    print("NEXUS shutting down...")


app = FastAPI(
    title="NEXUS",
    description="Agentic Personal Operating System",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@app.get("/")
async def root():

    print("ROOT AGENT:", agent)
    print("ROOT AGENT ID:", id(agent) if agent else None)

    return {
        "name": "NEXUS",
        "description": "Agentic Personal Operating System",
        "status": "running",
        "version": "0.1.0",
        "agent_ready": agent is not None,
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    print("\n==============================")
    print("CHAT REQUEST")
    print("AGENT:", agent)
    print("AGENT ID:", id(agent) if agent else None)
    print("==============================")

    if agent is None:
        raise HTTPException(
            status_code=503,
            detail="NEXUS agent is not ready.",
        )

    try:

        result = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": request.message,
                    }
                ]
            }
        )

        messages = result.get("messages", [])

        if not messages:
            raise RuntimeError("Agent returned no messages.")

        return {
            "response": messages[-1].content
        }

    except Exception as e:

        print("\n===== CHAT ERROR =====")

        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
