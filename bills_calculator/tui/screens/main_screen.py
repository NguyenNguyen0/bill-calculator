from __future__ import annotations

from datetime import datetime

from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Checkbox, DataTable, Footer, Header, Input, Select, Static

from bills_calculator.core.calculator import BillsCalculator
from bills_calculator.core.models import BillsData, Person
from bills_calculator.data.exporter import BillsExporter
from bills_calculator.data.history import BillsHistory
from bills_calculator.data.storage import Storage
from bills_calculator.tui.screens.history_screen import HistoryScreen
from bills_calculator.tui.widgets.header import build_gradient_figlet_title
from bills_calculator.tui.widgets.input_group import InputParser
from bills_calculator.tui.widgets.result_viewer import build_plain_result, build_result_renderable

try:
    import pyperclip
except ImportError:  # pragma: no cover - depends on runtime environment
    pyperclip = None


class MainScreen(Screen):
    BINDINGS = [
        Binding("ctrl+enter", "calculate", "Calculate"),
        Binding("ctrl+s", "save_people", "Save People"),
        Binding("ctrl+l", "load_people", "Load People"),
        Binding("ctrl+e", "export_txt", "Export TXT"),
        Binding("ctrl+h", "reload_history", "Reload History"),
        Binding("ctrl+r", "reset_form", "Reset"),
        Binding("ctrl+c", "copy_result", "Copy"),
        Binding("ctrl+k", "command_palette", "Commands"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.calculator = BillsCalculator()
        self.storage = Storage()
        self.exporter = BillsExporter()
        self.history = BillsHistory()
        self.people: list[Person] = []
        self.selected_person_index: int | None = None
        self.last_result: BillsData | None = None
        self.input_parser = InputParser(self)

    def compose(self):
        now = datetime.now()
        yield Header(show_clock=True)
        with Horizontal(id="layout"):
            with Vertical(id="controls"):
                yield Static(build_gradient_figlet_title(), id="hero")

                yield Static("Bill Context", classes="section-title")
                with Horizontal(classes="row"):
                    yield Input(value=str(now.year), id="year", placeholder="Nam (VD: 2026)")
                    yield Input(value=str(now.month), id="month", placeholder="Thang (1-12)")
                with Horizontal(classes="row"):
                    yield Input(value="0", id="electricity", placeholder="Tien dien (VND)")
                    yield Input(value="0", id="water", placeholder="Tien nuoc (VND)")
                yield Select(
                    options=[
                        ("Ty le (ratio)", "ratio"),
                        ("Bac thang (stair)", "stair"),
                        ("Binh quan (equal)", "equal"),
                    ],
                    value="ratio",
                    id="algorithm",
                    prompt="Chon thuat toan",
                )
                yield Checkbox("Luu lich su sau khi tinh", value=True, id="save-history")

                yield Static("People", classes="section-title")
                with Horizontal(classes="row"):
                    yield Input(id="person-name", placeholder="Ten")
                    yield Input(id="person-days", placeholder="So ngay o")
                with Horizontal(classes="button-row"):
                    yield Button("Them", id="add-person", variant="primary")
                    yield Button("Cap nhat", id="update-person")
                    yield Button("Xoa", id="delete-person", variant="error")
                yield DataTable(id="people-table", cursor_type="row")

                yield Static("File Paths", classes="section-title")
                yield Input(value="people.txt", id="people-file", placeholder="people file path")
                yield Input(value="dist/exports/bills_result.txt", id="export-file", placeholder="export file path")

                with Horizontal(classes="button-row"):
                    yield Button("Load", id="load-people")
                    yield Button("Save", id="save-people")
                with Horizontal(classes="button-row"):
                    yield Button("Tinh tien", id="calculate", variant="success")
                    yield Button("Reset", id="reset")
                with Horizontal(classes="button-row"):
                    yield Button("Export TXT", id="export-txt")
                    yield Button("Export CSV", id="export-csv")
                with Horizontal(classes="button-row"):
                    yield Button("Copy", id="copy-result")
                    yield Button("History", id="reload-history")
                with Horizontal(classes="row"):
                    yield Input(id="command-line", placeholder="/calculate | /history | /reset | /export txt | /export csv")
                    yield Button("Run", id="run-command")

                yield Static(
                    "Ctrl+Enter calculate | Ctrl+S save | Ctrl+L load | Ctrl+E export | Ctrl+H history | Ctrl+C copy | Q quit",
                    id="hints",
                )

            with Vertical(id="outputs"):
                yield Static("Result Preview", classes="section-title")
                yield Static("Chua co ket qua. Nhap du lieu va bam Tinh tien.", id="result-view")

        yield Footer()

    def on_mount(self) -> None:
        people_table = self.query_one("#people-table", DataTable)
        people_table.add_columns("#", "Ten", "So ngay", "Dien", "Nuoc", "Tong")

    def _safe_notify(self, message: str, severity: str = "information") -> None:
        try:
            self.notify(message, severity=severity)
        except Exception:
            pass

    def _parse_int(
        self,
        widget_id: str,
        label: str,
        min_value: int | None = None,
        max_value: int | None = None,
    ) -> int:
        return self.input_parser.parse_int(widget_id, label, min_value, max_value)

    def _parse_float(self, widget_id: str, label: str, min_value: float | None = None) -> float:
        return self.input_parser.parse_float(widget_id, label, min_value)

    def _format_money(self, amount: float) -> str:
        return f"{amount:,.0f}"

    def _refresh_people_table(self, calculated_people: list[Person] | None = None) -> None:
        table = self.query_one("#people-table", DataTable)
        table.clear()

        show_people = calculated_people if calculated_people is not None else self.people
        for index, person in enumerate(show_people, start=1):
            total = person.elec + person.water
            table.add_row(
                str(index),
                person.name,
                str(person.stay_days),
                self._format_money(person.elec),
                self._format_money(person.water),
                self._format_money(total),
            )

    def _set_result(self, bills_data: BillsData) -> None:
        renderable = build_result_renderable(bills_data)
        self.query_one("#result-view", Static).update(renderable)

    def _collect_bills_input(self) -> tuple[int, int, float, float, str]:
        now_year = datetime.now().year
        year = self._parse_int("year", "Nam", min_value=2000, max_value=now_year + 1)
        month = self._parse_int("month", "Thang", min_value=1, max_value=12)
        electricity = self._parse_float("electricity", "Tien dien", min_value=0)
        water = self._parse_float("water", "Tien nuoc", min_value=0)

        algorithm = self.query_one("#algorithm", Select).value
        if algorithm not in {"ratio", "stair", "equal"}:
            raise ValueError("Thuat toan khong hop le.")

        return year, month, electricity, water, str(algorithm)

    def _run_calculation(self) -> None:
        if not self.people:
            raise ValueError("Chua co nguoi nao de tinh tien.")

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
            self._safe_notify("Tinh tien thanh cong va da luu lich su.", severity="information")
            return

        self._safe_notify("Tinh tien thanh cong.", severity="information")

    def _add_person(self) -> None:
        name = self.input_parser.get_input("person-name")
        if not name:
            raise ValueError("Ten khong duoc de trong.")

        stay_days = self._parse_int("person-days", "So ngay o", min_value=0)
        self.people.append(Person(name=name, stay_days=stay_days))
        self.selected_person_index = None
        self._refresh_people_table()

    def _update_person(self) -> None:
        if self.selected_person_index is None:
            raise ValueError("Hay chon mot dong trong bang de cap nhat.")

        name = self.input_parser.get_input("person-name")
        if not name:
            raise ValueError("Ten khong duoc de trong.")

        stay_days = self._parse_int("person-days", "So ngay o", min_value=0)
        self.people[self.selected_person_index] = Person(name=name, stay_days=stay_days)
        self._refresh_people_table()

    def _delete_person(self) -> None:
        if self.selected_person_index is None:
            raise ValueError("Hay chon mot dong trong bang de xoa.")

        self.people.pop(self.selected_person_index)
        self.selected_person_index = None
        self._refresh_people_table()

    def _save_people(self) -> None:
        filename = self.input_parser.get_input("people-file") or "people.txt"
        self.storage.save_people_info(self.people, filename=filename)
        self._safe_notify("Da luu danh sach nguoi.")

    def _load_people(self) -> None:
        filename = self.input_parser.get_input("people-file") or "people.txt"
        self.people = self.storage.load_people_info(filename=filename)
        self.selected_person_index = None
        self._refresh_people_table()
        self._safe_notify(f"Da tai {len(self.people)} nguoi.")

    def _export(self, export_type: str) -> None:
        if self.last_result is None:
            raise ValueError("Chua co ket qua de export.")

        target = self.input_parser.get_input("export-file")
        if not target:
            target = "dist/exports/bills_result.csv" if export_type == "csv" else "dist/exports/bills_result.txt"

        if export_type == "csv" and not target.lower().endswith(".csv"):
            target = f"{target}.csv"
        if export_type == "txt" and not target.lower().endswith(".txt"):
            target = f"{target}.txt"

        if export_type == "csv":
            exported = self.exporter.export_csv(self.last_result, target)
        else:
            exported = self.exporter.export_txt(self.last_result, target)

        self._safe_notify(f"Da export: {exported}")

    def _copy_result(self) -> None:
        if self.last_result is None:
            raise ValueError("Chua co ket qua de copy.")
        if pyperclip is None:
            raise ValueError("Clipboard chua san sang. Hay cai pyperclip de dung tinh nang copy.")
        pyperclip.copy(build_plain_result(self.last_result))
        self._safe_notify("Da copy ket qua vao clipboard.")

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
        self.query_one("#result-view", Static).update("Chua co ket qua. Nhap du lieu va bam Tinh tien.")

    def _open_history(self) -> None:
        self.app.push_screen(HistoryScreen(self.history))

    def _run_command_line(self) -> None:
        command = self.input_parser.get_input("command-line")
        if not command:
            raise ValueError("Hay nhap command.")

        cmd = command.strip().lower()
        if cmd in {"/calculate", "/calc"}:
            self._run_calculation()
        elif cmd in {"/history", "/h"}:
            self._open_history()
        elif cmd in {"/reset", "/r"}:
            self._reset_form()
        elif cmd in {"/save", "/save people"}:
            self._save_people()
        elif cmd in {"/load", "/load people"}:
            self._load_people()
        elif cmd in {"/export txt", "/x txt"}:
            self._export("txt")
        elif cmd in {"/export csv", "/x csv"}:
            self._export("csv")
        elif cmd in {"/copy", "/c"}:
            self._copy_result()
        else:
            raise ValueError("Command khong ho tro. Dung /calculate, /history, /reset, /export txt, /export csv.")

        self.query_one("#command-line", Input).value = ""

    def _run_with_handling(self, action, label: str) -> None:
        try:
            action()
        except Exception as exc:
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
            "reload-history": (self._open_history, "Open history"),
            "reset": (self._reset_form, "Reset form"),
            "run-command": (self._run_command_line, "Run command"),
        }

        action = actions.get(event.button.id or "")
        if action:
            callback, label = action
            self._run_with_handling(callback, label)

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

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "command-line":
            self._run_with_handling(self._run_command_line, "Run command")

    def action_calculate(self) -> None:
        self._run_with_handling(self._run_calculation, "Calculate")

    def action_save_people(self) -> None:
        self._run_with_handling(self._save_people, "Save people")

    def action_load_people(self) -> None:
        self._run_with_handling(self._load_people, "Load people")

    def action_export_txt(self) -> None:
        self._run_with_handling(lambda: self._export("txt"), "Export TXT")

    def action_reload_history(self) -> None:
        self._run_with_handling(self._open_history, "Open history")

    def action_reset_form(self) -> None:
        self._run_with_handling(self._reset_form, "Reset form")

    def action_copy_result(self) -> None:
        self._run_with_handling(self._copy_result, "Copy result")

    def action_command_palette(self) -> None:
        self.app.action_command_palette()

    def action_quit(self) -> None:
        self.app.exit()
