"""SlashSuggest — overlay widget hiển thị suggest bên dưới input bar.

Widget này được mount vào Screen, dock bottom với offset để float
ngay phía trên CommandInput mà không đè lên header hay content area.
"""
from __future__ import annotations

from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import ListView, ListItem, Label
from rich.text import Text

# Command list — (slash_cmd, description)
COMMANDS: list[tuple[str, str]] = [
    ("/add",     "Thêm người — /add <tên> <ngày>"),
    ("/calc",    "Tính tiền"),
    ("/clear",   "Xoá log màn hình"),
    ("/copy",    "Copy kết quả vào clipboard"),
    ("/export",  "Export kết quả — txt|csv"),
    ("/help",    "Hiển thị trợ giúp"),
    ("/history", "Xem lịch sử"),
    ("/list",    "Xem danh sách người"),
    ("/load",    "Tải danh sách người"),
    ("/quit",    "Thoát ứng dụng"),
    ("/reset",   "Reset toàn bộ"),
    ("/rm",      "Xóa người — /rm <tên|số>"),
    ("/save",    "Lưu danh sách người"),
    ("/set",     "Đặt giá trị — elec|water|month|year|algo"),
]

_MAX_VISIBLE = 8  # số dòng tối đa hiện cùng lúc


class SlashSuggest(Widget):
    """Floating suggestion list, dock bottom, hiển thị phía trên input bar.

    Không được compose trong CommandInput — được mount trực tiếp vào Screen
    để tránh bị clip bởi CommandInput's own bounding box.
    """

    DEFAULT_CSS = """
    SlashSuggest {
        dock: bottom;
        layer: overlay;
        height: auto;
        max-height: 18;
        width: 100%;
        background: #2C313A;
        border-top: solid #4B5263;
        border-left: solid #4B5263;
        border-right: solid #4B5263;
        padding: 0;
        /* Đẩy lên trên CommandInput (3 hàng) + Footer (1 hàng) */
        margin-bottom: 4;
    }

    SlashSuggest > ListView {
        height: auto;
        max-height: 16;
        background: #2C313A;
        border: none;
        padding: 0;
        scrollbar-color: #3E4451 #2C313A;
        scrollbar-size: 1 1;
    }

    SlashSuggest > ListView > ListItem {
        height: 1;
        padding: 0 1;
        background: #2C313A;
    }

    SlashSuggest > ListView > ListItem:hover {
        background: #3E4451;
    }

    SlashSuggest > ListView > ListItem.-selected {
        background: #3E4451;
    }

    SlashSuggest > ListView > ListItem > Label {
        height: 1;
        padding: 0;
        background: transparent;
    }
    """

    class Selected(Message):
        """User chọn một lệnh từ suggest list."""
        def __init__(self, command: str) -> None:
            super().__init__()
            self.command = command

    # ── internal state ────────────────────────────────────────────────────────
    _matches: list[tuple[str, str]] = []

    def compose(self) -> ComposeResult:
        yield ListView(id="slash-list")

    def update(self, prefix: str) -> None:
        """Cập nhật danh sách suggest theo prefix đang gõ."""
        lv = self.query_one("#slash-list", ListView)
        lv.clear()

        p = prefix.lower()
        self._matches = [(c, d) for c, d in COMMANDS if c.startswith(p)][:_MAX_VISIBLE]

        for cmd, desc in self._matches:
            text = Text()
            text.append(f"{cmd:<12}", style="bold #98C379")
            text.append(desc, style="dim #5C6370")
            lv.append(ListItem(Label(text)))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        idx = event.list_view.index
        if idx is not None and 0 <= idx < len(self._matches):
            self.post_message(self.Selected(self._matches[idx][0]))
        event.stop()

    @property
    def matches(self) -> list[tuple[str, str]]:
        return self._matches

    def first_match(self) -> str | None:
        return self._matches[0][0] if self._matches else None

    def focus_list(self) -> None:
        lv = self.query_one("#slash-list", ListView)
        lv.focus()
        lv.index = 0
