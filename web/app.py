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
import sys
import requests
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import tradingagents
sys.path.insert(0, str(Path(__file__).parent.parent))

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
    openai_api_key: str
    alpha_vantage_api_key: str
    discord_webhook: Optional[str] = None
    discord_notify: bool = True


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


def send_discord_notification(webhook_url: str, ticker: str, decision: str, date: str, analysts: List[str]):
    """Send analysis results to Discord via webhook"""
    try:
        # Parse decision
        decision_text = str(decision).upper()
        if "KAUFEN" in decision_text or "BUY" in decision_text:
            color = 0x10b981  # Green
            emoji = "📈"
            action = "KAUFEN"
        elif "VERKAUFEN" in decision_text or "SELL" in decision_text:
            color = 0xef4444  # Red
            emoji = "📉"
            action = "VERKAUFEN"
        else:
            color = 0xf59e0b  # Yellow
            emoji = "⏸️"
            action = "HALTEN"

        # Create embed
        embed = {
            "title": f"{emoji} TradingAgents Analyse: {ticker}",
            "description": f"**Entscheidung: {action}**",
            "color": color,
            "fields": [
                {
                    "name": "📅 Analysedatum",
                    "value": date,
                    "inline": True
                },
                {
                    "name": "👥 Analysten",
                    "value": ", ".join(analysts),
                    "inline": True
                },
                {
                    "name": "🤖 Empfehlung",
                    "value": f"```{decision}```",
                    "inline": False
                }
            ],
            "footer": {
                "text": "TradingAgents Multi-Agent System"
            },
            "timestamp": datetime.utcnow().isoformat()
        }

        payload = {
            "embeds": [embed],
            "username": "TradingAgents Bot"
        }

        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Discord notification error: {e}")
        return False


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page with aggressive no-cache headers"""
    html_file = Path(__file__).parent / "templates" / "index.html"
    if html_file.exists():
        # Generate unique ETag based on file modification time and current timestamp
        mtime = html_file.stat().st_mtime
        etag = f'"{mtime}-{datetime.now().timestamp()}"'
        
        return FileResponse(
            html_file,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0",
                "ETag": etag,
                "Last-Modified": datetime.utcfromtimestamp(mtime).strftime('%a, %d %b %Y %H:%M:%S GMT')
            }
        )
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


import threading
import uuid
import sqlite3
from pathlib import Path as FilePath

# Store for analysis results (temporary, in-memory)
analysis_results = {}

# Database setup for persistent history
DB_PATH = FilePath(__file__).parent.parent / "analysis_history.db"

def init_database():
    """Initialize SQLite database for analysis history"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id TEXT PRIMARY KEY,
            ticker TEXT NOT NULL,
            date TEXT NOT NULL,
            decision TEXT NOT NULL,
            analysts TEXT NOT NULL,
            llm_provider TEXT,
            llm_model TEXT,
            research_depth INTEGER,
            duration REAL,
            full_analysis TEXT,
            created_at TEXT NOT NULL,
            UNIQUE(id)
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ Datenbank initialisiert: {DB_PATH}")

# Initialize database on startup
init_database()

