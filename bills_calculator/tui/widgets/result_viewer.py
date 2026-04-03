from __future__ import annotations

from rich.box import ROUNDED
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from bills_calculator.core.models import BillsData


def build_result_renderable(bills_data: BillsData) -> Panel:
    people = bills_data.people
    algorithm_name = {
        "ratio": "Ty Le",
        "stair": "Bac Thang",
        "equal": "Binh Quan",
    }.get(bills_data.algorithm, bills_data.algorithm)

    table = Table(show_header=True, header_style="bold #86b2ff", show_lines=True, box=ROUNDED)
    table.add_column("ID", justify="right")
    table.add_column("Nguoi")
    table.add_column("So ngay", justify="right")
    table.add_column("Dien", justify="right")
    table.add_column("Nuoc", justify="right")
    table.add_column("Tong", justify="right", style="bold yellow")

    elec_total = 0.0
    water_total = 0.0
    for index, person in enumerate(people, start=1):
        total = person.elec + person.water
        elec_total += person.elec
        water_total += person.water
        table.add_row(
            str(index),
            person.name,
            str(person.stay_days),
            f"{person.elec:,.0f} VND",
            f"{person.water:,.0f} VND",
            f"{total:,.0f} VND",
        )

    summary = Text()
    summary.append(f"Thang {bills_data.month}/{bills_data.year} | Thuat toan: {algorithm_name}\n", style="bold cyan")
    summary.append(f"Tong dien nhap: {bills_data.electricity:,.0f} VND | Thu thuc te: {elec_total:,.0f} VND\n")
    summary.append(f"Tong nuoc nhap: {bills_data.water:,.0f} VND | Thu thuc te: {water_total:,.0f} VND")

    return Panel(table, title=summary, border_style="yellow")


def build_plain_result(bills_data: BillsData) -> str:
    lines = [
        f"Bills Calculator - Thang {bills_data.month} Nam {bills_data.year}",
        f"Algorithm: {bills_data.algorithm}",
        "",
        f"{'Name':<20}{'Stay Days':>10}{'Elec':>15}{'Water':>15}{'Total':>15}",
    ]
    for person in bills_data.people:
        total = person.elec + person.water
        lines.append(
            f"{person.name:<20}{person.stay_days:>10}{person.elec:>15,.0f}{person.water:>15,.0f}{total:>15,.0f}"
        )

    return "\n".join(lines)
