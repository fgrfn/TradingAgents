import questionary
from typing import List, Optional, Tuple, Dict

from cli.models import AnalystType

ANALYST_ORDER = [
    ("Marktanalyst", AnalystType.MARKET),
    ("Social Media Analyst", AnalystType.SOCIAL),
    ("Nachrichtenanalyst", AnalystType.NEWS),
    ("Fundamentalanalyst", AnalystType.FUNDAMENTALS),
]


def get_ticker() -> str:
    """Fordert den Benutzer auf, ein Ticker-Symbol einzugeben."""
    ticker = questionary.text(
        "Geben Sie das zu analysierende Ticker-Symbol ein:",
        validate=lambda x: len(x.strip()) > 0 or "Bitte geben Sie ein gültiges Ticker-Symbol ein.",
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("highlighted", "noinherit"),
            ]
        ),
    ).ask()

    if not ticker:
        console.print("\n[red]Kein Ticker-Symbol angegeben. Programm wird beendet...[/red]")
        exit(1)

    return ticker.strip().upper()


def get_analysis_date() -> str:
    """Fordert den Benutzer auf, ein Datum im Format JJJJ-MM-TT einzugeben."""
    import re
    from datetime import datetime

    def validate_date(date_str: str) -> bool:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            return False
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    date = questionary.text(
        "Geben Sie das Analysedatum ein (JJJJ-MM-TT):",
        validate=lambda x: validate_date(x.strip())
        or "Bitte geben Sie ein gültiges Datum im Format JJJJ-MM-TT ein.",
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("highlighted", "noinherit"),
            ]
        ),
    ).ask()

    if not date:
        console.print("\n[red]Kein Datum angegeben. Programm wird beendet...[/red]")
        exit(1)

    return date.strip()


def select_analysts() -> List[AnalystType]:
    """Wählt Analysten über eine interaktive Checkbox aus."""
    choices = questionary.checkbox(
        "Wählen Sie Ihr [Analysten-Team]:",
        choices=[
            questionary.Choice(display, value=value) for display, value in ANALYST_ORDER
        ],
        instruction="\n- Drücken Sie Leertaste zum Auswählen/Abwählen\n- Drücken Sie 'a' zum Auswählen/Abwählen aller\n- Drücken Sie Enter zum Bestätigen",
        validate=lambda x: len(x) > 0 or "Sie müssen mindestens einen Analysten auswählen.",
        style=questionary.Style(
            [
                ("checkbox-selected", "fg:green"),
                ("selected", "fg:green noinherit"),
                ("highlighted", "noinherit"),
                ("pointer", "noinherit"),
            ]
        ),
    ).ask()

    if not choices:
        console.print("\n[red]Keine Analysten ausgewählt. Programm wird beendet...[/red]")
        exit(1)

    return choices


