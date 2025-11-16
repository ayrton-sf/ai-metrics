from typing import List, Callable, Awaitable
from ..claim_checking.claim_checker import ClaimChecker
from ..models.llm.llm_service import LLMService


class RetrieverChecker(ClaimChecker):
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    async def fetch_reference(
        self,
        retriever_request: Callable[[str], Awaitable[List[str]]],
        **kwargs
    ) -> List[str]:
        """
        Fetch reference documents using user-provided retriever function.
        
        Args:
            retriever_request: User's async function (query: str, **kwargs) -> List[str]
            **kwargs: Passed through to retriever_request (must include 'query')
        """
        query = kwargs.pop("query")
        documents = await retriever_request(query, **kwargs)
        return documents

    def chunk_content(self, documents: List[str]) -> List[str]:
        return documents