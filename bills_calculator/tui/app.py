from __future__ import annotations

from textual.app import App

from bills_calculator.tui.screens.main_screen import MainScreen


class BillsTextualApp(App):
    TITLE = "Bills Calculator"
    SUB_TITLE = "v2 · /help để bắt đầu"
    CSS_PATH = "styles/main.tcss"
    ENABLE_COMMAND_PALETTE = False  # dùng command bar riêng, không cần built-in palette

    def on_mount(self) -> None:
        self.push_screen(MainScreen())
