#!/usr/bin/env python3
"""Mistral CLI - Main entry point for the command-line interface."""

import os
import click
import time
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from .client import MistralClient
from .config import Config
from .themes import ThemeManager

console = Console()


@click.group(
    name="mistral",
    help="A command-line interface for Mistral AI.",
    invoke_without_command=True,
)
@click.pass_context
@click.option(
    "--version", "-v",
    is_flag=True,
    help="Show version and exit.",
)
@click.option(
    "--config", "-c",
    type=click.Path(),
    help="Path to config file.",
)
def cli(ctx, version, config):
    """Main CLI entry point."""
    if version:
        from . import __version__
        console.print(f"Mistral CLI v{__version__}")
        ctx.exit()

    # Initialize config
    if config:
        Config.load(config)
    else:
        Config.load()

    # Initialize client (will fail gracefully if no API key)
    try:
        ctx.obj = MistralClient()
    except ValueError as e:
        ctx.obj = None

    # If no subcommand, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.pass_context
@click.option(
    "--model", "-m",
    default=None,
    help="Model to use (e.g., mistral-tiny, mistral-small, mistral-medium).",
)
@click.option(
    "--temperature", "-t",
    type=float,
    default=0.7,
    help="Sampling temperature (0.0 to 1.0).",
)
@click.option(
    "--max-tokens",
    type=int,
    default=None,
    help="Maximum number of tokens to generate.",
)
@click.option(
    "--stream", "-s",
    is_flag=True,
    default=False,
    help="Stream the response token by token.",
)
@click.argument("prompt", type=str, required=False)
def chat(ctx, model, temperature, max_tokens, stream, prompt):
    """Start a chat session with Mistral AI."""
    client = ctx.obj

    if client is None:
        console.print("[red]Error:[/red] MISTRAL_API_KEY not set. Please set it first.")
        console.print("Run: mistral config --key YOUR_API_KEY")
        console.print("Or: export MISTRAL_API_KEY=your_api_key_here")
        ctx.exit(1)

    # Track if user explicitly provided a model
    explicit_model = model is not None

    # Use default model from config if not specified
    if model is None:
        model = Config.get("default_model", None)

    # If no prompt provided, start interactive mode
    if not prompt:
        # Show model selector if no model was explicitly specified via -m flag
        if not explicit_model:
            selected_model = select_model_interactively(client)
            if selected_model:  # User made a selection
                model = selected_model
            elif model is None:  # User cancelled and no default
                model = "mistral-tiny"
        interactive_chat(client, model, temperature, max_tokens, stream)
        return

    # Single prompt mode - use config default if model not specified
    if model is None:
        model = Config.get("default_model", "mistral-tiny")

    # Single prompt mode
    try:
        theme = ThemeManager.get_theme()
        console.print(f"[dim]Using model: {model}[/dim]")

        response = client.complete(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        if stream:
            console.print(f"[dim]Using model: {model}[/dim]")
            for chunk in response:
                sys.stdout.write(chunk)
                sys.stdout.flush()
                time.sleep(Config.get_typing_delay("cli"))  # CLI typing delay
            sys.stdout.write('\n')
        else:
            from rich.markup import escape
            # Type out the response with typing effect
            panel = Panel.fit(escape(response), title="AI Response", border_style=theme.response_border)
            with console.capture() as capture:
                console.print(panel)
            rendered = capture.get()

            for char in rendered:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(Config.get_typing_delay("cli"))  # CLI typing delay
            sys.stdout.write('\n')
    except Exception as e:
        from rich.markup import escape
        theme = ThemeManager.get_theme()
        console.print(f"[{theme.secondary_color}]Error:[/{theme.secondary_color}] {escape(str(e))}")
        ctx.exit(1)


def _select_file_browser():
    """Show a simple terminal file browser to select a file."""
    import os
    import sys
    from pathlib import Path
    
    console.print("[blue]File Browser[/blue] - Use numbers to select, 0 for parent directory, q to quit")
    
    # Start from user's home directory
    current_dir = Path.home()
    
    while True:
        try:
            # List files and directories
            items = []
            try:
                for item in current_dir.iterdir():
                    if item.is_file() and item.suffix.lower() in ['.txt', '.md', '.markdown', '.py', '.json', '.yaml', '.yml', '.csv', '.log', '.html', '.htm', '.xml', '.sql', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.hpp', '']:
                        items.append((f"📄 {item.name}", str(item), True))
                    elif item.is_dir():
                        items.append((f"📁 {item.name}/", str(item), False))
            except PermissionError:
                console.print("[red]Permission denied[/red] reading directory")
                return None
            
            if not items:
                console.print("[yellow]No readable files found in this directory.[/yellow]")
                return None
                
            # Sort items: directories first, then files alphabetically
            items.sort(key=lambda x: (x[2], x[0]))  # directories (False) come before files (True)
            
            console.print(f"\n[green]Current directory: {current_dir}[/green]")
            console.print("Available items:")
            
            # Display items in a two-column grid
            terminal_width = console.width
            if terminal_width == 0:
                terminal_width = 80  # Default fallback
            
            # Calculate column width (half of terminal width, minus padding)
            col_width = (terminal_width - 10) // 2
            
            # Display items in two columns
            for i in range(0, len(items), 2):
                left_item = items[i]
                left_text = f"  {i+1}. {left_item[0]}"
                
                if i + 1 < len(items):
                    right_item = items[i + 1]
                    right_text = f"  {i+2}. {right_item[0]}"
                    # Pad left text to align properly
                    left_text_padded = left_text.ljust(col_width)
                    console.print(f"{left_text_padded}{right_text}")
                else:
                    console.print(left_text)
            
            # Handle navigation options
            options_text = f"  0. Go to parent directory"
            quit_text = f"  q. Quit"
            console.print(f"{options_text.ljust(col_width)}{quit_text}")
            
            # Simple numeric selection
            choice = input("Select a file or directory (number, 0 for parent, q to quit): ").strip()
            
            if choice.lower() == 'q':
                return None
            elif choice == '0':
                if current_dir.parent != current_dir:  # Don't go above root
                    current_dir = current_dir.parent
                else:
                    console.print("[yellow]Already at root directory[/yellow]")
            elif choice.isdigit():
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(items):
                    display_name, path, is_file = items[choice_idx]
                    if is_file:
                        return path
                    else:
                        current_dir = Path(path)
                else:
                    console.print("[red]Invalid selection[/red]")
            else:
                console.print("[red]Invalid input. Please enter a number, 0, or q.[/red]")
                
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]File selection cancelled.[/yellow]")
            return None
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            return None


@cli.command()
@click.pass_context
@click.option(
    "--model", "-m",
    default=None,
    help="Model to use.",
)
@click.option(
    "--temperature", "-t",
    type=float,
    default=0.7,
    help="Sampling temperature.",
)
@click.option(
    "--max-tokens",
    type=int,
    default=None,
    help="Maximum number of tokens.",
)
@click.argument("file", type=click.Path(exists=True), required=False)
def file(ctx, model, temperature, max_tokens, file):
    """Process a file with Mistral AI."""
    client = ctx.obj

    # If no file provided, show file browser
    if file is None:
        file = _select_file_browser()
        if file is None:
            console.print("[yellow]No file selected. Aborting.[/yellow]")
            return

    # Use default model from config if not specified
    if model is None:
        model = Config.get("default_model", "mistral-tiny")

    if client is None:
        console.print("[red]Error:[/red] MISTRAL_API_KEY not set. Please set it first.")
        console.print("Run: mistral config --key YOUR_API_KEY")
        console.print("Or: export MISTRAL_API_KEY=your_api_key_here")
        ctx.exit(1)

    try:
        with open(file, "r") as f:
            content = f.read()

        theme = ThemeManager.get_theme()
        console.print(f"[{theme.secondary_color}]Processing {file}[/{theme.secondary_color}]...")

        response = client.complete(
            prompt=content,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        from rich.markup import escape
        console.print(Panel.fit(escape(response), title=f"Response for {file}", border_style=theme.response_border))
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        ctx.exit(1)


@cli.command()
@click.pass_context
def models(ctx):
    """List available Mistral models from the API with typing effect."""
    client = ctx.obj

    if client is None:
        console.print("[yellow]Warning:[/yellow] No API key set. Showing default model list.")
        console.print("Set your API key with: mistral config --key YOUR_API_KEY")

        # Fallback to hardcoded list if no API access
        table = Table(title="Available Mistral Models (Default List)")
        table.add_column("Model ID", style="cyan")
        table.add_column("Description", style="green")

        models = [
            ("mistral-tiny", "Fast and efficient for simple tasks"),
            ("mistral-small", "Balanced performance and cost"),
            ("mistral-medium", "More powerful, higher cost"),
            ("mistral-large", "Most powerful model"),
            ("codestral-latest", "Code generation specialized"),
            ("mistral-embed", "Embeddings model"),
            ("le-chonk", "Large model with extended context"),
        ]
    else:
        # Get models from API
        table = Table(title="Available Mistral Models (From API)")
        table.add_column("Model ID", style="cyan")
        table.add_column("Description", style="green")

        try:
            api_models = client.list_models()
            if api_models:
                for model in api_models:
                    model_id = model.get('id', 'Unknown')
                    description = model.get('description', model.get('object', 'No description'))
                    table.add_row(str(model_id), str(description))
            else:
                console.print("[yellow]No models found from API, using default list.[/yellow]")
                models = [
                    ("mistral-tiny", "Fast and efficient for simple tasks"),
                    ("mistral-small", "Balanced performance and cost"),
                    ("mistral-medium", "More powerful, higher cost"),
                    ("mistral-large", "Most powerful model"),
                    ("codestral-latest", "Code generation specialized"),
                    ("mistral-embed", "Embeddings model"),
                    ("le-chonk", "Large model with extended context"),
                ]
                for model_id, description in models:
                    table.add_row(model_id, description)
        except Exception as e:
            console.print(f"[yellow]Could not fetch models from API: {e}[/yellow]")
            console.print("Using default model list...")
            models = [
                ("mistral-tiny", "Fast and efficient for simple tasks"),
                ("mistral-small", "Balanced performance and cost"),
                ("mistral-medium", "More powerful, higher cost"),
                ("mistral-large", "Most powerful model"),
                ("codestral-latest", "Code generation specialized"),
                ("mistral-embed", "Embeddings model"),
                ("le-chonk", "Large model with extended context"),
            ]
            for model_id, description in models:
                table.add_row(model_id, description)

    # Print with typing effect
    with console.capture() as capture:
        console.print(table)
    rendered = capture.get()

    # Type out the table with visible speed
    sys.stdout.write('\n')  # Start on new line after config messages
    for char in rendered:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(Config.get_typing_delay("models"))  # Fixed fast speed for models list
    sys.stdout.write('\n')  # Final newline


@cli.command()
@click.argument("theme_name", required=False)
def theme(theme_name):
    """Set or list available themes."""
    themes = ThemeManager.list_themes()

    if not theme_name:
        # List available themes
        console.print("Available themes:")
        current_theme = Config.get("theme", "default")
        for theme in themes:
            marker = "✓" if theme == current_theme else " "
            console.print(f"  {marker} {theme}")
        return

    if theme_name in themes:
        ThemeManager.set_default_theme(theme_name)
        console.print(f"[green]Theme set to '{theme_name}'[/green]")
    else:
        console.print(f"[red]Theme '{theme_name}' not found. Available: {', '.join(themes)}[/red]")


@cli.command()
@click.argument("speed", required=False)
def typing(speed):
    """Set or show typing speed for banner and AI responses."""
    speeds = {
        "off": "Disable typing effect",
        "very_fast": "Very fast (instant)",
        "fast": "Fast",
        "medium": "Medium (default)",
        "slow": "Slow",
        "very_slow": "Very slow",
    }

    if not speed:
        # Show current typing speed
        current_speed = Config.get("typing_speed", "medium")
        console.print("Available typing speeds:")
        for speed_name, description in speeds.items():
            marker = "✓" if speed_name == current_speed else " "
            console.print(f"  {marker} {speed_name}: {description}")
        return

    if speed in speeds:
        Config.set("typing_speed", speed)
        console.print(f"[green]Typing speed set to '{speed}'[/green]")
    else:
        console.print(f"[red]Typing speed '{speed}' not found. Available: {', '.join(speeds.keys())}[/red]")


@cli.command()
@click.option(
    "--key", "-k",
    help="Set API key directly.",
)
@click.option(
    "--model", "-m",
    help="Set default model.",
)
@click.option(
    "--theme", "-t",
    help="Set default theme.",
)
@click.option(
    "--name", "-n",
    help="Set your name for AI conversations.",
)
def config(key, model, theme, name):
    """Configure Mistral CLI settings."""
    theme_manager = ThemeManager

    if key:
        Config.set("api_key", key)
        console.print("[green]API key saved to config.[/green]")
        console.print("You can now use the CLI commands.")

    if model:
        Config.set("default_model", model)
        console.print(f"[green]Default model set to {model}[/green]")

    if theme:
        if theme in theme_manager.list_themes():
            Config.set("theme", theme)
            console.print(f"[green]Default theme set to {theme}[/green]")
        else:
            console.print(f"[red]Theme '{theme}' not found. Available: {', '.join(theme_manager.list_themes())}[/red]")

    if name:
        Config.set("name", name)
        console.print(f"[green]Your name set to {name}[/green]")

    if not key and not model and not theme and not name:
        console.print("Current configuration:")
        for k, v in Config.get_all().items():
            if "key" in k.lower():
                console.print(f"  {k}: {'*' * len(str(v)) if v else 'Not set'}")
            else:
                console.print(f"  {k}: {v}")


@cli.command(name="which")
def cli_which():
    """Show the path to the mistral command."""
    import sys
    import os
    
    # Detect the operating system
    is_windows = os.name == 'nt'
    
    if is_windows:
        # On Windows, try to find the command path
        try:
            import subprocess
            result = subprocess.run(['where', 'mistral'], capture_output=True, text=True, shell=True)
            if result.stdout.strip():
                console.print(result.stdout.strip())
            else:
                # Fallback: try to find it in common locations
                venv_path = os.path.join(os.path.dirname(__file__), "..", "venv", "Scripts", "mistral.exe")
                if os.path.exists(venv_path):
                    console.print(venv_path)
                else:
                    console.print("[yellow]Could not find mistral command. Make sure your venv is activated.[/yellow]")
        except Exception:
            console.print("[yellow]Could not find mistral command. Make sure your venv is activated.[/yellow]")
    else:
        # On Linux/macOS
        try:
            import subprocess
            result = subprocess.run(['which', 'mistral'], capture_output=True, text=True)
            if result.stdout.strip():
                console.print(result.stdout.strip())
            else:
                # Fallback: try to find it in common locations
                venv_path = os.path.join(os.path.dirname(__file__), "..", "venv", "bin", "mistral")
                if os.path.exists(venv_path):
                    console.print(venv_path)
                else:
                    console.print("[yellow]Could not find mistral command. Make sure your venv is activated.[/yellow]")
        except Exception:
            console.print("[yellow]Could not find mistral command. Make sure your venv is activated.[/yellow]")


@cli.command(name="where")
def cli_where():
    """Show the path to the mistral command (Windows-style)."""
    import os
    
    # Detect the operating system
    is_windows = os.name == 'nt'
    
    if is_windows:
        # On Windows, use where command
        try:
            import subprocess
            result = subprocess.run(['where', 'mistral'], capture_output=True, text=True, shell=True)
            if result.stdout.strip():
                console.print(result.stdout.strip())
            else:
                # Fallback: try to find it in common locations
                venv_path = os.path.join(os.path.dirname(__file__), "..", "venv", "Scripts", "mistral.exe")
                if os.path.exists(venv_path):
                    console.print(venv_path)
                else:
                    console.print("[yellow]Could not find mistral command. Make sure your venv is activated.[/yellow]")
        except Exception:
            console.print("[yellow]Could not find mistral command. Make sure your venv is activated.[/yellow]")
    else:
        # User is on Linux/macOS but used 'where' command
        console.print("You are on Linux silly, try {mistral which}")


@cli.command(name="silly")
def cli_silly():
    """Easter egg command for the which/where functionality."""
    import os
    
    is_windows = os.name == 'nt'
    
    if is_windows:
        console.print("You are on Windows silly, try {mistral where}")
    else:
        console.print("You are on Linux silly, try {mistral which}")


@cli.command(name="locate")
def cli_locate():
    """Show the path to the mistral command (platform-agnostic)."""
    import os
    import sys
    
    # Detect the operating system
    is_windows = os.name == 'nt'
    
    if is_windows:
        # On Windows, try to find the command path
        try:
            import subprocess
            result = subprocess.run(['where', 'mistral'], capture_output=True, text=True, shell=True)
            if result.stdout.strip():
                console.print(result.stdout.strip())
            else:
                # Fallback: try to find it in common locations
                venv_path = os.path.join(os.path.dirname(__file__), "..", "venv", "Scripts", "mistral.exe")
                if os.path.exists(venv_path):
                    console.print(venv_path)
                else:
                    console.print("[yellow]Could not find mistral command. Make sure your venv is activated.[/yellow]")
        except Exception:
            console.print("[yellow]Could not find mistral command. Make sure your venv is activated.[/yellow]")
    else:
        # On Linux/macOS
        try:
            import subprocess
            result = subprocess.run(['which', 'mistral'], capture_output=True, text=True)
            if result.stdout.strip():
                console.print(result.stdout.strip())
            else:
                # Fallback: try to find it in common locations
                venv_path = os.path.join(os.path.dirname(__file__), "..", "venv", "bin", "mistral")
                if os.path.exists(venv_path):
                    console.print(venv_path)
                else:
                    console.print("[yellow]Could not find mistral command. Make sure your venv is activated.[/yellow]")
        except Exception:
            console.print("[yellow]Could not find mistral command. Make sure your venv is activated.[/yellow]")


def show_help_in_chat():
    """Display help menu during interactive chat."""
    theme = ThemeManager.get_theme()
    console.print(f"[{theme.secondary_color}]=== CLI Help ===[/{theme.secondary_color}]")
    console.print()
    console.print(f"[{theme.secondary_color}]Available Commands:[/{theme.secondary_color}]")
    console.print("  help, /help, ?             - Show this help menu")
    console.print("  exit, quit, q               - Exit the chat session")
    console.print("  /models                    - List available models")
    console.print("  /switch {name}             - Switch to a different model")
    console.print("  /theme {name}              - Switch to a different theme")
    console.print("  /config                    - Show current configuration")
    console.print("  /typing [{speed}]          - Set chat typing speed (off/very_fast/fast/medium/slow/very_slow)")
    console.print("  /dance                     - Show dancing parrot animation 🦜")
    console.print()
    console.print(f"[{theme.secondary_color}]Current Settings:[/{theme.secondary_color}]")

    # Show current config
    current_model = Config.get("default_model", "not set")
    current_theme = Config.get("theme", "not set")
    console.print(f"  Model: {current_model}")
    console.print(f"  Theme: {current_theme}")
    console.print()
    console.print(f"[{theme.secondary_color}]Type your message to continue chatting...[/{theme.secondary_color}]")
    console.print()


def select_model_interactively(client):
    """Show interactive model selector and return selected model."""
    theme = ThemeManager.get_theme()

    # Check if there's a default model in config
    default_model = Config.get("default_model", None)

    # First ask if user wants to use default model
    if default_model:
        while True:
            try:
                choice = input(f"Use default model '{default_model}'? (y[or enter] /n): ").strip().lower()
                if choice in ('y', 'yes', ''):
                    return default_model
                elif choice in ('n', 'no'):
                    break
                else:
                    console.print("Please enter 'y' for yes or 'n' for no.")
            except (KeyboardInterrupt, EOFError):
                console.print()
                return default_model

    # If no default or user said no, show model list
    # Try to get models from API first
    models = []
    if client:
        try:
            api_models = client.list_models()
            if api_models:
                models = [(m.get('id', m.id if hasattr(m, 'id') else 'unknown'),
                          m.get('description', 'No description') or
                          (m.description if hasattr(m, 'description') else 'No description'))
                         for m in api_models]
        except Exception:
            pass

    # Fallback to default list if API failed
    if not models:
        models = [
            ("mistral-tiny", "Fast and efficient for simple tasks"),
            ("mistral-small-latest", "Balanced performance and cost"),
            ("mistral-medium-latest", "More powerful, higher cost"),
            ("mistral-large-latest", "Most powerful model"),
            ("codestral-latest", "Code generation specialized"),
        ]

    console.print(f"[{theme.secondary_color}]Select a model:[/{theme.secondary_color}]")

    # Display models with numbers
    for i, (model_id, description) in enumerate(models, 1):
        console.print(f"  {i}. {model_id} - {description}")

    # Get user selection
    while True:
        try:
            choice = input(f"Enter model number (1-{len(models)}) or model name: ").strip()

            if not choice:
                # Use first model if no input
                return models[0][0] if models else "mistral-tiny"

            # Try as number first
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(models):
                    return models[choice_idx][0]
                else:
                    console.print(f"[{theme.secondary_color}]Please enter a number between 1 and {len(models)}[/{theme.secondary_color}]")
                    continue
            except ValueError:
                # Try as model name
                for model_id, _ in models:
                    if choice.lower() == model_id.lower():
                        return model_id
                console.print(f"[{theme.secondary_color}]Model not found. Try again.[/{theme.secondary_color}]")
        except (KeyboardInterrupt, EOFError):
            console.print()
            return models[0][0] if models else "mistral-tiny"


def interactive_chat(client, model, temperature, max_tokens, stream):
    """Run an interactive chat session."""
    theme = ThemeManager.get_theme()

    # Display themed header
    header = theme.create_header(model, temperature, "Type 'exit' or 'quit' to end the session | type 'help' or '?' for menu options")
    if header is not None:
        console.print(header)

    history = []

    while True:
        try:
            from rich.markup import escape
            # Use theme's prompt prefix with model info
            prompt = input(theme.prompt_prefix)

            if prompt.lower() in ('exit', 'quit', 'q'):
                console.print(f"[{theme.secondary_color}]Goodbye![/{theme.secondary_color}]")
                break

            if prompt.lower() in ('help', '/help', '?'):
                show_help_in_chat()
                continue

            elif prompt.lower().startswith('/models'):
                # List available models
                theme = ThemeManager.get_theme()
                try:
                    api_models = client.list_models()
                    if api_models:
                        console.print(f"[{theme.secondary_color}]Available Models:[/{theme.secondary_color}]")
                        for i, m in enumerate(api_models, 1):
                            model_id = m.get('id', m.id if hasattr(m, 'id') else 'unknown')
                            desc = m.get('description', 'No description') or getattr(m, 'description', 'No description')
                            console.print(f"  {i}. {model_id} - {desc}")
                    else:
                        console.print("[yellow]Could not fetch models from API[/yellow]")
                except Exception:
                    console.print("[yellow]Could not fetch models from API[/yellow]")
                continue

            elif prompt.lower().startswith('/switch '):
                # Switch model
                new_model = prompt[8:].strip()
                if new_model:
                    model = new_model
                    console.print(f"[green]Switched to model: {model}[/green]")
                else:
                    console.print("[red]Please specify a model name after /switch[/red]")
                continue

            elif prompt.lower().startswith('/theme '):
                # Switch theme
                new_theme = prompt[7:].strip()
                if new_theme:
                    themes = ThemeManager.list_themes()
                    if new_theme in themes:
                        ThemeManager.set_default_theme(new_theme)
                        console.print(f"[green]Switched to theme: {new_theme}[/green]")
                        theme = ThemeManager.get_theme()  # Refresh theme
                    else:
                        console.print(f"[red]Theme '{new_theme}' not found. Available: {', '.join(themes)}[/red]")
                else:
                    console.print("[red]Please specify a theme name after /theme[/red]")
                continue

            elif prompt.lower() == '/config':
                # Show current configuration
                theme = ThemeManager.get_theme()
                console.print(f"[{theme.secondary_color}]Current Configuration:[/{theme.secondary_color}]")
                for k, v in Config.get_all().items():
                    if "key" in k.lower():
                        console.print(f"  {k}: {'*' * len(str(v)) if v else 'Not set'}")
                    else:
                        console.print(f"  {k}: {v}")
                continue

            elif prompt.lower().startswith('/typing'):
                # Handle typing speed command (chat-specific)
                parts = prompt.split()
                if len(parts) > 1:
                    speed = parts[1]
                    speeds = {"off", "very_fast", "fast", "medium", "slow", "very_slow"}
                    if speed in speeds:
                        Config.set("chat_typing_speed", speed)
                        console.print(f"[green]Chat typing speed set to '{speed}'[/green]")
                    else:
                        console.print(f"[red]Invalid speed. Available: {', '.join(speeds)}[/red]")
                else:
                    # Show current typing speed
                    current_speed = Config.get("chat_typing_speed", "medium")
                    console.print(f"[green]Current chat typing speed: {current_speed}[/green]")
                    console.print("Available: off, very_fast, fast, medium, slow, very_slow")
                continue

            elif prompt.lower() == '/dance':
                # Display animated dancing parrot
                dance_parrot(model, temperature)
                continue

            if not prompt.strip():
                continue

            # Show model info for the prompt
            console.print(f"[dim]Model: {model}[/dim]")

            response = client.complete(
                prompt=prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                history=history,
            )

            if stream:
                for chunk in response:
                    sys.stdout.write(chunk)
                    sys.stdout.flush()
                    time.sleep(Config.get_typing_delay("chat"))  # Chat-specific typing delay
                sys.stdout.write('\n')
            else:
                # Use theme's styling for response with typing effect
                from rich.markup import escape

                # Create the panel
                escaped_response = escape(response)
                panel = Panel.fit(
                    escaped_response,
                    title="AI Response",
                    border_style=theme.response_border
                )

                # Render and type out the panel
                with console.capture() as capture:
                    console.print(panel)
                rendered = capture.get()

                for char in rendered:
                    sys.stdout.write(char)
                    sys.stdout.flush()
                    time.sleep(Config.get_typing_delay("chat"))  # Chat-specific typing delay
                sys.stdout.write('\n')

            # Add to history
            history.append({"role": "user", "content": prompt})
            if not stream:
                history.append({"role": "assistant", "content": response})

        except KeyboardInterrupt:
            console.print(f"\n[{theme.secondary_color}]Interrupted. Type 'exit' to quit.[/{theme.secondary_color}]")
        except EOFError:
            console.print(f"\n[{theme.secondary_color}]Goodbye![/{theme.secondary_color}]")
            break
        except Exception as e:
            from rich.markup import escape
            console.print(f"[{theme.secondary_color}]Error:[/{theme.secondary_color}] {escape(str(e))}")


def dance_parrot(model=None, temperature=None):
    """Display an animated dancing parrot from parrot.live in the terminal."""
    theme = ThemeManager.get_theme()

    # Get parrot.live frames
    frames = get_parrot_live_frames()

    if not frames:
        console.print("[yellow]Parrot frames not found![/yellow]")
        console.print("The parrot has finished dancing! 🎉")
        return

    # Print dancing message once using theme colors
    message = "🦜 OOOOH, you wanna go dancing?! 💃"
    console.print(f"[{theme.secondary_color}]{message}[/{theme.secondary_color}]")
    console.print()  # Empty line after message
    sys.stdout.flush()

    # Use the banner gradient colors from themes.py
    gradient_colors = ['#6200FF', '#9632FA', '#DE77F2', '#CFBCE9', '#ACDBDC', '#85FECE']

    # Display animation - using Rich's Live display for smooth animation
    try:
        from rich.live import Live
        from rich.text import Text

        # Use Live to handle animation with proper overwriting
        with Live(console=console, refresh_per_second=14) as live:
            for loop in range(3):  # Loop through all frames 3 times
                for i, frame in enumerate(frames):
                    # Cycle through banner gradient colors
                    color_index = i % len(gradient_colors)
                    color = gradient_colors[color_index]
                    colored_frame = Text(frame, style=color)
                    live.update(colored_frame)
                    time.sleep(0.07)
    except ImportError:
        # Fallback if rich.live is not available - simple animation with ANSI codes
        try:
            # Map gradient hex colors to closest ANSI color codes
            ansi_gradient_colors = ['\033[35m', '\033[95m', '\033[35m', '\033[96m', '\033[96m', '\033[92m']
            # Purple -> Bright Purple -> Purple -> Bright Cyan -> Bright Cyan -> Bright Green

            # Save cursor position
            sys.stdout.write('\033[s')
            sys.stdout.flush()

            for loop in range(3):
                for i, frame in enumerate(frames):
                    if loop > 0 or i > 0:
                        sys.stdout.write('\033[u\033[J')  # Restore and clear

                    color_index = i % len(ansi_gradient_colors)
                    color_code = ansi_gradient_colors[color_index]
                    sys.stdout.write(color_code + frame + '\033[0m')
                    sys.stdout.flush()
                    time.sleep(0.07)
        finally:
            sys.stdout.write('\033[u\033[J')
            sys.stdout.flush()

    # Print completion message
    console.print("Disco dancing! 🎉")
    console.print()


def _get_ansi_color_code(color_name: str) -> str:
    """Convert Rich color name to ANSI escape code."""
    color_mapping = {
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'bright_black': '\033[90m',
        'bright_red': '\033[91m',
        'bright_green': '\033[92m',
        'bright_yellow': '\033[93m',
        'bright_blue': '\033[94m',
        'bright_magenta': '\033[95m',
        'bright_cyan': '\033[96m',
        'bright_white': '\033[97m',
    }
    return color_mapping.get(color_name, '\033[37m')  # Default to white




def get_parrot_live_frames():
    """Get dancing parrot frames from parrot.live project.

    These are authentic dancing parrot ASCII art frames from:
    https://github.com/hugomd/parrot.live

    All frames are embedded directly in this project for the /dance command.
    """
    # Try to load from local project frames directory first
    local_frames_path = os.path.join(os.path.dirname(__file__), "frames")
    if os.path.exists(local_frames_path):
        try:
            frames = []
            for i in range(10):
                frame_path = os.path.join(local_frames_path, f"{i}.txt")
                if os.path.exists(frame_path):
                    with open(frame_path, 'r', encoding='utf-8') as f:
                        frame = f.read()
                    # Clean up the frame: strip trailing whitespace from each line and trailing newlines
                    lines = [line.rstrip() for line in frame.split('\n') if line.strip()]
                    frames.append('\n'.join(lines))
            if len(frames) == 10:
                return frames
        except Exception:
            pass

    # Fallback to external parrot.live project if available
    parrot_live_path = "/home/hex/Documents/Coding/parrot.live/frames"
    if os.path.exists(parrot_live_path):
        try:
            frames = []
            for i in range(10):
                frame_path = os.path.join(parrot_live_path, f"{i}.txt")
                if os.path.exists(frame_path):
                    with open(frame_path, 'r', encoding='utf-8') as f:
                        frame = f.read()
                    # Clean up the frame: strip trailing whitespace from each line and trailing newlines
                    lines = [line.rstrip() for line in frame.split('\n') if line.strip()]
                    frames.append('\n'.join(lines))
            if len(frames) == 10:
                return frames
        except Exception:
            pass

    # Fallback to embedded frames
    return [
        """                         .cccc;;cc;';c.
                      .,:dkdc:;;:c:,:d:.
                     .loc'.,cc::c:::,..;:.
                   .cl;....;dkdccc::,...c;
                  .c:,';:'..ckc',;::;....;c.
                .c:'.,dkkoc:ok:;llllc,,c,';:.
               .;c,';okkkkkkkk:;lllll,:kd;.;:,.
               co..:kkkkkkkkkk:;llllc':kkc..oNc
             .cl;.,oxkkkkkkkkkc,:cll;,okkc'.cO;
             ;k:..ckkkkkkkkkkkl..,;,.;xkko:',l'
            .,...';dkkkkkkkkkkd;.....ckkkl'.cO;
         .,,:,.;oo:ckkkkkkkkkkkdoc;;cdkkkc..cd,
      .cclo;,ccdkkl;llccdkkkkkkkkkkkkkkkd,.c;
     .lol:;;okkkkkxooc::coodkkkkkkkkkkkko'.oc
   .c:'..lkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkd,.oc
  .lo;,:cdkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkd,.c;
,dx:..;lllllllllllllllllllllllllllllllllc'...
cNO;........................................      """,
        """                .ckx;'........':c.
             .,:c:::::oxxocoo::::,',.
            .odc'..:lkkoolllllo;..;d,
            ;c..:o:..;:..',;'.......;.
           ,c..:0Xx::o:.,cllc:,'::,.,c.
           ;c;lkXKXXXXl.;lllll;lKXOo;':c.
         ,dc.oXXXXXXXXl.,lllll;lXXXXx,c0:
         ;Oc.oXXXXXXXXo.':ll:;'oXXXXO;,l'
         'l;;kXXXXXXXXd'.'::'..dXXXXO;,l'
         'l;:0XXXXXXXX0x:...,:o0XXXXx,:x,
         'l;;kXXXXXXXXXKkol;oXXXXXXXO;oNc
        ,c'..ckk0XXXXXXXXXX00XXXXXXX0:;o:.
      .':;..:do::ooookXXXXXXXXXXXXXXXo..c;
    .',',:co0XX0kkkxxOXXXXXXXXXXXXXXXOc..;l.
  .:;'..oXXXXXXXXXXXXXXXXXXXXXXXXXXXXXko;';:.
.ldc..:oOXKXXXXXXKXXKXXXXXXXXXXXXXXXXXXXo..oc
:0o...:dxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxo,.:,
cNo........................................;'     """,
        """            .cc;.  ...  .;c.
         .,,cc:cc:lxxxl:ccc:;,.
        .lo;...lKKklllookl..cO;
      .cl;.,:'.okl;..''.;,..';:.
     .:o;;dkd,.ll..,cc::,..,'.;:.
     co..lKKKkokl.':lloo;''ol..;dl.
   .,c;.,xKKKKKKo.':llll;.'oOxl,.cl,.
   cNo..lKKKKKKKo'';llll;;okKKKl..oNc
   cNo..lKKKKKKKko;':c:,'lKKKKKo'.oNc
   cNo..lKKKKKKKKKl.....'dKKKKKxc,l0:
   .c:'.lKKKKKKKKKk;....lKKKKKKo'.oNc
     ,:.'oxOKKKKKKKOxxxxOKKKKKKxc,;ol:.
     ;c..'':oookKKKKKKKKKKKKKKKKKk:.'clc.
   .xl'.,oxo;'';oxOKKKKKKKKKKKKKKKOxxl:::;,.
  .dOc..lKKKkoooookKKKKKKKKKKKKKKKKKxl,;ol.
  cx,';okKKKKKKKKKKKKKKKKKKKKKKKKKKKKl..;lc.
  co..:dddddddddddddddddddddddddddddddddl::',::.
  co...........................................   """,
        """           .ccccccc.
      .,,,;cooolccoo;;,,.
     .dOx;..;lllll;..;xOd.
   .cdo;',loOXXXXXkll;';odc.
  ,ol:;c,':oko:cccccc,...ckl.
  ;c.;kXo..::..;c::'.......oc
,dc..oXX0kk0o.':lll;..cxxc.,ld,
kNo.'oXXXXXXo',:lll;..oXXOo;cOd.
KOc;oOXXXXXXo.':lol;..dXXXXl';xc
Ol,:k0XXXXXX0c.,clc'.:0XXXXx,.oc
KOc;dOXXXXXXXl..';'..lXXXXXo..oc
dNo..oXXXXXXXOx:..'lxOXXXXXk,.:; ..
cNo..lXXXXXXXXXOolkXXXXXXXXXkl,..;:';.
.,;'.,dkkkkk0XXXXXXXXXXXXXXXXXOxxl;,;,;l:.
  ;c.;:''''':doOXXXXXXXXXXXXXXXXXXOdo;';clc.
  ;c.lOdood:'''oXXXXXXXXXXXXXXXXXXXXXk,..;ol.
  ';.:xxxxxocccoxxxxxxxxxxxxxxxxxxxxxxl::'.';;.
  ';........................................;l'   """,
        """
        .;:;;,.,;;::,.
     .;':;........'co:.
   .clc;'':cllllc::,.':c.
  .lo;;o:coxdllllllc;''::,,.
.c:'.,cl,.'l:',,;;'......cO;
do;';oxoc;:l;;llllc'.';;'.,;.
c..ckkkkkkkd,;llllc'.:kkd;.':c.
'.,okkkkkkkkc;lllll,.:kkkdl,cO;
..;xkkkkkkkkc,ccll:,;okkkkk:,co,
..,dkkkkkkkkc..,;,'ckkkkkkkc;ll.
..'okkkkkkkko,....'okkkkkkkc,:c.
c..ckkkkkkkkkdl;,:okkkkkkkkd,.',';.
d..':lxkkkkkkkkxxkkkkkkkkkkkdoc;,;'..'.,.
o...'';llllldkkkkkkkkkkkkkkkkkkdll;..'cdo.
o..,l;'''''';dkkkkkkkkkkkkkkkkkkkkdlc,..;lc.
o..;lc;;;;;;,,;clllllllllllllllllllllc'..,:c.
o..........................................;'     """,
        """
           .,,,,,,,,,.
         .ckKxodooxOOdcc.
      .cclooc'....';;cool.
     .loc;;;;clllllc;;;;;:;,.
   .c:'.,okd;;cdo:::::cl,..oc
  .:o;';okkx;';;,';::;'....,:,.
  co..ckkkkkddkc,cclll;.,c:,:o:.
  co..ckkkkkkkk:,cllll;.:kkd,.':c.
.,:;.,okkkkkkkk:,cclll;.ckkkdl;;o:.
cNo..ckkkkkkkkko,.;loc,.ckkkkkc..oc
,dd;.:kkkkkkkkkx;..;:,.'lkkkkko,.:,
  ;:.ckkkkkkkkkkc.....;ldkkkkkk:.,'
,dc..'okkkkkkkkkxoc;;cxkkkkkkkkc..,;,.
kNo..':lllllldkkkkkkkkkkkkkkkkkdcc,.;l.
KOc,c;''''''';lldkkkkkkkkkkkkkkkkkc..;lc.
xx:':;;;;,.,,...,;;cllllllllllllllc;'.;od,
cNo.....................................oc        """,
        """

                   .ccccccc.
               .ccckNKOOOOkdcc.
            .;;cc:ccccccc:,:c::,,.
         .c;:;.,cccllxOOOxlllc,;ol.
        .lkc,coxo:;oOOxooooooo;..:,
      .cdc.,dOOOc..cOd,.',,;'....':l.
      cNx'.lOOOOxlldOc..;lll;.....cO;
     ,do;,:dOOOOOOOOOl'':lll;..:d:''c,
     co..lOOOOOOOOOOOl'':lll;.'lOd,.cd.
     co.'dOOOOOOOOOOOo,.;llc,.,dOOc..dc
     co..lOOOOOOOOOOOOc.';:,..cOOOl..oc
   .,:;.'::lxOOOOOOOOOo:'...,:oOOOc.'dc
   ;Oc..cl'':lldOOOOOOOOdcclxOOOOx,.cd.
  .:;';lxl''''':lldOOOOOOOOOOOOOOc..oc
,dl,.'cooc:::,....,::coooooooooooc'.c:
cNo.................................oc            """,
        """


                        .cccccccc.
                  .,,,;;cc:cccccc:;;,.
                .cdxo;..,::cccc::,..;l.
               ,do:,,:c:coxxdllll:;,';:,.
             .cl;.,oxxc'.,cc,.';;;'...oNc
             ;Oc..cxxxc'.,c;..;lll;...cO;
           .;;',:ldxxxdoldxc..;lll:'...'c,
           ;c..cxxxxkxxkxxxc'.;lll:'','.cdc.
         .c;.;odxxxxxxxxxxxd;.,cll;.,l:.'dNc
        .:,''ccoxkxxkxxxxxxx:..,:;'.:xc..oNc
      .lc,.'lc':dxxxkxxxxxxxol,...',lx:..dNc
     .:,',coxoc;;ccccoxxxxxxxxo:::oxxo,.cdc.
  .;':;.'oxxxxxc''''';cccoxxxxxxxxxxxc..oc
,do:'..,:llllll:;;;;;;,..,;:lllllllll;..oc
cNo.....................................oc        """,
        """

                              .ccccc.
                         .cc;'coooxkl;.
                     .:c:::c:,,,,,;c;;,.'.
                   .clc,',:,..:xxocc;'..c;
                  .c:,';:ox:..:c,,,,,,...cd,
                .c:'.,oxxxxl::l:.,loll;..;ol.
                ;Oc..:xxxxxxxxx:.,llll,....oc
             .,;,',:loxxxxxxxxx:.,llll;.,,.'ld,
            .lo;..:xxxxxxxxxxxx:.'cllc,.:l:'cO;
           .:;...'cxxxxxxxxxxxxoc;,::,..cdl;;l'
         .cl;':,'';oxxxxxxdxxxxxx:....,cooc,cO;
     .,,,::;,lxoc:,,:lxxxxxxxxxxxo:,,;lxxl;'oNc
   .cdxo;':lxxxxxxc'';cccccoxxxxxxxxxxxxo,.;lc.
  .loc'.'lxxxxxxxxocc;''''';ccoxxxxxxxxx:..oc
olc,..',:cccccccccccc:;;;;;;;;:ccccccccc,.'c,
Ol;......................................;l'      """,
        """
                              ,ddoodd,
                         .cc' ,ooccoo,'cc.
                      .ccldo;...',,...;oxdc.
                   .,,:cc;.,'..;lol;;,'..lkl.
                  .dOc';:ccl;..;dl,.''.....oc
                .,lc',cdddddlccld;.,;c::'..,cc:.
                cNo..:ddddddddddd;':clll;,c,';xc
               .lo;,clddddddddddd;':clll;:kc..;'
             .,c;..:ddddddddddddd:';clll,;ll,..
             ;Oc..';:ldddddddddddl,.,c:;';dd;..
           .''',:c:,'cdddddddddddo:,''..'cdd;..
         .cdc';lddd:';lddddddddddddd;.';lddl,..
      .,;::;,cdddddol;;lllllodddddddlcldddd:.'l;
     .dOc..,lddddddddlcc:;'';cclddddddddddd;;ll.
   .coc,;::ldddddddddddddlcccc:ldddddddddl:,cO;
,xl::,..,cccccccccccccccccccccccccccccccc:;':xx,
cNd.........................................;lOc  """
    ]


def main():
    """Entry point for the CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
