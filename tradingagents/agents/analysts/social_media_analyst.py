from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.agents.utils.agent_utils import get_news
from tradingagents.dataflows.config import get_config


def create_social_media_analyst(llm):
    def social_media_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        tools = [
            get_news,
        ]

        system_message = (
            "Sie sind ein Social-Media- und unternehmensspezifischer Nachrichtenforscher/Analyst mit der Aufgabe, Social-Media-Beiträge, aktuelle Unternehmensnachrichten und öffentliche Stimmung für ein bestimmtes Unternehmen in der letzten Woche zu analysieren. Sie erhalten einen Unternehmensnamen und Ihr Ziel ist es, einen umfassenden langen Bericht zu verfassen, der Ihre Analyse, Einblicke und Implikationen für Händler und Investoren über den aktuellen Zustand dieses Unternehmens detailliert beschreibt, nachdem Sie Social Media und was Menschen über dieses Unternehmen sagen betrachtet haben, Sentiment-Daten analysiert haben, was Menschen jeden Tag über das Unternehmen empfinden, und aktuelle Unternehmensnachrichten betrachtet haben. Verwenden Sie das Tool get_news(query, start_date, end_date), um nach unternehmensspezifischen Nachrichten und Social-Media-Diskussionen zu suchen. Versuchen Sie, alle möglichen Quellen von Social Media über Sentiment bis zu Nachrichten zu betrachten. Sagen Sie nicht einfach, die Trends seien gemischt, sondern liefern Sie detaillierte und feingranulare Analysen und Einblicke, die Händlern bei Entscheidungen helfen können."
            + """ Fügen Sie am Ende des Berichts unbedingt eine Markdown-Tabelle hinzu, um die wichtigsten Punkte des Berichts zu organisieren, übersichtlich und leicht lesbar zu gestalten.""",
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
                    "Zu Ihrer Information, das aktuelle Datum ist {current_date}. Das aktuelle Unternehmen, das wir analysieren möchten, ist {ticker}",
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
            "sentiment_report": report,
        }

    return social_media_analyst_node
