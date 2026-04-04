from __future__ import annotations

from datetime import datetime

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import Footer, Header, RichLog, Static

from bills_calculator.core.calculator import BillsCalculator
from bills_calculator.core.models import BillsData, Person
from bills_calculator.data.exporter import BillsExporter
from bills_calculator.data.history import BillsHistory
from bills_calculator.data.storage import Storage
from bills_calculator.tui.widgets.command_input import CommandInput
from bills_calculator.tui.widgets.header import build_gradient_figlet_title
from bills_calculator.tui.widgets.result_viewer import (
    build_context_panel,
    build_people_table,
    build_plain_result,
    build_result_renderable,
)

try:
    import pyperclip
except ImportError:
    pyperclip = None

# ─── Help text ────────────────────────────────────────────────────────────────

HELP_TEXT = """\
[bold #ABB2BF]Danh sách lệnh[/]

  [bold #98C379]/add[/] [dim]<tên> <ngày>[/]        Thêm người  — VD: /add Nguyên 20
  [bold #98C379]/rm[/]  [dim]<tên|số>[/]             Xóa người   — VD: /rm 2  hoặc  /rm Nguyên
  [bold #98C379]/list[/]                         Xem danh sách người
  [bold #E06C75]/set[/]  [dim]elec|water|month|year|algo  <giá trị>[/]
        VD: /set elec 800000  ·  /set algo stair
  [bold #E5C07B]/calc[/]                         Tính tiền
  [bold #C678DD]/history[/]                      Xem lịch sử
  [bold #56B6C2]/export[/] [dim]txt|csv[/]              Export kết quả
  [bold #56B6C2]/copy[/]                         Copy kết quả vào clipboard
  [bold #E06C75]/save[/]  [dim][file][/]                  Lưu danh sách người
  [bold #E06C75]/load[/]  [dim][file][/]                  Tải danh sách người
  [bold #5C6370]/reset[/]                        Reset toàn bộ
  [bold #5C6370]/clear[/]                        Xoá log màn hình
  [bold #5C6370]/help[/]                         Hiển thị trợ giúp này
"""


