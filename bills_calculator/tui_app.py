from __future__ import annotations

from datetime import datetime
from typing import List

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    Button,
    Checkbox,
    DataTable,
    Footer,
    Header,
    Input,
    RichLog,
    Select,
    Static,
)

from .calculator import BillsCalculator
from .exporter import BillsExporter
from .history import BillsHistory
from .models import BillsData, Person
from .storage import Storage

try:
    import pyperclip
except ImportError:  # pragma: no cover - depends on runtime environment
    pyperclip = None


class BillsTextualApp(App):
    TITLE = "Bills Calculator TUI"
    SUB_TITLE = "Interactive bill sharing workspace"

    CSS = """
    Screen {
        background: #0f1218;
        color: #e9edf5;
    }

    #layout {
        height: 1fr;
    }

    #controls {
        width: 45;
        min-width: 38;
        border: tall #4f7dff;
        padding: 1;
        background: #131a25;
    }

    #outputs {
        border: tall #4f7dff;
        padding: 1;
        background: #0f141e;
    }

    #hero {
        content-align: center middle;
        height: 3;
        color: #8fc3ff;
        text-style: bold;
    }

    .section-title {
        margin: 1 0 0 0;
        color: #9ad9ff;
        text-style: bold;
    }

    Input, Select {
        margin: 0 0 1 0;
    }

    .row {
        height: auto;
        layout: horizontal;
    }

    .row > * {
        width: 1fr;
        margin-right: 1;
    }

    .row > *:last-child {
        margin-right: 0;
    }

    .button-row {
        height: auto;
        layout: horizontal;
        margin-bottom: 1;
    }

    .button-row Button {
        width: 1fr;
        margin-right: 1;
    }

    .button-row Button:last-child {
        margin-right: 0;
    }

    #people-table {
        height: 12;
        margin-bottom: 1;
    }

    #result-view {
        height: 16;
        border: round #2f4965;
        padding: 1;
        margin-bottom: 1;
    }

    #history-table {
        height: 10;
        margin-bottom: 1;
    }

    #activity-log {
        height: 1fr;
        border: round #2f4965;
    }

    #hints {
        color: #92a7c0;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("ctrl+enter", "calculate", "Calculate"),
        Binding("ctrl+s", "save_people", "Save People"),
        Binding("ctrl+l", "load_people", "Load People"),
        Binding("ctrl+e", "export_txt", "Export TXT"),
        Binding("ctrl+h", "reload_history", "Reload History"),
        Binding("ctrl+r", "reset_form", "Reset"),
        Binding("ctrl+c", "copy_result", "Copy"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.calculator = BillsCalculator()
        self.storage = Storage()
        self.exporter = BillsExporter()
        self.history = BillsHistory()
        self.people: List[Person] = []
        self.selected_person_index: int | None = None
        self.last_result: BillsData | None = None

    def compose(self) -> ComposeResult:
        now = datetime.now()
        yield Header(show_clock=True)
        with Horizontal(id="layout"):
            with Vertical(id="controls"):
                yield Static("BILLS CALCULATOR COMMAND CENTER", id="hero")

                yield Static("Bill Context", classes="section-title")
                with Horizontal(classes="row"):
                    yield Input(value=str(now.year), id="year", placeholder="Year")
                    yield Input(value=str(now.month), id="month", placeholder="Month")
                with Horizontal(classes="row"):
                    yield Input(value="0", id="electricity", placeholder="Electricity (VND)")
                    yield Input(value="0", id="water", placeholder="Water (VND)")
                yield Select(
                    options=[
                        ("Tỷ lệ (ratio)", "ratio"),
                        ("Bậc thang (stair)", "stair"),
                        ("Bình quân (equal)", "equal"),
                    ],
                    value="ratio",
                    id="algorithm",
                    prompt="Chọn thuật toán",
                )
                yield Checkbox("Lưu lịch sử sau khi tính", value=True, id="save-history")

                yield Static("People", classes="section-title")
                with Horizontal(classes="row"):
                    yield Input(id="person-name", placeholder="Tên")
                    yield Input(id="person-days", placeholder="Số ngày ở")
                with Horizontal(classes="button-row"):
                    yield Button("Thêm", id="add-person", variant="primary")
                    yield Button("Cập nhật", id="update-person")
                    yield Button("Xóa", id="delete-person", variant="error")
                yield DataTable(id="people-table", cursor_type="row")

                yield Static("File Paths", classes="section-title")
                yield Input(value="people.txt", id="people-file", placeholder="people file path")
                yield Input(value="dist/exports/bills_result.txt", id="export-file", placeholder="export file path")

                with Horizontal(classes="button-row"):
                    yield Button("Load", id="load-people")
                    yield Button("Save", id="save-people")
                with Horizontal(classes="button-row"):
                    yield Button("Tính tiền", id="calculate", variant="success")
                    yield Button("Reset", id="reset")
                with Horizontal(classes="button-row"):
                    yield Button("Export TXT", id="export-txt")
                    yield Button("Export CSV", id="export-csv")
                with Horizontal(classes="button-row"):
                    yield Button("Copy", id="copy-result")
                    yield Button("History", id="reload-history")

                yield Static("Ctrl+Enter calculate | Ctrl+S save | Ctrl+L load | Ctrl+E export | Ctrl+H history | Ctrl+C copy | Q quit", id="hints")

            with Vertical(id="outputs"):
                yield Static("Result Preview", classes="section-title")
                yield Static("Chưa có kết quả. Nhập dữ liệu và bấm Tính tiền.", id="result-view")
                yield Static("History", classes="section-title")
                yield DataTable(id="history-table")
                yield Static("Activity", classes="section-title")
                yield RichLog(id="activity-log", highlight=True, wrap=True)

        yield Footer()

    def on_mount(self) -> None:
        people_table = self.query_one("#people-table", DataTable)
        people_table.add_columns("#", "Tên", "Số ngày", "Điện", "Nước", "Tổng")

        history_table = self.query_one("#history-table", DataTable)
        history_table.add_columns("Saved At", "Month", "Year", "Algo", "People", "Elec", "Water")

        self._reload_history_table()
        self._log("App started. Ready for input.")

    def _safe_notify(self, message: str, severity: str = "information") -> None:
        try:
            self.notify(message, severity=severity)
        except Exception:
            pass

    def _log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.query_one("#activity-log", RichLog).write(f"[{timestamp}] {message}")

    def _get_input(self, widget_id: str) -> str:
        return self.query_one(f"#{widget_id}", Input).value.strip()

    def _parse_int(self, widget_id: str, label: str, min_value: int | None = None, max_value: int | None = None) -> int:
        raw = self._get_input(widget_id)
        try:
            value = int(raw)
        except ValueError as exc:
            raise ValueError(f"{label} phải là số nguyên.") from exc

        if min_value is not None and value < min_value:
            raise ValueError(f"{label} phải >= {min_value}.")
        if max_value is not None and value > max_value:
            raise ValueError(f"{label} phải <= {max_value}.")
        return value

    def _parse_float(self, widget_id: str, label: str, min_value: float | None = None) -> float:
        raw = self._get_input(widget_id)
        try:
            value = float(raw)
        except ValueError as exc:
            raise ValueError(f"{label} phải là số.") from exc

        if min_value is not None and value < min_value:
            raise ValueError(f"{label} phải >= {min_value}.")
        return value

    def _format_money(self, amount: float) -> str:
        return f"{amount:,.0f}"

    def _refresh_people_table(self, calculated_people: List[Person] | None = None) -> None:
        table = self.query_one("#people-table", DataTable)
        table.clear()

        show_people = calculated_people if calculated_people is not None else self.people
        for idx, person in enumerate(show_people, start=1):
            total = person.elec + person.water
            table.add_row(
                str(idx),
                person.name,
                str(person.stay_days),
                self._format_money(person.elec),
                self._format_money(person.water),
                self._format_money(total),
            )

    def _reload_history_table(self) -> None:
        table = self.query_one("#history-table", DataTable)
        table.clear()
        entries = self.history.load_all()

        for item in reversed(entries[-50:]):
            table.add_row(
                str(item.get("saved_at", "")),
                str(item.get("month", "")),
                str(item.get("year", "")),
                str(item.get("algorithm", "")),
                str(len(item.get("people", []))),
                self._format_money(float(item.get("electricity", 0))),
                self._format_money(float(item.get("water", 0))),
            )

    def _build_result_renderable(self, bills_data: BillsData):
        people = bills_data.people
        algorithm_name = {
            "ratio": "Tỷ Lệ",
            "stair": "Bậc Thang",
            "equal": "Bình Quân",
        }.get(bills_data.algorithm, bills_data.algorithm)

        table = Table(show_header=True, header_style="bold cyan", show_lines=True)
        table.add_column("ID", justify="right")
        table.add_column("Người")
        table.add_column("Số ngày", justify="right")
        table.add_column("Điện", justify="right")
        table.add_column("Nước", justify="right")
        table.add_column("Tổng", justify="right", style="bold yellow")

        elec_total = 0.0
        water_total = 0.0
        for idx, person in enumerate(people, start=1):
            total = person.elec + person.water
            elec_total += person.elec
            water_total += person.water
            table.add_row(
                str(idx),
                person.name,
                str(person.stay_days),
                f"{person.elec:,.0f} VNĐ",
                f"{person.water:,.0f} VNĐ",
                f"{total:,.0f} VNĐ",
            )

        summary = Text()
        summary.append(f"Tháng {bills_data.month}/{bills_data.year} | Thuật toán: {algorithm_name}\n", style="bold cyan")
        summary.append(f"Tổng điện nhập: {bills_data.electricity:,.0f} VNĐ | Thu thực tế: {elec_total:,.0f} VNĐ\n")
        summary.append(f"Tổng nước nhập: {bills_data.water:,.0f} VNĐ | Thu thực tế: {water_total:,.0f} VNĐ")

        return Panel(table, title=summary, border_style="yellow")

    def _build_plain_result(self, bills_data: BillsData) -> str:
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

    def _set_result(self, bills_data: BillsData) -> None:
        renderable = self._build_result_renderable(bills_data)
        self.query_one("#result-view", Static).update(renderable)

    def _collect_bills_input(self) -> tuple[int, int, float, float, str]:
        now_year = datetime.now().year
        year = self._parse_int("year", "Năm", min_value=2000, max_value=now_year + 1)
        month = self._parse_int("month", "Tháng", min_value=1, max_value=12)
        electricity = self._parse_float("electricity", "Tiền điện", min_value=0)
        water = self._parse_float("water", "Tiền nước", min_value=0)

        algorithm = self.query_one("#algorithm", Select).value
        if algorithm not in {"ratio", "stair", "equal"}:
            raise ValueError("Thuật toán không hợp lệ.")

        return year, month, electricity, water, algorithm

    def _run_calculation(self) -> None:
        if not self.people:
            raise ValueError("Chưa có người nào để tính tiền.")

        year, month, electricity, water, algorithm = self._collect_bills_input()

        people_for_calc = [Person(person.name, person.stay_days) for person in self.people]
        calculated_people = self.calculator.calculate_bills(
            people_for_calc,
            total_elec=electricity,
            total_water=water,
            algorithm=algorithm,
        )

        bills_data = BillsData(
            year=year,
            month=month,
            electricity=electricity,
            water=water,
            people=calculated_people,
            algorithm=algorithm,
        )

        self.last_result = bills_data
        self._set_result(bills_data)
        self._refresh_people_table(calculated_people)

        if self.query_one("#save-history", Checkbox).value:
            self.history.save(bills_data)
            self._reload_history_table()
            self._log("Calculation completed and saved to history.")
        else:
            self._log("Calculation completed.")

        self._safe_notify("Tính tiền thành công.", severity="information")

    def _add_person(self) -> None:
        name = self._get_input("person-name")
        if not name:
            raise ValueError("Tên không được để trống.")

        stay_days = self._parse_int("person-days", "Số ngày ở", min_value=0)
        self.people.append(Person(name=name, stay_days=stay_days))
        self.selected_person_index = None
        self._refresh_people_table()
        self._log(f"Added person: {name} ({stay_days} days).")

    def _update_person(self) -> None:
        if self.selected_person_index is None:
            raise ValueError("Hãy chọn một dòng trong bảng để cập nhật.")

        name = self._get_input("person-name")
        if not name:
            raise ValueError("Tên không được để trống.")

        stay_days = self._parse_int("person-days", "Số ngày ở", min_value=0)
        self.people[self.selected_person_index] = Person(name=name, stay_days=stay_days)
        self._refresh_people_table()
        self._log(f"Updated person at row {self.selected_person_index + 1}.")

    def _delete_person(self) -> None:
        if self.selected_person_index is None:
            raise ValueError("Hãy chọn một dòng trong bảng để xóa.")

        removed = self.people.pop(self.selected_person_index)
        self.selected_person_index = None
        self._refresh_people_table()
        self._log(f"Removed person: {removed.name}.")

    def _save_people(self) -> None:
        filename = self._get_input("people-file") or "people.txt"
        self.storage.save_people_info(self.people, filename=filename)
        self._log(f"People list saved to {filename}.")
        self._safe_notify("Đã lưu danh sách người.")

    def _load_people(self) -> None:
        filename = self._get_input("people-file") or "people.txt"
        self.people = self.storage.load_people_info(filename=filename)
        self.selected_person_index = None
        self._refresh_people_table()
        self._log(f"Loaded {len(self.people)} people from {filename}.")
        self._safe_notify(f"Đã tải {len(self.people)} người.")

    def _export(self, export_type: str) -> None:
        if self.last_result is None:
            raise ValueError("Chưa có kết quả để export.")

        target = self._get_input("export-file")
        if not target:
            target = (
                "dist/exports/bills_result.csv"
                if export_type == "csv"
                else "dist/exports/bills_result.txt"
            )

        if export_type == "csv" and not target.lower().endswith(".csv"):
            target = f"{target}.csv"
        if export_type == "txt" and not target.lower().endswith(".txt"):
            target = f"{target}.txt"

        if export_type == "csv":
            exported = self.exporter.export_csv(self.last_result, target)
        else:
            exported = self.exporter.export_txt(self.last_result, target)

        self._log(f"Exported result to {exported}.")
        self._safe_notify(f"Đã export: {exported}")

    def _copy_result(self) -> None:
        if self.last_result is None:
            raise ValueError("Chưa có kết quả để copy.")
        if pyperclip is None:
            raise ValueError("Clipboard chưa sẵn sàng. Hãy cài pyperclip để dùng tính năng copy.")
        pyperclip.copy(self._build_plain_result(self.last_result))
        self._log("Copied result to clipboard.")
        self._safe_notify("Đã copy kết quả vào clipboard.")

    def _reset_form(self) -> None:
        now = datetime.now()
        self.query_one("#year", Input).value = str(now.year)
        self.query_one("#month", Input).value = str(now.month)
        self.query_one("#electricity", Input).value = "0"
        self.query_one("#water", Input).value = "0"
        self.query_one("#algorithm", Select).value = "ratio"
        self.query_one("#person-name", Input).value = ""
        self.query_one("#person-days", Input).value = ""
        self.people = []
        self.selected_person_index = None
        self.last_result = None
        self._refresh_people_table()
        self.query_one("#result-view", Static).update("Chưa có kết quả. Nhập dữ liệu và bấm Tính tiền.")
        self._log("Form reset.")

    def _run_with_handling(self, action, label: str) -> None:
        try:
            action()
        except Exception as exc:
            self._log(f"{label} failed: {exc}")
            self._safe_notify(str(exc), severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        actions = {
            "add-person": (self._add_person, "Add person"),
            "update-person": (self._update_person, "Update person"),
            "delete-person": (self._delete_person, "Delete person"),
            "calculate": (self._run_calculation, "Calculate"),
            "save-people": (self._save_people, "Save people"),
            "load-people": (self._load_people, "Load people"),
            "export-txt": (lambda: self._export("txt"), "Export TXT"),
            "export-csv": (lambda: self._export("csv"), "Export CSV"),
            "copy-result": (self._copy_result, "Copy result"),
            "reload-history": (self._reload_history_table, "Reload history"),
            "reset": (self._reset_form, "Reset form"),
        }

        action = actions.get(event.button.id or "")
        if action:
            fn, label = action
            self._run_with_handling(fn, label)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.data_table.id != "people-table":
            return

        try:
            row_index = event.cursor_row
            person = self.people[row_index]
        except Exception:
            return

        self.selected_person_index = row_index
        self.query_one("#person-name", Input).value = person.name
        self.query_one("#person-days", Input).value = str(person.stay_days)

    def action_calculate(self) -> None:
        self._run_with_handling(self._run_calculation, "Calculate")

    def action_save_people(self) -> None:
        self._run_with_handling(self._save_people, "Save people")

    def action_load_people(self) -> None:
        self._run_with_handling(self._load_people, "Load people")

    def action_export_txt(self) -> None:
        self._run_with_handling(lambda: self._export("txt"), "Export TXT")

    def action_reload_history(self) -> None:
        self._run_with_handling(self._reload_history_table, "Reload history")

    def action_reset_form(self) -> None:
        self._run_with_handling(self._reset_form, "Reset form")

    def action_copy_result(self) -> None:
        self._run_with_handling(self._copy_result, "Copy result")
