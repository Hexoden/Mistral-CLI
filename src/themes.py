"""Mistral CLI - Theme system for customizing terminal appearance."""

import time
import sys
from typing import Dict, Any, Optional
from rich.text import Text
from rich.panel import Panel
from rich.console import Console

# Import Config at module level to avoid potential scope issues
from .config import Config


# ASCII Banner for Mistral CLI
MISTRAL_BANNER = r"""
 /$$      /$$ /$$             /$$                        /$$
| $$$    /$$$|__/            | $$                       | $$
| $$$$  /$$$$ /$$  /$$$$$$$ /$$$$$$    /$$$$$$  /$$$$$$ | $$
| $$ $$/$$ $$| $$ /$$_____/|_  $$_/   /$$__  $$|____  $$| $$
| $$  $$$| $$| $$|  $$$$$$   | $$    | $$  \__/ /$$$$$$$| $$
| $$\  $ | $$| $$ \____  $$  | $$ /$$| $$      /$$__  $$| $$
| $$ \/  | $$| $$ /$$$$$$$/  |  $$$$/| $$     |  $$$$$$$| $$
|__/     |__/|__/|_______/    \___/  |__/      \_______/|__/



  /$$$$$$  /$$       /$$$$$$       /$$$$$$$$                  /$$
 /$$__  $$| $$      |_  $$_/      |__  $$__/                 | $$
| $$  \__/| $$        | $$           | $$  /$$$$$$   /$$$$$$ | $$
| $$      | $$        | $$           | $$ /$$__  $$ /$$__  $$| $$
| $$      | $$        | $$           | $$| $$  \ $$| $$  \ $$| $$
| $$    $$| $$        | $$           | $$| $$  | $$| $$  | $$| $$
|  $$$$$$/| $$$$$$$$ /$$$$$$         | $$|  $$$$$$/|  $$$$$$/| $$
 \______/ |________/|______/         |__/ \______/  \______/ |__/

░█▄█░█▀█░█▀▄░█▀▀░░░█░█░▀█▀░▀█▀░█░█░░░█░░░█▀█░█░█░█▀▀░░░░
░█░█░█▀█░█░█░█▀▀░░░█▄█░░█░░░█░░█▀█░░░█░░░█░█░▀▄▀░█▀▀░░░░
░▀░▀░▀░▀░▀▀░░▀▀▀░░░▀░▀░▀▀▀░░▀░░▀░▀░░░▀▀▀░▀▀▀░░▀░░▀▀▀░▄▀░
░█▀▄░█░█░░░█░█░█▀▀░█░█
░█▀▄░░█░░░░█▀█░█▀▀░▄▀▄
░▀▀░░░▀░░░░▀░▀░▀▀▀░▀░▀
░█░█░░░░▀█░░░░░▄▀▄░░░░▄▀▄
░▀▄▀░░░░░█░░░░░█/█░░░░█/█
░░▀░░▀░░▀▀▀░▀░░░▀░░▀░░░▀░
"""


