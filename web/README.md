# TradingAgents Web UI

Modernes Web-Interface für TradingAgents mit FastAPI und Vanilla JavaScript.

## Features

- 🎨 Modernes, responsives Design
- 🔧 Vollständige Konfiguration über UI
- 📊 Live-Fortschrittsanzeige
- 🤖 Unterstützung für mehrere LLM-Provider (OpenAI, Anthropic, Google, etc.)
- 🌐 Deutsche Lokalisierung
- ⚡ Schnelle REST API mit FastAPI
- 🔌 WebSocket-Support für Echtzeit-Updates (optional)

## Installation

1. Navigieren Sie zum web-Verzeichnis:
```bash
cd /workspaces/TradingAgents/web
```

2. Installieren Sie die Abhängigkeiten:
```bash
pip install -r requirements.txt
```

## Verwendung

### Starten des Servers

```bash
python app.py
```

oder mit uvicorn direkt:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Die Anwendung ist dann unter http://localhost:8000 erreichbar.

### API-Endpunkte

- `GET /` - Haupt-UI
- `GET /api/providers` - Liste verfügbarer LLM-Provider
- `GET /api/models/{provider}` - Verfügbare Modelle für einen Provider
- `POST /api/analyze` - Analyse starten
- `GET /api/health` - Health Check
- `WS /ws` - WebSocket für Live-Updates

## Struktur

```
web/
├── app.py                 # FastAPI Hauptanwendung
├── requirements.txt       # Python-Abhängigkeiten
├── README.md             # Diese Datei
├── templates/
│   └── index.html        # Haupt-HTML-Template
└── static/
    ├── css/
    │   └── styles.css    # Stylesheet
    └── js/
        └── app.js        # Frontend-JavaScript
```

## Entwicklung

### Anpassungen

- **Styling**: Bearbeiten Sie `static/css/styles.css`
- **Frontend-Logik**: Bearbeiten Sie `static/js/app.js`
- **Backend-API**: Bearbeiten Sie `app.py`
- **UI-Layout**: Bearbeiten Sie `templates/index.html`

### Debugging

Starten Sie den Server im Debug-Modus:

```bash
uvicorn app:app --reload --log-level debug
```

## Browser-Kompatibilität

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Sicherheitshinweise

⚠️ **Wichtig**: Dies ist eine Entwicklungsversion. Für den Produktionseinsatz sollten Sie:

- API-Rate-Limiting hinzufügen
- Authentifizierung implementieren
- HTTPS verwenden
- Input-Validierung verstärken
- CORS richtig konfigurieren
- Sensible Daten (API-Keys) sicher speichern

## Lizenz

Siehe Haupt-Repository Lizenz (Apache 2.0)