def format_analysis_result(result_dict: dict) -> str:
    """Format analysis result dictionary into readable text"""
    if not result_dict:
        return "Keine Analysedaten verfügbar."
    
    sections = []
    
    # Market Report
    if "market_report" in result_dict and result_dict["market_report"]:
        sections.append("## 📊 Technische Marktanalyse\n" + result_dict["market_report"])
    
    # Fundamentals Report
    if "fundamentals_report" in result_dict and result_dict["fundamentals_report"]:
        sections.append("## 📈 Fundamentalanalyse\n" + result_dict["fundamentals_report"])
    
    # News Report
    if "news_report" in result_dict and result_dict["news_report"]:
        sections.append("## 📰 Nachrichten & Makroökonomie\n" + result_dict["news_report"])
    
    # Sentiment Report
    if "sentiment_report" in result_dict and result_dict["sentiment_report"]:
        sections.append("## 💬 Marktstimmung & Social Media\n" + result_dict["sentiment_report"])
    
    # Investment Debate
    if "investment_debate_state" in result_dict and result_dict["investment_debate_state"]:
        debate_state = result_dict["investment_debate_state"]
        
        # Bull/Bear History
        if "history" in debate_state and debate_state["history"]:
            sections.append("## 🎯 Investitionsdebatte (Bull vs. Bear)\n" + debate_state["history"])
        
        # Judge Decision
        if "judge_decision" in debate_state and debate_state["judge_decision"]:
            sections.append("## ⚖️ Urteil des Richters\n" + debate_state["judge_decision"])
    
    # Investment Plan
    if "investment_plan" in result_dict and result_dict["investment_plan"]:
        sections.append("## 📋 Investitionsplan\n" + result_dict["investment_plan"])
    
    # Final Trade Decision (from trader)
    if "trader_investment_plan" in result_dict and result_dict["trader_investment_plan"]:
        sections.append("## 🎯 Finale Handelsentscheidung des Traders\n" + result_dict["trader_investment_plan"])
    
    return "\n\n---\n\n".join(sections) if sections else "Keine detaillierten Analysedaten verfügbar."


def update_progress(analysis_id: str, step: str, percent: int, step_number: int, total_steps: int):
    """Update progress for an analysis"""
    if analysis_id in analysis_results:
        analysis_results[analysis_id]["progress"] = {
            "step": step,
            "percent": percent,
            "step_number": step_number,
            "total_steps": total_steps,
            "timestamp": datetime.now().isoformat()
        }
        print(f"📊 Progress [{analysis_id[:8]}]: {percent}% - [{step_number}/{total_steps}] {step}")


