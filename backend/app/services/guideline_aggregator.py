# Clinical AI
# Copyright (c) 2026 Гончарук Данил Максимович
# All rights reserved.
# Unauthorized copying, modification, or use is prohibited.
# See LICENSE file for details.

from typing import Dict, Any, List
from copy import deepcopy


class GuidelineAggregator:
    def __init__(self):
        self.result: Dict[str, Any] = {}

    def add(self, partial: Dict[str, Any]) -> None:
        """
        Добавляет частичный guideline JSON в общий результат
        """
        self.result = self._merge_dicts(self.result, partial)

    def get(self) -> Dict[str, Any]:
        """
        Возвращает итоговую агрегированную структуру
        """
        return deepcopy(self.result)


    def _merge_dicts(self, base: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        if not base:
            return deepcopy(new)

        merged = deepcopy(base)

        for key, new_value in new.items():
            if key not in merged:
                merged[key] = deepcopy(new_value)
                continue

            old_value = merged[key]

            # dict + dict → рекурсивно
            if isinstance(old_value, dict) and isinstance(new_value, dict):
                merged[key] = self._merge_dicts(old_value, new_value)

            # list + list → union
            elif isinstance(old_value, list) and isinstance(new_value, list):
                merged[key] = self._merge_lists(old_value, new_value)

            # string / scalar
            else:
                merged[key] = self._merge_scalar(old_value, new_value)

        return merged

    @staticmethod
    def _merge_lists(a: List[Any], b: List[Any]) -> List[Any]:
        result = list(a)
        for item in b:
            if item not in result:
                result.append(item)
        return result

    @staticmethod
    def _merge_scalar(old: Any, new: Any) -> Any:
        if old in (None, "", []):
            return new
        return old
