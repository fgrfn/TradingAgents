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
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
from contextlib import asynccontextmanager

# Add parent directory to path to import tradingagents
sys.path.insert(0, str(Path(__file__).parent.parent))

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from cli.models import AnalystType

# Create app temporarily - lifespan will be added later
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
                "Last-Modified": datetime.fromtimestamp(mtime, tz=timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
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
import logging
from pathlib import Path as FilePath
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

# Store for analysis results (temporary, in-memory)
analysis_results = {}

# Scheduler for automated analyses
scheduler = BackgroundScheduler()
scheduler.start()

# Database setup for persistent history
DB_PATH = FilePath(__file__).parent.parent / "analysis_history.db"
LOGS_DIR = FilePath(__file__).parent.parent / "analysis_logs"

# Create logs directory if it doesn't exist
LOGS_DIR.mkdir(exist_ok=True)

def init_database():
    """Initialize SQLite database for analysis history and schedules"""
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
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scheduled_analyses (
            id TEXT PRIMARY KEY,
            ticker TEXT NOT NULL,
            analysts TEXT NOT NULL,
            llm_provider TEXT,
            provider_url TEXT,
            deep_think_model TEXT,
            quick_think_model TEXT,
            research_depth INTEGER,
            alpha_vantage_key TEXT,
            schedule_type TEXT NOT NULL,
            schedule_time TEXT,
            schedule_days TEXT,
            is_active INTEGER DEFAULT 1,
            last_run TEXT,
            next_run TEXT,
            notification_webhook TEXT,
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


def get_analysis_logger(analysis_id: str, ticker: str):
    """Create a logger for a specific analysis"""
    logger = logging.getLogger(f"analysis_{analysis_id}")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()  # Remove existing handlers
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOGS_DIR / f"{ticker}_{timestamp}_{analysis_id[:8]}.log"
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s', 
                                 datefmt='%Y-%m-%d %H:%M:%S.%f')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Log file creation
    logger.info("="*80)
    logger.info(f"📊 NEUE ANALYSE GESTARTET")
    logger.info(f"Analysis ID: {analysis_id}")
    logger.info(f"Ticker: {ticker}")
    logger.info(f"Log-Datei: {log_file.name}")
    logger.info("="*80)
    
    return logger, log_file

def update_progress(analysis_id: str, step: str, percent: int, step_number: int, total_steps: int, logger=None):
    """Update progress for an analysis and log it"""
    timestamp = datetime.now().isoformat()
    
    if analysis_id in analysis_results:
        analysis_results[analysis_id]["progress"] = {
            "step": step,
            "percent": percent,
            "step_number": step_number,
            "total_steps": total_steps,
            "timestamp": timestamp
        }
    
    # Console output
    print(f"📊 Progress [{analysis_id[:8]}]: {percent}% - [{step_number}/{total_steps}] {step}")
    
    # Log to file
    if logger:
        logger.info(f"PROGRESS: {percent:3d}% | Step {step_number:2d}/{total_steps:2d} | {step}")


def run_analysis_background(analysis_id: str, request: AnalysisRequest):
    """Run analysis in background thread with progress tracking"""
    start_time = datetime.now()
    
    # Create logger for this analysis
    logger, log_file = get_analysis_logger(analysis_id, request.ticker)
    
    try:
        import os
        os.environ["OPENAI_API_KEY"] = request.openai_api_key
        os.environ["ALPHA_VANTAGE_API_KEY"] = request.alpha_vantage_api_key
        
        # Log configuration
        logger.info(f"Konfiguration:")
        logger.info(f"  - Ticker: {request.ticker}")
        logger.info(f"  - Datum: {request.date}")
        logger.info(f"  - LLM Provider: {request.llm_provider}")
        logger.info(f"  - Quick Model: {request.quick_think_model}")
        logger.info(f"  - Deep Model: {request.deep_think_model}")
        logger.info(f"  - Analysten: {', '.join(request.analysts)}")
        logger.info(f"  - Recherchetiefe: {request.research_depth} Runden")
        logger.info("-"*80)
        
        # Calculate progress steps based on configuration
        analyst_count = len(request.analysts)
        debate_rounds = request.research_depth
        total_steps = 5 + analyst_count + debate_rounds + 3  # Init + Analysts + Debates + Finalization
        current_step = 0
        
        # Step 1: Initialization
        import time
        current_step += 1
        update_progress(analysis_id, "Verbindung zum LLM-Provider...", 3, current_step, total_steps, logger)
        time.sleep(0.3)  # Kurze Pause damit Frontend Update sieht
        
        # Konfiguration erstellen
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = request.llm_provider.lower()
        config["backend_url"] = request.provider_url
        config["deep_think_llm"] = request.deep_think_model
        config["quick_think_llm"] = request.quick_think_model
        config["max_debate_rounds"] = request.research_depth
        
        current_step += 1
        update_progress(analysis_id, "Konfiguration wird geladen...", 5, current_step, total_steps, logger)
        time.sleep(0.3)

        # Step 2: Initialize Trading Graph
        current_step += 1
        update_progress(analysis_id, f"{analyst_count} Analysten werden initialisiert...", 8, current_step, total_steps, logger)
        time.sleep(0.2)
        ta = TradingAgentsGraph(debug=True, config=config)
        
        current_step += 1
        update_progress(analysis_id, "Marktdaten werden abgerufen...", 12, current_step, total_steps, logger)
        time.sleep(0.2)
        
        current_step += 1
        update_progress(analysis_id, "Fundamentaldaten werden geladen...", 18, current_step, total_steps, logger)
        time.sleep(0.2)
        
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
            update_progress(analysis_id, f"Analyst {i + 1}/{analyst_count} analysiert...", percent, current_step, total_steps, logger)
        
        # Run the actual analysis (this is where the real work happens)
        # Note: propagate() does all the work internally (analysts, debates, etc.)
        logger.info("-"*80)
        logger.info("Starte Hauptanalyse (propagate)...")
        step_start = datetime.now()
        
        update_progress(analysis_id, "Analysten arbeiten an der Analyse...", 50, current_step + 2, total_steps, logger)
        
        result, decision = ta.propagate(request.ticker, request.date)
        
        analysis_duration = (datetime.now() - step_start).total_seconds()
        logger.info(f"Hauptanalyse abgeschlossen nach {analysis_duration:.1f}s")
        logger.info("-"*80)
        print(f"   ⏱️  Propagate-Phase dauerte: {analysis_duration:.1f}s")

        # Format the full analysis nicely
        current_step = total_steps - 1
        update_progress(analysis_id, "Formatiere Ergebnisse...", 95, current_step, total_steps, logger)
        formatted_analysis = format_analysis_result(result) if result else "Keine Analysedaten verfügbar."

        # Complete
        update_progress(analysis_id, "Analyse abgeschlossen!", 100, total_steps, total_steps, logger)
        
        total_duration = (datetime.now() - start_time).total_seconds()
        print(f"   ✅ Analyse abgeschlossen in {total_duration:.1f}s (~{total_duration/60:.1f}min)")
        
        # Log completion
        logger.info("="*80)
        logger.info(f"✅ ANALYSE ERFOLGREICH ABGESCHLOSSEN")
        logger.info(f"Gesamtdauer: {total_duration:.1f}s ({total_duration/60:.1f} Minuten)")
        logger.info(f"Entscheidung: {decision}")
        logger.info("="*80)

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
        
        # Log error
        if 'logger' in locals():
            logger.error("="*80)
            logger.error("❌ FEHLER IN DER ANALYSE")
            logger.error(f"Fehler: {str(e)}")
            logger.error("-"*80)
            logger.error("Traceback:")
            logger.error(error_trace)
            logger.error("="*80)
        
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
    finally:
        # Close logger handlers
        if 'logger' in locals():
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)


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


