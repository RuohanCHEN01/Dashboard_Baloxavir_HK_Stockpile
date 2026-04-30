"""
Unified LLM Client for multi-provider AI integration.

Provides a consistent interface across OpenAI, Claude, MiMo, and DeepSeek APIs.
All providers use the OpenAI-compatible chat completion format where possible.
"""

import json
import os
import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProviderConfig:
    """Configuration for an LLM provider."""
    base_url: str
    default_model: str
    context_window: int
    supports_vision: bool = False
    supports_structured_output: bool = False


# Provider configurations
PROVIDER_REGISTRY = {
    "openai": ProviderConfig(
        base_url="https://api.openai.com/v1",
        default_model="gpt-4o",
        context_window=128_000,
        supports_vision=True,
        supports_structured_output=True,
    ),
    "claude": ProviderConfig(
        base_url="https://api.anthropic.com/v1",
        default_model="claude-3-5-sonnet-20241022",
        context_window=200_000,
        supports_vision=True,
        supports_structured_output=True,
    ),
    "mimo": ProviderConfig(
        base_url="https://api.xiaomimimo.com/v1",
        default_model="MiMo-V2.5-Pro",
        context_window=1_000_000,
        supports_vision=True,
        supports_structured_output=True,
    ),
    "deepseek": ProviderConfig(
        base_url="https://api.deepseek.com/v1",
        default_model="deepseek-chat",
        context_window=64_000,
        supports_vision=False,
        supports_structured_output=True,
    ),
}

# Model alias mapping
MODEL_ALIASES = {
    "gpt-4o": "openai",
    "gpt-4-turbo": "openai",
    "claude-3.5-sonnet": "claude",
    "claude-3-opus": "claude",
    "mimo-v2.5-pro": "mimo",
    "mimo-v2.5": "mimo",
    "mimo-v2-flash": "mimo",
    "deepseek-v3": "deepseek",
    "deepseek-r1": "deepseek",
}


class LLMClient:
    """Unified LLM client supporting multiple providers.

    Provides a consistent interface for chat completion, structured output,
    and embedding across OpenAI, Claude, MiMo, and DeepSeek APIs.

    Args:
        provider: LLM provider name ("openai", "claude", "mimo", "deepseek")
        model: Specific model name. If None, uses provider's default model.
        api_key: API key. If None, reads from environment variable.
        temperature: Default sampling temperature (0.0-2.0).
        max_tokens: Default max tokens for generation.

    Example:
        >>> client = LLMClient(provider="mimo", model="MiMo-V2.5-Pro")
        >>> response = client.complete([
        ...     {"role": "system", "content": "You are a helpful assistant."},
        ...     {"role": "user", "content": "What is the ICER formula?"}
        ... ])
    """

    def __init__(
        self,
        provider: str = "openai",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ):
        self.provider = provider.lower()
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Resolve provider config
        if self.provider not in PROVIDER_REGISTRY:
            raise ValueError(
                f"Unknown provider '{provider}'. "
                f"Supported: {list(PROVIDER_REGISTRY.keys())}"
            )

        self._config = PROVIDER_REGISTRY[self.provider]
        self.model = model or self._config.default_model

        # Resolve API key from environment
        env_var_map = {
            "openai": "OPENAI_API_KEY",
            "claude": "ANTHROPIC_API_KEY",
            "mimo": "MIMO_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
        }
        self.api_key = api_key or os.environ.get(env_var_map.get(self.provider, ""), "")

        if not self.api_key:
            logger.warning(
                "No API key provided for %s. Set %s environment variable "
                "or pass api_key parameter.",
                self.provider,
                env_var_map.get(self.provider, "API_KEY"),
            )

    def complete(
        self,
        messages: list[dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> str:
        """Send a chat completion request.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            temperature: Sampling temperature. Overrides default.
            max_tokens: Max tokens to generate. Overrides default.
            **kwargs: Additional provider-specific parameters.

        Returns:
            Generated text content as a string.
        """
        import openai

        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens

        try:
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self._config.base_url,
            )

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temp,
                max_tokens=tokens,
                **kwargs,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error("LLM completion failed: %s", str(e))
            raise RuntimeError(f"LLM completion failed: {e}") from e

    def complete_structured(
        self,
        messages: list[dict],
        output_schema: dict,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> dict:
        """Request structured JSON output from the model.

        Args:
            messages: List of message dicts.
            output_schema: JSON Schema describing expected output format.
            temperature: Sampling temperature.

        Returns:
            Parsed JSON object matching the output schema.
        """
        if not self._config.supports_structured_output:
            logger.warning(
                "Provider %s may not support structured output. "
                "Falling back to prompt-based extraction.",
                self.provider,
            )

        # Add JSON schema instruction to the last user message
        schema_instruction = (
            "\n\nYou MUST respond with valid JSON matching this schema:\n"
            f"{json.dumps(output_schema, indent=2)}\n"
            "Return ONLY the JSON object, no markdown or explanation."
        )

        messages = messages.copy()
        messages[-1]["content"] += schema_instruction

        response_text = self.complete(
            messages=messages,
            temperature=temperature,
            **kwargs,
        )

        # Parse JSON from response
        try:
            # Try direct parse first
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try extracting JSON from markdown code blocks
            import re
            json_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            raise ValueError(
                "Failed to parse structured output from LLM response. "
                f"Raw response: {response_text[:500]}"
            )

    def extract_from_text(
        self,
        text: str,
        extraction_task: str,
        output_schema: Optional[dict] = None,
        **kwargs,
    ) -> dict:
        """Convenience method for information extraction from text.

        Args:
            text: Source text to extract information from.
            extraction_task: Description of what to extract.
            output_schema: Optional JSON schema for structured output.

        Returns:
            Dictionary of extracted key-value pairs.
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert research assistant specializing in "
                    "epidemiology and health economics. Extract precise, "
                    "numerical values from scientific text. If a value is "
                    "not explicitly stated, return null. Always cite the "
                    "specific passage supporting each extraction."
                ),
            },
            {
                "role": "user",
                "content": f"Task: {extraction_task}\n\nSource text:\n{text}",
            },
        ]

        if output_schema:
            return self.complete_structured(messages, output_schema, **kwargs)

        return self.complete(messages, **kwargs)

    @property
    def info(self) -> dict:
        """Return provider and model information."""
        return {
            "provider": self.provider,
            "model": self.model,
            "context_window": self._config.context_window,
            "supports_vision": self._config.supports_vision,
            "api_base": self._config.base_url,
        }

    def __repr__(self) -> str:
        return f"LLMClient(provider='{self.provider}', model='{self.model}')"
