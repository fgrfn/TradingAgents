import time
import json


def create_research_manager(llm, memory):
    def research_manager_node(state) -> dict:
        history = state["investment_debate_state"].get("history", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        investment_debate_state = state["investment_debate_state"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""Als Portfoliomanager und Debattenleiter ist es Ihre Aufgabe, diese Debattenrunde kritisch zu bewerten und eine endgültige Entscheidung zu treffen: Stimmen Sie mit dem Bärenanalysten, dem Bull-Analysten überein oder wählen Sie Halten nur, wenn dies basierend auf den präsentierten Argumenten stark gerechtfertigt ist.

Fassen Sie die wichtigsten Punkte beider Seiten prägnant zusammen und konzentrieren Sie sich auf die überzeugendsten Beweise oder Argumente. Ihre Empfehlung – Kaufen, Verkaufen oder Halten – muss klar und umsetzbar sein. Vermeiden Sie es, standardmäßig Halten zu wählen, nur weil beide Seiten gültige Punkte haben; verpflichten Sie sich auf eine Haltung, die auf den stärksten Argumenten der Debatte basiert.

Entwickeln Sie zusätzlich einen detaillierten Investitionsplan für den Händler. Dieser sollte umfassen:

Ihre Empfehlung: Eine entschiedene Haltung, die von den überzeugendsten Argumenten gestützt wird.
Begründung: Eine Erklärung, warum diese Argumente zu Ihrer Schlussfolgerung führen.
Strategische Maßnahmen: Konkrete Schritte zur Umsetzung der Empfehlung.
Berücksichtigen Sie Ihre früheren Fehler in ähnlichen Situationen. Nutzen Sie diese Erkenntnisse, um Ihre Entscheidungsfindung zu verfeinern und sicherzustellen, dass Sie lernen und sich verbessern. Präsentieren Sie Ihre Analyse gesprächig, als würden Sie natürlich sprechen, ohne spezielle Formatierung. 

Hier sind Ihre früheren Reflexionen über Fehler:
\"{past_memory_str}\"

Hier ist die Debatte:
Debattenverlauf:
{history}"""
        response = llm.invoke(prompt)

        new_investment_debate_state = {
            "judge_decision": response.content,
            "history": investment_debate_state.get("history", ""),
            "bear_history": investment_debate_state.get("bear_history", ""),
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": response.content,
            "count": investment_debate_state["count"],
        }

        return {
            "investment_debate_state": new_investment_debate_state,
            "investment_plan": response.content,
        }

    return research_manager_node
