# Clinical AI
# Copyright (c) 2026
# Борщевский Иван Олегович
# Гардаш Владислав Викторович
# Гончарук Данил Максимович
# Жеревчук Данил Алексеевич
# Курбанов Марат Муслимович
# Меркурьев Максим Алексеевич
# Назаров Максим Сергеевич
# Решетнев Никита Ярославович
# Цветков Станислав Олегович
# Шулятьев Артем Андреевич
# All rights reserved.
# Unauthorized copying, modification, or use is prohibited.
# See LICENSE file for details.

from typing import Dict, Any, List

from app.services.llm_client import LLMClient


class DialogManager:
    def __init__(
        self,
        guideline: Dict[str, Any],
        prompts: Dict[str, str]
    ):
        self.guideline = guideline
        self.prompts = prompts
        self.llm = LLMClient()

        self.patient_data: Dict[str, Any] = {}
        self.asked_questions: List[str] = []
        self.status: str = "collecting"

    def handle_message(self, message: str) -> Dict[str, Any]:
        """
        Основная точка входа:
        принимает реплику врача
        возвращает ответ системы
        """
        if self.status == "done":
            return {
                "type": "info",
                "content": "Диалог завершён."
            }

        facts = self.llm.extract_patient_facts(
            text=message,
            prompt=self.prompts["extract_patient_facts"]
        )

        self._merge_patient_data(facts)

        questions = self.llm.ask_clarifying_questions(
            guideline_json=self.guideline,
            patient_json=self.patient_data,
            prompt=self.prompts["ask_clarifying_questions"]
        )

        questions = [
            q for q in questions
            if q not in self.asked_questions
        ]

        if questions:
            self.asked_questions.extend(questions)
            return {
                "type": "questions",
                "content": questions
            }

        decision = self.llm.final_decision(
            guideline_json=self.guideline,
            patient_json=self.patient_data,
            prompt=self.prompts["final_decision"]
        )

        self.status = "done"

        return {
            "type": "final_decision",
            "content": decision
        }

    def _merge_patient_data(self, new_data: Dict[str, Any]) -> None:
        """
        Мержим извлечённые факты в patient_data
        """
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
