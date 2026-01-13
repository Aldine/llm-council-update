"""
LLM Client Implementations
Supports multiple providers:
- Anthropic Claude (claude-4, claude-sonnet-4, etc.)
- OpenAI GPT (gpt-4, gpt-5.2, o1, o3, etc.)
- Google Gemini (gemini-2.0-flash, gemini-pro, etc.)
- OpenRouter (access to 100+ models via unified API)
- Mock client for testing
"""

import os
from typing import List, Dict, Any, Optional, Callable
from abc import ABC, abstractmethod


class BaseLLMClient(ABC):
    """Base class for LLM clients"""
    
    @abstractmethod
    def __call__(self, messages: List[Dict[str, str]]) -> str:
        """Generate completion from messages"""
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """Return info about the current model"""
        return {
            "provider": self.__class__.__name__,
            "model": getattr(self, "model", "unknown")
        }


class AnthropicClient(BaseLLMClient):
    """Anthropic Claude client"""
    
    def __init__(self, model: str = "claude-sonnet-4-20250514", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self._client = None
    
    @property
    def client(self):
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("Please install anthropic: pip install anthropic")
        return self._client
    
    def __call__(self, messages: List[Dict[str, str]]) -> str:
        # Separate system message
        system_msg = ""
        user_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                user_messages.append(msg)
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=8192,
            system=system_msg,
            messages=user_messages,
        )
        
        return response.content[0].text


class OpenAIClient(BaseLLMClient):
    """OpenAI GPT client - supports GPT-4, GPT-5.2, o1, o3, etc."""
    
    def __init__(self, model: str = "gpt-4", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self._client = None
    
    @property
    def client(self):
        if self._client is None:
            try:
                import openai
                self._client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("Please install openai: pip install openai")
        return self._client
    
    def __call__(self, messages: List[Dict[str, str]]) -> str:
        # Handle reasoning models (o1, o3) which don't support system messages the same way
        if self.model.startswith("o1") or self.model.startswith("o3"):
            # Convert system message to user message for reasoning models
            converted_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    converted_messages.append({
                        "role": "user",
                        "content": f"[System Instructions]\n{msg['content']}"
                    })
                else:
                    converted_messages.append(msg)
            messages = converted_messages
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=8192,
        )
        
        return response.choices[0].message.content


class GoogleGeminiClient(BaseLLMClient):
    """Google Gemini client - supports gemini-2.0-flash, gemini-pro, etc."""
    
    def __init__(self, model: str = "gemini-2.0-flash", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        self._client = None
    
    @property
    def client(self):
        if self._client is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(self.model)
            except ImportError:
                raise ImportError("Please install google-generativeai: pip install google-generativeai")
        return self._client
    
    def __call__(self, messages: List[Dict[str, str]]) -> str:
        # Convert messages to Gemini format
        system_instruction = None
        gemini_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            elif msg["role"] == "user":
                gemini_messages.append({"role": "user", "parts": [msg["content"]]})
            elif msg["role"] == "assistant":
                gemini_messages.append({"role": "model", "parts": [msg["content"]]})
        
        # Create chat with system instruction if present
        if system_instruction:
            chat = self._client.start_chat(history=gemini_messages[:-1] if gemini_messages else [])
            # Prepend system instruction to last message
            if gemini_messages:
                last_content = gemini_messages[-1]["parts"][0]
                response = chat.send_message(f"[System: {system_instruction}]\n\n{last_content}")
            else:
                response = chat.send_message(system_instruction)
        else:
            chat = self._client.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])
            if gemini_messages:
                response = chat.send_message(gemini_messages[-1]["parts"][0])
            else:
                response = chat.send_message("Hello")
        
        return response.text