def run_analysis_background(analysis_id: str, request: AnalysisRequest):
    """Run analysis in background thread with progress tracking"""
    start_time = datetime.now()
    
    try:
        import os
        os.environ["OPENAI_API_KEY"] = request.openai_api_key
        os.environ["ALPHA_VANTAGE_API_KEY"] = request.alpha_vantage_api_key
        
        # Calculate progress steps based on configuration
        analyst_count = len(request.analysts)
        debate_rounds = request.research_depth
        total_steps = 5 + analyst_count + debate_rounds + 3  # Init + Analysts + Debates + Finalization
        current_step = 0
        
        # Step 1: Initialization
        current_step += 1
        update_progress(analysis_id, "Verbindung zum LLM-Provider...", 3, current_step, total_steps)
        
        # Konfiguration erstellen
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = request.llm_provider.lower()
        config["backend_url"] = request.provider_url
        config["deep_think_llm"] = request.deep_think_model
        config["quick_think_llm"] = request.quick_think_model
        config["max_debate_rounds"] = request.research_depth
        
        current_step += 1
        update_progress(analysis_id, "Konfiguration wird geladen...", 5, current_step, total_steps)

        # Step 2: Initialize Trading Graph
        current_step += 1
        update_progress(analysis_id, f"{analyst_count} Analysten werden initialisiert...", 8, current_step, total_steps)
        ta = TradingAgentsGraph(debug=True, config=config)
        
        current_step += 1
        update_progress(analysis_id, "Marktdaten werden abgerufen...", 12, current_step, total_steps)
        
        current_step += 1
        update_progress(analysis_id, "Fundamentaldaten werden geladen...", 18, current_step, total_steps)
        
        # Step 3: Run analysis with progress tracking
        # We'll track progress through the analysis phases
        print(f"\n🚀 Starte Analyse für {request.ticker} (ID: {analysis_id[:8]})")
        print(f"   Analysten: {analyst_count}, Debatten: {debate_rounds}, Gesamt-Steps: {total_steps}")
        
        # Analyst phase (20-65%)
        analyst_start_percent = 20
        analyst_range = 45
        for i in range(analyst_count):
            current_step += 1
            percent = analyst_start_percent + int((i + 1) / analyst_count * analyst_range)
            update_progress(analysis_id, f"Analyst {i + 1}/{analyst_count} analysiert...", percent, current_step, total_steps)
        
        # Run the actual analysis (this is where the real work happens)
        step_start = datetime.now()
        result, decision = ta.propagate(request.ticker, request.date)
        analysis_duration = (datetime.now() - step_start).total_seconds()
        print(f"   ⏱️  Propagate-Phase dauerte: {analysis_duration:.1f}s")
        
        # Debate phase (65-88%)
        debate_start_percent = 65
        debate_range = 23
        for i in range(debate_rounds):
            current_step += 1
            percent = debate_start_percent + int((i + 1) / debate_rounds * debate_range)
            update_progress(analysis_id, f"Debatte Runde {i + 1}/{debate_rounds}...", percent, current_step, total_steps)
        
        # Finalization phase (88-98%)
        current_step += 1
        update_progress(analysis_id, "Risikomanagement-Bewertung...", 90, current_step, total_steps)
        
        current_step += 1
        update_progress(analysis_id, "Forschungsmanager erstellt Synthese...", 93, current_step, total_steps)
        
        current_step += 1
        update_progress(analysis_id, "Finale Empfehlung wird erstellt...", 96, current_step, total_steps)

        # Format the full analysis nicely
        formatted_analysis = format_analysis_result(result) if result else "Keine Analysedaten verfügbar."

        # Complete
        update_progress(analysis_id, "Analyse abgeschlossen!", 100, total_steps, total_steps)
        
        total_duration = (datetime.now() - start_time).total_seconds()
        print(f"   ✅ Analyse abgeschlossen in {total_duration:.1f}s (~{total_duration/60:.1f}min)")

        # Store result in memory
        analysis_results[analysis_id] = {
            "status": "completed",
            "success": True,
            "result": {
                "decision": str(decision),
                "ticker": request.ticker,
                "date": request.date,
                "full_analysis": formatted_analysis
            },
            "duration": total_duration,
            "progress": {
                "step": "Abgeschlossen",
                "percent": 100,
                "step_number": total_steps,
                "total_steps": total_steps,
                "timestamp": datetime.now().isoformat()
            }
        }

        # Save to persistent database
        try:
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO analysis_history 
                (id, ticker, date, decision, analysts, llm_provider, llm_model, 
                 research_depth, duration, full_analysis, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis_id,
                request.ticker,
                request.date,
                str(decision),
                ",".join(request.analysts),
                request.llm_provider,
                request.deep_think_model,
                request.research_depth,
                total_duration,
                formatted_analysis,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            print(f"   💾 Analyse in History gespeichert (ID: {analysis_id[:8]})")
        except Exception as db_error:
            print(f"   ⚠️ Fehler beim Speichern in History: {db_error}")

        # Send Discord notification if webhook provided
        if request.discord_webhook and request.discord_notify:
            send_discord_notification(
                request.discord_webhook,
                request.ticker,
                str(decision),
                request.date,
                request.analysts
            )

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"\n❌ Fehler in Analyse {analysis_id[:8]}:")
        print(error_trace)
        
        analysis_results[analysis_id] = {
            "status": "error",
            "success": False,
            "error": str(e),
            "error_trace": error_trace,
            "progress": {
                "step": f"Fehler: {str(e)[:50]}...",
                "percent": 0,
                "step_number": 0,
                "total_steps": 0,
                "timestamp": datetime.now().isoformat()
            }
        }


@app.post("/api/analyze")
async def analyze_stock(request: AnalysisRequest):
    """Start stock analysis (async)"""
    # Generate unique ID for this analysis
    analysis_id = str(uuid.uuid4())
    
    # Mark as running with initial progress at 0%
    analysis_results[analysis_id] = {
        "status": "running",
        "success": None,
        "progress": {
            "step": "Analyse wird vorbereitet...",
            "percent": 0,
            "step_number": 0,
            "total_steps": 15,  # Wird im Background-Thread aktualisiert
            "timestamp": datetime.now().isoformat()
        }
    }
    
    # Start background thread
    thread = threading.Thread(target=run_analysis_background, args=(analysis_id, request))
    thread.start()
    
    return {
        "success": True,
        "message": "Analyse gestartet",
        "analysis_id": analysis_id
    }


