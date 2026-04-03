import json
from datetime import datetime
from pathlib import Path


class BillsHistory:
    def __init__(self, history_path="data/history.json"):
        self.history_path = Path(history_path)

    def _ensure_parent_dir(self):
        self.history_path.parent.mkdir(parents=True, exist_ok=True)

    def load_all(self):
        if not self.history_path.exists():
            return []

        with open(self.history_path, "r", encoding="utf-8") as file_handle:
            try:
                data = json.load(file_handle)
            except json.JSONDecodeError:
                return []

        return data if isinstance(data, list) else []

    def save(self, bills_data):
        self._ensure_parent_dir()

        history = self.load_all()
        history.append(
            {
                "saved_at": datetime.now().isoformat(timespec="seconds"),
                "year": bills_data.year,
                "month": bills_data.month,
                "electricity": bills_data.electricity,
                "water": bills_data.water,
                "algorithm": bills_data.algorithm,
                "people": [person.to_dict() for person in bills_data.people],
            }
        )

        with open(self.history_path, "w", encoding="utf-8") as file_handle:
            json.dump(history, file_handle, ensure_ascii=False, indent=2)

    def get_by_month(self, year, month):
        return [
            item
            for item in self.load_all()
            if item.get("year") == year and item.get("month") == month
        ]