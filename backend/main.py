from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import chat, history
from backend.db.database import Base, engine
from backend.graph.graph import get_compiled_graph, close_graph

@asynccontextmanager
async def lifespan(app: FastAPI):
                                                                              
    Base.metadata.create_all(bind=engine)
                                                                    
    await get_compiled_graph()
    yield
    await close_graph()

app = FastAPI(
    title="Medical Chatbot API",
    description="Multi-agent medical information assistant (LangGraph + MCP + Groq)",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],                         
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(history.router)

@app.get("/health")
def health():
    return {"status": "ok"}
