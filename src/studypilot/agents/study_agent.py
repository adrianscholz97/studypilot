from typing import Annotated, TypedDict

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, AnyMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph

SYSTEM_PROMPT = """Du bist StudyPilot, ein Organisationsassistent für ein Fernstudium.
Du verwaltest Module und Deadlines (Einsendeaufgaben, Klausuren) mit deinen Tools.

Regeln:
- Nutze immer deine Tools, statt Daten zu raten oder zu erfinden.
- Rufe get_today auf, bevor du mit relativen Zeitangaben wie "nächste Woche" rechnest.
- Wenn ein Tool einen Fehler meldet, versuche das Problem zu lösen oder frag nach.
- Antworte auf Deutsch, knapp und freundlich."""


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


def build_study_agent(llm: BaseChatModel, tools: list[BaseTool]) -> CompiledStateGraph:
    llm_with_tools = llm.bind_tools(tools)
    tools_by_name = {t.name: t for t in tools}

    def call_model(state: AgentState) -> dict:
        messages = [SystemMessage(SYSTEM_PROMPT), *state["messages"]]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def call_tools(state: AgentState) -> dict:
        last_message = state["messages"][-1]
        results = []
        for call in last_message.tool_calls:
            tool = tools_by_name.get(call["name"])
            if tool is None:
                content = f"Fehler: Ein Tool namens '{call['name']}' gibt es nicht."
            else:
                try:
                    content = tool.invoke(call["args"])
                except Exception as exc:
                    content = f"Fehler beim Ausführen von {call['name']}: {exc}"
            results.append(ToolMessage(content=str(content), tool_call_id=call["id"]))
        return {"messages": results}

    def should_continue(state: AgentState) -> str:
        last_message = state["messages"][-1]
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            return "tools"
        return END

    graph = StateGraph(AgentState)
    graph.add_node("model", call_model)
    graph.add_node("tools", call_tools)
    graph.add_edge(START, "model")
    graph.add_conditional_edges("model", should_continue, ["tools", END])
    graph.add_edge("tools", "model")
    return graph.compile()