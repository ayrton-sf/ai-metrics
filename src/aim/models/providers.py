from enum import Enum


class ModelProvider(Enum):
    OPENAI = "OPENAI_API_KEY"
    ANTHROPIC = "ANTHROPIC_API_KEY"
    VOYAGE_AI = "VOYAGEAI_API_KEY"