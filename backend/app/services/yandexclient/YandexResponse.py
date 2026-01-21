from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime

"""
Общая информация по запросу в API Яндекса
"""
@dataclass
class YandexUsage:
    completionTokens: str
    inputTextTokens: str
    totalTokens: str
    completionTokensDetails: Optional[Dict[str, Any]] = None

    def to_int_dict(self) -> Dict[str, int]:
        return {
            'completionTokens': int(self.completionTokens),
            'inputTextTokens': int(self.inputTextTokens),
            'totalTokens': int(self.totalTokens)
        }


@dataclass
class YandexLlmRsDto:
    alternatives: List[Dict[str, Any]]
    modelVersion: str
    usage: YandexUsage
    timestamp: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def get_first_alternative(self) -> Dict[str, Any]:
        return self.alternatives[0] if self.alternatives else None

    def get_first_message_text(self) -> str:
        if self.alternatives:
            return self.alternatives[0].get('output', '')
        return ''

    def get_first_message_role(self) -> str:
        if self.alternatives:
            return self.alternatives[0].get('role', '')
        return ''