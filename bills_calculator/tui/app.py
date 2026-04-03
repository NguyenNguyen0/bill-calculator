from __future__ import annotations

from textual.app import App

from bills_calculator.tui.screens.main_screen import MainScreen


class BillsTextualApp(App):
    TITLE = "Bills Calculator TUI"
    SUB_TITLE = "Interactive bill sharing workspace"
    CSS_PATH = "styles/main.tcss"

    def on_mount(self) -> None:
        self.push_screen(MainScreen())
