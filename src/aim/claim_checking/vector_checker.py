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
            retriever_request: User's async function (query: str) -> List[str]
            **kwargs: Must include 'query'. Other kwargs are filtered out.
        """
        query = kwargs.get("query")
        if not query:
            raise ValueError("query is required for retriever_request")
        # Only pass the query to the retriever, not other kwargs like 'claims'
        documents = await retriever_request(query)
        return documents

    def chunk_content(self, documents: List[str]) -> List[str]:
        return documents