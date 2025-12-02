import time
import json


def create_neutral_debator(llm):
    def neutral_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        neutral_history = risk_debate_state.get("neutral_history", "")

        current_risky_response = risk_debate_state.get("current_risky_response", "")
        current_safe_response = risk_debate_state.get("current_safe_response", "")

        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        trader_decision = state["trader_investment_plan"]

        prompt = f"""Als Neutraler Risiko-Analyst ist Ihre Aufgabe, eine ausgewogene Perspektive zu bieten und sowohl die potenziellen Vorteile als auch Risiken der Entscheidung oder des Plans des Händlers abzuwägen. Sie priorisieren einen ausgewogenen Ansatz und bewerten Vor- und Nachteile unter Berücksichtigung breiterer Markttrends, potenzieller wirtschaftlicher Verschiebungen und Diversifizierungsstrategien. Hier ist die Entscheidung des Händlers:

{trader_decision}

Ihre Aufgabe ist es, sowohl die Risiko- als auch die Sicheren Analysten herauszufordern und aufzuzeigen, wo jede Perspektive übermäßig optimistisch oder übermäßig vorsichtig sein könnte. Nutzen Sie Erkenntnisse aus den folgenden Datenquellen, um eine moderate, nachhaltige Strategie zur Anpassung der Händlerentscheidung zu unterstützen:

Marktforschungsbericht: {market_research_report}
Social-Media-Sentiment-Bericht: {sentiment_report}
Aktueller Weltgeschehensbericht: {news_report}
Unternehmensfundamentalbericht: {fundamentals_report}
Hier ist der aktuelle Gesprächsverlauf: {history} Hier ist die letzte Antwort des Risiko-Analysten: {current_risky_response} Hier ist die letzte Antwort des sicheren Analysten: {current_safe_response}. Wenn es keine Antworten von den anderen Standpunkten gibt, halluzinieren Sie nicht und präsentieren Sie einfach Ihren Punkt.

Engagieren Sie sich aktiv, indem Sie beide Seiten kritisch analysieren und Schwächen in den risikoreichen und konservativen Argumenten ansprechen, um für einen ausgewogeneren Ansatz zu plädieren. Fordern Sie jeden ihrer Punkte heraus, um zu veranschaulichen, warum eine moderate Risikostrategie möglicherweise das Beste aus beiden Welten bietet, Wachstumspotenzial bietet und gleichzeitig vor extremer Volatilität schützt. Konzentrieren Sie sich auf Debattieren statt einfach Daten zu präsentieren, mit dem Ziel zu zeigen, dass eine ausgewogene Sicht zu den zuverlässigsten Ergebnissen führen kann. Geben Sie gesprächig aus, als würden Sie sprechen, ohne spezielle Formatierung."""

        response = llm.invoke(prompt)

        argument = f"Neutral Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risk_debate_state.get("risky_history", ""),
            "safe_history": risk_debate_state.get("safe_history", ""),
            "neutral_history": neutral_history + "\n" + argument,
            "latest_speaker": "Neutral",
            "current_risky_response": risk_debate_state.get(
                "current_risky_response", ""
            ),
            "current_safe_response": risk_debate_state.get("current_safe_response", ""),
            "current_neutral_response": argument,
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return neutral_node
