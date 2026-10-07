```
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
```

# Mistral CLI

A command-line interface for Mistral AI, making it easy to interact with Mistral's language models from your terminal. Features a **customizable theme system** with ASCII banners and gradient colors.

## Features

| **Chat Interface** | **File Processing** |
|---|---|
| Interactive and single-prompt modes | Process text files with Mistral, with interactive file browser support |
| **Multi-model Support** | **Model Context** |
| Use any Mistral model from the API | Automatically provides model identity to the AI in each request |
| **Personalization** | **Interactive Model Selector** |
| Set your name with `mistral config --name` | Choose model from menu when starting chat |
| **Chat Commands** | **Path Commands** |
| Special commands like /help, /models, /switch, /theme, /config, /typing, /dance | Find mistral executable with `mistral which`, `mistral where`, or `mistral locate` |
| **Typing Speed Control** | **Configuration Management** |
| Configurable typing animation speeds with separate controls | Save API keys and settings |
| **Streaming** | **Rich Output** |
| Get responses token by token | Beautiful terminal output with Rich |
| **🎨 Theme System** | **🌈 Gradient Colors** |
| Customizable appearance with ASCII banners | Left-to-right color gradients on banners |
| **⌨️ Typing Effect** | **🦜 Fun Animations** |
| Animated banner and AI responses with configurable speed | Dancing parrot animation with /dance command |

## Installation

### Prerequisites

- **Python 3.8 or higher**
- **pip** (Python package manager)

### 🐧 Linux/macOS Installation

#### Method 1: Install from Source (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/mistral-cli.git
cd mistral-cli

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate the virtual environment
source venv/bin/activate

# 4. Install in development mode
pip install -e .
```

#### Method 2: Quick Install

```bash
# 1. Navigate to project directory
cd mistral-cli

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run directly
python -m src.main
```

### 🪟 Windows Installation

#### Method 1: Install from Source (Recommended)

```cmd
:: 1. Clone the repository
git clone https://github.com/yourusername/mistral-cli.git
cd mistral-cli

:: 2. Create virtual environment
python -m venv venv

:: 3. Activate the virtual environment
venv\Scripts\activate

:: 4. Install in development mode
pip install -e .
```

#### Method 2: Quick Install

```cmd
:: 1. Navigate to project directory
cd mistral-cli

:: 2. Install dependencies
pip install -r requirements.txt

:: 3. Run directly
python -m src.main
```

### ⚡ Verify Installation

After installation, test that the `mistral` command works:

```bash
# Activate your virtual environment first
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Then verify the command is available
# Linux/macOS:
which mistral
# Should show: /path/to/mistral-cli/venv/bin/mistral

# Windows:
where mistral
# Should show: C:\path\to\mistral-cli\venv\Scripts\mistral.exe

# Test the CLI
mistral --help
```

**⚠️ Important:** The `mistral` command is installed in your virtual environment. You must **activate the venv** before using it. Once activated, it will work from any directory in your terminal.

## Configuration

1. **Get an API Key**: Sign up at [Mistral Console](https://console.mistral.ai/) to get your API key.

2. **Set up environment variables**:

   ```bash
   # Create .env file from template
   cp .env.example .env

   # Edit .env with your API key
   nano .env

   # Or set environment variable directly
   export MISTRAL_API_KEY=your_api_key_here
   ```

3. **Configure via CLI**:
   ```bash
   mistral config --key your_api_key_here
   mistral config --model mistral-small
   mistral config --theme mistral
   mistral config --name "Your Name"
   ```

### Personalization

Make your AI conversations more personal by setting your name:

```bash
# Set your name via CLI
mistral config --name "Your Name"

# Or via environment variable
export MISTRAL_NAME="Your Name"

# Or add to your ~/.mistral-cli/config.yaml
name: Your Name
```

Once set, the AI will address you by name in all conversations:

```
💬: Hello AI
AI: Hello John! How can I help you today?
```

**Note:** You'll be prompted for your name automatically on first install, or when starting the CLI if you don't have a name set in your config.

## Security

⚠️ **Important: API Key Security**

Your Mistral API key is **sensitive information** that should never be committed to version control. This project is configured to keep your API keys secure:

- **API keys are stored** in `~/.mistral-cli/config.yaml` (your home directory, NOT in the project directory)
- **`.gitignore`** excludes config files, environment files, and other sensitive data
- **Environment variables** (`MISTRAL_API_KEY`) take precedence and are never stored in files
- **Never commit** `.env` files, `config.yaml` files, or any files containing API keys

**Safe practices:**

- Use `.env.example` as a template (already committed)
- Add your actual API key to `.env` (excluded from git)
- Or use `mistral config --key` (stores in your home directory)
- Or use environment variables (`export MISTRAL_API_KEY=your_key`)

## Usage

### Basic Commands

```bash
# Show help
mistral --help

# Show version
mistral --version