class Theme:
    """Represents a visual theme for the Mistral CLI."""

    def __init__(
        self,
        name: str,
        banner: Optional[str] = None,
        primary_color: str = "cyan",
        secondary_color: str = "green",
        border_color: str = "blue",
        text_style: str = "white",
        dim_style: str = "dim",
        prompt_prefix: str = ">>> ",
        response_border: str = "blue",
        use_ascii_banner: bool = True,
    ):
        self.name = name
        self.banner = banner
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.border_color = border_color
        self.text_style = text_style
        self.dim_style = dim_style
        self.prompt_prefix = prompt_prefix
        self.response_border = response_border
        self.use_ascii_banner = use_ascii_banner

    def get_banner(self) -> Text:
        """Get the theme's banner as a Rich Text object with left-to-right gradient."""
        if self.use_ascii_banner and self.banner:
            # 6-color gradient, no white
            gradient_colors = ['#6200FF', '#9632FA', '#DE77F2', '#CFBCE9', '#ACDBDC', '#85FECE']

            text = Text()

            # Process line by line for left-to-right gradient on each line
            for line in self.banner.split('\n'):
                line_length = len(line)
                if line_length == 0:
                    text.append('\n')
                    continue

                # Left-to-right gradient for this line only
                for i, char in enumerate(line):
                    position = i / (line_length - 1) if line_length > 1 else 0
                    color_index = int(position * (len(gradient_colors) - 1))
                    color = gradient_colors[color_index % len(gradient_colors)]
                    text.append(char, style=color)

                text.append('\n')

            return text
        else:
            return Text(f"Mistral CLI - {self.name} Theme", style=f"bold {self.primary_color}")

    def create_header(self, model: str, temperature: float, additional_info: str = None):
        """Create the interactive chat header panel."""
        if self.use_ascii_banner and self.banner:
            # For ASCII banners, print with typing effect
            console = Console()
            banner = self.get_banner()

            # Type out the banner with 0.002s delay per character
            with console.capture() as capture:
                console.print(banner)
            rendered = capture.get()

            for char in rendered:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(Config.get_typing_delay("banner"))  # Fixed fast speed for banner

            console.print()

            # Print model info separately
            info_text = Text(f"Model: {model} | Temperature: {temperature}", style=self.secondary_color)
            if additional_info:
                info_text.append(f" | {additional_info}", style=self.dim_style)
            console.print(Panel(info_text, border_style=self.border_color))
            return None
        else:
            # For non-ASCII banners, use the panel approach
            content = self.get_banner()
            content.append("\n", style=self.text_style)
            content.append(f"Model: {model} | Temperature: {temperature}", style=self.secondary_color)
            if additional_info:
                content.append(f"\n{additional_info}", style=self.dim_style)
            return Panel(content, border_style=self.border_color)

    def format_prompt(self, prompt: str) -> Text:
        """Format the user's prompt text."""
        return Text(f"{self.prompt_prefix}{prompt}", style=self.dim_style)

    def format_response(self, response: str) -> str:
        """Format the AI response for display."""
        return response


# Predefined themes
THEMES = {
    "default": Theme(
        name="Default",
        banner=MISTRAL_BANNER,
        primary_color="cyan",
        secondary_color="green",
        border_color="blue",
        prompt_prefix=">>> ",
        use_ascii_banner=True,
    ),
    "mistral": Theme(
        name="Mistral",
        banner=MISTRAL_BANNER,
        primary_color="#6200FF",
        secondary_color="#85FF9B",
        border_color="#85FECE",
        prompt_prefix="💬: ",
        use_ascii_banner=True,
    ),
    "minimal": Theme(
        name="Minimal",
        banner=None,
        primary_color="white",
        secondary_color="dim",
        border_color="dim",
        prompt_prefix="> ",
        use_ascii_banner=False,
    ),
    "retro": Theme(
        name="Retro",
        banner=MISTRAL_BANNER,
        primary_color="yellow",
        secondary_color="green",
        border_color="red",
        prompt_prefix="$ ",
        use_ascii_banner=True,
    ),
    "dark": Theme(
        name="Dark",
        banner=MISTRAL_BANNER,
        primary_color="bright_white",
        secondary_color="bright_cyan",
        border_color="bright_black",
        prompt_prefix="💬 ",
        use_ascii_banner=True,
    ),
}


class ThemeManager:
    """Manages themes for the Mistral CLI."""

    @staticmethod
    def get_theme(name: str = None) -> Theme:
        """Get a theme by name, or the default theme."""
        if name is None:
            name = Config.get("theme", "default")

        if name in THEMES:
            return THEMES[name]
        else:
            # Create a custom theme if it doesn't exist
            return THEMES["default"]

    @staticmethod
    def list_themes() -> list:
        """List all available themes."""
        return list(THEMES.keys())

    @staticmethod
    def set_default_theme(name: str) -> bool:
        """Set the default theme."""
        if name in THEMES:
            Config.set("theme", name)
            return True
        return False

    @staticmethod
    def create_custom_theme(
        name: str,
        banner: str = None,
        primary_color: str = "cyan",
        secondary_color: str = "green",
        border_color: str = "blue",
        prompt_prefix: str = ">>> ",
        use_ascii_banner: bool = False,
    ) -> Theme:
        """Create a custom theme and add it to the available themes."""
        THEMES[name] = Theme(
            name=name,
            banner=banner,
            primary_color=primary_color,
            secondary_color=secondary_color,
            border_color=border_color,
            prompt_prefix=prompt_prefix,
            use_ascii_banner=use_ascii_banner,
        )
        return THEMES[name]
