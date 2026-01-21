from typing import Dict, Any, Optional, List
from .YandexResponse import YandexLlmRsDto, YandexUsage

class YandexLlmResponseParser:
    @staticmethod
    def parse_response(raw_response: Dict[str, Any]) -> Optional[YandexLlmRsDto]:
        result_data = raw_response['result']

        usage_data = result_data['usage']
        usage = YandexUsage(
            completionTokens=usage_data['completionTokens'],
            inputTextTokens=usage_data['inputTextTokens'],
            totalTokens=usage_data['totalTokens'],
            completionTokensDetails=usage_data.get('completionTokensDetails')
        )

        alternatives = []
        for alt_data in result_data['alternatives']:
            message = alt_data['message']
            alternative = {
                'output': message.get('text', ''),
                'role': message.get('role', '').replace('`', '')
            }
            alternatives.append(alternative)

        return YandexLlmRsDto(
            alternatives=alternatives,
            modelVersion=result_data['modelVersion'],
            usage=usage
        )