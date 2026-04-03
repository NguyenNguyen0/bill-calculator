from __future__ import annotations

from textual.widgets import Input


class InputParser:
    def __init__(self, owner):
        self.owner = owner

    def get_input(self, widget_id: str) -> str:
        return self.owner.query_one(f"#{widget_id}", Input).value.strip()

    def parse_int(
        self,
        widget_id: str,
        label: str,
        min_value: int | None = None,
        max_value: int | None = None,
    ) -> int:
        raw = self.get_input(widget_id)
        try:
            value = int(raw)
        except ValueError as exc:
            raise ValueError(f"{label} phải là số nguyên.") from exc

        if min_value is not None and value < min_value:
            raise ValueError(f"{label} phải >= {min_value}.")
        if max_value is not None and value > max_value:
            raise ValueError(f"{label} phải <= {max_value}.")
        return value

    def parse_float(self, widget_id: str, label: str, min_value: float | None = None) -> float:
        raw = self.get_input(widget_id)
        try:
            value = float(raw)
        except ValueError as exc:
            raise ValueError(f"{label} phải là số.") from exc

        if min_value is not None and value < min_value:
            raise ValueError(f"{label} phải >= {min_value}.")
        return value
