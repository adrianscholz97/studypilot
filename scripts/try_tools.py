from studypilot.storage import StudyRepository
from studypilot.tools.study_tools import make_study_tools

repo = StudyRepository("studypilot.db")
tools = {t.name: t for t in make_study_tools(repo)}

# Was das LLM über ein Tool erfährt:
print(tools["add_deadline"].description)
print(tools["add_deadline"].args)
print()

# Normale Aufrufe
print(tools["get_today"].invoke({}))
print(tools["list_deadlines"].invoke({}))

# Absichtliche Fehler: Hier soll eine verständliche Meldung kommen, kein Absturz
print(tools["add_deadline"].invoke({"module_code": "99999", "title": "Test", "due_date": "2026-12-01"}))
print(tools["add_deadline"].invoke({"module_code": "12345", "title": "Test", "due_date": "1. Dezember"}))
print(tools["mark_deadline_done"].invoke({"deadline_id": 999}))

from studypilot.llm import get_llm

llm_with_tools = get_llm().bind_tools(list(tools.values()))
response = llm_with_tools.invoke("Welche Abgaben habe ich noch offen?")
print(response.tool_calls)