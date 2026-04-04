from __future__ import annotations

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Input, ListView, ListItem, Label
from textual.message import Message
from textual.containers import Vertical
from rich.text import Text


# Command suggestions with descriptions
COMMANDS = [
    ("/add", "Thêm người — /add <tên> <ngày>"),
    ("/calc", "Tính tiền"),
    ("/clear", "Xoá log màn hình"),
    ("/copy", "Copy kết quả vào clipboard"),
    ("/export", "Export kết quả — txt|csv"),
    ("/help", "Hiển thị trợ giúp"),
    ("/history", "Xem lịch sử"),
    ("/list", "Xem danh sách người"),
    ("/load", "Tải danh sách người"),
    ("/quit", "Thoát ứng dụng"),
    ("/reset", "Reset toàn bộ"),
    ("/rm", "Xóa người — /rm <tên|số>"),
    ("/save", "Lưu danh sách người"),
    ("/set", "Đặt giá trị — elec|water|month|year|algo"),
]


class CommandInput(Widget):
    """Bottom-docked command bar — giống gemini-cli / claude-code.

    Hiển thị prefix "> " với màu accent, bắt Enter để dispatch CommandSubmitted.
    Lưu history lệnh, duyệt bằng ↑ ↓.
    Autocomplete khi gõ "/" — hiển thị danh sách lệnh.
    """
    CSS_PATH = "styles/input.tcss"

    class CommandSubmitted(Message):
        """Người dùng nhấn Enter trong command bar."""
        def __init__(self, command: str) -> None:
            super().__init__()
            self.command = command.strip()

    _history: list[str] = []
    _history_index: reactive[int] = reactive(-1)
    _show_suggestions: reactive[bool] = reactive(False)
    _current_matches: list[tuple[str, str]] = []  # Store current matching commands

    def compose(self) -> ComposeResult:
        from textual.widgets import Label
        from textual.containers import Horizontal
        with Vertical():
            with Horizontal(id="input-container"):
                yield Label("> ", id="cmd-prefix")
                yield Input(
                    placeholder="Nhập lệnh... /help để xem danh sách",
                    id="cmd-input",
                )
            yield ListView(id="suggestions-list", classes="hidden")

    def on_mount(self) -> None:
        """Initialize and ensure input has focus."""
        # Don't show suggestions on mount
        self._hide_suggestions()
        # Focus input after a short delay
        self.set_timer(0.05, lambda: self.query_one("#cmd-input", Input).focus())

    def on_input_changed(self, event: Input.Changed) -> None:
        """Show suggestions when typing '/'."""
        if event.input.id != "cmd-input":
            return
        
        value = event.value
        
        # Show suggestions if starts with / and has at least 1 char
        if value.startswith("/"):
            self._update_suggestions(value)
            self._show_suggestions = True
        else:
            self._show_suggestions = False
            self._hide_suggestions()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "cmd-input":
            return
        
        # Hide suggestions first
        self._hide_suggestions()
        
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
        
        # Always handle escape to hide suggestions and return to input
        if event.key == "escape":
            if self._show_suggestions:
                self._hide_suggestions()
                inp.focus()
                event.prevent_default()
                return
        
        suggestions_list = self.query_one("#suggestions-list", ListView)
        
        # If suggestions are shown and user presses down, move to suggestions
        if self._show_suggestions and not suggestions_list.has_class("hidden"):
            if event.key == "down" and inp.has_focus:
                # Only move to suggestions if input has focus
                if len(suggestions_list.children) > 0:
                    suggestions_list.focus()
                    suggestions_list.index = 0
                event.prevent_default()
                return
            elif event.key == "tab":
                # Accept first matching suggestion
                if len(self._current_matches) > 0:
                    cmd = self._current_matches[0][0]
                    inp.value = cmd + " "
                    inp.cursor_position = len(inp.value)
                    self._hide_suggestions()
                    inp.focus()
                event.prevent_default()
                return
        
        # History navigation (only when no suggestions shown)
        if not self._show_suggestions or suggestions_list.has_class("hidden"):
            if event.key == "up":
                if self._history:
                    if self._history_index == -1:
                        self._history_index = len(self._history) - 1
                    elif self._history_index > 0:
                        self._history_index -= 1
                    inp.value = self._history[self._history_index]
                    inp.cursor_position = len(inp.value)
                event.prevent_default()
            elif event.key == "down" and self._history_index != -1:
                if self._history_index < len(self._history) - 1:
                    self._history_index += 1
                    inp.value = self._history[self._history_index]
                else:
                    self._history_index = -1
                    inp.value = ""
                inp.cursor_position = len(inp.value)
                event.prevent_default()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle suggestion selection."""
        if event.list_view.id != "suggestions-list":
            return
        
        inp = self.query_one("#cmd-input", Input)
        # Get the index of selected item and look up the command
        index = event.list_view.index
        if index is not None and 0 <= index < len(self._current_matches):
            cmd = self._current_matches[index][0]
            inp.value = cmd + " "
            inp.cursor_position = len(inp.value)
            self._hide_suggestions()
            inp.focus()

    def _update_suggestions(self, prefix: str) -> None:
        """Update suggestions list based on input."""
        suggestions_list = self.query_one("#suggestions-list", ListView)
        suggestions_list.clear()
        
        if not prefix:
            prefix = "/"
        
        matching = [(cmd, desc) for cmd, desc in COMMANDS if cmd.startswith(prefix.lower())]
        self._current_matches = matching[:10]  # Store for later retrieval
        
        if self._current_matches:
            for cmd, desc in self._current_matches:
                text = Text()
                text.append(f"{cmd:<12}", style="bold #98C379")
                text.append(desc, style="dim")
                suggestions_list.append(ListItem(Label(text)))
        
        if not matching and prefix.startswith("/"):
            suggestions_list.add_class("hidden")
        else:
            suggestions_list.remove_class("hidden")

    def _hide_suggestions(self) -> None:
        """Hide suggestions list."""
        suggestions_list = self.query_one("#suggestions-list", ListView)
        suggestions_list.add_class("hidden")
        self._show_suggestions = False

    def focus_input(self) -> None:
        self.query_one("#cmd-input", Input).focus()
