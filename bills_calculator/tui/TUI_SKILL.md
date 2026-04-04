# TUI Design Skill — Bills Calculator
# Hướng dẫn cho Copilot khi làm việc với Textual TUI

## Triết lý thiết kế

Mục tiêu là TUI giống gemini-cli và claude-code:
- **Chat-first layout**: nội dung chính chạy dọc từ trên xuống, không chia cột sidebar chật.
- **Command-bar ở đáy màn hình**: một ô input duy nhất, người dùng nhập slash-commands.
- **Không có buttons thừa**: mọi hành động qua keyboard binding hoặc slash command.
- **Rich content area**: kết quả render bằng Rich, không phải plain text.
- **Gradient figlet header** luôn hiển thị ở trên cùng content area.

## Layout tổng thể

```
┌─────────────────────────────────────────────────────────────┐
│  [Textual Header — clock, title]                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ██████╗ ██╗██╗     ██╗     ███████╗                      │
│   ██╔══██╗██║██║     ██║     ██╔════╝   (gradient figlet)  │
│   ██████╔╝██║██║     ██║     ███████╗                      │
│   ...                                                       │
│                                                             │
│  ╭─ Context ──────────────────────────────╮                 │
│  │  Tháng 4/2026 · Điện 800k · Nước 200k │ (RichLog area)  │
│  │  Thuật toán: tỷ lệ                     │                 │
│  ╰────────────────────────────────────────╯                 │
│                                                             │
│  ╭─ Danh sách người ──────────────────────╮                 │
│  │  #  Tên          Ngày ở               │                 │
│  │  1  Nguyễn       20                   │                 │
│  │  2  Vũ           17                   │                 │
│  ╰────────────────────────────────────────╯                 │
│                                                             │
│  ╭─ Kết quả ──────────────────────────────╮                 │
│  │  [Rich result table renders here]      │                 │
│  ╰────────────────────────────────────────╯                 │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  > /add Nguyễn 20 █                             [command]  │
├─────────────────────────────────────────────────────────────┤
│  [Textual Footer — key hints]                               │
└─────────────────────────────────────────────────────────────┘
```

## Màu sắc (dark terminal theme)

```python
# Nền
BG_MAIN    = "#282C34"   # Nền toàn màn hình
BG_PANEL   = "#2C313A"   # Panel / card
BG_INPUT   = "#23272E"   # Input bar nền

# Gradient header: Cyan → Magenta (softer tones)
GRAD_START = (97, 218, 251)   # Soft Cyan #61DAFB
GRAD_END   = (198, 120, 221)  # Soft Magenta #C678DD

# Accent (brighter, more saturated for lighter background)
ACCENT_BLUE   = "#61AFEF"  # Softer blue
ACCENT_PURPLE = "#C678DD"  # Softer purple
ACCENT_GREEN  = "#98C379"  # Softer green
ACCENT_YELLOW = "#E5C07B"  # Softer yellow
ACCENT_CYAN   = "#56B6C2"  # Softer cyan
ACCENT_RED    = "#E06C75"  # Softer red

# Text (adjusted for better contrast on lighter bg)
TEXT_PRIMARY   = "#ABB2BF"  # Lighter gray
TEXT_SECONDARY = "#5C6370"  # Medium gray
TEXT_DIM       = "#4B5263"  # Dim gray

# Borders (lighter to match new background)
BORDER_PANEL  = "#3E4451"  # Lighter border
BORDER_INPUT  = "#4B5263"  # Input border
BORDER_ACCENT = "#61AFEF"  # Accent border
```

## Slash commands

| Command             | Mô tả                                  |
|---------------------|----------------------------------------|
| `/add <tên> <ngày>` | Thêm người, VD: `/add Nguyên 20`       |
| `/rm <tên|số>`      | Xóa người theo tên hoặc số thứ tự      |
| `/set elec <số>`    | Đặt tiền điện                          |
| `/set water <số>`   | Đặt tiền nước                          |
| `/set month <số>`   | Đặt tháng                              |
| `/set year <số>`    | Đặt năm                                |
| `/set algo <mode>`  | ratio | stair | equal                  |
| `/calc`             | Tính tiền                              |
| `/history`          | Xem lịch sử                            |
| `/export txt`       | Export kết quả .txt                    |
| `/export csv`       | Export kết quả .csv                    |
| `/copy`             | Copy kết quả vào clipboard             |
| `/save`             | Lưu danh sách người ra file            |
| `/load`             | Tải danh sách người từ file            |
| `/reset`            | Reset toàn bộ                          |
| `/help`             | Hiển thị help                          |
| `/clear`            | Xóa log trên màn hình                  |

## Widget structure

```
BillsTextualApp (App)
└── MainScreen (Screen)
    ├── Header (built-in, show_clock=True)
    ├── ScrollableContainer #content-area
    │   ├── Static #hero              ← gradient figlet
    │   ├── RichLog #output-log       ← chat-style scrollable log
    │   └── Static #status-bar       ← brief context summary
    ├── CommandInput #cmd-input       ← custom widget, bottom bar
    └── Footer (built-in)
```

## RichLog pattern (chat-style output)

Dùng `RichLog` thay vì `Static` cho khu vực kết quả — nó tự scroll và hỗ trợ append:

```python
from textual.widgets import RichLog

log = self.query_one("#output-log", RichLog)
log.write(Panel(table, title="Kết quả", border_style="cyan"))
log.write(Text("✓ Đã lưu lịch sử", style="bold green"))
```

Mỗi lần chạy lệnh → append output xuống log. Người dùng scroll lên xem lại.

## CommandInput widget

Widget custom cho input bar ở dưới, bắt chước style gemini-cli:

```python
class CommandInput(Widget):
    # Hiển thị: "> " prefix với màu accent
    # Placeholder: "Nhập lệnh... /help để xem danh sách"
    # Submit: Enter
    # History: ↑ ↓ để xem lịch sử lệnh đã nhập
```

## CSS conventions

- Dùng `layer` để CommandInput luôn ở dưới màn hình: `dock: bottom`
- Content area dùng `height: 1fr` và `overflow-y: auto`
- Không dùng Horizontal split cho layout chính
- Panel/card dùng `border: round` với màu BORDER_PANEL
- Khoảng cách: `margin: 1 2` (1 dòng trên/dưới, 2 chars trái/phải)

## Quy tắc khi sửa code

1. **Không dùng Button** cho actions chính — tất cả qua slash command hoặc key binding.
2. **Gradient figlet** phải render bằng `pyfiglet` + `rich.text.Text` với gradient Cyan→Magenta.
3. **Mọi output** đều append vào `RichLog`, không replace Static widget.
4. **Thông báo lỗi** hiển thị inline trong log với style `bold red`, không dùng `notify()` popup.
5. **State** (people list, bills context) hiển thị compact ở đầu log mỗi khi thay đổi.

## File mapping

```
bills_calculator/tui/
├── app.py              ← BillsTextualApp, CSS_PATH, BINDINGS
├── screens/
│   ├── main_screen.py  ← MainScreen, compose(), command dispatch
│   └── history_screen.py ← HistoryScreen (giữ nguyên cấu trúc)
├── widgets/
│   ├── header.py       ← build_gradient_figlet_title()
│   ├── command_input.py ← CommandInput widget mới
│   └── result_viewer.py ← build_result_renderable(), build_context_panel()
└── styles/
    └── main.tcss       ← theme, layout, command bar dock
```
