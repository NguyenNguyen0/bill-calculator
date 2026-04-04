from __future__ import annotations

from rich.box import ROUNDED, SIMPLE
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from bills_calculator.core.models import BillsData, Person


# ─── Money helper ────────────────────────────────────────────────────────────

def fmt(amount: float) -> str:
    return f"{amount:,.0f}"


# ─── Context summary panel ────────────────────────────────────────────────────

def build_context_panel(
    year: int,
    month: int,
    electricity: float,
    water: float,
    algorithm: str,
    people: list[Person],
) -> Panel:
    algo_label = {"ratio": "Tỷ lệ", "stair": "Bậc thang", "equal": "Bình quân"}.get(algorithm, algorithm)

    text = Text()
    text.append(f"Tháng {month}/{year}", style="bold #61AFEF")
    text.append("  ·  ")
    text.append("Điện ", style="dim")
    text.append(f"{fmt(electricity)} đ", style="bold #E5C07B")
    text.append("  ·  ")
    text.append("Nước ", style="dim")
    text.append(f"{fmt(water)} đ", style="bold #56B6C2")
    text.append("  ·  ")
    text.append("Thuật toán ", style="dim")
    text.append(algo_label, style="bold #C678DD")
    text.append(f"  ·  {len(people)} người", style="dim")

    return Panel(text, border_style="#3E4451", padding=(0, 1))


# ─── People table ─────────────────────────────────────────────────────────────

def build_people_table(people: list[Person]) -> Panel:
    if not people:
        return Panel(
            Text("Chưa có người nào. Dùng /add <tên> <ngày> để thêm.", style="dim italic"),
            title="[bold #61AFEF]Danh sách người[/]",
            border_style="#3E4451",
            padding=(0, 1),
        )

    table = Table(box=SIMPLE, show_header=True, header_style="bold #61AFEF", padding=(0, 1))
    table.add_column("#", justify="right", style="dim", width=4)
    table.add_column("Tên", style="bold #ABB2BF")
    table.add_column("Ngày ở", justify="right", style="#E5C07B")

    for i, p in enumerate(people, 1):
        table.add_row(str(i), p.name, str(p.stay_days))

    return Panel(table, title="[bold #61AFEF]Danh sách người[/]", border_style="#3E4451", padding=(0, 1))


# ─── Result panel ─────────────────────────────────────────────────────────────

def build_result_renderable(bills_data: BillsData) -> Panel:
    people = bills_data.people
    algo_label = {"ratio": "Tỷ Lệ", "stair": "Bậc Thang", "equal": "Bình Quân"}.get(
        bills_data.algorithm, bills_data.algorithm
    )

    table = Table(show_header=True, header_style="bold #61AFEF", show_lines=True, box=ROUNDED, padding=(0, 1))
    table.add_column("#",       justify="right",  width=4)
    table.add_column("Tên",     style="bold #ABB2BF")
    table.add_column("Ngày ở",  justify="right",  style="#E5C07B",  width=8)
    table.add_column("Điện ⚡",  justify="right",  style="#56B6C2",  width=18)
    table.add_column("Nước 💧",  justify="right",  style="#98C379",  width=18)
    table.add_column("Tổng 💰",  justify="right",  style="bold #E5C07B", width=18)

    elec_sum  = 0.0
    water_sum = 0.0
    for i, p in enumerate(people, 1):
        total = p.elec + p.water
        elec_sum  += p.elec
        water_sum += p.water
        table.add_row(str(i), p.name, str(p.stay_days),
                      f"{fmt(p.elec)} đ", f"{fmt(p.water)} đ", f"{fmt(total)} đ")

    title = Text()
    title.append(f"Tháng {bills_data.month}/{bills_data.year}", style="bold #61AFEF")
    title.append(f"  ·  {algo_label}", style="bold #C678DD")

    footer = Text()
    footer.append("Tổng điện thu: ", style="dim")
    footer.append(f"{fmt(elec_sum)} đ", style="#56B6C2")
    footer.append("   Tổng nước thu: ", style="dim")
    footer.append(f"{fmt(water_sum)} đ", style="#98C379")

    from rich.console import Group
    return Panel(Group(table, footer), title=title, border_style="#61AFEF", padding=(0, 1))


# ─── Plain text for clipboard ─────────────────────────────────────────────────

def build_plain_result(bills_data: BillsData) -> str:
    lines = [
        f"Bills Calculator — Tháng {bills_data.month} Năm {bills_data.year}",
        f"Thuật toán: {bills_data.algorithm}",
        "",
        f"{'Tên':<20}{'Ngày':>8}{'Điện':>15}{'Nước':>15}{'Tổng':>15}",
        "-" * 73,
    ]
    for p in bills_data.people:
        total = p.elec + p.water
        lines.append(f"{p.name:<20}{p.stay_days:>8}{p.elec:>15,.0f}{p.water:>15,.0f}{total:>15,.0f}")
    return "\n".join(lines)