# Start interactive chat
mistral chat

# Single prompt
mistral chat "Explain quantum computing in simple terms"

# With specific model and temperature
mistral chat -m mistral-small -t 0.9 "Write a creative story"

# Stream response
mistral chat -s "Tell me a long story"

# Process a file
mistral file my_document.txt

# List available models (live from Mistral API)
mistral models

# Configure settings
mistral config --key your_api_key
mistral config --model mistral-medium

# Show command path (platform-aware)
mistral which      # Shows path on Linux/macOS, silly message on Windows
mistral where      # Shows path on Windows, silly message on Linux
mistral locate    # Shows path regardless of OS (platform-agnostic)
```

### Theme Commands

```bash
# List available themes
mistral theme

# Set theme
mistral theme mistral      # Custom ASCII banner with gradient
mistral theme minimal      # Clean, simple interface
mistral theme retro        # Retro terminal style
mistral theme dark         # Dark mode

# Set theme via config
mistral config --theme mistral
```

### Interactive Mode

```bash
$ mistral chat
# First asks: "Use default model 'mistral-medium'? (y[or enter] /n):"
# If 'n' - shows full model list to select from
# Type your prompts, responses will appear below
# Type 'exit', 'quit', or 'q' to end the session
# Type 'help' or '?' for menu options
# Displays your theme's banner with gradient colors
```

### Model Selector Options

When starting chat, you first get asked:

```
Use default model 'mistral-medium'? (y[or enter] /n):
```

- **Press `y` or Enter** → Uses your default model from config
- **Press `n`** → Shows full model list to choose from

Then if you chose `n`, select from the list:

- Enter a number from the list
- Type the exact model name

### Chat Commands

While in interactive chat, use these special commands:

| Command              | Description                                         |
| -------------------- | --------------------------------------------------- |
| `help`, `/help`, `?` | Show help menu and current settings                 |
| `exit`, `quit`, `q`  | Exit the chat session                               |
| `/models`            | List available Mistral models                       |
| `/switch {model}`    | Switch to a different model                         |
| `/theme {name}`      | Switch to a different theme                         |
| `/config`            | Show current configuration                          |
| `/typing [{speed}]`  | Set chat typing speed (affects only chat responses) |
| `/dance`             | Show dancing parrot animation 🦜                    |

### Fun Commands

Add some fun to your chat session:

```bash
# Display animated dancing parrot
/dance

# Find where the mistral command is installed (with personality!)
mistral which      # Linux: shows path, Windows: "You are on Windows silly, try {mistral where}"
mistral where      # Windows: shows path, Linux: "You are on Linux silly, try {mistral which}"
mistral locate    # Always shows the path
```

The dancing parrot animation uses the official frames from [parrot.live](https://github.com/hugomd/parrot.live) with smooth frame-by-frame animation in your terminal.

### File Processing

```bash
# Process a text file
mistral file my_notes.txt

# With options
mistral file -m mistral-small -t 0.5 my_notes.txt

# Interactive file browser (no file specified)
mistral file
```

When you run `mistral file` without specifying a file, an interactive file browser will open, allowing you to navigate through directories and select a file to process. Use numbers to select files/directories, 0 to go to the parent directory, or q to quit.

## Models

The `mistral models` command pulls the latest model list directly from the Mistral API, showing exactly which models are available for your account.

### Common Models

| Model ID               | Description                         |
| ---------------------- | ----------------------------------- |
| `mistral-tiny`         | Fast and efficient for simple tasks |
| `mistral-small`        | Balanced performance and cost       |
| `mistral-medium`       | More powerful, higher cost          |
| `mistral-large`        | Most powerful model                 |
| `codestral-latest`     | Code generation specialized         |
| `mistral-embed`        | Embeddings model                    |
| `mistral-large-latest` | Official Mistral Large model        |

### Usage with Specific Models

```bash
# Use a specific model
mistral chat -m mistral-large-latest "Your prompt here"

# Start interactive chat with model selector
mistral chat
# -> Shows model menu if no default set

# Set as default
mistral config --model mistral-large-latest

# See all available models (live from API)
mistral models
```

## Themes

The CLI includes a powerful theme system for customizing the terminal appearance.

### Available Themes

| Theme     | Description                                                 | Banner |
| --------- | ----------------------------------------------------------- | ------ |
| `mistral` | **Custom ASCII banner** with left-to-right 6-color gradient | ✅ Yes |
| `default` | Clean, professional interface                               | ✅ Yes |
| `minimal` | Simple, no frills                                           | ❌ No  |
| `retro`   | Yellow/green terminal vibes                                 | ✅ Yes |
| `dark`    | Dark mode with bright colors                                | ✅ Yes |

### Theme Customization

Each theme controls:

- **ASCII Banner**: Custom banner art (optional)
- **Colors**: Primary, secondary, border colors
- **Prompt Prefix**: Input prompt style (`>>>`, `You:`, `$`, `💬`)
- **Response Styling**: Panel borders and formatting

### Custom Themes

Create your own theme:

```python
# In src/themes.py
from src.themes import ThemeManager