@app.get("/api/analysis/{analysis_id}")
async def get_analysis_result(analysis_id: str):
    """Get analysis result by ID with progress information"""
    if analysis_id not in analysis_results:
        return {
            "status": "not_found",
            "success": False,
            "message": "Analyse nicht gefunden"
        }
    
    result = analysis_results[analysis_id]
    
    if result["status"] == "running":
        # Include progress information if available
        progress_info = result.get("progress", {})
        return {
            "status": "running",
            "success": None,
            "message": "Analyse läuft noch...",
            "progress": progress_info
        }
    elif result["status"] == "completed":
        return {
            "status": "completed",
            "success": True,
            "message": "Analyse erfolgreich abgeschlossen",
            "result": result["result"],
            "duration": result.get("duration", 0)
        }
    else:  # error
        return {
            "status": "error",
            "success": False,
            "message": f"Fehler bei der Analyse: {result.get('error', 'Unbekannter Fehler')}",
            "error_trace": result.get("error_trace", "")
        }


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


@app.get("/api/config")
async def get_config():
    """Load existing API keys from .env file"""
    import os
    from pathlib import Path
    
    env_path = Path(__file__).parent.parent / ".env"
    config = {
        "openai_api_key": "",
        "alpha_vantage_api_key": "",
        "discord_webhook": ""
    }
    
    if env_path.exists():
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            
                            if key == "OPENAI_API_KEY":
                                config["openai_api_key"] = value
                            elif key == "ALPHA_VANTAGE_API_KEY":
                                config["alpha_vantage_api_key"] = value
                            elif key == "DISCORD_WEBHOOK_URL":
                                config["discord_webhook"] = value
        except Exception as e:
            print(f"Error reading .env: {e}")
    
    return config


@app.post("/api/save-config")
async def save_config(request: dict):
    """Save API keys to .env file"""
    import os
    from pathlib import Path
    
    env_path = Path(__file__).parent.parent / ".env"
    
    try:
        print(f"\n📝 Speichere Konfiguration nach: {env_path}")
        print(f"   Empfangene Daten: {list(request.keys())}")
        
        keys_to_update = {
            "OPENAI_API_KEY": request.get("openai_api_key", "").strip(),
            "ALPHA_VANTAGE_API_KEY": request.get("alpha_vantage_api_key", "").strip(),
            "DISCORD_WEBHOOK_URL": request.get("discord_webhook", "").strip()
        }
        
        # Debug: Zeige was gespeichert wird
        for key, value in keys_to_update.items():
            if value:
                print(f"   {key}: {'*' * min(len(value), 20)}")
            else:
                print(f"   {key}: (leer)")
        
        # Read existing .env content (preserve non-API lines)
        existing_lines = []
        existing_keys = set()
        
        if env_path.exists():
            print(f"   ✓ .env existiert bereits, lese bestehende Zeilen...")
            with open(env_path, 'r') as f:
                for line in f:
                    line_stripped = line.strip()
                    # Check if this line contains one of our keys
                    is_api_key_line = False
                    if '=' in line_stripped and not line_stripped.startswith('#'):
                        key = line_stripped.split('=', 1)[0].strip()
                        if key in keys_to_update:
                            is_api_key_line = True
                            existing_keys.add(key)
                    
                    # Keep the line if it's not an API key we're updating
                    if not is_api_key_line:
                        existing_lines.append(line)
            print(f"   Gefundene Keys: {existing_keys}")
        else:
            print(f"   ℹ .env existiert nicht, erstelle neu...")
        
        # Write updated .env
        print(f"   Schreibe aktualisierte .env...")
        with open(env_path, 'w') as f:
            # Write header if new file
            if not existing_lines or env_path.stat().st_size == 0:
                f.write("# TradingAgents Configuration\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
            
            # Write existing non-API lines
            for line in existing_lines:
                f.write(line)
            
            # Ensure newline before API keys section
            if existing_lines and not existing_lines[-1].endswith('\n'):
                f.write("\n")
            
            # Write API keys section
            f.write("\n# API Keys (updated via Web UI)\n")
            for key, value in keys_to_update.items():
                if value:  # Only write non-empty values
                    f.write(f'{key}="{value}"\n')
                    print(f"   ✓ Geschrieben: {key}")
        
        # Verify file was written
        if env_path.exists():
            file_size = env_path.stat().st_size
            print(f"   ✅ Datei geschrieben: {file_size} bytes")
            
            # Read back and verify
            with open(env_path, 'r') as f:
                content = f.read()
                for key in keys_to_update.keys():
                    if keys_to_update[key] and key in content:
                        print(f"   ✓ Verifiziert: {key} ist in der Datei")
        else:
            print(f"   ❌ Datei wurde NICHT erstellt!")
        
        return {"success": True, "message": "Konfiguration erfolgreich gespeichert"}
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"\n❌ Fehler beim Speichern der Konfiguration:")
        print(error_details)
        return {"success": False, "message": f"Fehler: {str(e)}"}