class MainScreen(Screen):
    BINDINGS = [
        Binding("ctrl+enter", "calculate",     "Calculate",  show=True),
        Binding("ctrl+h",     "show_history",  "History",    show=True),
        Binding("ctrl+r",     "reset_form",    "Reset",      show=False),
        Binding("ctrl+l",     "load_people",   "Load",       show=False),
        Binding("ctrl+s",     "save_people",   "Save",       show=False),
        Binding("ctrl+e",     "export_txt",    "Export",     show=False),
        Binding("ctrl+c",     "copy_result",   "Copy",       show=False),
        Binding("escape",     "focus_cmd",     "Focus cmd",  show=False),
        Binding("q",          "quit",          "Quit",       show=True),
    ]

    # ── State ──────────────────────────────────────────────────────────────────

    def __init__(self) -> None:
        super().__init__()
        self._calculator = BillsCalculator()
        self._storage    = Storage()
        self._exporter   = BillsExporter()
        self._history    = BillsHistory()

        now = datetime.now()
        self._year:        int   = now.year
        self._month:       int   = now.month
        self._electricity: float = 0.0
        self._water:       float = 0.0
        self._algorithm:   str   = "ratio"
        self._people:      list[Person] = []
        self._last_result: BillsData | None = None
        self._people_file: str = "people.txt"

    # ── Compose ────────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="content-area"):
            yield Static(build_gradient_figlet_title(), id="hero")
            yield RichLog(id="output-log", highlight=True, markup=True, wrap=True)
        yield CommandInput(id="cmd-bar")
        yield Footer()

    def on_mount(self) -> None:
        log = self.query_one("#output-log", RichLog)
        log.write(Text.from_markup(
            "[dim]Chào mừng đến Bills Calculator · Gõ [bold #98C379]/help[/] để xem lệnh[/]"
        ))
        self._print_context()
        self.query_one(CommandInput).focus_input()

    # ── Log helpers ────────────────────────────────────────────────────────────

    def _log(self, renderable) -> None:
        self.query_one("#output-log", RichLog).write(renderable)

    def _log_ok(self, msg: str) -> None:
        self._log(Text.from_markup(f"[bold #98C379]✓[/]  {msg}"))

    def _log_err(self, msg: str) -> None:
        self._log(Text.from_markup(f"[bold red]✗[/]  [red]{msg}[/]"))

    def _log_info(self, msg: str) -> None:
        self._log(Text.from_markup(f"[dim]ℹ  {msg}[/]"))

    def _print_context(self) -> None:
        self._log(build_context_panel(
            self._year, self._month,
            self._electricity, self._water,
            self._algorithm, self._people,
        ))

    def _print_people(self) -> None:
        self._log(build_people_table(self._people))

    # ── Command dispatch ───────────────────────────────────────────────────────

    def on_command_input_command_submitted(self, event: CommandInput.CommandSubmitted) -> None:
        self._dispatch(event.command)

    def _dispatch(self, raw: str) -> None:
        parts = raw.strip().split()
        if not parts:
            return
        cmd = parts[0].lower()
        args = parts[1:]

        routes = {
            "/add":     self._cmd_add,
            "/rm":      self._cmd_rm,
            "/remove":  self._cmd_rm,
            "/list":    lambda _: self._print_people(),
            "/set":     self._cmd_set,
            "/calc":    lambda _: self._cmd_calc(),
            "/calculate": lambda _: self._cmd_calc(),
            "/history": lambda _: self._cmd_history(),
            "/export":  self._cmd_export,
            "/copy":    lambda _: self._cmd_copy(),
            "/save":    self._cmd_save,
            "/load":    self._cmd_load,
            "/reset":   lambda _: self._cmd_reset(),
            "/clear":   lambda _: self.query_one("#output-log", RichLog).clear(),
            "/help":    lambda _: self._log(Text.from_markup(HELP_TEXT)),
        }

        handler = routes.get(cmd)
        if handler:
            try:
                handler(args)
            except Exception as exc:
                self._log_err(str(exc))
        else:
            self._log_err(f"Lệnh không hỗ trợ: {cmd}  ·  Gõ /help để xem danh sách.")

    # ── Command implementations ────────────────────────────────────────────────

    def _cmd_add(self, args: list[str]) -> None:
        if len(args) < 2:
            raise ValueError("Cú pháp: /add <tên> <ngày_ở>  —  VD: /add Nguyên 20")
        name = args[0]
        try:
            days = int(args[1])
        except ValueError:
            raise ValueError(f"Số ngày phải là số nguyên, nhận được: {args[1]}")
        if days < 0:
            raise ValueError("Số ngày ở phải >= 0.")
        self._people.append(Person(name=name, stay_days=days))
        self._log_ok(f"Đã thêm [{name}] — {days} ngày")
        self._print_people()

    def _cmd_rm(self, args: list[str]) -> None:
        if not args:
            raise ValueError("Cú pháp: /rm <tên|số>  —  VD: /rm 2  hoặc  /rm Nguyên")
        key = args[0]
        if key.isdigit():
            idx = int(key) - 1
            if not (0 <= idx < len(self._people)):
                raise ValueError(f"Không có người số {key}.")
            removed = self._people.pop(idx)
        else:
            matches = [i for i, p in enumerate(self._people) if p.name.lower() == key.lower()]
            if not matches:
                raise ValueError(f"Không tìm thấy người tên '{key}'.")
            removed = self._people.pop(matches[0])
        self._log_ok(f"Đã xóa [{removed.name}]")
        self._print_people()

    def _cmd_set(self, args: list[str]) -> None:
        if len(args) < 2:
            raise ValueError("Cú pháp: /set <elec|water|month|year|algo> <giá_trị>")
        field, value = args[0].lower(), args[1]
        if field in {"elec", "electricity"}:
            self._electricity = float(value)
            self._log_ok(f"Tiền điện: {self._electricity:,.0f} đ")
        elif field in {"water"}:
            self._water = float(value)
            self._log_ok(f"Tiền nước: {self._water:,.0f} đ")
        elif field in {"month"}:
            m = int(value)
            if not 1 <= m <= 12:
                raise ValueError("Tháng phải từ 1 đến 12.")
            self._month = m
            self._log_ok(f"Tháng: {self._month}")
        elif field in {"year"}:
            y = int(value)
            if not 2000 <= y <= 2100:
                raise ValueError("Năm không hợp lệ.")
            self._year = y
            self._log_ok(f"Năm: {self._year}")
        elif field in {"algo", "algorithm"}:
            if value not in {"ratio", "stair", "equal"}:
                raise ValueError("Thuật toán: ratio | stair | equal")
            self._algorithm = value
            label = {"ratio": "Tỷ lệ", "stair": "Bậc thang", "equal": "Bình quân"}[value]
            self._log_ok(f"Thuật toán: {label}")
        else:
            raise ValueError(f"Field không hỗ trợ: {field}")
        self._print_context()

    def _cmd_calc(self) -> None:
        if not self._people:
            raise ValueError("Chưa có người nào. Dùng /add <tên> <ngày> để thêm.")
        if self._electricity == 0 and self._water == 0:
            raise ValueError("Tiền điện và nước đều bằng 0. Dùng /set elec <số> để đặt.")

        people_copy = [Person(p.name, p.stay_days) for p in self._people]
        calculated = self._calculator.calculate_bills(
            people_copy,
            total_elec=self._electricity,
            total_water=self._water,
            algorithm=self._algorithm,
        )
        bills_data = BillsData(
            year=self._year, month=self._month,
            electricity=self._electricity, water=self._water,
            people=calculated, algorithm=self._algorithm,
        )
        self._last_result = bills_data
        self._log(build_result_renderable(bills_data))

        self._history.save(bills_data)
        self._log_ok("Đã lưu vào lịch sử.")

    def _cmd_history(self) -> None:
        from bills_calculator.tui.screens.history_screen import HistoryScreen
        self.app.push_screen(HistoryScreen(self._history))

    def _cmd_export(self, args: list[str]) -> None:
        if self._last_result is None:
            raise ValueError("Chưa có kết quả. Chạy /calc trước.")
        fmt = args[0].lower() if args else "txt"
        if fmt not in {"txt", "csv"}:
            raise ValueError("Định dạng: txt | csv")
        default = f"dist/exports/bills_{self._year}_{self._month:02d}.{fmt}"
        path = args[1] if len(args) > 1 else default
        if fmt == "csv":
            out = self._exporter.export_csv(self._last_result, path)
        else:
            out = self._exporter.export_txt(self._last_result, path)
        self._log_ok(f"Đã export: {out}")

    def _cmd_copy(self) -> None:
        if self._last_result is None:
            raise ValueError("Chưa có kết quả. Chạy /calc trước.")
        if pyperclip is None:
            raise ValueError("pyperclip chưa được cài. Chạy: uv add pyperclip")
        pyperclip.copy(build_plain_result(self._last_result))
        self._log_ok("Đã copy kết quả vào clipboard.")

    def _cmd_save(self, args: list[str]) -> None:
        filename = args[0] if args else self._people_file
        self._storage.save_people_info(self._people, filename=filename)
        self._log_ok(f"Đã lưu danh sách → {filename}")

    def _cmd_load(self, args: list[str]) -> None:
        filename = args[0] if args else self._people_file
        self._people = self._storage.load_people_info(filename=filename)
        self._log_ok(f"Đã tải {len(self._people)} người từ {filename}")
        self._print_people()

    def _cmd_reset(self) -> None:
        now = datetime.now()
        self._year = now.year; self._month = now.month
        self._electricity = 0.0; self._water = 0.0
        self._algorithm = "ratio"; self._people = []; self._last_result = None
        self.query_one("#output-log", RichLog).clear()
        self._log(Text.from_markup("[dim]Đã reset. Gõ /help để bắt đầu.[/]"))
        self._print_context()

    # ── Key binding actions ────────────────────────────────────────────────────

    def action_calculate(self)    -> None: self._dispatch("/calc")
    def action_show_history(self) -> None: self._dispatch("/history")
    def action_reset_form(self)   -> None: self._dispatch("/reset")
    def action_load_people(self)  -> None: self._dispatch("/load")
    def action_save_people(self)  -> None: self._dispatch("/save")
    def action_export_txt(self)   -> None: self._dispatch("/export txt")
    def action_copy_result(self)  -> None: self._dispatch("/copy")
    def action_focus_cmd(self)    -> None: self.query_one(CommandInput).focus_input()
    def action_quit(self)         -> None: self.app.exit()
