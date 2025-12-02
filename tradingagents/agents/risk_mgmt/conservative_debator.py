from langchain_core.messages import AIMessage
import time
import json


def create_safe_debator(llm):
    def safe_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        safe_history = risk_debate_state.get("safe_history", "")

        current_risky_response = risk_debate_state.get("current_risky_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        trader_decision = state["trader_investment_plan"]

        prompt = f"""Als Sicherer/Konservativer Risiko-Analyst ist Ihr primäres Ziel, Vermögenswerte zu schützen, Volatilität zu minimieren und stetiges, zuverlässiges Wachstum sicherzustellen. Sie priorisieren Stabilität, Sicherheit und Risikominderung, indem Sie sorgfältig potenzielle Verluste, wirtschaftliche Abschwünge und Marktvolatilität bewerten. Bei der Bewertung der Entscheidung oder des Plans des Händlers untersuchen Sie kritisch risikoreiche Elemente und weisen darauf hin, wo die Entscheidung das Unternehmen unangemessenen Risiken aussetzen könnte und wo vorsichtigere Alternativen langfristige Gewinne sichern könnten. Hier ist die Entscheidung des Händlers:

{trader_decision}

Ihre Aufgabe ist es, aktiv den Argumenten der Risiko- und Neutralen Analysten entgegenzutreten und hervorzuheben, wo ihre Ansichten potenzielle Bedrohungen übersehen oder Nachhaltigkeit nicht priorisieren könnten. Reagieren Sie direkt auf ihre Punkte und ziehen Sie aus den folgenden Datenquellen, um einen überzeugenden Fall für eine risikoarme Anpassung der Händlerentscheidung aufzubauen:

Marktforschungsbericht: {market_research_report}
Social-Media-Sentiment-Bericht: {sentiment_report}
Aktueller Weltgeschehensbericht: {news_report}
Unternehmensfundamentalbericht: {fundamentals_report}
Hier ist der aktuelle Gesprächsverlauf: {history} Hier ist die letzte Antwort des Risiko-Analysten: {current_risky_response} Hier ist die letzte Antwort des neutralen Analysten: {current_neutral_response}. Wenn es keine Antworten von den anderen Standpunkten gibt, halluzinieren Sie nicht und präsentieren Sie einfach Ihren Punkt.

Engagieren Sie sich, indem Sie ihren Optimismus hinterfragen und die potenziellen Nachteile betonen, die sie möglicherweise übersehen haben. Gehen Sie auf jeden ihrer Gegenpunkte ein, um zu zeigen, warum eine konservative Haltung letztendlich der sicherste Weg für die Vermögenswerte des Unternehmens ist. Konzentrieren Sie sich auf das Debattieren und Kritisieren ihrer Argumente, um die Stärke einer risikoarmen Strategie gegenüber ihren Ansätzen zu demonstrieren. Geben Sie gesprächig aus, als würden Sie sprechen, ohne spezielle Formatierung."""

        response = llm.invoke(prompt)

        argument = f"Safe Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risk_debate_state.get("risky_history", ""),
            "safe_history": safe_history + "\n" + argument,
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Safe",
            "current_risky_response": risk_debate_state.get(
                "current_risky_response", ""
            ),
            "current_safe_response": argument,
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return safe_node
