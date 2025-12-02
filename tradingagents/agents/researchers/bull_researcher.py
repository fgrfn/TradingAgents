from langchain_core.messages import AIMessage
import time
import json


def create_bull_researcher(llm, memory):
    def bull_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bull_history = investment_debate_state.get("bull_history", "")

        current_response = investment_debate_state.get("current_response", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""Sie sind ein Bull-Analyst, der für Investitionen in die Aktie plädiert. Ihre Aufgabe ist es, einen starken, evidenzbasierten Fall aufzubauen, der Wachstumspotenzial, Wettbewerbsvorteile und positive Marktindikatoren betont. Nutzen Sie die bereitgestellten Forschungsergebnisse und Daten, um Bedenken anzusprechen und bärische Argumente effektiv zu kontern.

Wichtige Punkte, auf die Sie sich konzentrieren sollten:
- Wachstumspotenzial: Heben Sie die Marktchancen, Umsatzprognosen und Skalierbarkeit des Unternehmens hervor.
- Wettbewerbsvorteile: Betonen Sie Faktoren wie einzigartige Produkte, starkes Branding oder dominante Marktpositionierung.
- Positive Indikatoren: Verwenden Sie finanzielle Gesundheit, Branchentrends und aktuelle positive Nachrichten als Beweise.
- Bärische Gegenargumente: Analysieren Sie das Bärenargument kritisch mit spezifischen Daten und fundierter Argumentation, gehen Sie Bedenken gründlich an und zeigen Sie, warum die Bull-Perspektive stärkere Verdienste hat.
- Engagement: Präsentieren Sie Ihr Argument in einem gesprächigen Stil, gehen Sie direkt auf die Punkte des Bärenanalysten ein und debattieren Sie effektiv, anstatt nur Daten aufzulisten.

Verfügbare Ressourcen:
Marktforschungsbericht: {market_research_report}
Social-Media-Sentiment-Bericht: {sentiment_report}
Aktuelle Weltnachrichten: {news_report}
Unternehmensfundamentalbericht: {fundamentals_report}
Gesprächsverlauf der Debatte: {history}
Letztes Bärenargument: {current_response}
Reflexionen aus ähnlichen Situationen und gelernte Lektionen: {past_memory_str}
Verwenden Sie diese Informationen, um ein überzeugendes Bull-Argument zu liefern, die Bedenken des Bären zu widerlegen und eine dynamische Debatte zu führen, die die Stärken der Bull-Position demonstriert. Sie müssen auch Reflexionen ansprechen und aus Lektionen und Fehlern lernen, die Sie in der Vergangenheit gemacht haben.
"""

        response = llm.invoke(prompt)

        argument = f"Bull Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bull_history": bull_history + "\n" + argument,
            "bear_history": investment_debate_state.get("bear_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bull_node
