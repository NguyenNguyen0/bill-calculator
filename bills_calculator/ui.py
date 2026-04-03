from datetime import datetime
import time
from rich.console import Console, Group
from rich.prompt import Prompt
from rich.table import Table
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from pyfiglet import Figlet
import pyperclip
from .models import Person, BillsData


class BillsUI:
    def __init__(self):
        self.console = Console()

    def _prompt_int(self, prompt_text, default, min_value=None, max_value=None):
        while True:
            try:
                value = int(Prompt.ask(prompt_text, default=str(default)))
                if min_value is not None and value < min_value:
                    raise ValueError(f"Giá trị phải >= {min_value}.")
                if max_value is not None and value > max_value:
                    raise ValueError(f"Giá trị phải <= {max_value}.")
                return value
            except ValueError as exc:
                self.show_error(str(exc))

    def _prompt_float(self, prompt_text, default, min_value=None):
        while True:
            try:
                value = float(Prompt.ask(prompt_text, default=str(default)))
                if min_value is not None and value < min_value:
                    raise ValueError(f"Giá trị phải >= {min_value}.")
                return value
            except ValueError as exc:
                self.show_error(str(exc))

    def clear(self):
        self.console.clear()

    def show_title(self):
        self.console.print(Markdown("\n\n---\n\n"))
        # kban, roman, epic, slant, doom, larry3d
        figlet = Figlet(font="doom", justify="left", width=180)
        raw_title = figlet.renderText("BILLS-CALCULATOR")

        # Create gradient title
        styled_title = Text()
        lines = raw_title.splitlines()
        total_lines = len(lines)

        start_color = (0, 255, 255)  # Cyan
        end_color = (255, 0, 255)  # Magenta

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

        self.console.print(styled_title)

    def format_money(self, label, amount, label_color="white"):
        label = f"[{label_color}]{label:<40}[/{label_color}]"
        money = f"[green]{amount:>15,.0f}  VNĐ[/green]💸"
        return f"{label}{money}"

    def get_date_now(self):
        now = datetime.now()
        return now.year, now.month

    def input_month_year_and_bills(self, date_now=False):
        self.clear()
        self.show_title()

        self.console.print(Markdown(markup="# NHẬP THÁNG NĂM VÀ TIỀN ĐIỆN NƯỚC"))

        curr_year, curr_month = self.get_date_now()
        if date_now:
            year = curr_year
            month = curr_month
        else:
            self.console.print(Markdown("## Thời gian"))
            self.console.print(Markdown("> Năm"))
            year = self._prompt_int("", curr_year, min_value=2000, max_value=curr_year + 1)
            self.console.print(Markdown("> Tháng"))
            month = self._prompt_int("", curr_month, min_value=1, max_value=12)

        self.console.print(Markdown("## Hóa đơn điện nước"))
        self.console.print(Markdown("> Tổng tiền điện (VNĐ)"))
        electricity = self._prompt_float("", 0, min_value=0)
        self.console.print(Markdown("> Tổng tiền nước (VNĐ)"))
        water = self._prompt_float("", 0, min_value=0)

        return BillsData(year=year, month=month, electricity=electricity, water=water)

    def input_people_info(self):
        people = []
        while True:
            self.clear()
            self.show_title()

            self.console.print(Markdown("# NHẬP TÊN VÀ SỐ NGÀY Ở"))

            if people:
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Người", justify="left")
                table.add_column("Số Ngày Ở 🕛", justify="center")

                for person in people:
                    table.add_row(person.name, str(person.stay_days))

                self.console.print(
                    Panel(table, title="Danh sách người đã nhập", border_style="cyan")
                )
            else:
                self.console.print(Markdown("\n*Chưa có người nào được nhập.*"))

            self.console.print(Markdown("\n> Tên (hoặc gõ *Enter* để tính tiền)"))
            name = Prompt.ask("").strip()
            if name.lower() == "q" or name.lower() == "":
                if not people:
                    self.console.print(
                        Panel(
                            "[red]Không có người nào được nhập. Trở lại từ đầu...[/red]",
                            border_style="red",
                        )
                    )
                    input("Nhấn Enter để tiếp tục...")
                    continue
                break

            self.console.print(Markdown("\n> Số ngày ở"))
            stay_days = self._prompt_int("", 0, min_value=0)
            people.append(Person(name=name, stay_days=stay_days))

        return people

    def confirm(self, message, default="n"):
        choice = Prompt.ask(message, choices=["y", "n"], default=default)
        return choice == "y"

    def input_algorithm_selection(self):
        """Allow user to select calculation algorithm interactively"""
        self.console.print(Markdown("\n## Chọn thuật toán tính tiền"))
        self.console.print(Markdown("1. **Tỷ lệ** (mặc định): Chia tiền theo tỷ lệ số ngày ở"))
        self.console.print(Markdown("2. **Bậc thang**: Người ở ít nhất trả cùng mức cơ bản, phần thêm chia đều"))
        self.console.print(Markdown("3. **Bình quân**: Chia đều mỗi khoản tiền cho tất cả mọi người"))
        
        choice = Prompt.ask(
            "Chọn thuật toán",
            choices=["1", "2", "3"],
            default="1"
        )
        
        if choice == "2":
            return "stair"
        if choice == "3":
            return "equal"
        return "ratio"

    def show_algorithm_info(self, algorithm, algorithm_name):
        """Show information about the selected algorithm"""
        self.console.print(f"\n[bold cyan]Sử dụng {algorithm_name}[/bold cyan]")
        
        if algorithm == "stair":
            self.console.print("[dim]Thuật toán bậc thang: Người ở ít ngày nhất trả cùng mức cơ bản, số ngày thêm sẽ chia đều số tiền còn lại.[/dim]")
        elif algorithm == "equal":
            self.console.print("[dim]Thuật toán bình quân: Chia đều tiền điện và tiền nước cho tất cả mọi người.[/dim]")
        else:
            self.console.print("[dim]Thuật toán tỷ lệ: Chia tiền theo tỷ lệ số ngày ở của mỗi người.[/dim]")

    def display_result(self, bills_data):
        people = bills_data.people
        total_elec = bills_data.electricity
        total_water = bills_data.water
        year = bills_data.year
        month = bills_data.month
        algorithm = getattr(bills_data, 'algorithm', 'ratio')

        self.clear()
        self.show_title()

        # Show algorithm information
        algorithm_name = {
            "stair": "Bậc Thang",
            "equal": "Bình Quân",
            "ratio": "Tỷ Lệ",
        }.get(algorithm, "Tỷ Lệ")
        self.console.print(f"[bold cyan]Thuật toán: {algorithm_name}[/bold cyan]")

        self.console.print(Markdown(f"# THÁNG {month} NĂM {year}"))

        table = Table(show_header=True, header_style="bold magenta", show_lines=True)
        table.add_column("ID", justify="right", style="bold")
        table.add_column("Người", justify="left", style="bold")
        if total_elec:
            table.add_column("Tiền Điện ⚡", justify="right")
        if total_water:
            table.add_column("Tiền Nước 💦", justify="right")
        table.add_column("Tổng Cộng 💰", justify="right", style="bold yellow")
        table.add_column("Số Ngày Ở 🕛", justify="center")

        for i, p in enumerate(people):
            row = [str(i + 1), p.name]
            if total_elec:
                row.append(f"{p.elec:,.0f} VNĐ")
            if total_water:
                row.append(f"{p.water:,.0f} VNĐ")
            row.append(f"[bold yellow]{(p.elec + p.water):,.0f} VNĐ[/bold yellow]")
            row.append(str(p.stay_days))
            table.add_row(*row)

        total_panel = self.show_total(
            total_elec=total_elec,
            total_elec_contrib=sum(p.elec for p in people),
            total_water=total_water,
            total_water_contrib=sum(p.water for p in people),
        )
        detail_panel = Panel(table, title="CHI TIẾT PHÂN CHIA", border_style="yellow")
        group = Group(total_panel, detail_panel)
        self.console.print(group)

    def show_total(
        self, total_elec=0, total_elec_contrib=0, total_water=0, total_water_contrib=0
    ):
        lines = []

        if total_elec:
            lines.append(self.format_money("TIỀN ĐIỆN:", total_elec))
            lines.append(self.format_money("TỔNG TIỀN ĐIỆN THU:", total_elec_contrib))
        if total_water:
            lines.append(self.format_money("TIỀN NƯỚC:", total_water))
            lines.append(self.format_money("TỔNG TIỀN NƯỚC THU:", total_water_contrib))

        panel = Panel("\n".join(lines), title="TỔNG TIỀN", border_style="yellow")
        return panel

    def show_status(self, message, action=None):
        """Show a status message with a spinner"""
        if action:
            with self.console.status(message, spinner="moon"):
                self.clear()
                self.show_title()
                result = action()
                time.sleep(1)  # Simulate calculation time
                return result
        else:
            return self.console.status(message, spinner="moon")

    def show_error(self, message):
        self.console.print("\n")
        self.console.print(
            Panel(
                f"[red]{message}[/red]",
                border_style="red",
            )
        )

    def show_success(self, message):
        self.console.print(Markdown(f"## **{message}**"), style="bold green")

    def format_result_text(self, bills_data):
        lines = []
        lines.append(f"Bills Calculator - Thang {bills_data.month} Nam {bills_data.year}")
        lines.append(f"Algorithm: {getattr(bills_data, 'algorithm', 'ratio')}")
        lines.append("")
        lines.append(f"{'Name':<20}{'Stay Days':>10}{'Elec':>15}{'Water':>15}{'Total':>15}")

        for person in bills_data.people:
            total = person.elec + person.water
            lines.append(
                f"{person.name:<20}{person.stay_days:>10}{person.elec:>15,.0f}{person.water:>15,.0f}{total:>15,.0f}"
            )

        return "\n".join(lines)

    def copy_text_to_clipboard(self, text):
        pyperclip.copy(text)
