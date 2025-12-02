import functools
import time
import json


def create_trader(llm, memory):
    def trader_node(state, name):
        company_name = state["company_of_interest"]
        investment_plan = state["investment_plan"]
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        if past_memories:
            for i, rec in enumerate(past_memories, 1):
                past_memory_str += rec["recommendation"] + "\n\n"
        else:
            past_memory_str = "No past memories found."

        context = {
            "role": "user",
            "content": f"Basierend auf einer umfassenden Analyse durch ein Team von Analysten, hier ist ein Investitionsplan, der auf {company_name} zugeschnitten ist. Dieser Plan integriert Erkenntnisse aus aktuellen technischen Markttrends, makroökonomischen Indikatoren und Social-Media-Stimmung. Verwenden Sie diesen Plan als Grundlage für die Bewertung Ihrer nächsten Handelsentscheidung.\n\nVorgeschlagener Investitionsplan: {investment_plan}\n\nNutzen Sie diese Erkenntnisse, um eine informierte und strategische Entscheidung zu treffen.",
        }

        messages = [
            {
                "role": "system",
                "content": f"""Sie sind ein Trading-Agent, der Marktdaten analysiert, um Investitionsentscheidungen zu treffen. Geben Sie basierend auf Ihrer Analyse eine spezifische Empfehlung zum Kaufen, Verkaufen oder Halten ab. Beenden Sie mit einer festen Entscheidung und schließen Sie Ihre Antwort immer mit 'FINALER TRANSAKTIONSVORSCHLAG: **KAUFEN/HALTEN/VERKAUFEN**' ab, um Ihre Empfehlung zu bestätigen. Vergessen Sie nicht, Lektionen aus vergangenen Entscheidungen zu nutzen, um aus Ihren Fehlern zu lernen. Hier sind einige Reflexionen aus ähnlichen Situationen, in denen Sie gehandelt haben, und die gelernten Lektionen: {past_memory_str}""",
            },
            context,
        ]

        result = llm.invoke(messages)

        return {
            "messages": [result],
            "trader_investment_plan": result.content,
            "sender": name,
        }

    return functools.partial(trader_node, name="Trader")
