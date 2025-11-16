from langchain_core.embeddings.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from langchain_voyageai import VoyageAIEmbeddings
from ..providers import ModelProvider
from .embed_models import EmbedModels

class EmbeddingService:
    def __init__(self, embed_api_key: str, embed_model: str):
        self.embed_api_key = embed_api_key
        self.embed_model_name = embed_model
        self.embed_model = self._get_model_enum()
        self.client = self._get_embeddings_client()

    def _get_model_enum(self) -> EmbedModels:
        """Find the model enum matching the model name string."""
        for model in EmbedModels:
            if model.value == self.embed_model_name:
                return model
        raise ValueError(f"Unknown embedding model: {self.embed_model_name}")

    def embed(self, content: str) -> list[float]:
        return self.client.embed_query(content)
    
    def _get_embeddings_client(self) -> Embeddings:
        client_factory = {
            ModelProvider.VOYAGE_AI: lambda: VoyageAIEmbeddings(
                voyage_api_key=self.embed_api_key, 
                model=self.embed_model_name
            ),
            ModelProvider.OPENAI: lambda: OpenAIEmbeddings(
                api_key=self.embed_api_key,
                model=self.embed_model_name
            )
        }.get(self.embed_model.provider)

        return client_factory()