import math
import time
from typing import List
import typer
from rich.console import Console, Group
from rich.prompt import Prompt
from rich.table import Table
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from datetime import datetime
from pyfiglet import Figlet

console = Console()
app = typer.Typer()


def round_money(amount):
    return math.ceil(int(amount) / 100) * 100


def format_money(label, amount, label_color="white"):
    label = f"[{label_color}]{label:<40}[/{label_color}]"
    money = f"[green]{amount:>15,.0f}  VNĐ[/green]"
    return f"{label}{money}"


def get_date_now():
    now = datetime.now()
    return now.year, now.month


def show_title():
    # roman, kban, fender
    figlet = Figlet(font="roman", justify="left", width=230)
    raw_title = figlet.renderText("BILLS-CALCULATOR")

    styled_title = Text()
    lines = raw_title.splitlines()
    total_lines = len(lines)
    
    start_color = (0, 255, 255)    # Cyan
    end_color = (255, 0, 255)      # Magenta
    
    for i, line in enumerate(lines):
        if total_lines > 1:
            ratio = i / (total_lines - 1)
            r = int(start_color[0] + ratio * (end_color[0] - start_color[0]))
            g = int(start_color[1] + ratio * (end_color[1] - start_color[1]))
            b = int(start_color[2] + ratio * (end_color[2] - start_color[2]))
            color = f"rgb({r},{g},{b})"
        else:
            color = "rgb(128, 128, 255)"
            
        styled_title.append(line + "\n", style=f"bold {color}")

    console.print(styled_title)


def parse_people(people):
    result = []
    for item in people:
        if "=" in item:
            try:
                name, days = item.split("=")
                result.append({"name": name.strip(), "days_off": int(days)})
            except ValueError:
                typer.echo(f"[❌] Sai định dạng: {item}. Dùng tên=ngày hoặc chỉ tên.")
                raise typer.Exit(code=1)
        else:
            result.append({"name": item.strip(), "days_off": 0})

    typer.echo("👥 Danh sách người + ngày nghỉ:")
    return result

def input_month_year_and_bills(date_now=False):
    console.clear()
    show_title()

    console.print(Markdown(markup="# NHẬP THÁNG NĂM VÀ TIỀN ĐIỆN NƯỚC"))

    curr_year, curr_month = get_date_now()
    if date_now:
        year = curr_year
        month = curr_month
    else:
        console.print(Markdown("## Thời gian"))
        console.print(Markdown("> Năm"))
        year = int(Prompt.ask("", default=str(curr_year)))
        console.print(Markdown("> Tháng"))
        month = int(Prompt.ask("", default=str(curr_month)))

    console.print(Markdown("## Hóa đơn điện nước"))
    console.print(Markdown("> Tổng tiền điện (VNĐ)"))
    electricity = float(Prompt.ask("", default="0"))
    console.print(Markdown("> Tổng tiền nước (VNĐ)"))
    water = float(Prompt.ask("", default="0"))

    return year, month, electricity, water


def input_people_info():
    people = []
    while True:
        console.clear()
        show_title()

        console.print(Markdown("# NHẬP TÊN VÀ SỐ NGÀY NGHỈ"))

        if people:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Người", justify="left")
            table.add_column("Số Ngày Nghỉ 🕛", justify="center")

            for person in people:
                table.add_row(person["name"], str(person["days_off"]))

            console.print(
                Panel(table, title="Danh sách người đã nhập", border_style="cyan")
            )
        else:
            console.print(Markdown("\n*Chưa có người nào được nhập.*"))

        console.print(Markdown("\n> Tên (hoặc gõ *Enter* để tính tiền)"))
        name = Prompt.ask("").strip()
        if name.lower() == "q" or name.lower() == "":
            if not people:
                console.print(
                    Panel(
                        "[red]Không có người nào được nhập. Trở lại từ đầu...[/red]",
                        border_style="red",
                    )
                )
                input("Nhấn Enter để tiếp tục...")
                continue
            break

        console.print(Markdown("\n> Số ngày nghỉ"))
        days_off = int(Prompt.ask("", default="0"))
        people.append({"name": name, "days_off": days_off})

    return people


