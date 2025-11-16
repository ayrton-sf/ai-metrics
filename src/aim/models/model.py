from enum import Enum

from .providers import ModelProvider


class ModelEnum(Enum):
    def __new__(cls, value, provider: ModelProvider):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.provider = provider
        return obj

    @property
    def model_name(self) -> str:
        return self.value
