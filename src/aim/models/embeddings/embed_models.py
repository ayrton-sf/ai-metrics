from ..model import ModelEnum
from ..providers import ModelProvider

class EmbedModels(ModelEnum):
    EMBEDDING_3_LARGE = (
        "text-embedding-3-large",
        ModelProvider.OPENAI,
    )
    EMBEDDING_3_SMALL = (
        "text-embedding-3-small",
        ModelProvider.OPENAI,
    )
    ADA_002 = (
        "text-embedding-ada-002",
        ModelProvider.OPENAI,
    )
    VOYAGE_3_LARGE = (
        "voyage-3-large",
        ModelProvider.VOYAGE_AI,
    )
    VOYAGE_3_5 = (
        "voyage-3.5",
        ModelProvider.VOYAGE_AI,
    )
    VOYAGE_3_5_LITE = (
        "voyage-3.5-lite",
        ModelProvider.VOYAGE_AI,
    )