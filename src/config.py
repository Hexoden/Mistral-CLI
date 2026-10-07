"""Mistral CLI - Configuration management."""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union

from rich.console import Console

console = Console()


class Config:
    """Configuration manager for Mistral CLI."""
    
    # Default config path
    DEFAULT_CONFIG_PATH = Path.home() / ".mistral-cli" / "config.yaml"
    
    # In-memory config storage
    _config: Dict[str, Any] = {}
    
    # Supported config formats
    SUPPORTED_FORMATS = {
        ".yaml": "yaml",
        ".yml": "yaml",
        ".json": "json",
    }
    
    @classmethod
    def load(cls, path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        """Load configuration from file.
        
        Args:
            path: Path to config file. If None, uses default path.
        
        Returns:
            Loaded configuration dictionary.
        """
        config_path = Path(path) if path else cls.DEFAULT_CONFIG_PATH
        
        # Ensure config directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        if config_path.exists():
            try:
                ext = config_path.suffix.lower()
                
                if ext in (".yaml", ".yml"):
                    with open(config_path, "r") as f:
                        cls._config = yaml.safe_load(f) or {}
                elif ext == ".json":
                    with open(config_path, "r") as f:
                        cls._config = json.load(f) or {}
                else:
                    console.print(f"[yellow]Warning: Unsupported config format {ext}[/yellow]")
                
                console.print(f"[green]Config loaded from {config_path}[/green]")
                
                # Prompt for user name if config exists but no name is set
                if not path and "name" not in cls._config:
                    cls._prompt_for_name()
            except Exception as e:
                console.print(f"[red]Error loading config: {e}[/red]")
                cls._config = {}
        else:
            # Create default config
            cls._config = {
                "api_key": None,
                "default_model": "mistral-tiny",
                "temperature": 0.7,
                "max_tokens": None,
                "theme": "mistral",
                "typing_speed": "medium",
                "chat_typing_speed": "medium",
                "name": None,
            }
            
            if not path:  # Only save default if using default path
                cls.save()
                # Prompt for user name on first install
                cls._prompt_for_name()
        
        # Override with environment variables
        if "MISTRAL_API_KEY" in os.environ:
            cls._config["api_key"] = os.environ["MISTRAL_API_KEY"]
        
        if "MISTRAL_NAME" in os.environ:
            cls._config["name"] = os.environ["MISTRAL_NAME"]
        
        return cls._config
    
    @classmethod
    def save(cls, path: Optional[Union[str, Path]] = None) -> None:
        """Save configuration to file.
        
        Args:
            path: Path to save config. If None, uses default path.
        """
        config_path = Path(path) if path else cls.DEFAULT_CONFIG_PATH
        
        try:
            # Ensure directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save based on extension
            ext = config_path.suffix.lower()
            
            if ext in (".yaml", ".yml"):
                with open(config_path, "w") as f:
                    yaml.dump(cls._config, f, default_flow_style=False)
            elif ext == ".json":
                with open(config_path, "w") as f:
                    json.dump(cls._config, f, indent=2)
            else:
                # Default to YAML
                config_path = config_path.with_suffix(".yaml")
                with open(config_path, "w") as f:
                    yaml.dump(cls._config, f, default_flow_style=False)
            
            console.print(f"[green]Config saved to {config_path}[/green]")
        except Exception as e:
            console.print(f"[red]Error saving config: {e}[/red]")
            raise
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: Configuration key.
            default: Default value if key not found.
        
        Returns:
            Configuration value or default.
        """
        return cls._config.get(key, default)
    
    @classmethod
    def set(cls, key: str, value: Any) -> None:
        """Set a configuration value.
        
        Args:
            key: Configuration key.
            value: Value to set.
        """
        cls._config[key] = value
        cls.save()
    
    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        """Get all configuration values."""
        return cls._config.copy()
    
    @classmethod
    def update(cls, values: Dict[str, Any]) -> None:
        """Update multiple configuration values.
        
        Args:
            values: Dictionary of key-value pairs to update.
        """
        cls._config.update(values)
        cls.save()
    
    @classmethod
    def reset(cls) -> None:
        """Reset configuration to defaults."""
        cls._config = {
            "api_key": None,
            "default_model": "mistral-tiny",
            "temperature": 0.7,
            "max_tokens": None,
            "typing_speed": "medium",
            "chat_typing_speed": "medium",
        }
        cls.save()
    
    @classmethod
    def get_typing_delay(cls, speed_type="cli") -> float:
        """Get the typing delay in seconds based on configured speed.
        
        Args:
            speed_type: Type of speed to get ('banner', 'models', 'cli', 'chat')
        """
        # Fixed speeds for certain contexts
        if speed_type == "banner":
            return 0.0  # Instant for banner
        elif speed_type == "models":
            return 0.0001  # Very fast for models list
        
        # Configurable speeds
        config_key = "typing_speed" if speed_type == "cli" else "chat_typing_speed"
        speed = cls.get(config_key, "medium")
        
        speeds = {
            "off": 0.0,
            "very_fast": 0.0001,
            "fast": 0.0005,
            "medium": 0.002,
            "slow": 0.005,
            "very_slow": 0.01,
        }
        return speeds.get(speed, 0.002)  # Default to medium
    
    @classmethod
    def _prompt_for_name(cls) -> None:
        """Prompt the user for their name on first install."""
        import sys
        
        console.print(f"\n[yellow]Welcome to Mistral CLI! Let's get started.[/yellow]")
        
        try:
            name = input("What's your name? (This will be used in AI conversations): ").strip()
            
            if name:  # Only save if user provided a name
                cls._config["name"] = name
                cls.save()
                console.print(f"[green]Hello, {name}! Your name has been saved.[/green]")
            else:
                console.print("[yellow]No name provided. You can set it later with: mistral config --name YourName[/yellow]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Skipping name setup. You can set it later with: mistral config --name YourName[/yellow]")
        except Exception as e:
            console.print(f"[red]Error setting up name: {e}[/red]")
