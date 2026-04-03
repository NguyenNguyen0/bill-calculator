import csv
from pathlib import Path


class BillsExporter:
    @staticmethod
    def _ensure_parent_dir(filename):
        Path(filename).parent.mkdir(parents=True, exist_ok=True)

    def export_txt(self, bills_data, filename):
        self._ensure_parent_dir(filename)

        lines = []
        lines.append(f"Bills Calculator - THANG {bills_data.month} NAM {bills_data.year}")
        lines.append(f"Algorithm: {bills_data.algorithm}")
        lines.append("")
        lines.append(f"{'ID':<4}{'Name':<20}{'Stay Days':>10}{'Elec':>15}{'Water':>15}{'Total':>15}")

        for index, person in enumerate(bills_data.people, start=1):
            total = person.elec + person.water
            lines.append(
                f"{index:<4}{person.name:<20}{person.stay_days:>10}{person.elec:>15,.0f}{person.water:>15,.0f}{total:>15,.0f}"
            )

        with open(filename, "w", encoding="utf-8") as file_handle:
            file_handle.write("\n".join(lines) + "\n")

        return filename

    def export_csv(self, bills_data, filename):
        self._ensure_parent_dir(filename)

        with open(filename, "w", newline="", encoding="utf-8") as file_handle:
            writer = csv.writer(file_handle)
            writer.writerow(["name", "stay_days", "elec", "water", "total"])
            for person in bills_data.people:
                writer.writerow([
                    person.name,
                    person.stay_days,
                    round(person.elec, 0),
                    round(person.water, 0),
                    round(person.elec + person.water, 0),
                ])

        return filename