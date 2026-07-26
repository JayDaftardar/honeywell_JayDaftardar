import httpx
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List

from core.config import settings

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """
    Abstract base class for LLM providers (e.g. Ollama, Llama, Qwen, DeepSeek).
    """
    
    @abstractmethod
    async def chat_complete(self, messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 512) -> str:
        """
        Sends a chat completion request to the provider.
        Returns the raw text content of the response.
        """
        pass
        
    @abstractmethod
    async def check_health(self) -> bool:
        """
        Checks if the provider is reachable and ready.
        Returns True if healthy, False otherwise.
        """
        pass

class OllamaProvider(LLMProvider):
    """
    Implementation for Ollama using its OpenAI-compatible endpoint.
    """
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.timeout = 120.0 # Increased timeout for initial model loading into memory
        
    async def check_health(self) -> bool:
        """
        Verify Ollama is reachable before making inference requests.
        """
        # The Ollama API provides a /api/tags endpoint or simply the base URL for a simple ping.
        # But we are using the /v1 OpenAI compatible endpoint base URL (http://localhost:11434/v1).
        # We can just hit the root URL of Ollama (http://localhost:11434/) to see if it's up.
        health_url = self.base_url.replace("/v1", "") 
        if not health_url.endswith("/"):
            health_url += "/"
            
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(health_url)
                if response.status_code == 200:
                    logger.info(f"Ollama is reachable at {health_url}")
                    return True
                else:
                    logger.error(f"Ollama returned unexpected status {response.status_code} at {health_url}")
                    return False
        except httpx.RequestError as e:
            logger.error(f"Failed to reach Ollama at {health_url}. Is the service running? Error: {e}")
            return False

    async def chat_complete(self, messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 512) -> str:
        """
        Call Ollama via the OpenAI compatible endpoint.
        """
        endpoint = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer ollama" # Dummy key as requested
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(endpoint, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama API HTTP error: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error communicating with Ollama: {e}")
            raise

# Provide a factory function or default instance
def get_llm_provider() -> LLMProvider:
    # Future enhancement: logic to select provider based on config
    return OllamaProvider()
