import requests
from typing import List, Optional
import logging
import os

logger = logging.getLogger(__name__)


class OllamaService:
    """Service for interacting with local Ollama instance for embeddings"""

    def __init__(self, base_url: str = None, model: str = "bge-m3"):
        # Read from environment variable, fallback to localhost
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model
        self.embeddings_url = f"{self.base_url}/api/embeddings"

    def generate_embedding(self, text: str, timeout: int = 10) -> Optional[List[float]]:
        """
        Generate embedding vector for given text using Ollama.

        Args:
            text: Input text to generate embedding for
            timeout: Request timeout in seconds

        Returns:
            List of floats representing the embedding vector, or None if failed
        """
        try:
            payload = {
                "model": self.model,
                "prompt": text
            }

            response = requests.post(
                self.embeddings_url,
                json=payload,
                timeout=timeout
            )

            if response.status_code == 200:
                result = response.json()
                embedding = result.get("embedding")

                if embedding and isinstance(embedding, list):
                    logger.info(f"Generated embedding for query: '{text[:50]}...' (dim: {len(embedding)})")
                    return embedding
                else:
                    logger.error(f"Invalid embedding format received from Ollama: {result}")
                    return None
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.Timeout:
            logger.error(f"Ollama request timed out after {timeout} seconds")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to Ollama service. Is it running on localhost:11434?")
            return None
        except Exception as e:
            logger.error(f"Unexpected error generating embedding: {str(e)}")
            return None

    def health_check(self) -> bool:
        """Check if Ollama service is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False


# Global instance
ollama_service = OllamaService()
