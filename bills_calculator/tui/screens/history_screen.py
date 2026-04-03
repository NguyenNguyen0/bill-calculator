from __future__ import annotations

from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Static

from bills_calculator.data.history import BillsHistory


class HistoryScreen(Screen):
    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("q", "close", "Close"),
        Binding("r", "reload_history", "Reload"),
    ]

    def __init__(self, history_service: BillsHistory) -> None:
        super().__init__()
        self.history_service = history_service

    def compose(self):
        with Vertical(id="history-root"):
            yield Static("LICH SU TINH TIEN", id="history-title")
            yield DataTable(id="history-table")
            yield Static("R: reload | ESC/Q: back", id="history-hint")
            yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#history-table", DataTable)
        table.add_columns("Saved At", "Month", "Year", "Algo", "People", "Elec", "Water")
        self._reload_history_table()

    def _reload_history_table(self) -> None:
        table = self.query_one("#history-table", DataTable)
        table.clear()
        entries = self.history_service.load_all()
        for item in reversed(entries[-100:]):
            table.add_row(
                str(item.get("saved_at", "")),
                str(item.get("month", "")),
                str(item.get("year", "")),
                str(item.get("algorithm", "")),
                str(len(item.get("people", []))),
                f"{float(item.get('electricity', 0)):,.0f}",
                f"{float(item.get('water', 0)):,.0f}",
            )

    def action_reload_history(self) -> None:
        self._reload_history_table()

    def action_close(self) -> None:
        self.app.pop_screen()
