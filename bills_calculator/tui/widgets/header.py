from __future__ import annotations

from pyfiglet import Figlet
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.box import ROUNDED

from bills_calculator.core.models import BillsData


def build_gradient_figlet_title(text: str = "BILLS-CALCULATOR") -> Text:
    """Render figlet text with Soft Cyan → Soft Magenta gradient, matching One Dark theme."""
    figlet = Figlet(font="doom", justify="left", width=180)
    raw_title = figlet.renderText(text)

    styled_title = Text()
    lines = raw_title.splitlines()
    total_lines = len(lines)

    start_color = (97, 218, 251)    # Soft Cyan #61DAFB
    end_color   = (198, 120, 221)   # Soft Magenta #C678DD

    for i, line in enumerate(lines):
        if total_lines > 1:
            ratio = i / (total_lines - 1)
            r = int(start_color[0] + ratio * (end_color[0] - start_color[0]))
            g = int(start_color[1] + ratio * (end_color[1] - start_color[1]))
            b = int(start_color[2] + ratio * (end_color[2] - start_color[2]))
            color = f"rgb({r},{g},{b})"
        else:
            color = "rgb(97,218,251)"

        styled_title.append(line + "\n", style=f"bold {color}")

    return styled_title
