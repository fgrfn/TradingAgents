import time
import json


def create_risky_debator(llm):
    def risky_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        risky_history = risk_debate_state.get("risky_history", "")

        current_safe_response = risk_debate_state.get("current_safe_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        trader_decision = state["trader_investment_plan"]

        prompt = f"""Als Risiko-Analyst für hohe Risiken ist Ihre Aufgabe, aktiv für hochlohnende, risikoreiche Chancen einzutreten und mutige Strategien sowie Wettbewerbsvorteile zu betonen. Bei der Bewertung der Entscheidung oder des Plans des Händlers konzentrieren Sie sich intensiv auf das potenzielle Aufwärtspotenzial, Wachstumspotenzial und innovative Vorteile – selbst wenn diese mit erhöhtem Risiko einhergehen. Nutzen Sie die bereitgestellten Marktdaten und Sentiment-Analysen, um Ihre Argumente zu stärken und gegensätzliche Ansichten herauszufordern. Reagieren Sie speziell direkt auf jeden Punkt der konservativen und neutralen Analysten, indem Sie mit datengestützten Widerlegungen und überzeugender Argumentation kontern. Heben Sie hervor, wo ihre Vorsicht kritische Chancen verpassen könnte oder wo ihre Annahmen übermäßig konservativ sein könnten. Hier ist die Entscheidung des Händlers:

{trader_decision}

Ihre Aufgabe ist es, einen überzeugenden Fall für die Entscheidung des Händlers zu erstellen, indem Sie die konservativen und neutralen Haltungen hinterfragen und kritisieren, um zu demonstrieren, warum Ihre Hochrendite-Perspektive den besten Weg nach vorne bietet. Integrieren Sie Erkenntnisse aus den folgenden Quellen in Ihre Argumente:

Marktforschungsbericht: {market_research_report}
Social-Media-Sentiment-Bericht: {sentiment_report}
Aktueller Weltgeschehensbericht: {news_report}
Unternehmensfundamentalbericht: {fundamentals_report}
Hier ist der aktuelle Gesprächsverlauf: {history} Hier sind die letzten Argumente des konservativen Analysten: {current_safe_response} Hier sind die letzten Argumente des neutralen Analysten: {current_neutral_response}. Wenn es keine Antworten von den anderen Standpunkten gibt, halluzinieren Sie nicht und präsentieren Sie einfach Ihren Punkt.

Engagieren Sie sich aktiv, indem Sie auf spezifische Bedenken eingehen, Schwächen in ihrer Logik widerlegen und die Vorteile der Risikobereitschaft betonen, um Marktnormen zu übertreffen. Konzentrieren Sie sich auf Debattieren und Überzeugen, nicht nur auf das Präsentieren von Daten. Fordern Sie jeden Gegenpunkt heraus, um zu unterstreichen, warum ein hochriskanter Ansatz optimal ist. Geben Sie gesprächig aus, als würden Sie sprechen, ohne spezielle Formatierung."""

        response = llm.invoke(prompt)

        argument = f"Risky Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risky_history + "\n" + argument,
            "safe_history": risk_debate_state.get("safe_history", ""),
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Risky",
            "current_risky_response": argument,
            "current_safe_response": risk_debate_state.get("current_safe_response", ""),
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return risky_node
