from typing import Dict, Any
from app.services.llm_client import LLMClient


def process_chunk(
    chunk: str,
    prompt: str
) -> Dict[str, Any]:
    llm = LLMClient()
    return llm.extract_guideline(
        text=chunk,
        prompt=prompt
    )
