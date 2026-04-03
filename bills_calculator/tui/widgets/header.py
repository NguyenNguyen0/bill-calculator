from __future__ import annotations

from pyfiglet import Figlet
from rich.text import Text


def build_gradient_figlet_title(text: str = "BILLS-CALCULATOR") -> Text:
    figlet = Figlet(font="doom", justify="left", width=180)
    raw_title = figlet.renderText(text)

    styled_title = Text()
    lines = raw_title.splitlines()
    total_lines = len(lines)
    start_color = (0, 170, 255)
    end_color = (156, 92, 255)

    for index, line in enumerate(lines):
        if total_lines > 1:
            ratio = index / (total_lines - 1)
            red = int(start_color[0] + ratio * (end_color[0] - start_color[0]))
            green = int(start_color[1] + ratio * (end_color[1] - start_color[1]))
            blue = int(start_color[2] + ratio * (end_color[2] - start_color[2]))
            color = f"rgb({red},{green},{blue})"
        else:
            color = "rgb(120,120,255)"

        styled_title.append(line + "\n", style=f"bold {color}")

    return styled_title