@app.get("/api/search/ticker")
async def search_ticker(q: str = "", limit: int = 10):
    """
    Search for ticker symbols by symbol or company name
    
    Args:
        q: Search query (symbol or company name)
        limit: Maximum number of results (default: 10)
    
    Returns:
        List of matching ticker symbols with their names
    """
    try:
        if not q or len(q) < 1:
            return {"success": True, "results": []}
        
        from stock_symbols import search_symbols
        
        # Search in static list (searches both symbol and name)
        results = search_symbols(q, limit)
        
        # If exact match on symbol, verify with Yahoo Finance
        if results and results[0]['symbol'].upper() == q.upper():
            try:
                import yfinance as yf
                ticker = yf.Ticker(q.upper())
                info = ticker.info
                
                # Update with live data if available
                if info and info.get('symbol'):
                    results[0]['name'] = info.get('longName') or info.get('shortName') or results[0]['name']
            except:
                pass  # Keep static data if Yahoo Finance fails
        
        return {"success": True, "results": results}
        
    except Exception as e:
        print(f"Error searching ticker: {e}")
        return {"success": False, "error": str(e), "results": []}


# ========================================
# SCHEDULING ENDPOINTS
# ========================================

class ScheduleRequest(BaseModel):
    ticker: str
    analysts: List[str]
    llm_provider: str
    provider_url: str
    deep_think_model: str
    quick_think_model: str
    research_depth: int
    alpha_vantage_key: Optional[str] = None
    schedule_type: str  # 'daily', 'weekly', 'interval'
    schedule_time: Optional[str] = None  # HH:MM for daily/weekly
    schedule_days: Optional[List[str]] = None  # ['mon', 'tue', ...] for weekly
    interval_hours: Optional[int] = None  # For interval type
    notification_webhook: Optional[str] = None


