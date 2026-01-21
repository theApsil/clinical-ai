# Clinical AI
# Copyright (c) 2026 Гончарук Данил Максимович
# All rights reserved.
# Unauthorized copying, modification, or use is prohibited.
# See LICENSE file for details.

from typing import List


class TextChunker:
    # TIP: 3500 - потому что это ПРИМЕРНАЯ длина одного абзаца => 1 чанк = 1 абзац
    def __init__(self, max_chunk_size: int = 3500):
        self.max_chunk_size = max_chunk_size

    def split(self, text: str) -> List[str]:
        paragraphs = self._split_to_paragraphs(text)

        chunks: List[str] = []
        current_chunk: List[str] = []
        current_size = 0

        for paragraph in paragraphs:
            p_len = len(paragraph)

            if p_len > self.max_chunk_size:
                self._flush(chunks, current_chunk)
                chunks.extend(self._hard_split(paragraph))
                current_size = 0
                continue

            if current_size + p_len > self.max_chunk_size:
                self._flush(chunks, current_chunk)
                current_chunk = [paragraph]
                current_size = p_len
            else:
                current_chunk.append(paragraph)
                current_size += p_len

        self._flush(chunks, current_chunk)
        return chunks

    @staticmethod
    def _split_to_paragraphs(text: str) -> List[str]:
        return [p.strip() for p in text.split("\n\n") if p.strip()]

    @staticmethod
    def _hard_split(text: str, size: int = 3500) -> List[str]:
        return [text[i:i + size] for i in range(0, len(text), size)]

    @staticmethod
    def _flush(chunks: List[str], current_chunk: List[str]):
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk.clear()