class OpenRouterClient(BaseLLMClient):
    """
    OpenRouter client - unified API for 100+ models
    
    Supports models from:
    - Anthropic (claude-3-opus, claude-3-sonnet, etc.)
    - OpenAI (gpt-4, gpt-4-turbo, etc.)
    - Google (gemini-pro, gemini-1.5-pro, etc.)
    - Meta (llama-3, llama-3.1, etc.)
    - Mistral (mistral-large, mixtral, etc.)
    - And many more!
    
    Model format: "provider/model-name" e.g., "anthropic/claude-3-opus"
    """
    
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(
        self, 
        model: str = "anthropic/claude-3-sonnet", 
        api_key: Optional[str] = None,
        site_url: Optional[str] = None,
        app_name: Optional[str] = "Confucius-Agent"
    ):
        self.model = model
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        self.site_url = site_url or os.environ.get("OPENROUTER_SITE_URL", "")
        self.app_name = app_name
        self._client = None
    
    @property
    def client(self):
        if self._client is None:
            try:
                import openai
                self._client = openai.OpenAI(
                    base_url=self.OPENROUTER_BASE_URL,
                    api_key=self.api_key,
                    default_headers={
                        "HTTP-Referer": self.site_url,
                        "X-Title": self.app_name,
                    }
                )
            except ImportError:
                raise ImportError("Please install openai: pip install openai")
        return self._client
    
    def __call__(self, messages: List[Dict[str, str]]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=8192,
        )
        
        return response.choices[0].message.content
    
    @classmethod
    def list_popular_models(cls) -> Dict[str, List[str]]:
        """Return a dict of popular models by provider"""
        return {
            "anthropic": [
                "anthropic/claude-3-opus",
                "anthropic/claude-3-sonnet",
                "anthropic/claude-3-haiku",
                "anthropic/claude-3.5-sonnet",
            ],
            "openai": [
                "openai/gpt-4-turbo",
                "openai/gpt-4",
                "openai/gpt-4o",
                "openai/gpt-4o-mini",
                "openai/o1-preview",
                "openai/o1-mini",
            ],
            "google": [
                "google/gemini-pro",
                "google/gemini-1.5-pro",
                "google/gemini-1.5-flash",
            ],
            "meta": [
                "meta-llama/llama-3-70b-instruct",
                "meta-llama/llama-3.1-405b-instruct",
            ],
            "mistral": [
                "mistralai/mistral-large",
                "mistralai/mixtral-8x22b-instruct",
            ],
        }


class MockClient(BaseLLMClient):
    """Mock client for testing without API calls"""
    
    def __init__(self, responses: Optional[List[str]] = None):
        self.responses = responses or []
        self.call_count = 0
        self.call_history = []
        self.model = "mock"
    
    def __call__(self, messages: List[Dict[str, str]]) -> str:
        self.call_history.append(messages)
        
        if self.responses:
            response = self.responses[self.call_count % len(self.responses)]
        else:
            # Generate a default response
            response = self._generate_mock_response(messages)
        
        self.call_count += 1
        return response
    
    def _generate_mock_response(self, messages: List[Dict]) -> str:
        """Generate a simple mock response"""
        last_msg = messages[-1]["content"] if messages else ""
        
        if "test" in last_msg.lower():
            return "<bash>pytest tests/</bash>\n\nRunning tests..."
        elif "read" in last_msg.lower() or "file" in last_msg.lower():
            return "<file_read>README.md</file_read>\n\nReading file..."
        elif "fix" in last_msg.lower() or "bug" in last_msg.lower():
            return "<thinking>Analyzing the issue...</thinking>\n\n<bash>git status</bash>"
        else:
            return "TASK_COMPLETE\n\nTask completed successfully."


# Model name mappings for convenience
MODEL_ALIASES = {
    # GPT-5.2 and latest OpenAI models
    "gpt-5.2": "gpt-5.2-turbo",
    "gpt5": "gpt-5.2-turbo",
    "gpt-5": "gpt-5.2-turbo",
    
    # Claude aliases
    "claude": "claude-sonnet-4-20250514",
    "claude-4": "claude-sonnet-4-20250514",
    "sonnet": "claude-sonnet-4-20250514",
    "opus": "claude-opus-4-20250514",
    
    # Gemini aliases
    "gemini": "gemini-2.0-flash",
    "gemini-flash": "gemini-2.0-flash",
    "gemini-pro": "gemini-1.5-pro",
    
    # OpenRouter shortcuts
    "openrouter": "anthropic/claude-3-sonnet",
    "llama": "meta-llama/llama-3.1-405b-instruct",
    "mixtral": "mistralai/mixtral-8x22b-instruct",
}