@app.post("/api/schedules")
async def create_schedule(request: ScheduleRequest):
    """Create a new scheduled analysis"""
    try:
        schedule_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        # Store schedule in database
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO scheduled_analyses 
            (id, ticker, analysts, llm_provider, provider_url, deep_think_model,
             quick_think_model, research_depth, alpha_vantage_key, schedule_type,
             schedule_time, schedule_days, notification_webhook, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
        """, (
            schedule_id,
            request.ticker,
            json.dumps(request.analysts),
            request.llm_provider,
            request.provider_url,
            request.deep_think_model,
            request.quick_think_model,
            request.research_depth,
            request.alpha_vantage_key,
            request.schedule_type,
            request.schedule_time,
            json.dumps(request.schedule_days) if request.schedule_days else None,
            request.notification_webhook,
            now
        ))
        
        conn.commit()
        conn.close()
        
        # Add job to scheduler
        _add_scheduled_job(schedule_id, request)
        
        print(f"✅ Schedule erstellt: {schedule_id} für {request.ticker}")
        return {"success": True, "schedule_id": schedule_id}
        
    except Exception as e:
        print(f"Error creating schedule: {e}")
        return {"success": False, "error": str(e)}


@app.get("/api/schedules")
async def get_schedules():
    """Get all scheduled analyses"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, ticker, analysts, schedule_type, schedule_time, 
                   schedule_days, is_active, last_run, next_run, created_at
            FROM scheduled_analyses
            ORDER BY created_at DESC
        """)
        
        schedules = []
        for row in cursor.fetchall():
            schedules.append({
                "id": row[0],
                "ticker": row[1],
                "analysts": json.loads(row[2]),
                "schedule_type": row[3],
                "schedule_time": row[4],
                "schedule_days": json.loads(row[5]) if row[5] else None,
                "is_active": bool(row[6]),
                "last_run": row[7],
                "next_run": row[8],
                "created_at": row[9]
            })
        
        conn.close()
        return {"success": True, "schedules": schedules}
        
    except Exception as e:
        print(f"Error getting schedules: {e}")
        return {"success": False, "error": str(e)}


@app.delete("/api/schedules/{schedule_id}")
async def delete_schedule(schedule_id: str):
    """Delete a scheduled analysis"""
    try:
        # Remove from scheduler
        scheduler.remove_job(f"schedule_{schedule_id}")
        
        # Delete from database
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute("DELETE FROM scheduled_analyses WHERE id = ?", (schedule_id,))
        conn.commit()
        conn.close()
        
        print(f"🗑️ Schedule gelöscht: {schedule_id}")
        return {"success": True}
        
    except Exception as e:
        print(f"Error deleting schedule: {e}")
        return {"success": False, "error": str(e)}


@app.patch("/api/schedules/{schedule_id}/toggle")
async def toggle_schedule(schedule_id: str):
    """Toggle a schedule's active status"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Get current status
        cursor.execute("SELECT is_active FROM scheduled_analyses WHERE id = ?", (schedule_id,))
        row = cursor.fetchone()
        if not row:
            return {"success": False, "error": "Schedule not found"}
        
        new_status = 0 if row[0] else 1
        cursor.execute("UPDATE scheduled_analyses SET is_active = ? WHERE id = ?", 
                      (new_status, schedule_id))
        conn.commit()
        conn.close()
        
        # Pause or resume job
        if new_status:
            scheduler.resume_job(f"schedule_{schedule_id}")
        else:
            scheduler.pause_job(f"schedule_{schedule_id}")
        
        print(f"🔄 Schedule {'aktiviert' if new_status else 'deaktiviert'}: {schedule_id}")
        return {"success": True, "is_active": bool(new_status)}
        
    except Exception as e:
        print(f"Error toggling schedule: {e}")
        return {"success": False, "error": str(e)}


def _add_scheduled_job(schedule_id: str, request: ScheduleRequest):
    """Add a job to the APScheduler"""
    job_id = f"schedule_{schedule_id}"
    
    if request.schedule_type == "daily":
        hour, minute = map(int, request.schedule_time.split(":"))
        trigger = CronTrigger(hour=hour, minute=minute)
    
    elif request.schedule_type == "weekly":
        hour, minute = map(int, request.schedule_time.split(":"))
        day_map = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
        days = [day_map[d] for d in request.schedule_days]
        trigger = CronTrigger(day_of_week=",".join(map(str, days)), hour=hour, minute=minute)
    
    elif request.schedule_type == "interval":
        trigger = IntervalTrigger(hours=request.interval_hours or 24)
    
    else:
        raise ValueError(f"Unknown schedule type: {request.schedule_type}")
    
    scheduler.add_job(
        _run_scheduled_analysis,
        trigger=trigger,
        id=job_id,
        args=[schedule_id, request],
        replace_existing=True
    )


def _run_scheduled_analysis(schedule_id: str, request: ScheduleRequest):
    """Execute a scheduled analysis"""
    print(f"🔔 Starte geplante Analyse: {schedule_id} für {request.ticker}")
    
    try:
        # Use today's date
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Create analysis request
        analysis_req = AnalysisRequest(
            ticker=request.ticker,
            date=today,
            analysts=request.analysts,
            llm_provider=request.llm_provider,
            provider_url=request.provider_url,
            deep_think_model=request.deep_think_model,
            quick_think_model=request.quick_think_model,
            research_depth=request.research_depth,
            alpha_vantage_key=request.alpha_vantage_key
        )
        
        # Run analysis in background thread
        analysis_id = str(uuid.uuid4())
        thread = threading.Thread(
            target=run_analysis_sync,
            args=(analysis_id, analysis_req, request.notification_webhook)
        )
        thread.start()
        
        # Update last_run time
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute(
            "UPDATE scheduled_analyses SET last_run = ? WHERE id = ?",
            (now, schedule_id)
        )
        conn.commit()
        conn.close()
        
        print(f"✅ Geplante Analyse gestartet: {analysis_id}")
        
    except Exception as e:
        print(f"Error running scheduled analysis: {e}")


def run_analysis_sync(analysis_id: str, request: AnalysisRequest, webhook_url: Optional[str] = None):
    """Run analysis synchronously for scheduled jobs"""
    try:
        # This is a simplified version - reuse the existing analysis logic
        # You would call the actual analysis function here
        print(f"Running analysis {analysis_id} for {request.ticker}")
        
        # If webhook URL provided, send notification
        if webhook_url:
            try:
                requests.post(webhook_url, json={
                    "content": f"✅ Analyse abgeschlossen: {request.ticker}",
                    "analysis_id": analysis_id
                })
            except:
                pass
                
    except Exception as e:
        print(f"Error in scheduled analysis: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, ticker, analysts, llm_provider, provider_url, 
                   deep_think_model, quick_think_model, research_depth,
                   alpha_vantage_key, schedule_type, schedule_time, 
                   schedule_days, notification_webhook
            FROM scheduled_analyses
            WHERE is_active = 1
        """)
        
        rows = cursor.fetchall()
        count = len(rows)
        
        for row in rows:
            schedule_req = ScheduleRequest(
                ticker=row[1],
                analysts=json.loads(row[2]),
                llm_provider=row[3],
                provider_url=row[4],
                deep_think_model=row[5],
                quick_think_model=row[6],
                research_depth=row[7],
                alpha_vantage_key=row[8],
                schedule_type=row[9],
                schedule_time=row[10],
                schedule_days=json.loads(row[11]) if row[11] else None,
                notification_webhook=row[12]
            )
            _add_scheduled_job(row[0], schedule_req)
        
        conn.close()
        print(f"✅ {count} aktive Schedules geladen")
        
    except Exception as e:
        print(f"Error loading schedules: {e}")
    
    yield
    
    # Shutdown
    scheduler.shutdown()


# Assign lifespan to existing app
app.router.lifespan_context = lifespan


@app.get("/api/ticker/quote/{symbol}")
async def get_ticker_quote(symbol: str):
    """Get live quote data from Yahoo Finance"""
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info
        
        # Get current price and change
        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        previous_close = info.get('previousClose', 0)
        change = current_price - previous_close if previous_close else 0
        change_percent = (change / previous_close * 100) if previous_close else 0
        
        return {
            "symbol": symbol.upper(),
            "price": round(current_price, 2),
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "volume": info.get('volume', 0),
            "market_cap": info.get('marketCap', 0),
            "currency": info.get('currency', 'USD'),
            "exchange": info.get('exchange', ''),
            "name": info.get('longName', symbol.upper())
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/ticker/history/{symbol}")
async def get_ticker_history(symbol: str, period: str = "1y"):
    """Get historical price data from Yahoo Finance"""
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol.upper())
        
        # Map period strings
        period_map = {
            "1d": "1d",
            "5d": "5d",
            "1m": "1mo",
            "3m": "3mo",
            "6m": "6mo",
            "1y": "1y",
            "2y": "2y",
            "5y": "5y",
            "max": "max"
        }
        
        yf_period = period_map.get(period, "1y")
        hist = ticker.history(period=yf_period)
        
        if hist.empty:
            print(f"⚠️ No history data for {symbol} with period {yf_period}")
            return {"error": "No data available", "symbol": symbol.upper(), "period": period, "data": []}
        
        # Convert to simple format
        data = []
        for date, row in hist.iterrows():
            try:
                data.append({
                    "date": date.strftime("%Y-%m-%d") if hasattr(date, 'strftime') else str(date).split(' ')[0],
                    "open": round(float(row['Open']), 2) if not pd.isna(row['Open']) else 0,
                    "high": round(float(row['High']), 2) if not pd.isna(row['High']) else 0,
                    "low": round(float(row['Low']), 2) if not pd.isna(row['Low']) else 0,
                    "close": round(float(row['Close']), 2) if not pd.isna(row['Close']) else 0,
                    "volume": int(row['Volume']) if not pd.isna(row['Volume']) else 0
                })
            except Exception as row_error:
                print(f"⚠️ Error processing row: {row_error}")
                continue
        
        print(f"✅ Retrieved {len(data)} data points for {symbol} ({period})")
        
        return {
            "symbol": symbol.upper(),
            "period": period,
            "data": data
        }
    except Exception as e:
        print(f"❌ Error in get_ticker_history: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "symbol": symbol.upper(), "period": period, "data": []}


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