@app.get("/api/history")
async def get_analysis_history(limit: int = 50):
    """Get analysis history from database"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, ticker, date, decision, analysts, llm_provider, llm_model,
                   research_depth, duration, created_at
            FROM analysis_history
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to list of dicts
        history = []
        for row in rows:
            history.append({
                "id": row["id"],
                "ticker": row["ticker"],
                "date": row["date"],
                "decision": row["decision"],
                "analysts": row["analysts"].split(",") if row["analysts"] else [],
                "llm_provider": row["llm_provider"],
                "llm_model": row["llm_model"],
                "research_depth": row["research_depth"],
                "duration": row["duration"],
                "created_at": row["created_at"]
            })
        
        return {"success": True, "history": history, "count": len(history)}
    
    except Exception as e:
        print(f"Error loading history: {e}")
        return {"success": False, "error": str(e), "history": [], "count": 0}


@app.get("/api/history/{analysis_id}")
async def get_analysis_from_history(analysis_id: str):
    """Get full analysis details from history"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM analysis_history WHERE id = ?
        """, (analysis_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return {"success": False, "message": "Analyse nicht in History gefunden"}
        
        return {
            "success": True,
            "result": {
                "id": row["id"],
                "ticker": row["ticker"],
                "date": row["date"],
                "decision": row["decision"],
                "analysts": row["analysts"].split(",") if row["analysts"] else [],
                "llm_provider": row["llm_provider"],
                "llm_model": row["llm_model"],
                "research_depth": row["research_depth"],
                "duration": row["duration"],
                "full_analysis": row["full_analysis"],
                "created_at": row["created_at"]
            }
        }
    
    except Exception as e:
        print(f"Error loading analysis from history: {e}")
        return {"success": False, "error": str(e)}


@app.delete("/api/history/{analysis_id}")
async def delete_analysis_from_history(analysis_id: str):
    """Delete an analysis from history"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM analysis_history WHERE id = ?", (analysis_id,))
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        if deleted_count > 0:
            print(f"🗑️ Analyse {analysis_id[:8]} aus History gelöscht")
            return {"success": True, "message": "Analyse erfolgreich gelöscht"}
        else:
            return {"success": False, "message": "Analyse nicht gefunden"}
    
    except Exception as e:
        print(f"Error deleting analysis: {e}")
        return {"success": False, "error": str(e)}


@app.delete("/api/history")
async def clear_all_history():
    """Clear all analysis history"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM analysis_history")
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        print(f"🗑️ Gesamte History gelöscht ({deleted_count} Einträge)")
        return {"success": True, "message": f"{deleted_count} Analysen gelöscht"}
    
    except Exception as e:
        print(f"Error clearing history: {e}")
        return {"success": False, "error": str(e)}


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
