"""CommandInput — bottom-docked input bar, gemini-cli / claude-code style.

Không chứa suggestion list bên trong. Thay vào đó, post message lên Screen
để Screen điều phối SlashSuggest overlay.
"""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Input, Label


class CommandInput(Widget):
    """Input bar cố định ở bottom, prefix "> " màu accent.

    Messages:
        CommandSubmitted  — user nhấn Enter
        SlashTyped        — user gõ ký tự, value bắt đầu bằng "/"
        SlashCleared      — user xóa hết hoặc không còn bắt đầu bằng "/"
        NavigateSuggest   — user nhấn ↓ khi input đang focus (→ chuyển focus xuống suggest)
        TabComplete       — user nhấn Tab (→ Screen chọn match đầu tiên)
    """

    DEFAULT_CSS = """
    CommandInput {
        dock: bottom;
        height: 3;
        background: #282C34;
        border-top: solid #4B5263;
        padding: 0;
        layer: base;
    }

    CommandInput > #input-container {
        height: 3;
        padding: 0 1;
        width: 100%;
    }

    CommandInput Input {
        background: #282C34;
        border: none;
        height: 1;
        padding: 0 1;
        color: #ABB2BF;
        margin: 0;
    }

    CommandInput Input:focus {
        border: none;
        background: #282C34;
    }

    CommandInput #cmd-prefix {
        width: 2;
        height: 1;
        color: #98C379;
        padding: 1 0 0 0;
    }
    """

    # ── Messages ──────────────────────────────────────────────────────────────

    class CommandSubmitted(Message):
        def __init__(self, command: str) -> None:
            super().__init__()
            self.command = command.strip()

    class SlashTyped(Message):
        def __init__(self, prefix: str) -> None:
            super().__init__()
            self.prefix = prefix

    class SlashCleared(Message):
        pass

    class NavigateSuggest(Message):
        pass

    class TabComplete(Message):
        pass

    # ── State ─────────────────────────────────────────────────────────────────
    _history: list[str] = []
    _history_index: int = -1

    # ── Compose ───────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        with Horizontal(id="input-container"):
            yield Label("> ", id="cmd-prefix")
            yield Input(
                placeholder="Nhập lệnh... /help để xem danh sách",
                id="cmd-input",
            )

    def on_mount(self) -> None:
        self.set_timer(0.05, lambda: self.query_one("#cmd-input", Input).focus())

    # ── Input events ──────────────────────────────────────────────────────────

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id != "cmd-input":
            return
        value = event.value
        if value.startswith("/"):
            self.post_message(self.SlashTyped(value))
        else:
            self.post_message(self.SlashCleared())

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "cmd-input":
            return
        self.post_message(self.SlashCleared())
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
        if not inp.has_focus:
            return

        if event.key == "down":
            self.post_message(self.NavigateSuggest())
            event.prevent_default()

        elif event.key == "tab":
            self.post_message(self.TabComplete())
            event.prevent_default()

        elif event.key == "up":
            if self._history:
                if self._history_index == -1:
                    self._history_index = len(self._history) - 1
                elif self._history_index > 0:
                    self._history_index -= 1
                inp.value = self._history[self._history_index]
                inp.cursor_position = len(inp.value)
            event.prevent_default()

        elif event.key == "escape":
            self.post_message(self.SlashCleared())
            event.prevent_default()

    # ── Public API ────────────────────────────────────────────────────────────

    def focus_input(self) -> None:
        self.query_one("#cmd-input", Input).focus()

    def set_value(self, value: str) -> None:
        inp = self.query_one("#cmd-input", Input)
        inp.value = value
        inp.cursor_position = len(value)
