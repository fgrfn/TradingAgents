import time
import json


def create_risk_manager(llm, memory):
    def risk_manager_node(state) -> dict:

        company_name = state["company_of_interest"]

        history = state["risk_debate_state"]["history"]
        risk_debate_state = state["risk_debate_state"]
        market_research_report = state["market_report"]
        news_report = state["news_report"]
        fundamentals_report = state["news_report"]
        sentiment_report = state["sentiment_report"]
        trader_plan = state["investment_plan"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""Als Risikomanagement-Richter und Debattenleiter ist es Ihr Ziel, die Debatte zwischen drei Risikoanalysten – Risikoreich, Neutral und Sicher/Konservativ – zu bewerten und den besten Handlungsweg für den Händler zu bestimmen. Ihre Entscheidung muss zu einer klaren Empfehlung führen: Kaufen, Verkaufen oder Halten. Wählen Sie Halten nur, wenn dies durch spezifische Argumente stark gerechtfertigt ist, nicht als Rückfallebene, wenn alle Seiten gültig erscheinen. Streben Sie nach Klarheit und Entscheidungsfreudigkeit.

Richtlinien für die Entscheidungsfindung:
1. **Zusammenfassung der Schlüsselargumente**: Extrahieren Sie die stärksten Punkte jedes Analysten und konzentrieren Sie sich auf die Relevanz für den Kontext.
2. **Begründung liefern**: Unterstützen Sie Ihre Empfehlung mit direkten Zitaten und Gegenargumenten aus der Debatte.
3. **Plan des Händlers verfeinern**: Beginnen Sie mit dem ursprünglichen Plan des Händlers, **{trader_plan}**, und passen Sie ihn basierend auf den Erkenntnissen der Analysten an.
4. **Aus vergangenen Fehlern lernen**: Nutzen Sie Lektionen aus **{past_memory_str}**, um frühere Fehleinschätzungen anzugehen und die Entscheidung, die Sie jetzt treffen, zu verbessern, um sicherzustellen, dass Sie keinen falschen KAUFEN/VERKAUFEN/HALTEN-Aufruf tätigen, der Geld verliert.

Ergebnisse:
- Eine klare und umsetzbare Empfehlung: Kaufen, Verkaufen oder Halten.
- Detaillierte Begründung, die in der Debatte und vergangenen Reflexionen verankert ist.

---

**Debattenverlauf der Analysten:**  
{history}

---

Konzentrieren Sie sich auf umsetzbare Erkenntnisse und kontinuierliche Verbesserung. Bauen Sie auf vergangenen Lektionen auf, bewerten Sie alle Perspektiven kritisch und stellen Sie sicher, dass jede Entscheidung bessere Ergebnisse vorantreibt."""

        response = llm.invoke(prompt)

        new_risk_debate_state = {
            "judge_decision": response.content,
            "history": risk_debate_state["history"],
            "risky_history": risk_debate_state["risky_history"],
            "safe_history": risk_debate_state["safe_history"],
            "neutral_history": risk_debate_state["neutral_history"],
            "latest_speaker": "Judge",
            "current_risky_response": risk_debate_state["current_risky_response"],
            "current_safe_response": risk_debate_state["current_safe_response"],
            "current_neutral_response": risk_debate_state["current_neutral_response"],
            "count": risk_debate_state["count"],
        }

        return {
            "risk_debate_state": new_risk_debate_state,
            "final_trade_decision": response.content,
        }

    return risk_manager_node
