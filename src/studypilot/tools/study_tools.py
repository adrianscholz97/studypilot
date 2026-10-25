import sqlite3
from datetime import date

from langchain_core.tools import BaseTool, tool

from studypilot.models import Deadline, DeadlineKind, Module
from studypilot.storage import StudyRepository


def make_study_tools(repo: StudyRepository) -> list[BaseTool]:
    """Erzeugt die Tools des Agenten, gebunden an ein konkretes Repository."""

    @tool
    def get_today() -> str:
        """Gibt das heutige Datum zurück. Nutze dieses Tool immer, bevor du mit
        relativen Zeitangaben wie 'morgen' oder 'nächste Woche' rechnest."""
        today = date.today()
        return f"Heute ist {today:%A}, der {today.isoformat()}."

    @tool
    def list_modules() -> str:
        """Listet alle gespeicherten Studienmodule auf."""
        modules = repo.list_modules()
        if not modules:
            return "Es sind noch keine Module gespeichert."
        lines = []
        for m in modules:
            semester = f" ({m.semester})" if m.semester else ""
            lines.append(f"- {m.code}: {m.name}{semester}")
        return "\n".join(lines)

    @tool
    def add_module(code: str, name: str, semester: str | None = None) -> str:
        """Legt ein neues Studienmodul an.
        code: Modulnummer, z. B. '63413'. name: Name des Moduls.
        semester: optional, z. B. 'WS 2026/27'."""
        try:
            saved = repo.add_module(Module(code=code, name=name, semester=semester))
        except sqlite3.IntegrityError:
            return f"Fehler: Ein Modul mit der Nummer {code} existiert bereits."
        return f"Modul {saved.code} ({saved.name}) wurde angelegt."

    @tool
    def add_deadline(
        module_code: str,
        title: str,
        due_date: str,
        kind: DeadlineKind = "einsendeaufgabe",
    ) -> str:
        """Legt eine neue Deadline für ein bestehendes Modul an.
        module_code: Modulnummer eines vorhandenen Moduls.
        title: kurze Beschreibung, z. B. 'Einsendeaufgabe 2'.
        due_date: Fälligkeitsdatum im Format JJJJ-MM-TT.
        kind: Art des Termins."""
        try:
            parsed_date = date.fromisoformat(due_date)
        except ValueError:
            return f"Fehler: '{due_date}' ist kein gültiges Datum. Nutze das Format JJJJ-MM-TT."
        try:
            saved = repo.add_deadline(
                Deadline(module_code=module_code, title=title, due_date=parsed_date, kind=kind)
            )
        except sqlite3.IntegrityError:
            return (
                f"Fehler: Das Modul {module_code} existiert nicht. "
                "Prüfe mit list_modules oder lege es zuerst an."
            )
        return f"Deadline '{saved.title}' am {saved.due_date.isoformat()} angelegt (ID {saved.id})."

    @tool
    def list_deadlines(include_done: bool = False) -> str:
        """Listet Deadlines chronologisch auf. Standardmäßig nur offene,
        mit include_done=True auch erledigte."""
        deadlines = repo.list_deadlines(include_done=include_done)
        if not deadlines:
            return "Keine Deadlines gefunden."
        lines = []
        for d in deadlines:
            status = "erledigt" if d.done else "offen"
            lines.append(
                f"- [ID {d.id}] {d.due_date.isoformat()} | {d.module_code} | "
                f"{d.title} ({d.kind}, {status})"
            )
        return "\n".join(lines)

    @tool
    def mark_deadline_done(deadline_id: int) -> str:
        """Markiert eine Deadline als erledigt. Die ID liefert list_deadlines."""
        if repo.mark_done(deadline_id):
            return f"Deadline {deadline_id} ist als erledigt markiert."
        return f"Fehler: Keine Deadline mit ID {deadline_id} gefunden."

    return [get_today, list_modules, add_module, add_deadline, list_deadlines, mark_deadline_done]