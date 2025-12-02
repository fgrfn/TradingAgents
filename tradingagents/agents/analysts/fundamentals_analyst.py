from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.agents.utils.agent_utils import get_fundamentals, get_balance_sheet, get_cashflow, get_income_statement, get_insider_sentiment, get_insider_transactions
from tradingagents.dataflows.config import get_config


def create_fundamentals_analyst(llm):
    def fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        tools = [
            get_fundamentals,
            get_balance_sheet,
            get_cashflow,
            get_income_statement,
        ]

        system_message = (
            "Sie sind ein Forscher mit der Aufgabe, fundamentale Informationen der letzten Woche über ein Unternehmen zu analysieren. Bitte schreiben Sie einen umfassenden Bericht über die fundamentalen Informationen des Unternehmens wie Finanzdokumente, Unternehmensprofil, grundlegende Unternehmensfinanzen und Unternehmensfinanzgeschichte, um einen vollständigen Überblick über die fundamentalen Informationen des Unternehmens zu erhalten, um Händler zu informieren. Achten Sie darauf, so viele Details wie möglich einzubeziehen. Sagen Sie nicht einfach, die Trends seien gemischt, sondern liefern Sie detaillierte und feingranulare Analysen und Einblicke, die Händlern bei Entscheidungen helfen können."
            + " Fügen Sie am Ende des Berichts unbedingt eine Markdown-Tabelle hinzu, um die wichtigsten Punkte des Berichts zu organisieren, übersichtlich und leicht lesbar zu gestalten."
            + " Verwenden Sie die verfügbaren Tools: `get_fundamentals` für umfassende Unternehmensanalyse, `get_balance_sheet`, `get_cashflow` und `get_income_statement` für spezifische Finanzberichte.",
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
                    "Zu Ihrer Information, das aktuelle Datum ist {current_date}. Das Unternehmen, das wir betrachten möchten, ist {ticker}",
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
            "fundamentals_report": report,
        }

    return fundamentals_analyst_node
