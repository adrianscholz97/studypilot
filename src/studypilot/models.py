from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

DealineKind = Literal["einsendeaufgabe", "klausur", "sonstiges"]

class Module(BaseModel):
    """Ein Studienmodul"""

    id: int | None = None
    code: str = Field(description="Modulnummer, z.B. 63413")
    name: str
    semester: str | None = None

class Deadline(BaseModel):
    """Ein Termin, der zu einem Modul gehört"""

    id: int | None = None
    module_code: str
    title: str
    due_date: date
    kind: DeadlineKind = "einsendeaufgabe"
    done: bool = False