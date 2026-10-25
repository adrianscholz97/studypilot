from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from studypilot.agents.study_agent import build_study_agent
from studypilot.config import get_settings
from studypilot.llm import get_llm
from studypilot.storage import StudyRepository
from studypilot.tools.study_tools import make_study_tools

settings = get_settings()
repo = StudyRepository(settings.database_path)
agent = build_study_agent(get_llm(), make_study_tools(repo))

print("StudyPilot – tippe 'exit' zum Beenden.")
messages = []

while True:
    user_input = input("\nDu: ").strip()
    if user_input.lower() in {"exit", "quit"}:
        break
    if not user_input:
        continue

    messages.append(HumanMessage(user_input))
    result = agent.invoke({"messages": messages})

    # Zum Lernen: anzeigen, was der Agent zwischendurch gemacht hat
    for msg in result["messages"][len(messages):]:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for call in msg.tool_calls:
                print(f"  → Tool: {call['name']}({call['args']})")
        elif isinstance(msg, ToolMessage):
            print(f"  ← Ergebnis: {msg.content}")

    messages = result["messages"]
    print(f"\nStudyPilot: {messages[-1].content}")