def save_people_info(people, filename="people_info.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        for person in people:
            f.write(f"{person['name']}\n")


def load_people_info(filename="people_info.txt"):
    people = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and "=" in line:
                    name, days_off = line.split("=")
                    people.append({"name": name, "days_off": int(days_off)})
                elif line:
                    people.append({"name": line, "days_off": 0})
    except FileNotFoundError:
        return []
    return people

def calculate_bills(people, total_elec, total_water):
    for p in people:
        p["stay_days"] = 30 - p["days_off"]
    total_stay_days = sum(p["stay_days"] for p in people)
    for p in people:
        ratio = p["stay_days"] / total_stay_days if total_stay_days > 0 else 0
        p["elec"] = round_money(total_elec * ratio) if total_elec else 0
        p["water"] = round_money(total_water * ratio) if total_water else 0
    return people


def display_result(year, month, people, total_elec, total_water):
    console.clear()
    show_title()

    console.print(Markdown(f"# KẾT QUẢ THÁNG {month} NĂM {year}"))

    table = Table(show_header=True, header_style="bold magenta", show_lines=True)
    table.add_column("Người", justify="left", style="bold")
    if total_elec:
        table.add_column("Tiền Điện ⚡", justify="right")
    if total_water:
        table.add_column("Tiền Nước 💦", justify="right")
    table.add_column("Số Ngày Ở 🕛", justify="center")

    for p in people:
        row = [p["name"]]
        if total_elec:
            row.append(f"{p['elec']:,.0f} VNĐ")
        if total_water:
            row.append(f"{p['water']:,.0f} VNĐ")
        row.append(str(p["stay_days"]))
        table.add_row(*row)

    total_panel = show_total(
        total_elec=total_elec,
        total_elec_contrib=sum(p["elec"] for p in people),
        total_water=total_water,
        total_water_contrib=sum(p["water"] for p in people),
    )
    detail_panel = Panel(table, title="CHI TIẾT PHÂN CHIA", border_style="yellow")
    group = Group(total_panel, detail_panel)
    console.print(group)

    console.print(Markdown("> Nhấn **Q** để quay lại hoặc **Ctrl+C** để thoát."))
    Prompt.ask("")


def show_total(
    total_elec=0, total_elec_contrib=0, total_water=0, total_water_contrib=0
):
    lines = []

    if total_elec:
        lines.append(format_money("TIỀN ĐIỆN:", total_elec))
        lines.append(format_money("TỔNG TIỀN ĐIỆN THU:", total_elec_contrib))
    if total_water:
        lines.append(format_money("TIỀN NƯỚC:", total_water))
        lines.append(format_money("TỔNG TIỀN NƯỚC THU:", total_water_contrib))

    panel = Panel("\n".join(lines), title="TỔNG TIỀN", border_style="yellow")
    return panel


@app.command("main")
def run(
    date_now: bool = typer.Option(False, "--date-now", "-dn", help="Sử dụng ngày hiện tại"),
    month: int = typer.Option(None, "--month", "-m", help="Tháng tính tiền"),
    year: int = typer.Option(None, "--year", "-y", help="Năm tính tiền"),
    electric_bill: float = typer.Option(0, "--electric-bill", "-e", help="Tiền điện (VNĐ)"),
    water_bill: float = typer.Option(0, "--water-bill", "-w", help="Tiền nước (VNĐ)"),
    people: List[str] = typer.Option(None, "--people", "-p", help="Danh sách tên hoặc tên=ngày nghỉ"),
    load_file: str = typer.Option(None, "--load-file", "-lf", help="Tải danh sách người từ file"),
    save_file: str = typer.Option(None, "--save-file", "-sf", help="Lưu danh sách người vào file"),
):
    try:
        while True:
            if not electric_bill and not water_bill:
                year, month, electric_bill, water_bill = input_month_year_and_bills(
                    date_now=date_now
                )

            if load_file:
                people = load_people_info(load_file)
                if not people:
                    console.print(
                        Panel(
                            "[red]Không có người nào được tải từ file.[/red]",
                            border_style="red",
                        )
                    )
                    return
            elif not people:
                people = input_people_info()
            else:
                people = parse_people(people)

            with console.status("Caculating bills...", spinner="moon"):
                console.clear()
                show_title()
                calculated = calculate_bills(people, electric_bill, water_bill)
                time.sleep(1)

            if date_now:
                year, month = get_date_now()
                display_result(year, month, calculated, electric_bill, water_bill)
            else:
                display_result(year, month, calculated, electric_bill, water_bill)

    except KeyboardInterrupt:
        if save_file:
            save_people_info(people, save_file)
            console.print(Markdown("## **Đã lưu danh sách người vào file!**"), style="bold green")

        console.print(Markdown("## **Chương trình đã thoát!**"), style="bold red")


if __name__ == "__main__":
    app()
