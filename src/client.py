"""Mistral CLI - Client module for Mistral API interaction."""

import os
from typing import List, Dict, Any, Optional, Union, Iterator

from mistralai import client as mistralai_client
from rich.console import Console

from .config import Config

console = Console()


class MistralClient:
    """Client for interacting with Mistral AI API."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Mistral client.

        Args:
            api_key: Mistral API key. If not provided, uses MISTRAL_API_KEY
                    environment variable or config.
        """
        # Get API key from parameter, env, or config
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY") or Config.get("api_key")

        if not self.api_key:
            raise ValueError(
                "MISTRAL_API_KEY not set. "
                "Set it via environment variable or use --config to set it."
            )

        # Initialize the Mistral client
        self.client = mistralai_client.Mistral(api_key=self.api_key)

        console.print("[green]Mistral client initialized, lets vibe![/green]")

    def complete(
        self,
        prompt: str,
        model: str = "mistral-tiny",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        history: Optional[List[Dict[str, str]]] = None,
        stream: bool = False,
    ) -> Union[str, Iterator[str]]:
        """Get a completion from Mistral.

        Args:
            prompt: The prompt to send.
            model: Model to use.
            temperature: Sampling temperature (0.0 to 1.0).
            max_tokens: Maximum tokens to generate.
            history: Conversation history.
            stream: Whether to stream the response.

        Returns:
            The response text, or an iterator of chunks if stream=True.
        """
        # Build messages list
        messages = []

        # Add model context and user name as system message (only if not already in history)
        has_system_message = any(msg.get("role") == "system" for msg in (history or []))
        if not has_system_message:
            # Get user's name from config
            user_name = Config.get("name")
            system_content = f"You are {model}, a Mistral AI language model. Respond accordingly."
            
            # Add user name context if available
            if user_name:
                system_content = f"You are {model}, a Mistral AI language model. The user is {user_name}. Respond accordingly and address them by name."
            
            messages.append({
                "role": "system", 
                "content": system_content
            })

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": prompt})

        # Common parameters
        chat_params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }

        if max_tokens:
            chat_params["max_tokens"] = max_tokens

        try:
            if stream:
                return self._stream_chat(**chat_params)
            else:
                return self._get_chat(**chat_params)
        except Exception as e:
            error_str = str(e)
            if "Invalid API Key" in error_str or "401" in error_str:
                console.print("[red]Error:[/red] Invalid Mistral API key.")
                console.print("Please check your API key with: mistral config")
                console.print("Or set a new one with: mistral config --key YOUR_API_KEY")
            else:
                console.print(f"[red]Mistral API Error:[/red] {e}")
            raise

    def _get_chat(self, **kwargs) -> str:
        """Get a single chat completion."""
        response = self.client.chat.complete(**kwargs)

        # Extract the response text from the new API format (mistralai v3.x+)
        if hasattr(response, 'choices') and response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content
            
            # Handle case where content is an object with text attribute (new API format)
            if hasattr(content, 'text'):
                return content.text or ""
            
            # Handle case where content might be a list
            if isinstance(content, list):
                # Filter out thinking chunks and get only text
                text_parts = []
                for item in content:
                    if hasattr(item, 'text') and item.text:
                        text_parts.append(item.text)
                    elif isinstance(item, str):
                        text_parts.append(item)
                return ''.join(text_parts)
            
            # Handle case where content is a string
            if isinstance(content, str):
                return content
                
            # Handle case where content has both thinking and text
            if hasattr(content, 'type') and content.type == 'text':
                return getattr(content, 'text', '') or ""
                
            return str(content) or ""

        # Try alternative response structure
        if hasattr(response, 'outputs') and response.outputs:
            return response.outputs[0].text

        if hasattr(response, 'content'):
            return response.content

        return ""

    def _stream_chat(self, **kwargs) -> Iterator[str]:
        """Stream a chat completion."""
        for chunk in self.client.chat.stream(**kwargs):
            # Handle the new streaming format
            if hasattr(chunk, 'data') and chunk.data:
                if hasattr(chunk.data, 'choices') and chunk.data.choices:
                    content = chunk.data.choices[0].delta.content
                    if content:
                        # Handle case where content might be a list
                        if isinstance(content, list):
                            for item in content:
                                if hasattr(item, 'text') and item.text:
                                    yield item.text
                                elif isinstance(item, str) and item:
                                    yield item
                        elif hasattr(content, 'text'):
                            yield content.text
                        elif isinstance(content, str):
                            yield content
                        else:
                            yield str(content)
            elif hasattr(chunk, 'choices') and chunk.choices:
                content = chunk.choices[0].delta.content
                if content:
                    # Handle case where content might be a list
                    if isinstance(content, list):
                        for item in content:
                            if hasattr(item, 'text') and item.text:
                                yield item.text
                            elif isinstance(item, str) and item:
                                yield item
                    elif hasattr(content, 'text'):
                        yield content.text
                    elif isinstance(content, str):
                        yield content
                    else:
                        yield str(content)

    def embed(
        self,
        text: str,
        model: str = "mistral-embed",
    ) -> List[float]:
        """Get embeddings for text.

        Args:
            text: Text to embed.
            model: Embedding model to use.

        Returns:
            Embedding vector.
        """
        response = self.client.embeddings.create(
            model=model,
            input=[text],
        )

        # Handle different response formats
        if hasattr(response, 'data') and response.data:
            embedding = response.data[0].embedding
            if isinstance(embedding, list):
                return embedding
            else:
                return list(embedding) if hasattr(embedding, '__iter__') else []
        elif hasattr(response, 'embeddings') and response.embeddings:
            return list(response.embeddings[0])

        return []

    def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
        try:
            response = self.client.models.list()
            if hasattr(response, 'data') and response.data:
                # Convert model objects to dictionaries
                models = []
                for model in response.data:
                    try:
                        if hasattr(model, 'id'):
                            # BaseModelCard object - extract all available fields
                            model_dict = {
                                'id': str(getattr(model, 'id', '')),
                                'description': str(getattr(model, 'description', None) or f"Model: {getattr(model, 'id', '')}"),
                                'object': str(getattr(model, 'object', 'model')),
                                'created': str(getattr(model, 'created', None)),
                                'owned_by': str(getattr(model, 'owned_by', None))
                            }
                            # Remove None values
                            model_dict = {k: v for k, v in model_dict.items() if v is not None and v != ''}
                            models.append(model_dict)
                        elif isinstance(model, dict):
                            # Already a dict - clean it up
                            clean_model = {k: str(v) for k, v in model.items() if v is not None and v != ''}
                            models.append(clean_model)
                        else:
                            # Convert to string representation
                            models.append({'id': str(model), 'description': f"Model: {model}"})
                    except Exception as model_error:
                        console.print(f"[yellow]Warning: Could not process model {model}: {model_error}[/yellow]")
                return models
        except Exception as e:
            console.print(f"[yellow]Warning: Could not fetch models list: {e}[/yellow]")
        return []

    def get_model(self, model_id: str) -> Dict[str, Any]:
        """Get details for a specific model."""
        return self.client.models.retrieve(model_id)
