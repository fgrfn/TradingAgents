from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.agents.utils.agent_utils import get_news, get_global_news
from tradingagents.dataflows.config import get_config


def create_news_analyst(llm):
    def news_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        tools = [
            get_news,
            get_global_news,
        ]

        system_message = (
            "Sie sind ein Nachrichtenforscher mit der Aufgabe, aktuelle Nachrichten und Trends der letzten Woche zu analysieren. Bitte schreiben Sie einen umfassenden Bericht über den aktuellen Zustand der Welt, der für Trading und Makroökonomie relevant ist. Verwenden Sie die verfügbaren Tools: get_news(query, start_date, end_date) für unternehmensspezifische oder gezielte Nachrichtensuchen, und get_global_news(curr_date, look_back_days, limit) für breitere makroökonomische Nachrichten. Sagen Sie nicht einfach, die Trends seien gemischt, sondern liefern Sie detaillierte und feingranulare Analysen und Einblicke, die Händlern bei Entscheidungen helfen können."
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
                    "Zu Ihrer Information, das aktuelle Datum ist {current_date}. Wir betrachten das Unternehmen {ticker}",
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
            "news_report": report,
        }

    return news_analyst_node
