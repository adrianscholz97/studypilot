import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from studypilot.models import Deadline, Module

SCHEMA = """
CREATE TABLE IF NOT EXISTS modules (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    code     TEXT NOT NULL UNIQUE,
    name     TEXT NOT NULL,
    semester TEXT
);
CREATE TABLE IF NOT EXISTS deadlines (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    module_code TEXT NOT NULL REFERENCES modules(code),
    title       TEXT NOT NULL,
    due_date    TEXT NOT NULL,
    kind        TEXT NOT NULL,
    done        INTEGER NOT NULL DEFAULT 0
);
"""


class StudyRepository:
    """Kapselt jeden Datenbankzugriff für Module und Deadlines"""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = str(db_path)
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    @contextmanager
    def _connect(self) -> Generator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            with conn:  # commit bei Erfolg, rollback bei Fehler
                yield conn
        finally:
            conn.close()

    # --- Module ---------------------------------------------------------

    def add_module(self, module: Module) -> Module:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO modules (code, name, semester) VALUES (?, ?, ?)",
                (module.code, module.name, module.semester),
            )
            new_id = cur.lastrowid
        return module.model_copy(update={"id": new_id})

    def list_modules(self) -> list[Module]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM modules ORDER BY code").fetchall()
        return [Module(**dict(row)) for row in rows]

    # --- Deadlines ------------------------------------------------------

    def add_deadline(self, deadline: Deadline) -> Deadline:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO deadlines (module_code, title, due_date, kind, done) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    deadline.module_code,
                    deadline.title,
                    deadline.due_date.isoformat(),
                    deadline.kind,
                    int(deadline.done),
                ),
            )
            new_id = cur.lastrowid
        return deadline.model_copy(update={"id": new_id})

    def list_deadlines(self, include_done: bool = False) -> list[Deadline]:
        query = "SELECT * FROM deadlines"
        if not include_done:
            query += " WHERE done = 0"
        query += " ORDER BY due_date"
        with self._connect() as conn:
            rows = conn.execute(query).fetchall()
        return [Deadline(**dict(row)) for row in rows]

    def mark_done(self, deadline_id: int) -> bool:
        with self._connect() as conn:
            cur = conn.execute("UPDATE deadlines SET done = 1 WHERE id = ?", (deadline_id,))
            changed = cur.rowcount > 0
        return changed