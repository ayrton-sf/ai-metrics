from enum import Enum, auto


class DataSource(Enum):
    WEB = auto()
    MCP = auto()
    RETRIEVER = auto()

    @property
    def required_args(self):
        return {
            DataSource.WEB: ["urls"],
            DataSource.MCP: ["params"],
            DataSource.RETRIEVER: ["retriever_request", "query"]
        }[self]