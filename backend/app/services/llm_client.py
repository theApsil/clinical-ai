import requests
import json
from typing import List, Dict, Any
from app.config import settings
from app.logger import logger
from app.logger import logger


class LLMClient:
    def __init__(self):
        self.api_url = settings.LLM_API_URL
        self.auth_token = settings.LLM_AUTH_TOKEN

    def _call(
        self,
        model: str,
        system_prompt: str,
        user_content: str,
        max_tokens: int = 4096,
        temperature: float = 0.01,
    ) -> str:
        payload = {
            "auth_token": self.auth_token,
            "model_name": model,
            "conversation": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_content
                }
            ],
            "generation_config": {
                "temperature": temperature,
                "max_new_tokens": max_tokens,
                "top_p": 1.0,
                "repetition_penalty": 1.0
            }
        }
        logger.info(
            f"LLM call started | model={model} | max_tokens={max_tokens}"
        )

        response = requests.post(
            self.api_url,
            json=payload,
            timeout=120
        )
        response.raise_for_status()

        data = response.json()

        return data["output"]


    def extract_guideline(self, text: str, prompt: str) -> Dict[str, Any]:
        result = self._call(
            model="qwen_3_4b",
            system_prompt="Ты медицинский эксперт.",
            user_content=prompt.replace("{{TEXT}}", text),
            max_tokens=4000
        )
        return self._safe_json(result)

    def extract_patient_facts(self, text: str, prompt: str, system_prompt: str) -> Dict[str, Any]:
        result = self._call(
            model="qwen_3_4b",
            system_prompt=system_prompt,
            user_content=prompt.replace("{{TEXT}}", text),
            max_tokens=1000
        )
        return self._safe_json(result)

    def ask_clarifying_questions(
            self,
            guideline_json: Dict[str, Any],
            patient_json: Dict[str, Any],
            prompt: str,
            system_prompt: str,
    ) -> List[str]:
        content = (
            prompt
            .replace("{{GUIDELINE_JSON}}", json.dumps(guideline_json, ensure_ascii=False))
            .replace("{{PATIENT_JSON}}", json.dumps(patient_json, ensure_ascii=False))
        )

        result = self._call(
            model="gemma_3_27b",
            system_prompt=system_prompt,
            user_content=content,
            max_tokens=800
        )

        questions = self._safe_json(result)

        if not isinstance(questions, list):
            raise ValueError("Clarifying questions must be JSON array")

        return questions

    def final_decision(
            self,
            guideline_json: Dict[str, Any],
            patient_json: Dict[str, Any],
            prompt: str,
            system_prompt: str
    ) -> str:
        content = (
            prompt
            .replace(
                "{{GUIDELINE_JSON}}",
                json.dumps(guideline_json, ensure_ascii=False, indent=2)
            )
            .replace(
                "{{PATIENT_JSON}}",
                json.dumps(patient_json, ensure_ascii=False, indent=2)
            )
        )

        return self._call(
            model="gemma_3_27b",
            system_prompt=system_prompt,
            user_content=content,
            max_tokens=1200
        )

    @staticmethod
    def _safe_json(text: str):
        import json
        import re

        if not text or not text.strip():
            raise ValueError("LLM returned empty response")

        cleaned = re.sub(r"```(?:json)?", "", text).strip("` \n")

        return json.loads(cleaned)
