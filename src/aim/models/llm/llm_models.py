from ..model import ModelEnum
from ..providers import ModelProvider


class LLMModel(ModelEnum):
    GPT_4_O = (
        "gpt-4o",
        ModelProvider.OPENAI,
    )
    GPT_4_1 = (
        "gpt-4.1",
        ModelProvider.OPENAI,
    )
    O3 = (
        "o3",
        ModelProvider.OPENAI,
    )
    GPT_5 = (
        "gpt-5",
        ModelProvider.OPENAI,
    )
    CLAUDE_SONNET_3_5 = (
        "claude-3-5-sonnet-latest",
        ModelProvider.ANTHROPIC,
    )
    CLAUDE_SONNET_3_7 = (
        "claude-3-7-sonnet-latest",
        ModelProvider.ANTHROPIC,
    )
    CLAUDE_SONNET_4 = (
        "claude-sonnet-4-20250514",
        ModelProvider.ANTHROPIC,
    )
    CLAUDE_SONNET_4_5 = (
        "claude-sonnet-4-5-latest",
        ModelProvider.ANTHROPIC,
    )
    CLAUDE_HAIKU_4_5 = (
        "claude-haiku-4-5-20251001",
        ModelProvider.ANTHROPIC,
    )
    CLAUDE_OPUS_4_1 = (
        "claude-opus-4-1-latest",
        ModelProvider.ANTHROPIC,
    )