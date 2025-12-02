from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.agents.utils.agent_utils import get_stock_data, get_indicators
from tradingagents.dataflows.config import get_config


def create_market_analyst(llm):

    def market_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        tools = [
            get_stock_data,
            get_indicators,
        ]

        system_message = (
            """Sie sind ein Trading-Assistent mit der Aufgabe, Finanzmärkte zu analysieren. Ihre Rolle besteht darin, die **relevantesten Indikatoren** für eine bestimmte Marktsituation oder Handelsstrategie aus der folgenden Liste auszuwählen. Ziel ist es, bis zu **8 Indikatoren** zu wählen, die sich ergänzende Einblicke bieten, ohne Redundanz. Kategorien und die Indikatoren jeder Kategorie sind:

Gleitende Durchschnitte:
- close_50_sma: 50 SMA: Ein mittelfristiger Trendindikator. Verwendung: Trendrichtung identifizieren und als dynamische Unterstützung/Widerstand dienen. Tipps: Hinkt dem Preis hinterher; mit schnelleren Indikatoren für zeitnahe Signale kombinieren.
- close_200_sma: 200 SMA: Ein langfristiger Trend-Benchmark. Verwendung: Gesamtmarkttrend bestätigen und Golden/Death Cross-Setups identifizieren. Tipps: Reagiert langsam; am besten für strategische Trendbestätigung statt häufige Trading-Einstiege.
- close_10_ema: 10 EMA: Ein reaktionsschneller kurzfristiger Durchschnitt. Verwendung: Schnelle Momentum-Verschiebungen und potenzielle Einstiegspunkte erfassen. Tipps: Anfällig für Rauschen in unruhigen Märkten; zusammen mit längeren Durchschnitten zur Filterung falscher Signale verwenden.

MACD-Bezogen:
- macd: MACD: Berechnet Momentum über Differenzen von EMAs. Verwendung: Auf Überkreuzungen und Divergenz als Signale für Trendänderungen achten. Tipps: Mit anderen Indikatoren in Niedrigvolatilitäts- oder Seitwärtsmärkten bestätigen.
- macds: MACD-Signal: Eine EMA-Glättung der MACD-Linie. Verwendung: Überkreuzungen mit der MACD-Linie zur Auslösung von Trades nutzen. Tipps: Sollte Teil einer breiteren Strategie sein, um Fehlsignale zu vermeiden.
- macdh: MACD-Histogramm: Zeigt die Lücke zwischen MACD-Linie und Signal. Verwendung: Momentum-Stärke visualisieren und Divergenz früh erkennen. Tipps: Kann volatil sein; in schnelllebigen Märkten mit zusätzlichen Filtern ergänzen.

Momentum-Indikatoren:
- rsi: RSI: Misst Momentum zur Kennzeichnung überkaufter/überverkaufter Bedingungen. Verwendung: 70/30-Schwellenwerte anwenden und auf Divergenz für Umkehrsignale achten. Tipps: In starken Trends kann RSI extrem bleiben; immer mit Trendanalyse gegenprüfen.

Volatilitätsindikatoren:
- boll: Bollinger Mitte: Ein 20-SMA als Basis für Bollinger-Bänder. Verwendung: Dient als dynamischer Benchmark für Preisbewegung. Tipps: Mit oberen und unteren Bändern kombinieren, um Ausbrüche oder Umkehrungen effektiv zu erkennen.
- boll_ub: Bollinger Oberes Band: Typischerweise 2 Standardabweichungen über der Mittellinie. Verwendung: Signalisiert potenzielle überkaufte Bedingungen und Breakout-Zonen. Tipps: Signale mit anderen Tools bestätigen; Preise können das Band in starken Trends begleiten.
- boll_lb: Bollinger Unteres Band: Typischerweise 2 Standardabweichungen unter der Mittellinie. Verwendung: Deutet auf potenzielle überverkaufte Bedingungen hin. Tipps: Zusätzliche Analyse verwenden, um falsche Umkehrsignale zu vermeiden.
- atr: ATR: Mittelt True Range zur Messung der Volatilität. Verwendung: Stop-Loss-Level setzen und Positionsgrößen basierend auf aktueller Marktvolatilität anpassen. Tipps: Ist eine reaktive Maßnahme, daher als Teil einer breiteren Risikomanagementstrategie verwenden.

Volumenbasierte Indikatoren:
- vwma: VWMA: Ein nach Volumen gewichteter gleitender Durchschnitt. Verwendung: Trends durch Integration von Preisaction und Volumendaten bestätigen. Tipps: Auf verzerrte Ergebnisse durch Volumenspitzen achten; in Kombination mit anderen Volumenanalysen verwenden.

- Wählen Sie Indikatoren, die vielfältige und sich ergänzende Informationen bieten. Vermeiden Sie Redundanz (z.B. nicht sowohl RSI als auch StochRSI auswählen). Erklären Sie auch kurz, warum sie für den gegebenen Marktkontext geeignet sind. Verwenden Sie beim Tool-Aufruf bitte die exakten Namen der oben angegebenen Indikatoren, da diese definierte Parameter sind, sonst schlägt Ihr Aufruf fehl. Rufen Sie zuerst get_stock_data auf, um die benötigte CSV-Datei abzurufen. Verwenden Sie dann get_indicators mit den spezifischen Indikatornamen. Schreiben Sie einen sehr detaillierten und nuancierten Bericht über die beobachteten Trends. Sagen Sie nicht einfach, die Trends seien gemischt, sondern liefern Sie detaillierte und feingranulare Analysen und Einblicke, die Händlern bei Entscheidungen helfen können."""
            + """ Fügen Sie am Ende des Berichts unbedingt eine Markdown-Tabelle hinzu, um die wichtigsten Punkte des Berichts zu organisieren, übersichtlich und leicht lesbar zu gestalten."""
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Sie sind ein hilfreicher KI-Assistent, der mit anderen Assistenten zusammenarbeitet."
                    " Verwenden Sie die bereitgestellten Tools, um bei der Beantwortung der Frage voranzukommen."
                    " Wenn Sie nicht vollständig antworten können, ist das in Ordnung; ein anderer Assistent mit anderen Tools"
                    " wird dort weitermachen, wo Sie aufgehört haben. Führen Sie aus, was Sie können, um Fortschritte zu erzielen."
                    " Wenn Sie oder ein anderer Assistent den FINALEN TRANSAKTIONSVORSCHLAG: **KAUFEN/HALTEN/VERKAUFEN** oder das Ergebnis hat,"
                    " stellen Sie Ihrer Antwort FINALER TRANSAKTIONSVORSCHLAG: **KAUFEN/HALTEN/VERKAUFEN** voran, damit das Team weiß, dass es aufhören muss."
                    " Sie haben Zugriff auf die folgenden Tools: {tool_names}.\n{system_message}"
                    "Zu Ihrer Information, das aktuelle Datum ist {current_date}. Das Unternehmen, das wir betrachten möchten, ist {ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content
       
        return {
            "messages": [result],
            "market_report": report,
        }

    return market_analyst_node
