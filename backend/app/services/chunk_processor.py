from typing import Dict, Any
from app.services.llm_client import LLMClient
from yandexclient import YandexLlmClient


def process_chunk(
    chunk: str,
    prompt: str
) -> Dict[str, Any]:
    llm = YandexLlmClient()
    print('test llm' + llm)
    return llm.extract_guideline(
        text=chunk,
        prompt=prompt
    )
