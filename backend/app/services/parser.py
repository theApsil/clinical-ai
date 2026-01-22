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

import pdfplumber
from typing import List


class PDFParser:
    def __init__(self):
        pass

    def parse(self, file_path: str) -> str:
        pages_text: List[str] = []

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(self._normalize(text))

        return "\n\n".join(pages_text)

    @staticmethod
    def _normalize(text: str) -> str:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return " ".join(lines)