def select_research_depth() -> int:
    """Wählt die Recherchetiefe über eine interaktive Auswahl aus."""

    # Definiere Recherchetiefe-Optionen mit ihren zugehörigen Werten
    DEPTH_OPTIONS = [
        ("Oberflächlich - Schnelle Recherche, wenige Debatten- und Strategiediskussionsrunden", 1),
        ("Mittel - Mittelweg, moderate Debatten- und Strategiediskussionsrunden", 3),
        ("Tiefgehend - Umfassende Recherche, ausführliche Debatten und Strategiediskussionen", 5),
    ]

    choice = questionary.select(
        "Wählen Sie Ihre [Recherchetiefe]:",
        choices=[
            questionary.Choice(display, value=value) for display, value in DEPTH_OPTIONS
        ],
        instruction="\n- Pfeiltasten zum Navigieren\n- Enter zum Bestätigen",
        style=questionary.Style(
            [
                ("selected", "fg:yellow noinherit"),
                ("highlighted", "fg:yellow noinherit"),
                ("pointer", "fg:yellow noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print("\n[red]Keine Recherchetiefe ausgewählt. Programm wird beendet...[/red]")
        exit(1)

    return choice


def select_shallow_thinking_agent(provider) -> str:
    """Wählt eine schnell denkende LLM-Engine über eine interaktive Auswahl aus."""

    # Definiere Optionen für schnell denkende LLM-Engines mit ihren Modellnamen
    SHALLOW_AGENT_OPTIONS = {
        "openai": [
            ("GPT-4o-mini - Schnell und effizient für schnelle Aufgaben", "gpt-4o-mini"),
            ("GPT-4.1-nano - Ultraleichtes Modell für grundlegende Operationen", "gpt-4.1-nano"),
            ("GPT-4.1-mini - Kompaktes Modell mit guter Leistung", "gpt-4.1-mini"),
            ("GPT-4o - Standardmodell mit soliden Fähigkeiten", "gpt-4o"),
            ("GPT-5-mini - Kompaktes Next-Gen-Modell für schnelle Aufgaben", "gpt-5-mini"),
            ("GPT-5 - Next-Generation-Modell mit erweiterten Fähigkeiten", "gpt-5"),
        ],
        "anthropic": [
            ("Claude Haiku 3.5 - Schnelle Inferenz und Standardfähigkeiten", "claude-3-5-haiku-latest"),
            ("Claude Sonnet 3.5 - Hochleistungsfähiges Standardmodell", "claude-3-5-sonnet-latest"),
            ("Claude Sonnet 3.7 - Außergewöhnliche hybride Reasoning- und Agentenfähigkeiten", "claude-3-7-sonnet-latest"),
            ("Claude Sonnet 4 - Hohe Leistung und exzellentes Reasoning", "claude-sonnet-4-0"),
        ],
        "google": [
            ("Gemini 2.0 Flash-Lite - Kosteneffizienz und niedrige Latenz", "gemini-2.0-flash-lite"),
            ("Gemini 2.0 Flash - Next-Gen-Features, Geschwindigkeit und Denken", "gemini-2.0-flash"),
            ("Gemini 2.5 Flash - Adaptives Denken, Kosteneffizienz", "gemini-2.5-flash-preview-05-20"),
        ],
        "openrouter": [
            ("Meta: Llama 4 Scout", "meta-llama/llama-4-scout:free"),
            ("Meta: Llama 3.3 8B Instruct - Leichtgewichtige und ultraschnelle Variante von Llama 3.3 70B", "meta-llama/llama-3.3-8b-instruct:free"),
            ("google/gemini-2.0-flash-exp:free - Gemini Flash 2.0 bietet deutlich schnellere Zeit bis zum ersten Token", "google/gemini-2.0-flash-exp:free"),
        ],
        "ollama": [
            ("llama3.1 lokal", "llama3.1"),
            ("llama3.2 lokal", "llama3.2"),
        ]
    }

    choice = questionary.select(
        "Wählen Sie Ihre [Schnell-Denkende LLM-Engine]:",
        choices=[
            questionary.Choice(display, value=value)
            for display, value in SHALLOW_AGENT_OPTIONS[provider.lower()]
        ],
        instruction="\n- Pfeiltasten zum Navigieren\n- Enter zum Bestätigen",
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print(
            "\n[red]Keine schnell denkende LLM-Engine ausgewählt. Programm wird beendet...[/red]"
        )
        exit(1)

    return choice


def select_deep_thinking_agent(provider) -> str:
    """Wählt eine tiefgehend denkende LLM-Engine über eine interaktive Auswahl aus."""

    # Definiere Optionen für tiefgehend denkende LLM-Engines mit ihren Modellnamen
    DEEP_AGENT_OPTIONS = {
        "openai": [
            ("GPT-4.1-nano - Ultraleichtes Modell für grundlegende Operationen", "gpt-4.1-nano"),
            ("GPT-4.1-mini - Kompaktes Modell mit guter Leistung", "gpt-4.1-mini"),
            ("GPT-4o - Standardmodell mit soliden Fähigkeiten", "gpt-4o"),
            ("GPT-5-mini - Kompaktes Next-Gen-Modell mit verbessertem Reasoning", "gpt-5-mini"),
            ("GPT-5 - Next-Generation-Modell mit erweiterten Fähigkeiten", "gpt-5"),
            ("GPT-5-turbo - Hochleistungsvariante mit optimierter Geschwindigkeit", "gpt-5-turbo"),
            ("o4-mini - Spezialisiertes Reasoning-Modell (kompakt)", "o4-mini"),
            ("o3-mini - Fortgeschrittenes Reasoning-Modell (leichtgewichtig)", "o3-mini"),
            ("o3 - Vollständiges fortgeschrittenes Reasoning-Modell", "o3"),
            ("o1 - Premium-Reasoning- und Problemlösungsmodell", "o1"),
        ],
        "anthropic": [
            ("Claude Haiku 3.5 - Schnelle Inferenz und Standardfähigkeiten", "claude-3-5-haiku-latest"),
            ("Claude Sonnet 3.5 - Hochleistungsfähiges Standardmodell", "claude-3-5-sonnet-latest"),
            ("Claude Sonnet 3.7 - Außergewöhnliche hybride Reasoning- und Agentenfähigkeiten", "claude-3-7-sonnet-latest"),
            ("Claude Sonnet 4 - Hohe Leistung und exzellentes Reasoning", "claude-sonnet-4-0"),
            ("Claude Opus 4 - Leistungsstärkstes Anthropic-Modell", "claude-opus-4-0"),
        ],
        "google": [
            ("Gemini 2.0 Flash-Lite - Kosteneffizienz und niedrige Latenz", "gemini-2.0-flash-lite"),
            ("Gemini 2.0 Flash - Next-Gen-Features, Geschwindigkeit und Denken", "gemini-2.0-flash"),
            ("Gemini 2.5 Flash - Adaptives Denken, Kosteneffizienz", "gemini-2.5-flash-preview-05-20"),
            ("Gemini 2.5 Pro", "gemini-2.5-pro-preview-06-05"),
        ],
        "openrouter": [
            ("DeepSeek V3 - 685B-Parameter Mixture-of-Experts-Modell", "deepseek/deepseek-chat-v3-0324:free"),
            ("Deepseek - Neueste Iteration der Flagship-Chat-Modellfamilie vom DeepSeek-Team", "deepseek/deepseek-chat-v3-0324:free"),
        ],
        "ollama": [
            ("llama3.1 lokal", "llama3.1"),
            ("qwen3", "qwen3"),
        ]
    }
    
    choice = questionary.select(
        "Wählen Sie Ihre [Tiefgehend-Denkende LLM-Engine]:",
        choices=[
            questionary.Choice(display, value=value)
            for display, value in DEEP_AGENT_OPTIONS[provider.lower()]
        ],
        instruction="\n- Pfeiltasten zum Navigieren\n- Enter zum Bestätigen",
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print("\n[red]Keine tiefgehend denkende LLM-Engine ausgewählt. Programm wird beendet...[/red]")
        exit(1)

    return choice

def select_llm_provider() -> tuple[str, str]:
    """Wählt die LLM-Provider-URL über eine interaktive Auswahl aus."""
    # Definiere LLM-Provider-Optionen mit ihren zugehörigen Endpunkten
    BASE_URLS = [
        ("OpenAI", "https://api.openai.com/v1"),
        ("Anthropic", "https://api.anthropic.com/"),
        ("Google", "https://generativelanguage.googleapis.com/v1"),
        ("Openrouter", "https://openrouter.ai/api/v1"),
        ("Ollama", "http://localhost:11434/v1"),        
    ]
    
    choice = questionary.select(
        "Wählen Sie Ihren LLM-Provider:",
        choices=[
            questionary.Choice(display, value=(display, value))
            for display, value in BASE_URLS
        ],
        instruction="\n- Pfeiltasten zum Navigieren\n- Enter zum Bestätigen",
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()
    
    if choice is None:
        console.print("\n[red]Kein LLM-Provider ausgewählt. Programm wird beendet...[/red]")
        exit(1)
    
    display_name, url = choice
    print(f"Sie haben ausgewählt: {display_name}\tURL: {url}")
    
    return display_name, url
