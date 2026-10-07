"""Tests for Mistral CLI."""

import pytest
from click.testing import CliRunner

from src.main import cli, chat, file, models, config


@pytest.fixture
def runner():
    """Create a Click test runner."""
    return CliRunner()


class TestCLI:
    """Test CLI commands."""
    
    def test_version(self, runner):
        """Test version command."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "Mistral CLI v" in result.output
    
    def test_help(self, runner):
        """Test help command."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "A command-line interface for Mistral AI" in result.output
    
    def test_models(self, runner):
        """Test models command."""
        result = runner.invoke(models)
        assert result.exit_code == 0
        assert "Available Mistral Models" in result.output
        assert "mistral-tiny" in result.output
        assert "mistral-small" in result.output


class TestConfig:
    """Test configuration."""
    
    def test_config_help(self, runner):
        """Test config help."""
        result = runner.invoke(config, ["--help"])
        assert result.exit_code == 0
        assert "Configure Mistral CLI settings" in result.output


class TestChat:
    """Test chat command."""
    
    def test_chat_help(self, runner):
        """Test chat help."""
        result = runner.invoke(chat, ["--help"])
        assert result.exit_code == 0
        assert "Start a chat session with Mistral AI" in result.output
    
    def test_chat_no_prompt_starts_interactive(self, runner):
        """Test that chat without prompt starts interactive mode."""
        # This is hard to test fully as interactive mode requires input
        result = runner.invoke(chat, [])
        # Should either start interactive or show help
        assert result.exit_code in [0, 1]  # 0 for success, 1 for missing API key


class TestFile:
    """Test file command."""
    
    def test_file_help(self, runner):
        """Test file help."""
        result = runner.invoke(file, ["--help"])
        assert result.exit_code == 0
        assert "Process a file with Mistral AI" in result.output
