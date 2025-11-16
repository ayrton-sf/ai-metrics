from typing import Dict, List
from ..claim_checking.claim_checker import ClaimChecker
from ..models.llm.llm_service import LLMService
from mcp import StdioServerParameters

class MCPChecker(ClaimChecker):
    def __init__(self, llm_service: LLMService, params: StdioServerParameters):
        self.llm_service = llm_service
        self.mcp_server_params = params

    async def fetch_reference(self, claims: List[str]) -> List[str]:
        reference = []
        for claim in claims:
            relevant_content = await self.llm_service.run_mcp_agent(
                input=claim, server=self.mcp_server_params
            )
            if relevant_content:
                reference.append(relevant_content)

        return reference

    def chunk_content(self, content: List[Dict]) -> List[Dict]:
        return content
