from typing import Dict, Any, List

from app.services.llm_client import LLMClient


class DialogManager:
    """
    Управляет диалогом врача с системой:
    1) сбор базовых данных
    2) уточняющие вопросы
    3) финальное решение
    """

    # Минимальные данные, без которых нельзя идти в LLM-вопросы
    MIN_REQUIRED_FIELDS = ["age", "symptoms"]

    def __init__(
        self,
        guideline: Dict[str, Any],
        prompts: Dict[str, str],
        system_prompts: Dict[str, str],
    ):
        self.guideline = guideline
        self.prompts = prompts
        self.system_prompts = system_prompts
        self.llm = LLMClient()

        self.patient_data: Dict[str, Any] = {}
        self.asked_questions: List[str] = []
        self.status: str = "collecting"

    def handle_message(self, message: str) -> Dict[str, Any]:
        if self.status == "done":
            return {
                "type": "info",
                "content": "Диалог завершён."
            }

        # 1️⃣ Извлекаем факты
        facts = self.llm.extract_patient_facts(
            text=message,
            prompt=self.prompts["extract_patient_facts"],
            system_prompt=self.system_prompts["extract_patient_facts"],
        )

        self._merge_patient_data(facts)

        # 2️⃣ ПРОВЕРКА: хватает ли базовых данных
        missing = [
            field for field in self.MIN_REQUIRED_FIELDS
            if not self.patient_data.get(field)
        ]

        if missing:
            questions = []

            if "age" in missing:
                questions.append("Уточните возраст пациента.")

            if "symptoms" in missing:
                questions.append("Опишите основные жалобы и симптомы пациента.")

            return {
                "type": "questions",
                "content": questions
            }

        # 3️⃣ Уточняющие вопросы через LLM
        try:
            questions = self.llm.ask_clarifying_questions(
                guideline_json=self.guideline,
                patient_json=self.patient_data,
                prompt=self.prompts["ask_clarifying_questions"],
                system_prompt=self.system_prompts["ask_clarifying_questions"],
            )
        except Exception as e:
            # Если LLM сломалась — идём в финал
            return self._final_decision()

        # Фильтруем уже заданные
        questions = [q for q in questions if q not in self.asked_questions]

        if questions:
            self.asked_questions.extend(questions)
            return {
                "type": "questions",
                "content": questions
            }

        # 4️⃣ Финальное решение
        return self._final_decision()

    def _final_decision(self) -> Dict[str, Any]:
        decision = self.llm.final_decision(
            guideline_json=self.guideline,
            patient_json=self.patient_data,
            prompt=self.prompts["final_decision"],
            system_prompt=self.system_prompts["final_decision"],
        )

        self.status = "done"

        return {
            "type": "final_decision",
            "content": decision
        }

    def _merge_patient_data(self, new_data: Dict[str, Any]) -> None:
        for key, value in new_data.items():
            if value in (None, "", [], {}):
                continue

            if key not in self.patient_data:
                self.patient_data[key] = value
            else:
                existing = self.patient_data[key]

                if isinstance(existing, list) and isinstance(value, list):
                    for item in value:
                        if item not in existing:
                            existing.append(item)
                elif existing in (None, "", []):
                    self.patient_data[key] = value
