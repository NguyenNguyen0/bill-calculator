from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Person:
    name: str
    stay_days: int = 0
    elec: float = 0
    water: float = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Person":
        return cls(
            name=data["name"],
            stay_days=data.get("stay_days", 0),
            elec=data.get("elec", 0),
            water=data.get("water", 0),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BillsData:
    year: int | None = None
    month: int | None = None
    electricity: float = 0
    water: float = 0
    people: list[Person] = field(default_factory=list)
    algorithm: str = "ratio"

    def to_dict(self) -> dict[str, Any]:
        return {
            "year": self.year,
            "month": self.month,
            "electricity": self.electricity,
            "water": self.water,
            "algorithm": self.algorithm,
            "people": [person.to_dict() for person in self.people],
        }
