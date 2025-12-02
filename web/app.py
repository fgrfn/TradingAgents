"""
TradingAgents Web Application
FastAPI-basiertes Web-Interface für TradingAgents
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import json
from datetime import datetime
from pathlib import Path

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from cli.models import AnalystType

app = FastAPI(title="TradingAgents Web UI", version="1.0.0")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Statische Dateien
static_path = Path(__file__).parent / "static"
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


class AnalysisRequest(BaseModel):
    ticker: str
    date: str
    analysts: List[str]
    llm_provider: str
    provider_url: str
    deep_think_model: str
    quick_think_model: str
    research_depth: int


class AnalysisResponse(BaseModel):
    success: bool
    message: str
    result: Optional[dict] = None


# WebSocket Manager für Live-Updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    html_file = Path(__file__).parent / "templates" / "index.html"
    if html_file.exists():
        return FileResponse(html_file)
    return HTMLResponse(content="<h1>TradingAgents Web UI</h1><p>Templates nicht gefunden</p>")


@app.get("/api/providers")
async def get_providers():
    """Get available LLM providers"""
    return {
        "providers": [
            {"name": "OpenAI", "url": "https://api.openai.com/v1"},
            {"name": "Anthropic", "url": "https://api.anthropic.com/"},
            {"name": "Google", "url": "https://generativelanguage.googleapis.com/v1"},
            {"name": "Openrouter", "url": "https://openrouter.ai/api/v1"},
            {"name": "Ollama", "url": "http://localhost:11434/v1"},
        ]
    }


@app.get("/api/models/{provider}")
async def get_models(provider: str):
    """Get available models for a provider"""
    models = {
        "openai": {
            "quick": [
                {"name": "GPT-4o-mini", "value": "gpt-4o-mini"},
                {"name": "GPT-4.1-nano", "value": "gpt-4.1-nano"},
                {"name": "GPT-4.1-mini", "value": "gpt-4.1-mini"},
                {"name": "GPT-4o", "value": "gpt-4o"},
                {"name": "GPT-5-mini", "value": "gpt-5-mini"},
                {"name": "GPT-5", "value": "gpt-5"},
            ],
            "deep": [
                {"name": "GPT-4.1-nano", "value": "gpt-4.1-nano"},
                {"name": "GPT-4.1-mini", "value": "gpt-4.1-mini"},
                {"name": "GPT-4o", "value": "gpt-4o"},
                {"name": "GPT-5-mini", "value": "gpt-5-mini"},
                {"name": "GPT-5", "value": "gpt-5"},
                {"name": "GPT-5-turbo", "value": "gpt-5-turbo"},
                {"name": "o4-mini", "value": "o4-mini"},
                {"name": "o3-mini", "value": "o3-mini"},
                {"name": "o3", "value": "o3"},
                {"name": "o1", "value": "o1"},
            ],
        },
        "anthropic": {
            "quick": [
                {"name": "Claude Haiku 3.5", "value": "claude-3-5-haiku-latest"},
                {"name": "Claude Sonnet 3.5", "value": "claude-3-5-sonnet-latest"},
                {"name": "Claude Sonnet 3.7", "value": "claude-3-7-sonnet-latest"},
                {"name": "Claude Sonnet 4", "value": "claude-sonnet-4-0"},
            ],
            "deep": [
                {"name": "Claude Haiku 3.5", "value": "claude-3-5-haiku-latest"},
                {"name": "Claude Sonnet 3.5", "value": "claude-3-5-sonnet-latest"},
                {"name": "Claude Sonnet 3.7", "value": "claude-3-7-sonnet-latest"},
                {"name": "Claude Sonnet 4", "value": "claude-sonnet-4-0"},
                {"name": "Claude Opus 4", "value": "claude-opus-4-0"},
            ],
        },
        "google": {
            "quick": [
                {"name": "Gemini 2.0 Flash-Lite", "value": "gemini-2.0-flash-lite"},
                {"name": "Gemini 2.0 Flash", "value": "gemini-2.0-flash"},
                {"name": "Gemini 2.5 Flash", "value": "gemini-2.5-flash-preview-05-20"},
            ],
            "deep": [
                {"name": "Gemini 2.0 Flash-Lite", "value": "gemini-2.0-flash-lite"},
                {"name": "Gemini 2.0 Flash", "value": "gemini-2.0-flash"},
                {"name": "Gemini 2.5 Flash", "value": "gemini-2.5-flash-preview-05-20"},
                {"name": "Gemini 2.5 Pro", "value": "gemini-2.5-pro-preview-06-05"},
            ],
        },
    }
    
    provider_lower = provider.lower()
    return models.get(provider_lower, {"quick": [], "deep": []})


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_stock(request: AnalysisRequest):
    """Start stock analysis"""
    try:
        # Konfiguration erstellen
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = request.llm_provider.lower()
        config["backend_url"] = request.provider_url
        config["deep_think_llm"] = request.deep_think_model
        config["quick_think_llm"] = request.quick_think_model
        config["max_debate_rounds"] = request.research_depth

        # Trading Graph initialisieren
        ta = TradingAgentsGraph(debug=True, config=config)

        # Analyse durchführen
        _, decision = ta.propagate(request.ticker, request.date)

        return AnalysisResponse(
            success=True,
            message="Analyse erfolgreich abgeschlossen",
            result={"decision": str(decision)}
        )

    except Exception as e:
        return AnalysisResponse(
            success=False,
            message=f"Fehler bei der Analyse: {str(e)}"
        )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket für Live-Updates"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Hier können Live-Updates während der Analyse gesendet werden
            await manager.send_message(
                {"type": "status", "message": f"Empfangen: {data}"}, 
                websocket
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