ThemeManager.create_custom_theme(
    name="my_theme",
    banner=YOUR_ASCII_ART,
    primary_color="purple",
    secondary_color="pink",
    border_color="blue",
    prompt_prefix="Me: ",
    use_ascii_banner=True
)
```

### Banner Gradient

Banners with `use_ascii_banner=True` automatically get a **6-color left-to-right gradient** on each line:

- Purple → Pink → Light Purple → Light Blue → Light Cyan → Light Green
- No white colors used
- Each line has independent horizontal gradient

### Typing Effect

Different parts of the CLI have different typing speed controls:

#### Speed Contexts

| Context              | Config Setting      | Speed Control     | Default |
| -------------------- | ------------------- | ----------------- | ------- |
| **Banner**           | Fixed               | Instant           | 0.0s    |
| **Models List**      | Fixed               | Very fast         | 0.0001s |
| **CLI Commands**     | `typing_speed`      | `mistral typing`  | medium  |
| **Single Prompt**    | `typing_speed`      | `mistral typing`  | medium  |
| **Interactive Chat** | `chat_typing_speed` | `/typing` in chat | medium  |

#### Typing Speeds

| Speed       | Delay   | Characters/Second | Description      |
| ----------- | ------- | ----------------- | ---------------- |
| `off`       | 0s      | Instant           | No typing effect |
| `very_fast` | 0.0001s | ~10,000           | Nearly instant   |
| `fast`      | 0.0005s | ~2,000            | Fast typing      |
| `medium`    | 0.002s  | ~500              | Default speed    |
| `slow`      | 0.005s  | ~200              | Noticeable delay |
| `very_slow` | 0.01s   | ~100              | Slow typing      |

#### Usage

**CLI Commands (affects help, theme, single prompt responses):**

```bash
mistral typing           # Show current CLI speed
mistral typing fast     # Set CLI to fast
mistral typing off      # Disable CLI typing effects
```

**Interactive Chat (affects only chat responses):**

```bash
/typing                # Show current chat speed
/typing slow           # Set chat to slow
/typing off            # Disable chat typing effects
```

**Note:** Banner and models list always use fast speed regardless of settings to ensure good UX.

### Model Context

Each API request automatically includes model context:

- Adds a system message: `"You are {model-name}, a Mistral AI language model. Respond accordingly."`
- Helps the model understand its identity and respond appropriately
- Only added once per conversation to avoid duplication

## Configuration File

The CLI uses `~/.mistral-cli/config.yaml` for persistent configuration:

```yaml
api_key: your_api_key_here
default_model: mistral-tiny
temperature: 0.7
max_tokens: null
theme: mistral # Your default theme
typing_speed: medium # Typing speed for CLI commands and single prompts
chat_typing_speed: medium # Typing speed for interactive chat only
name: Your Name # Your name for AI conversations (optional)
```

## Environment Variables

- `MISTRAL_API_KEY`: Your Mistral API key
- `MISTRAL_DEFAULT_MODEL`: Default model to use
- `MISTRAL_TEMPERATURE`: Default temperature
- `MISTRAL_MAX_TOKENS`: Default max tokens
- `MISTRAL_NAME`: Your name for AI conversations

## Project Structure

```
mistral-cli/
├── src/
│   ├── __init__.py
│   ├── main.py         # CLI entry point
│   ├── client.py       # Mistral API client
│   ├── config.py       # Configuration management
│   ├── themes.py       # Theme system with gradient banners
│   └── frames/         # Parrot animation frames
├── config/
│   └── default.yaml
├── tests/
│   └── test_cli.py     # Tests
├── requirements.txt
├── setup.py
├── pyproject.toml
├── .env.example
├── LICENSE
└── README.md
```

## Development

```bash
# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/

# Run directly
python src/main.py chat
```

## Customization Examples

### Change Banner Colors

Edit `src/themes.py` line ~67:

```python
gradient_colors = ['red', 'orange', 'yellow', 'green', 'blue', 'magenta']
```

Try: `['purple', 'pink', 'cyan']` or `['blue', 'cyan', 'green']`

### Add Your Own ASCII Banner

Edit the `MISTRAL_BANNER` variable in `themes.py` or create a new theme:

```python
MY_BANNER = r"""
  ____    ____  __  __   ______
 / ___|  / ___| |  \/  | | ___ \
 \___ \  | |     | |\/| | | |_/ /
  ___) | | |___  | |  | | |  __/
 |____/   \____| |_|  |_| |_|
"""

THEMES["custom"] = Theme(
    name="Custom",
    banner=MY_BANNER,
    primary_color="bright_white",
    use_ascii_banner=True
)
```

## License

MIT License - see LICENSE file for details.
