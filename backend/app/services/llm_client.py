import requests
from typing import List, Dict, Any
from app.config import settings


class LLMClient:
    def __init__(self):
        self.api_url = settings.LLM_API_URL
        self.auth_token = settings.LLM_AUTH_TOKEN

    def _call(
        self,
        model: str,
        system_prompt: str,
        user_content: str,
        max_tokens: int = 2048,
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

    def extract_patient_facts(self, text: str, prompt: str) -> Dict[str, Any]:
        result = self._call(
            model="qwen_3_4b",
            system_prompt="Ты медицинский NLP-парсер.",
            user_content=prompt.replace("{{TEXT}}", text),
            max_tokens=1000
        )
        return self._safe_json(result)

    def ask_clarifying_questions(
        self,
        guideline_json: Dict[str, Any],
        patient_json: Dict[str, Any],
        prompt: str
    ) -> List[str]:
        content = (
            prompt
            .replace("{{GUIDELINE_JSON}}", str(guideline_json))
            .replace("{{PATIENT_JSON}}", str(patient_json))
        )

        result = self._call(
            model="gemma_3_27b",
            system_prompt="Ты клинический ассистент.",
            user_content=content,
            max_tokens=800
        )
        return self._safe_json(result)

    def final_decision(
        self,
        guideline_json: Dict[str, Any],
        patient_json: Dict[str, Any],
        prompt: str
    ) -> str:
        content = (
            prompt
            .replace("{{GUIDELINE_JSON}}", str(guideline_json))
            .replace("{{PATIENT_JSON}}", str(patient_json))
        )

        return self._call(
            model="gemma_3_27b",
            system_prompt="Ты врач-эксперт.",
            user_content=content,
            max_tokens=1200
        )

    @staticmethod
    def _safe_json(text: str) -> Any:
        import json
        try:
            return json.loads(text)
        except Exception:
            raise ValueError(f"LLM returned invalid JSON:\n{text}")
