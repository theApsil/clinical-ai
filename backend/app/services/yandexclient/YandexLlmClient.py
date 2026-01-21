import requests
from typing import List, Dict, Any
from app.config import settings
from app.logger import logger
import asyncio
import aiohttp
import json
import re
from .YandexLlmResponseParser import YandexLlmResponseParser

def _safe_json(text: str) -> Dict[str, Any]:
    if not text or not text.strip():
        raise ValueError("LLM returned empty response")

    text = text.strip()
    logger.debug(f"LLM raw response: {text[:200]}...")

    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}\nText: {text}")
        raise ValueError(f"LLM returned invalid JSON:\n{text}")

class YandexLlmClient:

    def __init__(self):
        self.api_url = settings.YANDEX_API_URL
        self.auth_token = settings.YANDEX_AUTH_TOKEN
        self.model_package = settings.YANDEX_MODEL_PACKAGE

    def _call(
            self,
            system_prompt: str,
            user_content: str,
            max_tokens: int = 4096,
            temperature: float = 0.01,
    ) -> str:
        payload = {
            "modelUri" : f"gpt://{self.model_package}/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": temperature,
                "maxTokens": max_tokens
            },
            "messages" : [
                {
                    "role": "system",
                    "text": system_prompt
                },
                {
                    "role": "user",
                    "text": user_content
                }
            ]
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self.auth_token}"
        }

        logger.info(f'START YandexLlmClient: Calling YandexLlmClient: payload={payload}')
        resource = requests.post(url=self.api_url, json=payload, headers=headers)
        resource.raise_for_status()
        body = resource.json()
        result = YandexLlmResponseParser.parse_response(body)
        logger.info(f'END YandexLlmClient: Calling YandexLlmClient: payload={payload}, result={result}')

        return result.get_first_message_text()

    def extract_guideline(self, text: str, prompt: str) -> Dict[str, Any]:
        result = self._call(
            system_prompt="Ты медицинский эксперт.",
            user_content=prompt.replace("{{TEXT}}", text),
            max_tokens=4000
        )
        return _safe_json(result)

class AsyncYandexLlmClient:
    def __init__(self, max_concurrent_requests: int = 5):
        self.api_url = settings.YANDEX_API_URL
        self.auth_token = settings.YANDEX_AUTH_TOKEN
        self.model_package = settings.YANDEX_MODEL_PACKAGE
        self.max_concurrent = max_concurrent_requests
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.timeout = aiohttp.ClientTimeout(total=300)  # 5 минут таймаут

    async def _call(
            self,
            session: aiohttp.ClientSession,
            system_prompt: str,
            user_content: str,
            max_tokens: int = 4096,
            temperature: float = 0.01,
    ) -> str:
        async with self.semaphore:
            payload = {
                "modelUri": f"gpt://{self.model_package}/yandexgpt-lite",
                "completionOptions": {
                    "stream": False,
                    "temperature": temperature,
                    "maxTokens": max_tokens
                },
                "messages": [
                    {
                        "role": "system",
                        "text": system_prompt
                    },
                    {
                        "role": "user",
                        "text": user_content
                    }
                ]
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Api-Key {self.auth_token}"
            }

            logger.info(f'START AsyncYandexLlmClient: Calling YandexLlm')
            try:
                async with session.post(
                        url=self.api_url,
                        json=payload,
                        headers=headers,
                        timeout=self.timeout
                ) as response:
                    response.raise_for_status()
                    body = await response.json()
                    result = YandexLlmResponseParser.parse_response(body)
                    logger.info(f'END AsyncYandexLlmClient: Request completed')

                    return result.get_first_message_text()
            except asyncio.TimeoutError:
                logger.error(f"Timeout error for Yandex LLM request")
                raise
            except Exception as e:
                logger.error(f"Error in Yandex LLM request: {str(e)}")
                raise

    async def extract_guideline_batch(
            self,
            chunks: List[str],
            prompt: str,
            task_id: str,
            update_callback
    ) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            tasks = []

            for i, chunk in enumerate(chunks):
                task = self._process_chunk(
                    session=session,
                    chunk=chunk,
                    prompt=prompt,
                    chunk_index=i,
                    total_chunks=len(chunks),
                    task_id=task_id,
                    update_callback=update_callback
                )
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error processing chunk {i}: {str(result)}")
                    processed_results.append({})
                else:
                    processed_results.append(result)

            return processed_results

    async def _process_chunk(
            self,
            session: aiohttp.ClientSession,
            chunk: str,
            prompt: str,
            chunk_index: int,
            total_chunks: int,
            task_id: str,
            update_callback
    ) -> Dict[str, Any]:
        try:
            result_text = await self._call(
                session=session,
                system_prompt="Ты медицинский эксперт.",
                user_content=prompt.replace("{{TEXT}}", chunk),
                max_tokens=4000
            )

            result = _safe_json(result_text)

            progress_increment = 40 / max(total_chunks, 1)
            await update_callback(
                task_id=task_id,
                progress_increment=progress_increment,
                message=f"Обработан чанк {chunk_index + 1}/{total_chunks}"
            )

            return result

        except Exception as e:
            logger.error(f"Error in chunk {chunk_index}: {str(e)}")
            raise
