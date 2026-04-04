from __future__ import annotations

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Input
from textual.message import Message


class CommandInput(Widget):
    """Bottom-docked command bar — giống gemini-cli / claude-code.

    Hiển thị prefix "> " với màu accent, bắt Enter để dispatch CommandSubmitted.
    Lưu history lệnh, duyệt bằng ↑ ↓.
    """
    CSS_PATH = "styles/input.tcss"

    class CommandSubmitted(Message):
        """Người dùng nhấn Enter trong command bar."""
        def __init__(self, command: str) -> None:
            super().__init__()
            self.command = command.strip()

    _history: list[str] = []
    _history_index: reactive[int] = reactive(-1)

    def compose(self) -> ComposeResult:
        from textual.widgets import Label
        from textual.containers import Horizontal
        with Horizontal():
            yield Label("> ", id="cmd-prefix")
            yield Input(
                placeholder="Nhập lệnh... /help để xem danh sách",
                id="cmd-input",
            )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "cmd-input":
            return
        cmd = event.value.strip()
        if cmd:
            if not self._history or self._history[-1] != cmd:
                self._history.append(cmd)
            self._history_index = -1
            self.post_message(self.CommandSubmitted(cmd))
        event.input.value = ""
        event.stop()

    def on_key(self, event) -> None:
        inp = self.query_one("#cmd-input", Input)
        if event.key == "up":
            if self._history:
                if self._history_index == -1:
                    self._history_index = len(self._history) - 1
                elif self._history_index > 0:
                    self._history_index -= 1
                inp.value = self._history[self._history_index]
                inp.cursor_position = len(inp.value)
            event.prevent_default()
        elif event.key == "down":
            if self._history_index != -1:
                if self._history_index < len(self._history) - 1:
                    self._history_index += 1
                    inp.value = self._history[self._history_index]
                else:
                    self._history_index = -1
                    inp.value = ""
                inp.cursor_position = len(inp.value)
            event.prevent_default()

    def focus_input(self) -> None:
        self.query_one("#cmd-input", Input).focus()