def create_llm_client(
    model: str = "claude-sonnet-4-20250514",
    api_key: Optional[str] = None,
    mock_responses: Optional[List[str]] = None,
    provider: Optional[str] = None,
    **kwargs
) -> Callable[[List[Dict]], str]:
    """
    Factory function to create appropriate LLM client.
    
    Args:
        model: Model name - supports:
            - Anthropic: claude-*, claude-sonnet-4, claude-opus-4
            - OpenAI: gpt-4, gpt-5.2, o1-*, o3-*
            - Google: gemini-*, gemini-2.0-flash, gemini-pro
            - OpenRouter: provider/model format (e.g., "anthropic/claude-3-opus")
            - Aliases: "claude", "gpt5", "gemini", "llama", etc.
        api_key: Optional API key (or set via environment variables)
        mock_responses: Responses for mock client
        provider: Force a specific provider ("anthropic", "openai", "google", "openrouter")
        **kwargs: Additional arguments passed to the client
    
    Environment Variables:
        ANTHROPIC_API_KEY: For Claude models
        OPENAI_API_KEY: For GPT models  
        GOOGLE_API_KEY or GEMINI_API_KEY: For Gemini models
        OPENROUTER_API_KEY: For OpenRouter models
    
    Returns:
        LLM client callable
    
    Examples:
        # Anthropic Claude
        client = create_llm_client("claude-sonnet-4-20250514")
        client = create_llm_client("claude")  # alias
        
        # OpenAI GPT-5.2
        client = create_llm_client("gpt-5.2")
        client = create_llm_client("gpt-5.2-turbo")
        
        # Google Gemini
        client = create_llm_client("gemini-2.0-flash")
        client = create_llm_client("gemini")  # alias
        
        # OpenRouter (100+ models)
        client = create_llm_client("anthropic/claude-3-opus")
        client = create_llm_client("meta-llama/llama-3.1-405b-instruct")
    """
    # Handle mock client
    if model == "mock" or mock_responses is not None:
        return MockClient(responses=mock_responses)
    
    # Resolve aliases
    model = MODEL_ALIASES.get(model.lower(), model)
    
    # Detect provider from model name or explicit provider argument
    if provider:
        provider = provider.lower()
    elif "/" in model:
        # OpenRouter format: provider/model
        provider = "openrouter"
    elif model.startswith("claude") or model.startswith("anthropic"):
        provider = "anthropic"
    elif model.startswith("gpt") or model.startswith("o1") or model.startswith("o3"):
        provider = "openai"
    elif model.startswith("gemini"):
        provider = "google"
    else:
        # Default to Anthropic
        provider = "anthropic"
    
    # Create appropriate client
    if provider == "anthropic":
        return AnthropicClient(model=model, api_key=api_key)
    
    elif provider == "openai":
        return OpenAIClient(model=model, api_key=api_key)
    
    elif provider == "google":
        return GoogleGeminiClient(model=model, api_key=api_key)
    
    elif provider == "openrouter":
        return OpenRouterClient(
            model=model, 
            api_key=api_key,
            site_url=kwargs.get("site_url"),
            app_name=kwargs.get("app_name", "Confucius-Agent")
        )
    
    else:
        raise ValueError(f"Unknown provider: {provider}")


def list_supported_models() -> Dict[str, List[str]]:
    """List all supported models by provider"""
    return {
        "anthropic": [
            "claude-sonnet-4-20250514",
            "claude-opus-4-20250514",
            "claude-3.5-sonnet",
            "claude-3-opus",
        ],
        "openai": [
            "gpt-5.2-turbo",
            "gpt-5.2",
            "gpt-4-turbo",
            "gpt-4o",
            "gpt-4o-mini",
            "o1-preview",
            "o1-mini",
            "o3-mini",
        ],
        "google": [
            "gemini-2.0-flash",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-pro",
        ],
        "openrouter": OpenRouterClient.list_popular_models(),
        "aliases": list(MODEL_ALIASES.keys()),
    }


__all__ = [
    "BaseLLMClient",
    "AnthropicClient",
    "OpenAIClient",
    "GoogleGeminiClient",
    "OpenRouterClient",
    "MockClient",
    "create_llm_client",
    "list_supported_models",
    "MODEL_ALIASES",
]
