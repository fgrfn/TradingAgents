from langchain_core.messages import AIMessage
import time
import json


def create_bear_researcher(llm, memory):
    def bear_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bear_history = investment_debate_state.get("bear_history", "")

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

        prompt = f"""Sie sind ein Bären-Analyst, der den Fall gegen Investitionen in die Aktie vorbringt. Ihr Ziel ist es, ein gut begründetes Argument zu präsentieren, das Risiken, Herausforderungen und negative Indikatoren betont. Nutzen Sie die bereitgestellten Forschungsergebnisse und Daten, um potenzielle Nachteile hervorzuheben und bullische Argumente effektiv zu kontern.

Wichtige Punkte, auf die Sie sich konzentrieren sollten:

- Risiken und Herausforderungen: Heben Sie Faktoren wie Marktsättigung, finanzielle Instabilität oder makroökonomische Bedrohungen hervor, die die Performance der Aktie behindern könnten.
- Wettbewerbsschwächen: Betonen Sie Schwachstellen wie schwächere Marktpositionierung, nachlassende Innovation oder Bedrohungen durch Wettbewerber.
- Negative Indikatoren: Verwenden Sie Beweise aus Finanzdaten, Markttrends oder aktuellen negativen Nachrichten zur Unterstützung Ihrer Position.
- Bull-Gegenargumente: Analysieren Sie das Bull-Argument kritisch mit spezifischen Daten und fundierter Argumentation, legen Sie Schwächen oder übermäßig optimistische Annahmen offen.
- Engagement: Präsentieren Sie Ihr Argument in einem gesprächigen Stil, gehen Sie direkt auf die Punkte des Bull-Analysten ein und debattieren Sie effektiv, anstatt einfach nur Fakten aufzulisten.

Verfügbare Ressourcen:

Marktforschungsbericht: {market_research_report}
Social-Media-Sentiment-Bericht: {sentiment_report}
Aktuelle Weltnachrichten: {news_report}
Unternehmensfundamentalbericht: {fundamentals_report}
Gesprächsverlauf der Debatte: {history}
Letztes Bull-Argument: {current_response}
Reflexionen aus ähnlichen Situationen und gelernte Lektionen: {past_memory_str}
Verwenden Sie diese Informationen, um ein überzeugendes Bärenargument zu liefern, die Behauptungen des Bulls zu widerlegen und eine dynamische Debatte zu führen, die die Risiken und Schwächen einer Investition in die Aktie demonstriert. Sie müssen auch Reflexionen ansprechen und aus Lektionen und Fehlern lernen, die Sie in der Vergangenheit gemacht haben.
"""

        response = llm.invoke(prompt)

        argument = f"Bear Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bear_history": bear_history + "\n" + argument,
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bear_node
